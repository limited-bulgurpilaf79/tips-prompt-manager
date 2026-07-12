from __future__ import annotations

import os
import tempfile
import unittest

from tips_prompt_manager.i18n import load_language, normalize_language, save_language


class I18nTests(unittest.TestCase):
    def test_normalize_language(self) -> None:
        self.assertEqual(normalize_language("zh"), "zh")
        self.assertEqual(normalize_language("en"), "en")
        self.assertEqual(normalize_language("fr"), "zh")

    def test_language_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old = os.environ.get("TIPS_DATA_DIR")
            os.environ["TIPS_DATA_DIR"] = temp
            try:
                save_language("en")
                self.assertEqual(load_language(), "en")
                save_language("zh")
                self.assertEqual(load_language(), "zh")
            finally:
                if old is None:
                    os.environ.pop("TIPS_DATA_DIR", None)
                else:
                    os.environ["TIPS_DATA_DIR"] = old


if __name__ == "__main__":
    unittest.main()
