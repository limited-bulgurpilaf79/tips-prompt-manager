from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from tips_prompt_manager import auth


class AuthTests(unittest.TestCase):
    def test_password_hash_verifies_with_same_salt(self) -> None:
        salt, digest = auth.password_hash("correct horse")
        _, second = auth.password_hash("correct horse", salt)
        self.assertEqual(digest, second)

    def test_password_hash_rejects_wrong_password(self) -> None:
        salt, digest = auth.password_hash("correct horse")
        config = {"password_salt": salt, "password_hash": digest}
        self.assertTrue(auth.verify_password("correct horse", config))
        self.assertFalse(auth.verify_password("wrong", config))

    def test_config_roundtrip_uses_data_dir_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old = os.environ.get("TIPS_DATA_DIR")
            os.environ["TIPS_DATA_DIR"] = temp
            try:
                config = auth.create_password_config("abcd")
                auth.save_config(config)
                self.assertTrue((Path(temp) / "config.json").exists())
                self.assertTrue(auth.verify_password("abcd", auth.load_config()))
            finally:
                if old is None:
                    os.environ.pop("TIPS_DATA_DIR", None)
                else:
                    os.environ["TIPS_DATA_DIR"] = old


if __name__ == "__main__":
    unittest.main()
