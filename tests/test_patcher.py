import json
from pathlib import Path
import tempfile
import unittest

import gamma22_patcher as patcher


ROOT = Path(__file__).resolve().parents[1]


class RecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipes = []
        for path in sorted((ROOT / "recipes").glob("*.json")):
            with path.open("r", encoding="utf-8") as stream:
                cls.recipes.append(json.load(stream))
        cls.recipe = next(
            recipe
            for recipe in cls.recipes
            if recipe["id"] == "chrome-for-testing-win64-151.0.7922.138"
        )

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
        for recipe in self.recipes:
            for key in ("original_sha256", "patched_sha256"):
                value = recipe[key]
                self.assertEqual(len(value), 64, recipe["id"])
                int(value, 16)

    def test_recipe_patch_kinds_are_known(self):
        supported = {
            patcher.PATCH_KIND_LOADS_TRAMPOLINE,
            patcher.PATCH_KIND_EDGE_SINGLETON_USAGE_TABLE,
        }
        for recipe in self.recipes:
            self.assertIn(
                recipe.get("patch_kind", patcher.PATCH_KIND_LOADS_TRAMPOLINE),
                supported,
            )

    def test_launcher_uses_isolated_public_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "chrome.exe").touch()
            launcher = patcher.write_launcher(root / "chrome.dll")
            content = launcher.read_text(encoding="utf-8")
            self.assertIn("%PUBLIC%\\ChromeGamma22PortableProfile", content)
            self.assertIn('--user-data-dir="%GAMMA22_PROFILE%"', content)
            self.assertIn('"%~dp0chrome.exe"', content)

    def test_portableapps_launcher_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            launcher = root / "GoogleChromePortable.exe"
            launcher.touch()
            dll = root / "App" / "Chrome-bin" / "150.0.0.0" / "chrome.dll"
            dll.parent.mkdir(parents=True)
            self.assertEqual(patcher.write_launcher(dll), launcher)

    def test_edge_launcher_uses_portable_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            application = root / "Application"
            version = application / "151.0.4129.78"
            version.mkdir(parents=True)
            (application / "msedge.exe").touch()
            launcher = patcher.write_launcher(version / "msedge.dll")
            self.assertEqual(launcher, root / "Start Edge Gamma22.cmd")
            content = launcher.read_text(encoding="utf-8")
            self.assertIn("%~dp0EdgeGamma22Profile", content)
            self.assertIn("%~dp0Application\\msedge.exe", content)

    def test_resolve_dll_accepts_edge(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dll = root / "Application" / "151.0.0.0" / "msedge.dll"
            dll.parent.mkdir(parents=True)
            dll.touch()
            self.assertEqual(patcher.resolve_dll(root), dll)


if __name__ == "__main__":
    unittest.main()
