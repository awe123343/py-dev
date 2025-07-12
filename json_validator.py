#!/usr/bin/env python3
# ruff: noqa: T201
from collections.abc import Callable


class JsonValidator:
    def __init__(self) -> None:
        self.json_string = ""
        self.pos = 0
        self.allow_arrays = False

    def validate(
        self,
        json_string: str,
        *,
        allow_arrays: bool = False,
    ) -> bool:
        self.json_string = json_string
        self.pos = 0
        self.allow_arrays = allow_arrays

        is_valid = self._parse_value()
        self._skip_whitespace()
        return is_valid and self.pos == len(self.json_string)

    def _skip_whitespace(self) -> None:
        """Advances the parser position past any whitespace."""
        while self.pos < len(self.json_string) and self.json_string[self.pos].isspace():
            self.pos += 1

    def _parse_literal(self, literal: str) -> bool:
        """Parses a literal like `null`."""
        if self.json_string[self.pos : self.pos + len(literal)] == literal:
            self.pos += len(literal)
            return True
        return False

    def _parse_string(self) -> bool:
        """Parses a string token, handling escaped characters."""
        if self.pos >= len(self.json_string) or self.json_string[self.pos] != '"':
            return False
        self.pos += 1  # Consume starting '"'

        while self.pos < len(self.json_string) and self.json_string[self.pos] != '"':
            if self.json_string[self.pos] == '"' and self.pos + 1 < len(
                self.json_string,
            ):
                self.pos += 2
            else:
                self.pos += 1

        if self.pos >= len(self.json_string) or self.json_string[self.pos] != '"':
            return False  # Unterminated string
        self.pos += 1  # Consume ending '"'
        return True

    def _parse_key_value_pair(self) -> bool:
        """Parses a key-value pair in a JSON object."""
        self._skip_whitespace()
        if not self._parse_string():
            return False
        self._skip_whitespace()

        if self.pos >= len(self.json_string) or self.json_string[self.pos] != ":":
            return False
        self.pos += 1
        self._skip_whitespace()

        return self._parse_value()

    def _parse_comma_separated_values(
        self,
        parse_func: Callable[[], bool],
        end_char: str,
    ) -> bool:
        """Handles comma-separated values for objects and arrays."""
        while self.pos < len(self.json_string):
            self._skip_whitespace()
            if not parse_func():
                return False
            self._skip_whitespace()

            if self.pos < len(self.json_string) and self.json_string[self.pos] == end_char:
                self.pos += 1
                return True

            if self.pos >= len(self.json_string) or self.json_string[self.pos] != ",":
                return False
            self.pos += 1

        return False

    def _parse_object(self) -> bool:
        """Parses an object token: { "key": value, ... }."""
        if self.pos >= len(self.json_string) or self.json_string[self.pos] != "{":
            return False
        self.pos += 1  # Consume '{'

        self._skip_whitespace()
        if self.pos < len(self.json_string) and self.json_string[self.pos] == "}":
            self.pos += 1
            return True

        return self._parse_comma_separated_values(self._parse_key_value_pair, "}")

    def _parse_array(self) -> bool:
        """Parses an array token: [ value, ... ]."""
        if self.pos >= len(self.json_string) or self.json_string[self.pos] != "[":
            return False
        self.pos += 1  # Consume '['
        self._skip_whitespace()

        if self.pos < len(self.json_string) and self.json_string[self.pos] == "]":
            self.pos += 1
            return True

        return self._parse_comma_separated_values(self._parse_value, "]")

    def _parse_value(self) -> bool:
        """Dispatches to the correct parser based on the current character."""
        self._skip_whitespace()
        if self.pos >= len(self.json_string):
            return False

        char = self.json_string[self.pos]
        if char == "{":
            return self._parse_object()
        if char == '"':
            return self._parse_string()
        if char == "n":
            return self._parse_literal("null")
        if self.allow_arrays and char == "[":
            return self._parse_array()

        return False


if __name__ == "__main__":
    # --- Test Cases ---
    valid_obj_str = ' { "key" : "value", "nested" : { "a" : "b" } } '
    valid_with_array = '[ { "key": [ "v1", "v2" ] }, "second" ]'
    valid_with_null = ' { "key": null, "other": "value" } '
    invalid_number = '{"key": 123}'
    invalid_array_in_step1 = '["a", "b"]'
    invalid_trailing_comma = '{"key": "value",}'
    invalid_unterminated_str = '{"key": "value'

    # Create a single instance of the validator
    validator = JsonValidator()

    print("--- Running Validator (Step 1: Arrays NOT allowed) ---")
    print(
        f"'{valid_obj_str[:30]}...': {validator.validate(valid_obj_str, allow_arrays=False)}",
    )
    print(
        f"'{valid_with_array[:30]}...': {validator.validate(valid_with_array, allow_arrays=False)}",
    )
    print(
        f"'{valid_with_null[:30]}...': {validator.validate(valid_with_null, allow_arrays=False)}",
    )
    print(
        f"'{invalid_array_in_step1[:30]}...': {validator.validate(invalid_array_in_step1, allow_arrays=False)}",
    )
    print("-" * 20)

    print("\n--- Running Validator (Step 2: Arrays ARE allowed) ---")
    print(
        f"'{valid_obj_str[:30]}...': {validator.validate(valid_obj_str, allow_arrays=True)}",
    )
    print(
        f"'{valid_with_array[:30]}...': {validator.validate(valid_with_array, allow_arrays=True)}",
    )
    print(
        f"'{valid_with_null[:30]}...': {validator.validate(valid_with_null, allow_arrays=True)}",
    )
    print(
        f"'{invalid_number[:30]}...': {validator.validate(invalid_number, allow_arrays=True)}",
    )
    print(
        f"'{invalid_trailing_comma[:30]}...': {validator.validate(invalid_trailing_comma, allow_arrays=True)}",
    )
    print("-" * 20)
