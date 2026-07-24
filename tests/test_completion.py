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
        "readline_tab_binding": namespace["_readline_tab_binding"],
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
        # The current myline.py may carry an extra `iM` (manual import) leaf
        # alongside `i`. Compare as a set so the test stays valid as the
        # commands dict grows on the upstream branch.
        self.assertEqual(set(leaves), {"i", "iM"})

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


class TestReadlineBinding(unittest.TestCase):
    def test_gnu_readline_uses_standard_binding(self):
        module = types.SimpleNamespace(backend="readline", __doc__="GNU readline")
        self.assertEqual(HELPERS["readline_tab_binding"](module), "tab: complete")

    def test_libedit_backend_uses_editline_binding(self):
        module = types.SimpleNamespace(backend="editline", __doc__="")
        self.assertEqual(
            HELPERS["readline_tab_binding"](module), "bind ^I rl_complete"
        )

    def test_older_macos_python_detects_libedit_from_doc(self):
        module = types.SimpleNamespace(__doc__="Importing this module enables libedit")
        self.assertEqual(
            HELPERS["readline_tab_binding"](module), "bind ^I rl_complete"
        )


class TestLineCompleter(unittest.TestCase):
    """Drive ``_line_completer`` with a stub readline module."""

    def setUp(self):
        self.fake_readline = mock.MagicMock()
        self.line_buffer = ""
        self.begin_index = 0
        self.fake_readline.get_line_buffer.side_effect = lambda: self.line_buffer
        self.fake_readline.get_begidx.side_effect = lambda: self.begin_index
        self._original_readline = HELPERS["line_completer"].__globals__.get(
            "readline"
        )
        HELPERS["line_completer"].__globals__["readline"] = self.fake_readline

    def tearDown(self):
        HELPERS["line_completer"].__globals__["readline"] = self._original_readline

    def _candidates(self, line, partial):
        """Return candidates as readline sees them for a real input buffer."""
        self.line_buffer = line
        self.begin_index = len(line) - len(partial)
        out = []
        state = 0
        while True:
            candidate = HELPERS["line_completer"](partial, state)
            if candidate is None:
                break
            out.append(candidate)
            state += 1
        return out

    def test_complete_top_level_partial_in_line_buffer(self):
        self.assertEqual(self._candidates("da", "da"), ["data"])

    def test_complete_sub_after_data(self):
        self.assertEqual(self._candidates("data W", "W"), ["WRITE"])

    def test_complete_sub_sub(self):
        # Use a prefix that doesn't match `iM` so the assertion stays
        # stable even if upstream adds more leaves to data GET later.
        self.assertEqual(self._candidates("data GET i", "i"), ["i", "iM"])

    def test_complete_empty_token_after_space(self):
        self.assertIn("WRITE", self._candidates("data ", ""))

    def test_no_completion_for_flags(self):
        self.assertEqual(
            self._candidates("data GET i --data-file", "--data-file"), []
        )

    def test_handles_quoted_path(self):
        self.assertEqual(
            self._candidates('data GET i "path', '"path'),
            [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
