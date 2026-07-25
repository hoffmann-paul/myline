"""Unit tests for data WRITE value coercion (issues #44 and #84)."""

import ast
import os
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MYLINE_PATH = os.path.join(REPO_ROOT, "myline.py")


def _load_coerce():
    """Pull ``_coerce_write_value`` out of myline.py without running the REPL."""
    with open(MYLINE_PATH, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=MYLINE_PATH)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_coerce_write_value":
            module = ast.Module(body=[node], type_ignores=[])
            ns = {}
            exec(compile(module, MYLINE_PATH, "exec"), ns)
            return ns["_coerce_write_value"]
    raise RuntimeError("_coerce_write_value not found in myline.py")


coerce = _load_coerce()


class TestCoerceWriteValue(unittest.TestCase):
    def test_plain_int_still_coerces(self):
        self.assertEqual(coerce("42"), 42)
        self.assertEqual(coerce("-7"), -7)
        self.assertEqual(coerce("0"), 0)

    def test_float_coerces(self):
        self.assertEqual(coerce("3.14"), 3.14)

    def test_bool_and_null(self):
        self.assertIs(coerce("true"), True)
        self.assertIs(coerce("FALSE"), False)
        self.assertIsNone(coerce("null"))
        self.assertIsNone(coerce("None"))

    def test_leading_zero_phone_stays_string(self):
        phone = "0491701234567"
        self.assertEqual(coerce(phone), phone)
        self.assertIsInstance(coerce(phone), str)

    def test_zero_padded_id_stays_string(self):
        self.assertEqual(coerce("007"), "007")

    def test_quoted_forces_literal_string(self):
        self.assertEqual(coerce('"true"'), "true")
        self.assertEqual(coerce("'false'"), "false")
        self.assertEqual(coerce('"0491"'), "0491")
        self.assertEqual(coerce('"42"'), "42")

    def test_ordinary_text_unchanged(self):
        self.assertEqual(coerce("Alice"), "Alice")


if __name__ == "__main__":
    unittest.main(verbosity=2)
