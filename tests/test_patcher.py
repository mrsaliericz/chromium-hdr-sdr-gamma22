import json
from pathlib import Path
import unittest

import gamma22_patcher as patcher


ROOT = Path(__file__).resolve().parents[1]


class RecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "recipes" / "chrome-for-testing-win64-151.0.7922.138.json").open(
            "r", encoding="utf-8"
        ) as stream:
            cls.recipe = json.load(stream)

    def test_named_transfer_functions_are_distinct(self):
        self.assertEqual(len(patcher.SRGB_TRANSFER_FUNCTION), 28)
        self.assertEqual(len(patcher.GAMMA22_TRANSFER_FUNCTION), 28)
        self.assertNotEqual(
            patcher.SRGB_TRANSFER_FUNCTION,
            patcher.GAMMA22_TRANSFER_FUNCTION,
        )

    def test_trampoline_fits_verified_code_cave(self):
        trampoline = patcher.make_trampoline(self.recipe)
        self.assertLessEqual(
            len(trampoline), self.recipe["hdr_output"]["cave_size"]
        )
        self.assertEqual(trampoline[:4], bytes.fromhex("48 89 0C 24"))
        self.assertEqual(trampoline[-5], 0xE9)

    def test_recipe_hashes_are_sha256(self):
        for key in ("original_sha256", "patched_sha256"):
            value = self.recipe[key]
            self.assertEqual(len(value), 64)
            int(value, 16)


if __name__ == "__main__":
    unittest.main()
