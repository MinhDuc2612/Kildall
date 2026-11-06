"""Local-file image decoding and OCR through the host interface."""
from kildall_platform import ocr


def read_image(path):
    return ocr().read_image(path)
