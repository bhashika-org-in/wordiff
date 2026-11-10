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


class CrossLineBlockTest(unittest.TestCase):
    def test_inline_join_two_lines_into_one(self):
        old = ["alpha beta", "gamma delta", "same tail"]
        new = ["alpha beta gamma delta", "same tail"]
        html = wordiff.diff_lines_html(old, new, context=3, mode="inline")
        # One merged change row: the moved text must not also linger
        # as a separate delete row.
        self.assertEqual(html.count('class="line chg"'), 1)
        self.assertNotIn('class="line del"', html)
        self.assertEqual(html.count("gamma delta"), 1)
        # The join itself is shown as a removed line break.
        self.assertIn("<del>\n</del>", html)

    def test_inline_reword_across_line_boundary(self):
        old = ["story start sande-", "hanam middle end.", "next para same."]
        new = ["story start sandehanam middle end.", "next para same."]
        html = wordiff.diff_lines_html(old, new, context=3, mode="inline")
        self.assertEqual(html.count('class="line chg"'), 1)
        self.assertNotIn('class="line del"', html)
        self.assertIn("<ins>sandehanam</ins>", html)
        # The untouched tail must not be swallowed into a giant insert.
        self.assertNotIn("<ins>sandehanam middle end.</ins>", html)

    def test_unified_join_shows_move_without_highlights(self):
        old = ["alpha beta", "gamma delta", "same tail"]
        new = ["alpha beta gamma delta", "same tail"]
        html = wordiff.diff_lines_html(old, new, context=3)
        self.assertEqual(html.count('class="line del"'), 2)
        self.assertEqual(html.count('class="line ins"'), 1)
        self.assertNotIn("<del>", html)
        # Only the join itself (newline turned into a space) is marked.
        self.assertIn(
            '<div class="line ins"><span class="sign">+</span>'
            "alpha beta<ins> </ins>gamma delta</div>",
            html,
        )
        self.assertNotIn("<ins> gamma delta</ins>", html)

    def test_single_line_pair_is_unchanged(self):
        old, new = ["hello brave world"], ["hello bright world"]
        self.assertIn(
            '<div class="line del"><span class="sign">-</span>'
            "hello <del>brave</del> world</div>",
            wordiff.diff_lines_html(old, new, context=0),
        )
        self.assertIn(
            '<div class="line chg"><span class="sign">~</span>'
            "hello <del>brave</del><ins>bright</ins> world</div>",
            wordiff.diff_lines_html(old, new, context=0, mode="inline"),
        )

    def test_large_block_keeps_positional_pairing(self):
        old = [f"old line {i} here" for i in range(20)]
        new = [f"new line {i} there" for i in range(20)]
        html = wordiff.diff_lines_html(old, new, context=0, mode="inline")
        # Too big for whole-block matching: falls back to one row per line.
        self.assertEqual(html.count('class="line chg"'), 20)


if __name__ == "__main__":
    unittest.main()
