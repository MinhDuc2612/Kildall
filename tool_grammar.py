"""Schema-constrained Gemma 4 native calls for llama.cpp b10809.

Generation and parsing accept any property order without duplicate keys. Unsupported
schema constraints fail closed. Native strings are raw (including backslashes),
so their delimiter cannot itself be represented inside a string.
Unbounded integers generate at most 100 digits. Unbounded numbers generate at most 100 integer/fractional digits and exponent
magnitude 99, keeping all generated decimals finite without repairing values.
"""

import json
import math
import re


TOOL_START = "<|tool_call>"
TOOL_END = "<tool_call|>"
STRING_MARKER = '<|"|>'
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")
_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_METADATA = {"description", "title", "default", "$comment", "examples"}


def _literal(text):
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    return '"' + "".join(escapes.get(c, f"\\u{ord(c):04x}" if ord(c) < 32 else c)
                          for c in text) + '"'


def _digits(count):
    return "" if not count else f"[0-9]{{{count}}}"


def _fixed_range(low, high):
    """Compact equal-width decimal range; never enumerate numeric values."""
    if low == high:
        return _literal(low)
    if low == "0" * len(low) and high == "9" * len(high):
        return _digits(len(low))
    common = 0
    while low[common] == high[common]:
        common += 1
    if common:
        return f"{_literal(low[:common])} ({_fixed_range(low[common:], high[common:])})"
    first, last, remaining = int(low[0]), int(high[0]), len(low) - 1
    if not remaining:
        return f"[{first}-{last}]"
    pieces = [f'{_literal(low[0])} ({_fixed_range(low[1:], "9" * remaining)})']
    if first + 1 <= last - 1:
        pieces.append(f"[{first + 1}-{last - 1}] {_digits(remaining)}")
    pieces.append(f'{_literal(high[0])} ({_fixed_range("0" * remaining, high[1:])})')
    return " | ".join(pieces)


def _unsigned_range(low, high):
    if high is None:
        size = len(str(low))
        if size > 100:
            raise ValueError("Integer bounds exceed the 100-digit generation limit")
        first = f"({_fixed_range(str(low), '9' * size)})"
        return first if size == 100 else first + f" | [1-9] [0-9]{{{size},99}}"
    if len(str(high)) > 100:
        raise ValueError("Integer bounds exceed the 100-digit generation limit")
    pieces = []
    for size in range(len(str(low)), len(str(high)) + 1):
        first = max(low, 0 if size == 1 else 10 ** (size - 1))
        last = min(high, 10 ** size - 1)
        pieces.append(_fixed_range(str(first), str(last)))
    return " | ".join(f"({piece})" for piece in pieces)


def _integer_bounds(schema):
    low, high = None, None
    for key in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
        if key not in schema:
            continue
        value = schema[key]
        if type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)):
            raise ValueError(f"Invalid {key}")
        if key == "minimum":
            low = math.ceil(value) if low is None else max(low, math.ceil(value))
        elif key == "exclusiveMinimum":
            low = math.floor(value) + 1 if low is None else max(low, math.floor(value) + 1)
        elif key == "maximum":
            high = math.floor(value) if high is None else min(high, math.floor(value))
        else:
            high = math.ceil(value) - 1 if high is None else min(high, math.ceil(value) - 1)
    if low is not None and high is not None and low > high:
        raise ValueError("Empty integer range")
    return low, high


def _integer_rule(schema):
    low, high = _integer_bounds(schema)
    pieces = []
    if low is None or low < 0:
        pieces.append(f'"-" ({_unsigned_range(max(1, -high) if high is not None else 1, None if low is None else -low)})')
    if high is None or high >= 0:
        pieces.append(_unsigned_range(max(0, low) if low is not None else 0, high))
    return " | ".join(pieces)


def _native(value):
    if isinstance(value, str):
        if STRING_MARKER in value:
            raise ValueError("Native string contains its delimiter")
        return STRING_MARKER + value + STRING_MARKER
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class _Compiler:
    def __init__(self):
        self.rules = {
            "ws": r"[ \t\r\n]*",
            "native-string": f"{_literal(STRING_MARKER)} string-body",
            "string-body": r'[^<]* "<" string-one',
            "string-one": r'"<" string-one | "|" string-two | [^<|] string-body',
            "string-two": r'"<" string-one | "\"" string-three | [^<"] string-body',
            "string-three": r'"<" string-one | "|" string-four | [^<|] string-body',
            "string-four": r'">" | "<" string-one | [^<>] string-body',
        }

    def add(self, expression):
        name = f"s-{len(self.rules)}"
        self.rules[name] = expression
        return name

    def schema(self, schema):
        if not isinstance(schema, dict):
            raise ValueError("Schema must be an object")
        kind = schema.get("type")
        if isinstance(kind, list):
            if (len(kind) != 2 or any(not isinstance(t, str) for t in kind)
                    or kind.count("null") != 1 or len(set(kind)) != 2):
                raise ValueError("Only nullable type unions are supported")
            branch = dict(schema, type=next(t for t in kind if t != "null"))
            if "enum" in schema:
                # Compile all branches first so an enum cannot hide unsupported constraints.
                self.schema({k: v for k, v in branch.items() if k != "enum"})
                return self.enum(schema)
            return self.add(f'{self.schema(branch)} | "null"')
        supported = {
            "object": {"properties", "required", "additionalProperties"},
            "array": {"items", "minItems", "maxItems"},
            "string": set(), "boolean": set(), "null": set(), "number": set(),
            "integer": {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"},
        }
        if not isinstance(kind, str) or kind not in supported:
            raise ValueError(f"Unsupported schema type: {kind!r}")
        unknown = set(schema) - supported[kind] - _METADATA - {"type", "enum"}
        if unknown:
            raise ValueError(f"Unsupported schema constraints: {sorted(unknown)}")
        if "enum" in schema:
            self.schema({k: v for k, v in schema.items() if k != "enum"})
            return self.enum(schema)
        if kind == "object":
            if schema.get("additionalProperties") is not False:
                raise ValueError("Object schemas must explicitly disallow additionalProperties")
            properties, required = schema.get("properties", {}), schema.get("required", [])
            if not isinstance(properties, dict) or not isinstance(required, list):
                raise ValueError("Invalid object properties/required")
            if any(not isinstance(k, str) or not _NAME.fullmatch(k) for k in properties):
                raise ValueError("Unsupported native object property name")
            if any(not isinstance(k, str) for k in required) or len(required) != len(set(required)) or set(required) - properties.keys():
                raise ValueError("Invalid required property names")
            children = [(key, self.schema(value)) for key, value in properties.items()]
            # ponytail: subset states cap objects at 10 keys; larger schemas need a different compiler.
            if len(children) > 10:
                raise ValueError("Native object schemas support at most 10 properties")
            states = {}
            required_bits = sum(1 << i for i, (key, _) in enumerate(children) if key in required)
            def state(mask):
                if mask in states:
                    return states[mask]
                name = self.add('"}"')
                states[mask] = name
                choices = ['"}"'] if mask & required_bits == required_bits else []
                for i, (key, child) in enumerate(children):
                    if not mask & (1 << i):
                        prefix = '"," ws ' if mask else ''
                        choices.append(f'{prefix}{_literal(key)} ws ":" ws {child} ws {state(mask | (1 << i))}')
                self.rules[name] = " | ".join(choices)
                return name
            return self.add(f'"{{" ws {state(0)}')
        if kind == "array":
            low, high = schema.get("minItems", 0), schema.get("maxItems")
            if (type(low) is not int or low < 0
                    or ("maxItems" in schema and (type(high) is not int or high < low))):
                raise ValueError("Invalid array length bounds")
            item = self.schema(schema.get("items"))
            if high == 0:
                return self.add('"[" ws "]"')
            rest = f'( "," ws {item} ws ){{{max(0, low - 1)},{"" if high is None else high - 1}}}'
            sequence = f"{item} ws {rest}"
            if low == 0:
                sequence = f"({sequence})?"
            return self.add(f'"[" ws {sequence} "]"')
        expression = {
            "string": "native-string", "boolean": '"true" | "false"', "null": '"null"',
            "number": r'"-"? ("0" | [1-9] [0-9]{0,99}) ("." [0-9]{1,100})? ([eE] [+-]? [0-9]{1,2})?',
        }.get(kind)
        return self.add(_integer_rule(schema) if kind == "integer" else expression)

    def enum(self, schema):
        values = schema["enum"]
        if not isinstance(values, list) or not values or any(type(v) in (dict, list) for v in values):
            raise ValueError("Only nonempty primitive enums are supported")
        for value in values:
            _validate({k: v for k, v in schema.items() if k != "enum"}, value)
        return self.add(" | ".join(_literal(_native(value)) for value in values))


def _validate(schema, value):
    kind = schema["type"]
    if isinstance(kind, list):
        if value is None:
            kind = "null"
        else:
            kind = next(t for t in kind if t != "null")
    match = {"null": value is None, "boolean": type(value) is bool,
             "integer": type(value) is int,
             "number": type(value) in (int, float), "string": isinstance(value, str),
             "array": isinstance(value, list), "object": isinstance(value, dict)}
    if not match[kind]:
        raise ValueError(f"Expected {kind}")
    if "enum" in schema and not any(type(value) is type(v) and value == v for v in schema["enum"]):
        raise ValueError("Value outside enum")
    if kind == "object":
        properties = schema.get("properties", {})
        if value.keys() - properties.keys() or set(schema.get("required", [])) - value.keys():
            raise ValueError("Unknown or missing object properties")
        for key, item in value.items():
            _validate(properties[key], item)
    elif kind == "array":
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", math.inf):
            raise ValueError("Array length outside bounds")
        for item in value:
            _validate(schema["items"], item)
    elif kind in ("number", "integer"):
        if type(value) is float and not math.isfinite(value):
            raise ValueError("Non-finite number")
        if kind == "integer":
            low, high = _integer_bounds(schema)
            if (low is not None and value < low) or (high is not None and value > high):
                raise ValueError("Integer outside bounds")
    elif kind == "string" and STRING_MARKER in value:
        raise ValueError("Native string contains its delimiter")


def validate_arguments(schema, value):
    """Validate both the supported schema and decoded arguments, without repair."""
    _Compiler().schema(schema)
    _validate(schema, value)


def _tool_schemas(tools, allowed_names):
    schemas = {}
    for tool in tools:
        function = tool.get("function", {})
        name = function.get("name")
        if tool.get("type") != "function" or not isinstance(name, str) or not _NAME.fullmatch(name) or name in schemas:
            raise ValueError("Invalid or duplicate tool name")
        schema = function.get("parameters")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            raise ValueError("Tool arguments must be an object")
        schemas[name] = schema
    if allowed_names is not None:
        allowed = set(allowed_names)
        if allowed - schemas.keys():
            raise ValueError("Unknown allowed tool name")
        schemas = {k: v for k, v in schemas.items() if k in allowed}
    if not schemas:
        raise ValueError("No permitted tools")
    return schemas


def tool_grammar(tools, allowed_names=None):
    """GBNF for exactly one complete call; use TOOL_START as the lazy trigger."""
    compiler = _Compiler()
    choices = [f"{_literal('call:' + name)} {compiler.schema(schema)}"
               for name, schema in _tool_schemas(tools, allowed_names).items()]
    root = f"{_literal(TOOL_START)} ({' | '.join(choices)}) {_literal(TOOL_END)}"
    return "\n".join(f"{key} ::= {value}" for key, value in {"root": root, **compiler.rules}.items()) + "\n"


class _Parser:
    def __init__(self, text):
        self.text, self.pos = text, 0

    def take(self, token):
        if not self.text.startswith(token, self.pos):
            raise ValueError(f"Expected {token!r} at {self.pos}")
        self.pos += len(token)

    def space(self):
        while self.pos < len(self.text) and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def value(self):
        self.space()
        if self.text.startswith(STRING_MARKER, self.pos):
            self.take(STRING_MARKER)
            end = self.text.find(STRING_MARKER, self.pos)
            if end < 0:
                raise ValueError("Unterminated native string")
            value, self.pos = self.text[self.pos:end], end + len(STRING_MARKER)
            return value
        if self.text.startswith(("{", "["), self.pos):
            is_object = self.text[self.pos] == "{"
            self.pos += 1
            value, close = ({}, "}") if is_object else ([], "]")
            self.space()
            if not self.text.startswith(close, self.pos):
                while True:
                    if is_object:
                        match = re.match(r"[A-Za-z_][A-Za-z0-9_.-]*", self.text[self.pos:])
                        if not match:
                            raise ValueError("Invalid native object key")
                        key = match[0]
                        if key in value:
                            raise ValueError("Duplicate native object key")
                        self.pos += len(key)
                        self.space()
                        self.take(":")
                        value[key] = self.value()
                    else:
                        value.append(self.value())
                    self.space()
                    if self.text.startswith(close, self.pos):
                        break
                    self.take(",")
                    self.space()
            self.take(close)
            return value
        for token, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(token, self.pos):
                self.pos += len(token)
                return value
        match = _NUMBER.match(self.text, self.pos)
        if not match:
            raise ValueError(f"Invalid native value at {self.pos}")
        self.pos = match.end()
        return json.loads(match[0])


def parse_tool_call(raw, tools, allowed_names=None):
    """Parse one complete raw native call, rejecting trailing data and bad schemas."""
    schemas = _tool_schemas(tools, allowed_names)
    parser = _Parser(raw)
    parser.take(TOOL_START + "call:")
    end = raw.find("{", parser.pos)
    name = raw[parser.pos:end]
    if end < 0 or name not in schemas:
        raise ValueError("Unknown native tool name")
    parser.pos = end
    arguments = parser.value()
    parser.take(TOOL_END)
    if parser.pos != len(raw):
        raise ValueError("Trailing data or multiple tool calls")
    validate_arguments(schemas[name], arguments)
    return {"name": name, "arguments": arguments}
