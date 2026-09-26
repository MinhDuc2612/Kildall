"""Deterministic parser and real b10809 GBNF checks; no model is allocated.

Run: .venv/bin/python test_tool_grammar.py
The ctypes bridge is deliberately pinned to the shipped macOS libc++ ABI and
llama.cpp's exported grammar test API. Production does not use this bridge.
API: https://github.com/ggml-org/llama.cpp/blob/b10809/src/llama-grammar.h
"""

import ctypes
import json
from pathlib import Path

from tool_grammar import (STRING_MARKER, TOOL_END, TOOL_START, _Compiler,
                          parse_tool_call, tool_grammar, validate_arguments)


class _Vector(ctypes.Structure):
    _fields_ = [(name, ctypes.c_void_p) for name in ("begin", "end", "capacity")]


class NativeGrammar:
    def __init__(self):
        library = Path(__file__).parent / ".tools/llama-b10809/llama-b10809/libllama.dylib"
        self.lib = ctypes.CDLL(str(library))
        self.init = getattr(self.lib, "_Z23llama_grammar_init_implPK11llama_vocabPKcS3_bPS3_mPKim")
        self.init.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
                              ctypes.c_bool, ctypes.c_void_p, ctypes.c_size_t,
                              ctypes.c_void_p, ctypes.c_size_t]
        self.init.restype = ctypes.c_void_p
        self.accept = getattr(self.lib, "_Z20llama_grammar_acceptP13llama_grammarj")
        self.accept.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.stacks = getattr(self.lib, "_Z24llama_grammar_get_stacksP13llama_grammar")
        self.stacks.argtypes = [ctypes.c_void_p]
        self.stacks.restype = ctypes.POINTER(_Vector)
        self.free = getattr(self.lib, "_Z23llama_grammar_free_implP13llama_grammar")
        self.free.argtypes = [ctypes.c_void_p]
        self.checks = 0

    def matches(self, grammar, text):
        pointer = self.init(None, grammar.encode(), b"root", False, None, 0, None, 0)
        assert pointer, "Pinned llama.cpp rejected generated GBNF"
        try:
            for character in text:
                self.accept(pointer, ord(character))
                vector = self.stacks(pointer).contents
                if vector.begin == vector.end:
                    return False
            vector = self.stacks(pointer).contents
            count = ((vector.end or 0) - (vector.begin or 0)) // ctypes.sizeof(_Vector)
            stacks = (_Vector * count).from_address(vector.begin or 0)
            return any(stack.begin == stack.end for stack in stacks)
        finally:
            self.checks += 1
            self.free(pointer)


def native(value):
    if isinstance(value, str):
        assert STRING_MARKER not in value
        return STRING_MARKER + value + STRING_MARKER
    if isinstance(value, list):
        return "[" + ",".join(native(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(key + ":" + native(item) for key, item in value.items()) + "}"
    return json.dumps(value, allow_nan=False)


def call(name, arguments):
    return TOOL_START + "call:" + name + native(arguments) + TOOL_END


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError(f"Expected rejection: {args!r}")


def scalar_grammar(schema):
    compiler = _Compiler()
    root = compiler.schema(schema)
    return "\n".join(f"{key} ::= {value}" for key, value in {"root": root, **compiler.rules}.items())


def main():
    from kildall import TOOLS

    fixture = json.loads(Path(__file__).with_name("bench_cases.json").read_text())
    grammar = NativeGrammar()
    frozen_tools = fixture["tools"]
    frozen_grammar = tool_grammar(frozen_tools)
    for case in fixture["tool_calls"]:
        expected = case["expected"]
        raw = call(expected["name"], expected["arguments"])
        assert grammar.matches(frozen_grammar, raw), case["id"]
        assert parse_tool_call(raw, frozen_tools) == expected, case["id"]

    current = tool_grammar(TOOLS)
    for name, arguments in (("remember", {"text": "Remember \\\\ and \" and\n日本語 <tag> <| <<|\" text",
                                           "scope": "global", "tier": "L1"}),
                            ("recall", {"query": "owner?", "scope": "both"})):
        raw = call(name, arguments)
        assert grammar.matches(current, raw)
        assert parse_tool_call(raw, TOOLS) == {"name": name, "arguments": arguments}
        reversed_arguments = dict(reversed(list(arguments.items())))
        assert parse_tool_call(call(name, reversed_arguments), TOOLS)["arguments"] == arguments
        assert grammar.matches(current, call(name, reversed_arguments)), "Generation accepts any key order"

    schema = {"type": "object", "properties": {
        "optional": {"type": "string"}, "required": {"type": "boolean"},
        "last": {"type": ["integer", "null"], "minimum": -2, "maximum": 3}},
        "required": ["required"], "additionalProperties": False}
    tools = [{"type": "function", "function": {"name": "sample", "parameters": schema}}]
    compiled = tool_grammar(tools)
    for arguments in ({"required": True}, {"optional": "", "required": False},
                      {"required": True, "last": None},
                      {"optional": "x", "required": True, "last": -2}):
        raw = call("sample", arguments)
        assert grammar.matches(compiled, raw)
        assert parse_tool_call(raw, tools)["arguments"] == arguments
    for arguments in ({}, {"optional": "x"}, {"required": 1}, {"required": True, "last": 4},
                      {"required": True, "unknown": "oops"}):
        raw = call("sample", arguments)
        assert not grammar.matches(compiled, raw)
        rejects(parse_tool_call, raw, tools)
    valid = call("sample", {"required": True})
    for raw in (valid + valid, valid[:-1], valid + "junk", valid.replace("sample", "sudo"),
                valid.replace("true", "true,required:false"),
                valid.replace("true", "__import__('os').system('anything')")):
        assert not grammar.matches(compiled, raw)
        rejects(parse_tool_call, raw, tools)

    for low, high in ((None, None), (1, None), (147, None), (None, -147),
                      (-100, 200), (7, 7), (109, 121), (-321, -109), (0, 0)):
        schema = {"type": "integer"}
        if low is not None:
            schema["minimum"] = low
        if high is not None:
            schema["maximum"] = high
        compiled = scalar_grammar(schema)
        assert len(compiled) < 5000
        for value in range(-400, 402):
            expected = (low is None or value >= low) and (high is None or value <= high)
            assert grammar.matches(compiled, str(value)) == expected, (schema, value)
        for raw in ("01", "+1", "1.0", "1e0", "true", "NaN", "Infinity", ""):
            assert not grammar.matches(compiled, raw), (schema, raw)
    for schema, values in (({"type": "integer", "minimum": 1.1, "maximum": 3.9}, [2, 3]),
                           ({"type": "integer", "exclusiveMinimum": 1, "exclusiveMaximum": 4}, [2, 3])):
        compiled = scalar_grammar(schema)
        for value in range(0, 6):
            assert grammar.matches(compiled, str(value)) == (value in values)

    integers = scalar_grammar({"type": "integer"})
    assert grammar.matches(integers, "9" * 100)
    assert not grammar.matches(integers, "9" * 101)
    assert not grammar.matches(integers, "9" * 4301)

    huge = scalar_grammar({"type": "integer", "minimum": 10 ** 40, "maximum": 10 ** 60})
    assert len(huge) < 100_000, "Numeric range must not enumerate its members"
    assert grammar.matches(huge, str(10 ** 50))
    assert not grammar.matches(huge, str(10 ** 40 - 1))

    for low, high in ((0, None), (1, None), (0, 0), (0, 1), (1, 1), (2, 4)):
        schema = {"type": "array", "items": {"type": "boolean"}, "minItems": low}
        if high is not None:
            schema["maxItems"] = high
        compiled = scalar_grammar(schema)
        for size in range(7):
            assert grammar.matches(compiled, native([True] * size)) == (size >= low and (high is None or size <= high))
        assert not grammar.matches(compiled, "[true,]")
        assert not grammar.matches(compiled, "[1]")

    strings = scalar_grammar({"type": "string"})
    for value in ("", "<", "<<", "<|", '<|"', '<|"|', "<|text|>", "x\\n\n\t\u0001", "😀日本語", "<" * 100):
        assert grammar.matches(strings, native(value)), repr(value)
    assert not grammar.matches(strings, native("x") + native("y"))
    enum = scalar_grammar({"type": ["string", "null"], "enum": ["one", "two", None]})
    for value in ("one", "two", None):
        assert grammar.matches(enum, native(value))
    for value in ("three", 1, False):
        assert not grammar.matches(enum, native(value))
    numbers = scalar_grammar({"type": "number"})
    for raw in ("0", "-0.5", "0.25", "9", "9" * 100, "0." + "0" * 99 + "1",
                "9" * 100 + "." + "9" * 100 + "e99", "0." + "0" * 99 + "1e-99"):
        assert grammar.matches(numbers, raw), raw
        validate_arguments({"type": "number"}, json.loads(raw))
    for raw in ("1e309", "1e9999", "1e100", "1e-100", "9" * 101, "0." + "1" * 101):
        assert not grammar.matches(numbers, raw), raw
    validate_arguments({"type": "number"}, 1e308)
    recall_only = tool_grammar(TOOLS, ["recall"])
    assert not grammar.matches(recall_only, call("remember", {"text": "x", "scope": "global", "tier": "L1"}))
    rejects(tool_grammar, TOOLS, ["unknown"])
    rejects(tool_grammar, TOOLS, [])
    rejects(tool_grammar, TOOLS + TOOLS)
    for schema in ({"type": "string", "pattern": "^x$"}, {"type": "string", "minLength": 1},
                   {"type": "number", "maximum": 2}, {"type": "object"},
                   {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
                   {"type": "array", "items": {"type": "string"}, "maxItems": None},
                   {"type": ["null", {}]}, {"type": {}},
                   {"type": "integer", "minimum": 3, "maximum": 2},
                   {"type": "integer", "minimum": True},
                   {"type": "string", "enum": [STRING_MARKER]},
                   {"type": "integer", "enum": [True]},
                   {"type": "string", "format": "email", "enum": ["a@b.com"]}):
        rejects(scalar_grammar, schema)
    rejects(validate_arguments, {"type": "number"}, float("inf"))
    print(f"PASS: frozen 20 calls, current tools, strict parsing, and {grammar.checks} actual b10809 grammar acceptance checks; no model allocated.")
    print("Limits: at most 10 object properties; no native delimiter inside strings; unsupported constraints fail closed; number generation limited to 100 integer/fractional digits and exponent magnitude 99.")


if __name__ == "__main__":
    main()
