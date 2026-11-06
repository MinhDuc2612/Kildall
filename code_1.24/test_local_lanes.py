"""Local lane gates using a localhost stub only: no model, network or paid calls."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
from unittest.mock import patch

import kildall
import local_lanes


class Stub(BaseHTTPRequestHandler):
    seen = None
    busy = 0

    def do_POST(self):
        Stub.seen = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if Stub.busy:
            Stub.busy -= 1
            self.send_response(503)
            self.send_header("Content-Length", "4")
            self.end_headers()
            self.wfile.write(b"full")
            return
        events = [{"choices": [{"delta": {"role": "assistant", "content": "o"}, "finish_reason": None}]},
                  {"choices": [{"delta": {"content": "k"}, "finish_reason": None}]},
                  {"choices": [{"delta": {}, "finish_reason": "stop"}]}]
        data = "".join(f"data: {json.dumps(e)}\n\n" for e in events).encode() + b"data: [DONE]\n\n"
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def config(url):
    return {"lanes": {"local": {"skills": {"deep_research": "flash"},
                                "servers": {"flash": {"url": url, "model": "m", "start": "run me"}}}}}


def main():
    http = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{http.server_port}/v1"
    conf = config(url)
    assert local_lanes.endpoint({}, "deep_research") is None
    assert local_lanes.endpoint({"lanes": {}}, "deep_research") is None
    assert local_lanes.endpoint(conf, "translation") is None
    server = local_lanes.endpoint(conf, "deep_research")
    assert server["name"] == "flash"
    assert local_lanes.reply(server, [{"role": "user", "content": "hi"}])["content"] == "ok"
    assert Stub.seen["model"] == "m" and Stub.seen["messages"][0]["content"] == "hi"
    tools = [{"type": "function", "function": {"name": "t", "parameters": {"type": "object", "properties": {}}}}]
    local_lanes.reply(server, [], tools)
    assert Stub.seen["tools"] == tools and Stub.seen["parallel_tool_calls"] is False
    shown = []
    assert local_lanes.reply(server, [], on_text=shown.append)["content"] == "ok" and shown == ["o", "k"]
    call = {"index": 0, "id": "call_1", "function": {"name": "t", "arguments": '{"a"'}}
    more = {"index": 0, "function": {"arguments": ":1}"}}
    lines = [b"data: " + json.dumps({"choices": [{"delta": {"tool_calls": [part]}, "finish_reason": None}]}).encode() + b"\n"
             for part in (call, more)] + [b'data: {"choices": [{"delta": {}, "finish_reason": "tool_calls"}]}\n']
    joined = local_lanes.collect(lines)["choices"][0]
    assert joined["message"]["tool_calls"] == [{"type": "function", "id": "call_1",
                                                "function": {"name": "t", "arguments": '{"a":1}'}}]
    cut = local_lanes.collect([b'data: {"choices": [{"delta": {"content": "half"}, "finish_reason": "length"}]}\n'])
    assert cut["choices"][0]["finish_reason"] == "stop" and "half" in cut["choices"][0]["message"]["content"]
    with tempfile.TemporaryDirectory() as directory:
        (Path(directory) / "algo.py").write_text("x")
        names = local_lanes.named_files("Read algo.py and ../outside.py and missing.py", directory)
        assert [Path(name).name for name in names] == ["algo.py"]
    assert local_lanes.turns({"tool_rounds": 4}) == 5 and local_lanes.turns({}) == 8
    assert local_lanes.plain("O(n)\n\n<tool_call>\n<function=x>") == "O(n)"
    assert "tool limit" in local_lanes.plain("<tool_call>\n<function=x>")
    with tempfile.TemporaryDirectory() as directory:
        mark = Path(directory) / "stopped"
        local_lanes.stop_servers({"lanes": {"local": {"servers": {"a": {"stop": f"touch {mark}"}, "b": {}}}}})
        assert mark.exists()
        kept = Path(directory) / "kept"
        servers = {"a": {"stop": f"touch {kept}"}}
        local_lanes.stop_servers({"lanes": {"local": {"servers": servers}}}, keep="a")
        assert not kept.exists()
    step = local_lanes.finished_step("read_image", {"path": "p"}, {"text": "t"}, 2)
    assert step[0]["tool_calls"][0]["id"] == step[1]["tool_call_id"] == "call_read_image_2"
    assert json.loads(step[0]["tool_calls"][0]["function"]["arguments"]) == {"path": "p"}
    big = {"context_tokens": 1000, "max_tokens": 100}
    assert local_lanes.window(big) == {"limit": 1000, "room": 100} and local_lanes.window({}) == {"room": 2048}
    picture = [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": "x" * 99999}}]}]
    assert not local_lanes.over(big, picture, "x")  # An image in the request is not text to count.
    assert not local_lanes.over(big, [], "x" * 2600) and local_lanes.over(big, [], "x" * 2800)
    assert not local_lanes.over({}, [], "x" * 99999)
    pages = {1: dict(text="a\nb\n", truncated=True), 3: dict(text="c\n", truncated=False)}
    asked = []

    def read(args):
        asked.append(args["start_line"])
        return None if args["path"] == "bad" else pages[args["start_line"]]

    pieces = list(local_lanes.read_ahead(read, ["bad", "f"], 9999))
    assert asked == [1, 1, 3] and [args["path"] for args, _ in pieces] == ["f", "f"]
    assert len(list(local_lanes.read_ahead(read, ["f"], 1))) == 1  # The budget stops further pages.
    sent = []

    def counted(endpoint, body, **_):
        if endpoint.endswith("/apply-template"):
            sent.append(body["messages"])
            return {"prompt": "p"}
        return {"tokens": [0] * 3000}

    with patch.object(kildall, "json_request", side_effect=counted):
        conf_big = dict(runtime=dict(port=1, embedding_port=2, context_size=4096))
        user = [dict(role="user", content="u")]
        assert kildall.fit_messages(conf_big, "s", "m", [], user, limit=8192, room=2048)[-1]["role"] == "user"
        for limit in (None, 3000):
            try:
                kildall.fit_messages(conf_big, "s", "", [], user, limit=limit, room=2048 if limit is None else 512)
            except kildall.ContextOverflow as error:
                assert f"{limit or 4096:,}-token" in str(error)
            else:
                raise AssertionError("A prompt over the limit must overflow")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        database = root / "k.db"
        settings = dict(paths=dict(code_dir=root, db_path=database), runtime=dict(parallel=3, port=1))
        assert not kildall.busy(database)
        with kildall.activity(database), patch("router_warmth.stop_monitor") as stop:
            assert kildall.busy(database)
            kildall.ensure_runtime(settings, stop=True, idle=True)
            stop.assert_not_called()  # An idle stop must never hit a running turn.
        with patch("router_warmth.stop_monitor") as stop:
            kildall.ensure_runtime(settings, stop=True, idle=True)
            stop.assert_called_once()
    import subagents, urllib.error
    loading = urllib.error.HTTPError("http://x/slots", 503, "Loading model", {}, None)
    with patch.object(kildall, "json_request", side_effect=loading):
        subagents.wait_idle(dict(runtime=dict(port=1)), 1)  # A server still loading must not fail the job.
    Stub.busy = 2
    assert local_lanes.reply(server, [], wait=0)["content"] == "ok"  # Retries while memory recovers.
    Stub.busy = local_lanes.RECOVERY_TRIES
    try:
        local_lanes.reply(server, [], wait=0)
    except local_lanes.LaneDown as error:
        assert "full" in str(error)
    else:
        raise AssertionError("A server that stays full must raise LaneDown")
    local_lanes.ensure_up(server, "/dev/null", tries=1, wait=0)  # Already up: starts nothing.
    http.shutdown()
    http.server_close()
    try:
        local_lanes.ensure_up(dict(server, start="true"), "/dev/null", tries=1, wait=0)
    except local_lanes.LaneDown as error:
        assert "did not start" in str(error)
    else:
        raise AssertionError("A server that never comes up must raise LaneDown")
    try:
        local_lanes.reply(server, [], timeout=2)
    except local_lanes.LaneDown as error:
        assert "run me" in str(error)
    else:
        raise AssertionError("Stopped server must raise LaneDown")
    for bad in ("https://example.com/v1", "http://192.168.1.5:8000/v1"):
        try:
            local_lanes.endpoint(config(bad), "deep_research")
        except ValueError:
            continue
        raise AssertionError("Non-loopback server must be refused")
    print("local lane gates: OK")


if __name__ == "__main__":
    main()
