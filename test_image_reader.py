"""Native file-image OCR check; draws a bitmap, never captures a screen."""

import ctypes as C
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import image_reader as reader


def text_image(path, text):
    libraries, _ = reader._native()
    cf, cg, imageio = (libraries[name] for name in ("CoreFoundation", "CoreGraphics", "ImageIO"))
    P, bind = reader.P, reader._bind

    class Point(C.Structure):
        _fields_ = [("x", C.c_double), ("y", C.c_double)]

    class Size(C.Structure):
        _fields_ = [("width", C.c_double), ("height", C.c_double)]

    class Rect(C.Structure):
        _fields_ = [("origin", Point), ("size", Size)]

    bind(cg, "CGColorSpaceCreateDeviceRGB", P)
    bind(cg, "CGBitmapContextCreate", P, P, C.c_size_t, C.c_size_t, C.c_size_t, C.c_size_t, P, C.c_uint)
    bind(cg, "CGContextSetRGBFillColor", None, P, C.c_double, C.c_double, C.c_double, C.c_double)
    bind(cg, "CGContextFillRect", None, P, Rect)
    bind(cg, "CGContextSelectFont", None, P, C.c_char_p, C.c_double, C.c_int)
    bind(cg, "CGContextShowTextAtPoint", None, P, C.c_double, C.c_double, C.c_char_p, C.c_size_t)
    bind(cg, "CGBitmapContextCreateImage", P, P)
    bind(cf, "CFURLCreateFromFileSystemRepresentation", P, P, C.c_char_p, C.c_long, C.c_bool)
    bind(cf, "CFStringCreateWithCString", P, P, C.c_char_p, C.c_uint)
    bind(imageio, "CGImageDestinationCreateWithURL", P, P, P, C.c_size_t, P)
    bind(imageio, "CGImageDestinationAddImage", None, P, P, P)
    bind(imageio, "CGImageDestinationFinalize", C.c_bool, P)
    retained = []
    try:
        color = cg.CGColorSpaceCreateDeviceRGB()
        retained.append(color)
        context = cg.CGBitmapContextCreate(None, 1024, 180, 8, 4096, color, 1)
        assert context
        retained.append(context)
        cg.CGContextSetRGBFillColor(context, 1, 1, 1, 1)
        cg.CGContextFillRect(context, Rect(Point(0, 0), Size(1024, 180)))
        cg.CGContextSetRGBFillColor(context, 0, 0, 0, 1)
        cg.CGContextSelectFont(context, b"Helvetica", 56, 1)  # kCGEncodingMacRoman, not glyph indices.
        cg.CGContextShowTextAtPoint(context, 32, 72, text, len(text))
        image = cg.CGBitmapContextCreateImage(context)
        assert image
        retained.append(image)
        filename = os.fsencode(path)
        url = cf.CFURLCreateFromFileSystemRepresentation(None, filename, len(filename), False)
        retained.append(url)
        kind = cf.CFStringCreateWithCString(None, b"public.png", 0x08000100)
        retained.append(kind)
        destination = imageio.CGImageDestinationCreateWithURL(url, kind, 1, None)
        assert destination
        retained.append(destination)
        imageio.CGImageDestinationAddImage(destination, image, None)
        assert imageio.CGImageDestinationFinalize(destination)
        assert path.is_file() and path.stat().st_size > 0
    finally:
        for item in reversed(retained):
            if item:
                cf.CFRelease(item)


def main():
    with tempfile.TemporaryDirectory(prefix="kildall-image-") as directory:
        root = Path(directory)
        image = root / "text.png"
        text_image(image, b"ORBI LOCAL TEXT 12345")
        result = reader.read_image(image)
        assert (result["width"], result["height"]) == (1024, 180), result
        assert result["text"] == "ORBI LOCAL TEXT 12345", result
        assert result["scene_understanding"].startswith("unavailable")
        assert not result["text_truncated"] and result["frame_count"] == 1
        with patch.object(reader, "MAX_TEXT", 8):
            limited = reader.read_image(image)
        assert limited["text"] == "ORBI LOC" and limited["text_truncated"]
        with patch.object(reader, "MAX_PIXELS", 1):
            try:
                reader.read_image(image)
            except ValueError:
                pass
            else:
                raise AssertionError("Oversized image was decoded")
        blank = root / "blank.png"
        text_image(blank, b"")
        assert reader.read_image(blank)["text"] == ""
        invalid = root / "invalid.png"
        invalid.write_bytes(b"This is not an image")
        fifo = root / "fifo"
        os.mkfifo(fifo)
        for path, expected in ((invalid, ValueError), (fifo, PermissionError)):
            try:
                reader.read_image(path)
            except expected:
                pass
            else:
                raise AssertionError(f"Invalid image accepted: {path}")
    print("PASS: ImageIO dimensions, exact Vision OCR, OCR/pixel limits, blank image, invalid file and FIFO rejection; scene understanding explicitly unavailable")


if __name__ == "__main__":
    main()
