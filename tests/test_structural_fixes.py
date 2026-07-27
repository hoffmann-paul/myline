"""Structural checks for kill/restore/startup fixes (#80, #83, #85, #86)."""

import ast
import os
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC = os.path.join(REPO, "myline.py")


class TestStructuralFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SRC, encoding="utf-8") as f:
            cls.source = f.read()
        cls.tree = ast.parse(cls.source)

    def test_only_one_kill_definition(self):
        kills = [
            n
            for n in self.tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "kill"
        ]
        self.assertEqual(len(kills), 1)

    def test_exit_helper_exists(self):
        names = {n.name for n in self.tree.body if isinstance(n, ast.FunctionDef)}
        self.assertIn("_exit_and_close_terminal", names)

    def test_startup_calls_check_temp_saves_once(self):
        # The dual call pattern must be gone.
        self.assertNotIn("elif not check_temp_saves()", self.source)
        self.assertIn("_has_restorable = check_temp_saves()", self.source)

    def test_restore_guards_non_list_temp_data(self):
        self.assertIn("Nothing to restore", self.source)
        self.assertIn("not isinstance(temp_data, list)", self.source)

    def test_check_changes_handles_io_errors(self):
        # Function body must try/except the open
        self.assertIn("Can't read", self.source)
        freefuncs = [
            n
            for n in self.tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "myline_check_changes"
        ]
        self.assertEqual(len(freefuncs), 1)
        src = ast.get_source_segment(self.source, freefuncs[0]) or ""
        self.assertIn("try:", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
