"""Decode local image files with ImageIO and extract text with macOS Vision."""

import ctypes as C
from functools import lru_cache
import os
from pathlib import Path
import stat

P = C.c_void_p
MAX_BYTES = 32_000_000
MAX_PIXELS = 40_000_000
MAX_TEXT = 100_000


def _bind(library, name, result, *arguments):
    function = getattr(library, name)
    function.restype, function.argtypes = result, arguments
    return function


@lru_cache(maxsize=1)
def _native():
    libraries = {name: C.CDLL(f"/System/Library/Frameworks/{name}.framework/{name}")
                 for name in ("Foundation", "CoreFoundation", "ImageIO", "CoreGraphics", "Vision")}
    objc = C.CDLL("/usr/lib/libobjc.A.dylib")
    _bind(objc, "objc_getClass", P, C.c_char_p)
    _bind(objc, "sel_registerName", P, C.c_char_p)
    cf, imageio, cg = (libraries[name] for name in ("CoreFoundation", "ImageIO", "CoreGraphics"))
    _bind(cf, "CFDataCreate", P, P, P, C.c_long)
    _bind(cf, "CFRelease", None, P)
    _bind(cf, "CFDictionaryGetValue", P, P, P)
    _bind(cf, "CFNumberGetValue", C.c_bool, P, C.c_int, P)
    _bind(imageio, "CGImageSourceCreateWithData", P, P, P)
    _bind(imageio, "CGImageSourceCopyPropertiesAtIndex", P, P, C.c_size_t, P)
    _bind(imageio, "CGImageSourceCreateImageAtIndex", P, P, C.c_size_t, P)
    _bind(imageio, "CGImageSourceGetCount", C.c_size_t, P)
    _bind(cg, "CGImageGetWidth", C.c_size_t, P)
    _bind(cg, "CGImageGetHeight", C.c_size_t, P)
    return libraries, objc


def _send(receiver, selector, result=P, *arguments):
    """Call fixed Objective-C methods with their actual ABI, without PyObjC."""
    _, objc = _native()
    types = [argument[0] for argument in arguments]
    values = [argument[1] for argument in arguments]
    function = C.CFUNCTYPE(result, P, P, *types)(C.cast(objc.objc_msgSend, P).value)
    return function(receiver, objc.sel_registerName(selector.encode()), *values)


def read_image(path):
    """Read one regular file; return decoded dimensions and actual OCR, never a scene guess."""
    path = Path(os.path.abspath(os.path.expanduser(os.fspath(path))))
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise PermissionError("Image input must be a regular file")
        if info.st_size > MAX_BYTES:
            raise ValueError(f"Image exceeds {MAX_BYTES} bytes")
        data = stream.read(MAX_BYTES + 1)
    if not data or len(data) > MAX_BYTES:
        raise ValueError("Image is empty or exceeds the input limit")

    libraries, objc = _native()
    cf, imageio, cg = (libraries[name] for name in ("CoreFoundation", "ImageIO", "CoreGraphics"))
    pool = _send(objc.objc_getClass(b"NSAutoreleasePool"), "new")
    retained, objects = [], []
    try:
        buffer = C.create_string_buffer(data)
        native_data = cf.CFDataCreate(None, buffer, len(data))
        if not native_data:
            raise RuntimeError("Could not allocate native image data")
        retained.append(native_data)
        source = imageio.CGImageSourceCreateWithData(native_data, None)
        if not source:
            raise ValueError("ImageIO could not decode this file")
        retained.append(source)
        properties = imageio.CGImageSourceCopyPropertiesAtIndex(source, 0, None)
        if not properties:
            raise ValueError("ImageIO could not read image dimensions")
        retained.append(properties)

        def property_number(name, default=0):
            key = P.in_dll(imageio, name).value
            value = cf.CFDictionaryGetValue(properties, key)
            number = C.c_longlong()
            return number.value if value and cf.CFNumberGetValue(value, 4, C.byref(number)) else default

        width = property_number("kCGImagePropertyPixelWidth")
        height = property_number("kCGImagePropertyPixelHeight")
        orientation = property_number("kCGImagePropertyOrientation", 1)
        if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
            raise ValueError(f"Image dimensions must contain at most {MAX_PIXELS} pixels")
        if not 1 <= orientation <= 8:
            raise ValueError("Invalid image orientation")
        # ponytail: first frame only; add explicit frame selection when animated-image reading is needed.
        image = imageio.CGImageSourceCreateImageAtIndex(source, 0, None)
        if not image:
            raise ValueError("ImageIO failed to decode image pixels")
        retained.append(image)
        if (cg.CGImageGetWidth(image), cg.CGImageGetHeight(image)) != (width, height):
            raise ValueError("Decoded image dimensions differ from its metadata")
        request = _send(objc.objc_getClass(b"VNRecognizeTextRequest"), "new")
        if not request:
            raise RuntimeError("Vision text recognition is unavailable")
        objects.append(request)
        _send(request, "setRecognitionLevel:", None, (C.c_long, 0))  # accurate
        _send(request, "setUsesLanguageCorrection:", None, (C.c_bool, False))
        _send(request, "setAutomaticallyDetectsLanguage:", None, (C.c_bool, True))
        options = _send(objc.objc_getClass(b"NSDictionary"), "dictionary")
        handler = _send(objc.objc_getClass(b"VNImageRequestHandler"), "alloc")
        handler = _send(handler, "initWithCGImage:orientation:options:", P,
                        (P, image), (C.c_uint, orientation), (P, options))
        if not handler:
            raise RuntimeError("Vision could not initialize image recognition")
        objects.append(handler)
        requests = _send(objc.objc_getClass(b"NSArray"), "arrayWithObject:", P, (P, request))
        error = P()
        if not _send(handler, "performRequests:error:", C.c_bool,
                     (P, requests), (C.POINTER(P), C.byref(error))):
            description = _send(error.value, "localizedDescription") if error.value else None
            message = _send(description, "UTF8String", C.c_char_p) if description else None
            raise RuntimeError("Vision OCR failed: " + (message.decode() if message else "unknown native error"))
        observations = _send(request, "results")
        lines, length, truncated = [], 0, False
        for index in range(_send(observations, "count", C.c_ulong)):
            observation = _send(observations, "objectAtIndex:", P, (C.c_ulong, index))
            candidates = _send(observation, "topCandidates:", P, (C.c_ulong, 1))
            if not _send(candidates, "count", C.c_ulong):
                continue
            candidate = _send(candidates, "objectAtIndex:", P, (C.c_ulong, 0))
            text = _send(_send(candidate, "string"), "UTF8String", C.c_char_p).decode("utf-8")
            remaining = MAX_TEXT - length - bool(lines)
            if remaining < 0:
                truncated = True
                break
            if len(text) > remaining:
                lines.append(text[:max(0, remaining)])
                truncated = True
                break
            lines.append(text)
            length += len(text) + (len(lines) > 1)
        return dict(path=str(path), width=width, height=height, orientation=orientation,
                    frame_index=0, frame_count=imageio.CGImageSourceGetCount(source),
                    text="\n".join(lines), text_truncated=truncated,
                    ocr_engine="macOS Vision", scene_understanding="unavailable; dimensions and OCR only")
    finally:
        for item in reversed(objects):
            _send(item, "release", None)
        for item in reversed(retained):
            cf.CFRelease(item)
        _send(pool, "drain", None)
