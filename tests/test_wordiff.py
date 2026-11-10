"""Focused regression tests for wordiff tokenization and diff options.

Run: python3 -m unittest discover -s tests -v
"""
import os
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

_HERE = os.path.dirname(os.path.abspath(__file__))
_LOADER = SourceFileLoader("wordiff", os.path.join(_HERE, "..", "wordiff"))
_SPEC = spec_from_loader("wordiff", _LOADER)
wordiff = module_from_spec(_SPEC)
_LOADER.exec_module(wordiff)


class TokenizerTest(unittest.TestCase):
    def test_devanagari_word_stays_whole(self):
        self.assertEqual(wordiff.tokenize("हिंदी"), ["हिंदी"])

    def test_danda_stays_separate(self):
        self.assertEqual(wordiff.tokenize("हिन्दी।"), ["हिन्दी", chr(0x964)])

    def test_ascii_behavior_unchanged(self):
        self.assertEqual(
            wordiff.tokenize("hello, world"), ["hello", ",", " ", "world"]
        )


class InlineDiffTest(unittest.TestCase):
    def test_hindi_word_swap_is_atomic(self):
        self.assertEqual(
            wordiff.word_diff_inline("हिंदी", "हिन्दी"),
            "<del>हिंदी</del><ins>हिन्दी</ins>",
        )


class NormalizeTest(unittest.TestCase):
    def test_nfc_unifies_combining_acute(self):
        decomposed = "e" + chr(0x301)
        self.assertEqual(wordiff.apply_normalization(decomposed, "nfc"), chr(0xE9))


class IgnorePunctTest(unittest.TestCase):
    def test_danda_only_change_ignored(self):
        old = ["राम" + chr(0x964)]
        new = ["राम" + chr(0x965)]
        html = wordiff.diff_lines_html(old, new, context=0, ignore_punct=True)
        self.assertIn("No changes", html)

    def test_danda_only_change_shown_by_default(self):
        old = ["राम" + chr(0x964)]
        new = ["राम" + chr(0x965)]
        html = wordiff.diff_lines_html(old, new, context=0)
        self.assertIn("<del>", html)


class ZwjTest(unittest.TestCase):
    def test_zwj_rendered_visibly(self):
        self.assertIn("zwj", wordiff.esc_html("a" + chr(0x200D) + "b"))


if __name__ == "__main__":
    unittest.main()
