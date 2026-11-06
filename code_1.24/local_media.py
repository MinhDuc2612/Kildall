"""Image, video, speech and vision jobs on local tools (sample 1.24). No cloud, no new models."""

import base64
import json
import mimetypes
from pathlib import Path
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

from local_lanes import LaneDown

IMAGES = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO = {".wav", ".mp3", ".m4a", ".aiff", ".flac", ".ogg"}
VISION_JOBS = {"document_ocr", "visual_grounding"}
STARTS = re.compile(r"(?:^|(?<=[\s'\"]))[~/]")
ENDS = re.compile(r"\.[A-Za-z0-9]{2,5}(?=$|[\s'\",;:).])")


def input_file(prompt, kinds):
    """Return the first existing file named in the prompt with one of these suffixes. Paths may hold spaces."""
    for start in STARTS.finditer(prompt):
        rest = prompt[start.start():]
        for end in ENDS.finditer(rest):
            path = Path(rest[:end.end()]).expanduser()
            if path.suffix.lower() in kinds and path.is_file():
                return path
    return None


def data_uri(path):
    kind = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{kind};base64,{base64.b64encode(path.read_bytes()).decode()}"


def vision(category, messages, request):
    """Attach the image named in the user's request, never one named in recalled memory."""
    if category not in VISION_JOBS:
        return messages
    image = input_file(request, IMAGES)
    if image is None:
        raise LaneDown("Name an image file in your request.")
    return [*messages[:-1], dict(role="user", content=[
        dict(type="text", text=messages[-1]["content"]), dict(type="image_url", image_url=dict(url=data_uri(image)))])]


def post(url, data, timeout):
    request = urllib.request.Request(url, json.dumps(data).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise LaneDown(f"{url} refused the request: {error.read(300).decode(errors='replace')}") from error


def swarm(server, category, prompt):
    base = server["url"].rstrip("/")
    settings = dict(server["image"], prompt=prompt, images=1)
    if category == "video_generation":
        settings.update(server["video"])
        image = input_file(prompt, IMAGES)
        if image:
            settings.update(initimage=data_uri(image), initimagecreativity=0)
    session = post(f"{base}/API/GetNewSession", {}, 30)["session_id"]
    result = post(f"{base}/API/GenerateText2Image", dict(settings, session_id=session), 3600)
    if result.get("error") or not result.get("images"):
        raise LaneDown(f"SwarmUI made nothing: {result.get('error', 'no file returned')}")
    name = result["images"][-1].removeprefix("View/local/")
    return "Saved: " + str(Path(server["output"]).expanduser() / name)


def whisper(server, prompt):
    audio = input_file(prompt, AUDIO)
    if audio is None:
        raise LaneDown("Name an audio file in your request.")
    with tempfile.TemporaryDirectory() as directory:
        wav = Path(directory) / "input.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(audio), "-ar", "16000", "-ac", "1", str(wav)],
                       check=True)
        done = subprocess.run([server["binary"], "-nt", "-m", server["model"], "-f", str(wav)],
                              capture_output=True, text=True, check=True)
    return done.stdout.strip()


def spoken(prompt):
    """Return the words to say: quoted text, else what follows the first colon, else the whole request."""
    quoted = re.search(r'"([^"]+)"', prompt)
    return quoted.group(1) if quoted else prompt.split(":", 1)[-1].strip() or prompt


def kokoro(server, prompt):
    stem = Path(server["output"]).expanduser() / f"speech-{int(time.time())}"
    stem.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([*server["command"], "--model", server["model"], "--text",
                    spoken(prompt), "--file_prefix", str(stem),
                    "--audio_format", "wav", "--voice", server["voice"]],
                   check=True, capture_output=True, text=True)
    made = sorted(stem.parent.glob(stem.name + "*"))
    if not made:
        raise LaneDown("Kokoro made no audio file")
    return f"Saved: {made[0]}"


def run(server, category, prompt):
    """Run one media job and return the text or the saved file path."""
    try:
        if server["kind"] == "swarm":
            return swarm(server, category, prompt)
        return (whisper if server["kind"] == "whisper" else kokoro)(server, prompt)
    except subprocess.CalledProcessError as error:
        raise LaneDown(f"{server['name']} failed: {(error.stderr or '')[-300:]}") from error
