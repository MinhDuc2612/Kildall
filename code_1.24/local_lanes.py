"""Send Lane B/C text work to local OpenAI-compatible servers (sample 1.24 lanes)."""

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TIMEOUT = 1800  # Longest silence between stream events; prefill can take minutes.
HINT = (" Each model step here takes minutes. Use as few tool calls as you can and answer as soon as you "
        "have enough. Do not change files unless the user asks. run_command takes one plain command, with no ; or &&.")
LAST_TURN = "\n\nNo tool calls remain. Answer now."
NO_TOOLS = "Tools are no longer available. Write your final answer now in plain text, using what you already have."
RECOVERY_TRIES, RECOVERY_WAIT = 24, 5  # Up to 2 minutes for memory to come back.
OCR_CHARS = 1500  # ponytail: longer pages print as read; Lane A replies stop at 512 tokens.


class LaneDown(RuntimeError):
    """The configured local server did not answer."""


def endpoint(config, skill):
    """Return the local server for a routed skill, or None when the skill has none."""
    local = config.get("lanes", {}).get("local", {})
    name = local.get("skills", {}).get(skill)
    if name is None:
        return None
    server = dict(local["servers"][name], name=name)
    # Trust boundary: Lane B/C are local-only, so a prompt must never leave this machine.
    if "url" in server and urllib.parse.urlsplit(server["url"]).hostname not in ("127.0.0.1", "localhost"):
        raise ValueError(f"Local lane server {name} must use a loopback address")
    return server


def ensure_up(server, log, *, tries=120, wait=2):
    """Start a stopped server from its configured command and wait until it answers."""
    if "url" not in server:
        return
    url = server["url"].rstrip("/") + "/models"

    def up():
        try:
            with urllib.request.urlopen(url, timeout=3):
                return True
        except urllib.error.HTTPError:
            return True  # It answered, so it is up.
        except (urllib.error.URLError, OSError):
            return False

    if up():
        return
    with open(log, "ab") as output:
        subprocess.Popen(server["start"], shell=True, stdin=subprocess.DEVNULL, stdout=output,
                         stderr=output, start_new_session=True)
    for _ in range(tries):
        if up():
            return
        time.sleep(wait)
    raise LaneDown(f"{server['name']} did not start. See {log}")


def named_files(prompt, project, limit=3):
    """Return project files the prompt names, so a slow model skips the calls that find them."""
    root = Path(project).resolve()
    found = []
    for name in dict.fromkeys(re.findall(r"[\w./-]+\.\w+", prompt)):
        path = (root / name).resolve()
        if path.is_file() and path.is_relative_to(root):
            found.append(str(path))
    return found[:limit]


def window(server):
    """fit_messages limits for a job: the server's context, with room for a full reply."""
    room = dict(room=server.get("max_tokens", 2048))
    return dict(room, limit=server["context_tokens"]) if "context_tokens" in server else room


def over(server, messages, content):
    """True when a new tool result would not fit. Lane A has stopped, so this estimates at 3 characters a token."""
    used = sum(len(json.dumps(message)) for message in messages if isinstance(message.get("content"), str)) + len(content)
    return "context_tokens" in server and used / 3 + server.get("max_tokens", 2048) > server["context_tokens"]


def read_ahead(read, paths, budget):
    """Yield (args, result) for each piece of the named files, until they end or the character budget runs out."""
    for path in paths:
        start = 1
        while budget > 0:
            args = dict(path=path, start_line=start, max_lines=200)
            result = read(args)
            if result is None:
                break
            yield args, result
            budget -= len(json.dumps(result))
            lines = result.get("text", "").count("\n")
            if not result.get("truncated") or not lines:
                break
            start += lines


def finished_step(name, args, result, number):
    """A tool call and its result, shown as done: a model given only pasted text still spends a turn reading."""
    call = dict(id=f"call_{name}_{number}", type="function", function=dict(name=name, arguments=json.dumps(args)))
    return [dict(role="assistant", content="", tool_calls=[call]),
            dict(role="tool", tool_call_id=call["id"], content=json.dumps(result))]


def stop_servers(config, keep=None):
    """Stop the local servers that say how, except `keep`; only one big model fits in memory."""
    for name, server in config.get("lanes", {}).get("local", {}).get("servers", {}).items():
        if "stop" in server and name != keep:
            subprocess.run(server["stop"], shell=True, stdin=subprocess.DEVNULL, capture_output=True, timeout=60)


def warm_later(code_dir):
    """Reload Lane A in the background after a big job, so the next job does not wait for it."""
    with open(Path(code_dir) / ".session" / "warm.log", "ab") as output:
        subprocess.Popen([sys.executable, str(Path(code_dir) / "kildall.py"), "--warm"], cwd=code_dir,
                         stdin=subprocess.DEVNULL, stdout=output, stderr=output, start_new_session=True)


def plain(text):
    """Keep only prose: with no tools declared, a model can still write a tool call as text."""
    return text.split("<tool_call>")[0].strip() or "Stopped at the tool limit. Try a smaller request."


def turns(server):
    """Allowed tool rounds plus one last turn for the answer."""
    return server.get("tool_rounds", 7) + 1


def collect(lines, on_text=None):
    """Join a chat completion event stream into the plain reply shape, showing text as it arrives."""
    content, calls, finish = "", {}, None
    for line in lines:
        if not line.startswith(b"data:"):
            continue
        data = line[5:].strip()
        if data == b"[DONE]":
            break
        event = json.loads(data)
        if "error" in event:
            raise ValueError(str(event["error"]))
        choice = event["choices"][0]
        finish = choice.get("finish_reason") or finish
        delta = choice.get("delta") or {}
        text = delta.get("content") or ""
        content += text
        if text and on_text:
            on_text(text)
        for part in delta.get("tool_calls") or []:
            call = calls.setdefault(part.get("index", 0), dict(type="function", function=dict(name="", arguments="")))
            call["id"] = part.get("id") or call.get("id")
            call["function"]["name"] += (part.get("function") or {}).get("name") or ""
            call["function"]["arguments"] += (part.get("function") or {}).get("arguments") or ""
    if finish == "length":  # Keep what a slow model already wrote; a half tool call cannot run.
        content, calls, finish = content + "\n\n[Stopped at the reply limit.]", {}, "stop"
    return dict(choices=[dict(finish_reason=finish, message=dict(
        role="assistant", content=content, tool_calls=[calls[i] for i in sorted(calls)]))])


def reply(server, messages, tools=None, *, timeout=TIMEOUT, wait=RECOVERY_WAIT, on_text=None):
    """Return a validated assistant message. Raises LaneDown with the reason."""
    from cloud import validate_message

    body = dict(model=server["model"], messages=messages, temperature=0,
                max_tokens=server.get("max_tokens", 2048), stream=True)
    if tools:
        body.update(tools=tools, tool_choice="auto", parallel_tool_calls=False)
    request = urllib.request.Request(server["url"].rstrip("/") + "/chat/completions", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"})
    for attempt in range(RECOVERY_TRIES):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return validate_message(collect(response, on_text), tools or [])
        except urllib.error.HTTPError as error:
            detail = error.read(300).decode(errors="replace")
            if error.code != 503 or attempt + 1 == RECOVERY_TRIES:
                raise LaneDown(f"{server['name']} refused the request: {detail}") from error
            time.sleep(wait)  # Memory is still being released by the previous model.
        except ValueError as error:
            raise LaneDown(f"{server['name']} returned an invalid reply: {error}") from error
        except (urllib.error.URLError, OSError) as error:
            raise LaneDown(f"{server['name']} is not answering. Start it with: {server['start']}") from error
