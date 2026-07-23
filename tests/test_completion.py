"""Tests for the Tab-completion helper in ``myline.py``.

The project ships as a single-file REPL with no ``tests/`` directory, so
these tests intentionally stay small and self-contained. They exercise
the pure helper functions (``_complete_sub_keywords``,
``_complete_sub_sub_keywords``, ``_all_command_keywords``) directly.

We avoid importing the whole ``myline`` module because importing it
would start the REPL. Instead we ``exec`` the module text in a
controlled namespace where the REPL's blocking ``input()`` is mocked
out, then grab the helper functions from that namespace.

Run with::

    /tmp/myline-venv/bin/python -m unittest tests/test_completion.py -v
"""

import os
import sys
import types
import unittest
from unittest import mock

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MYLINE_PATH = os.path.join(REPO_ROOT, "myline.py")


def _load_myline_helpers():
    """Execute ``myline.py`` in an isolated namespace and return the
    completion-related names.

    We stub the heavy import (``bleak``) and feed a single ``kill``
    command to the REPL so the ``while True: input()`` loop terminates
    cleanly. Once the loop exits, the helper functions defined at
    module level are available in the namespace.
    """
    with open(MYLINE_PATH, encoding="utf-8") as f:
        source = f.read()

    # Stub ``bleak`` so ``from bleak import BleakScanner`` doesn't fail
    # on machines without the Bluetooth stack.
    fake_bleak = types.ModuleType("bleak")
    fake_bleak.BleakScanner = mock.MagicMock()
    sys.modules.setdefault("bleak", fake_bleak)

    namespace = {"__name__": "_myline_test_ns", "__file__": MYLINE_PATH}
    # ``input`` is called once by the REPL, returns ``kill``; the
    # dispatcher's ``kill`` branch calls ``sys.exit`` so the loop ends.
    # We catch the SystemExit so the test process isn't terminated.
    with mock.patch("builtins.input", return_value="kill"), mock.patch(
        "sys.argv", ["myline.py", "--no-completion"]
    ):
        try:
            exec(compile(source, MYLINE_PATH, "exec"), namespace)
        except SystemExit:
            pass  # expected: ``kill`` calls sys.exit()

    return {
        "all_command_keywords": namespace["_all_command_keywords"],
        "complete_sub_keywords": namespace["_complete_sub_keywords"],
        "complete_sub_sub_keywords": namespace["_complete_sub_sub_keywords"],
        "line_completer": namespace["_line_completer"],
        "commands": namespace["commands"],
        "fast_commands": namespace["fast_commands"],
    }


HELPERS = _load_myline_helpers()


class TestCompletionHelpers(unittest.TestCase):
    def test_top_level_keywords_include_all_sections(self):
        keywords = HELPERS["all_command_keywords"]()
        # Each top-level section of the ``commands`` dict must be present.
        for section in ("data", "net", "ble", "myline"):
            self.assertIn(section, keywords)
        # And both fast commands.
        self.assertIn("kill", keywords)
        self.assertIn("last", keywords)

    def test_sub_keywords_for_data(self):
        # ``data`` has GET, HEAD, WRITE, POST, card, inspect.
        subs = HELPERS["complete_sub_keywords"]("data", "")
        self.assertEqual(
            set(subs), {"GET", "HEAD", "WRITE", "POST", "card", "inspect"}
        )

    def test_sub_keyword_prefix_filter(self):
        subs = HELPERS["complete_sub_keywords"]("data", "W")
        self.assertEqual(subs, ["WRITE"])

    def test_sub_sub_keywords_for_data_get(self):
        leaves = HELPERS["complete_sub_sub_keywords"]("data", "GET", "")
        self.assertEqual(leaves, ["i"])

    def test_sub_sub_keywords_for_data_write(self):
        leaves = HELPERS["complete_sub_sub_keywords"]("data", "WRITE", "")
        self.assertEqual(set(leaves), {"t", "POST"})

    def test_sub_sub_keywords_for_myline_help(self):
        leaves = HELPERS["complete_sub_sub_keywords"]("myline", "help", "")
        self.assertEqual(set(leaves), {"c", "info", "paths"})

    def test_unknown_keyword_returns_empty(self):
        # ``frobnicate`` is not a command; sub-keyword lookup must be safe.
        self.assertEqual(HELPERS["complete_sub_keywords"]("frobnicate", ""), [])
        self.assertEqual(
            HELPERS["complete_sub_sub_keywords"]("frobnicate", "x", ""), []
        )

    def test_fast_command_has_no_sub_completion(self):
        # ``kill`` is a fast command — it takes flags, not sub-keywords.
        self.assertEqual(HELPERS["complete_sub_keywords"]("kill", ""), [])


class TestLineCompleter(unittest.TestCase):
    """Drive ``_line_completer`` with a stub readline module."""

    def setUp(self):
        # Build a fake readline that lets us control what the completer
        # "sees" as the line buffer and cursor position.
        self.fake_readline = mock.MagicMock()
        self.line_buffer = ""
        # The completer reads end-of-line cursor; default to end of buffer.
        self.fake_readline.get_line_buffer.side_effect = lambda: self.line_buffer
        self.fake_readline.get_endidx.side_effect = lambda: len(self.line_buffer)
        self.fake_readline.get_begidx.return_value = 0
        # Patch the module-level ``readline`` name inside the loaded namespace.
        self._original_readline = HELPERS["line_completer"].__globals__.get(
            "readline"
        )
        HELPERS["line_completer"].__globals__["readline"] = self.fake_readline

    def tearDown(self):
        HELPERS["line_completer"].__globals__["readline"] = self._original_readline

    def _candidates(self, line, partial):
        """Return the full list of candidates for ``line`` with ``partial``
        as the current word under the cursor."""
        self.line_buffer = line
        out = []
        state = 0
        while True:
            candidate = HELPERS["line_completer"](partial, state)
            if candidate is None:
                break
            out.append(candidate)
            state += 1
        return out

    def test_complete_top_level(self):
        # Empty line, partial word "d" -> should offer data.
        self.assertIn("data", self._candidates("", "d"))

    def test_complete_sub_after_data(self):
        # ``data`` typed, completing sub-keyword starting with "W".
        self.assertEqual(self._candidates("data ", "W"), ["WRITE"])

    def test_complete_sub_sub(self):
        # ``data GET`` typed, completing leaf starting with "i".
        self.assertEqual(self._candidates("data GET ", "i"), ["i"])

    def test_no_completion_for_flags(self):
        # Fourth token onwards: no command completion, completer returns None.
        self.assertIsNone(HELPERS["line_completer"]("--data-file", 0))

    def test_handles_quoted_path(self):
        # A quoted path with a space should not be split by shlex.
        # ``data GET i "path with space"`` -> the partial word is after
        # the last space, so the completer should still walk the typed
        # tokens and not be confused by the quote.
        self.assertEqual(
            self._candidates('data GET i "path', '"path'),
            [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
