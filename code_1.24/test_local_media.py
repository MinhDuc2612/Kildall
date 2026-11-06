"""Media lane gates using temp files and a localhost stub: no model or network."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading

from local_lanes import LaneDown
import local_media


class Stub(BaseHTTPRequestHandler):
    seen, reply = None, {"images": ["View/local/raw/a.png"]}

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        session = self.path.endswith("GetNewSession")
        if not session:
            Stub.seen = body
        data = json.dumps({"session_id": "s"} if session else Stub.reply).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def main():
    with tempfile.TemporaryDirectory() as directory:
        picture = Path(directory) / "a.png"
        picture.write_bytes(b"\x89PNG")
        prompt = f"Read this: {picture} please"
        assert local_media.input_file(prompt, local_media.IMAGES) == picture
        assert local_media.input_file(prompt, local_media.AUDIO) is None
        assert local_media.input_file("no file here", local_media.IMAGES) is None
        spaced = Path(directory) / "my photo 1.png"
        spaced.write_bytes(b"\x89PNG")
        for text in (f"Look at {spaced} now", f"Look at '{spaced}'", f"Look at {spaced}."):
            assert local_media.input_file(text, local_media.IMAGES) == spaced, text
        plain = [dict(role="user", content=prompt)]
        assert local_media.vision("translation", plain, prompt) is plain
        parts = local_media.vision("document_ocr", plain, prompt)[-1]["content"]
        assert parts[0]["text"] == prompt and parts[1]["image_url"]["url"].startswith("data:image/png;base64,")
        recalled = [dict(role="user", content=f"Describe it.\n\n<memory>\n{picture}\n</memory>")]
        try:
            local_media.vision("document_ocr", recalled, "Describe it.")
        except LaneDown:
            pass
        else:
            raise AssertionError("An image named only in recalled memory must not be used")
        http = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        server = dict(kind="swarm", name="swarm", url=f"http://127.0.0.1:{http.server_port}", output="/out",
                      image=dict(model="i"), video=dict(videomodel="v"))
        assert local_media.run(server, "image_generation", "a cat") == "Saved: /out/raw/a.png"
        assert Stub.seen["model"] == "i" and "videomodel" not in Stub.seen
        local_media.run(server, "video_generation", f"animate {picture}")
        assert Stub.seen["videomodel"] == "v" and Stub.seen["initimagecreativity"] == 0
        Stub.reply = {"error": "broken"}
        try:
            local_media.run(server, "image_generation", "a cat")
        except LaneDown as error:
            assert "broken" in str(error)
        else:
            raise AssertionError("A SwarmUI error must raise LaneDown")
        http.shutdown()
        http.server_close()
    assert local_media.spoken('Say "hi there" now') == "hi there"
    assert local_media.spoken("Read this aloud: Hello.") == "Hello."
    assert local_media.spoken("Say hello") == "Say hello"
    try:
        local_media.run(dict(kind="whisper", name="w"), "speech_recognition", "transcribe nothing")
    except LaneDown as error:
        assert "audio file" in str(error)
    else:
        raise AssertionError("Speech recognition without a file must raise LaneDown")
    print("local media gates: OK")


if __name__ == "__main__":
    main()
