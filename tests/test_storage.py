from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tips_prompt_manager.storage import DEFAULT_CATEGORY, PromptRepository


class StorageTests(unittest.TestCase):
    def test_repository_initializes_default_category(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = PromptRepository(Path(temp) / "prompts.db")
            try:
                names = [row["name"] for row in repo.list_categories()]
                self.assertIn(DEFAULT_CATEGORY, names)
            finally:
                repo.close()

    def test_prompt_crud_and_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = PromptRepository(Path(temp) / "prompts.db")
            try:
                category_id = repo.get_category_by_name(DEFAULT_CATEGORY)["id"]
                prompt_id = repo.save_prompt(None, "Summarize", "Summarize this text", category_id)
                self.assertEqual(repo.get_prompt(prompt_id)["title"], "Summarize")
                repo.save_prompt(prompt_id, "Summarize now", "Summarize this text carefully", category_id)
                rows = repo.list_prompts(query="carefully")
                self.assertEqual(len(rows), 1)
                repo.delete_prompt(prompt_id)
                self.assertEqual(repo.list_prompts(), [])
            finally:
                repo.close()

    def test_delete_category_moves_prompts_to_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = PromptRepository(Path(temp) / "prompts.db")
            try:
                custom_id = repo.add_category("Work")
                prompt_id = repo.save_prompt(None, "Idea", "Use this prompt", custom_id)
                repo.delete_category(custom_id)
                prompt = repo.get_prompt(prompt_id)
                self.assertEqual(prompt["category_name"], DEFAULT_CATEGORY)
            finally:
                repo.close()


if __name__ == "__main__":
    unittest.main()
