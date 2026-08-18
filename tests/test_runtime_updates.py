import hashlib
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import hot_attach_gamma22 as hot
import tray_gamma22 as tray
from tray_gamma22 import BrowserGenerations


class RuntimeUpdateTests(unittest.TestCase):
    def make_installation(self, root: Path):
        application = root / "Application"
        application.mkdir()
        browser = application / "msedge.exe"
        browser.write_bytes(b"test browser")
        first = application / "151.0.1.1" / "msedge.dll"
        second = application / "151.0.1.2" / "msedge.dll"
        first.parent.mkdir()
        second.parent.mkdir()
        first.write_bytes(b"first compatible generation")
        second.write_bytes(b"second compatible generation")
        return browser, first, second

    @staticmethod
    def fake_plan(dll: Path):
        data = dll.read_bytes()
        if data.startswith(b"unsupported"):
            raise hot.PatchError("unknown structural layout")
        return SimpleNamespace(
            dll=dll,
            dll_hash=hashlib.sha256(data).hexdigest().upper(),
            checks=[],
            writes=[],
        )

    def test_new_version_is_activated_without_dropping_old_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            browser, first, second = self.make_installation(Path(directory))
            selected = [first]
            registry = BrowserGenerations(
                browser,
                locator=lambda _browser, _explicit: selected[0],
                planner=self.fake_plan,
                clock=lambda: 100.0,
            )
            registry.activate(first)
            selected[0] = second

            update = registry.poll(force=True)

            self.assertEqual(update[0], "updated")
            self.assertEqual(registry.active_dll, second.resolve())
            self.assertEqual(len(registry.plans_by_dll), 2)
            self.assertIn(hot.normalized_path(first), registry.plans_by_dll)
            self.assertIn(hot.normalized_path(second), registry.plans_by_dll)

    def test_in_place_replacement_keeps_both_memory_generations(self):
        with tempfile.TemporaryDirectory() as directory:
            browser, first, _second = self.make_installation(Path(directory))
            registry = BrowserGenerations(
                browser,
                locator=lambda _browser, _explicit: first,
                planner=self.fake_plan,
                clock=lambda: 100.0,
            )
            registry.activate(first)
            first.write_bytes(b"replacement generation with a different size")

            update = registry.poll(force=True)

            key = hot.normalized_path(first)
            self.assertEqual(update[0], "updated")
            self.assertEqual(len(registry.plans_by_dll[key]), 2)

    def test_unsupported_update_preserves_last_verified_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            browser, first, second = self.make_installation(Path(directory))
            registry = BrowserGenerations(
                browser,
                locator=lambda _browser, _explicit: second,
                planner=self.fake_plan,
                clock=lambda: 100.0,
            )
            registry.activate(first)
            second.write_bytes(b"unsupported new layout")

            update = registry.poll(force=True)

            self.assertEqual(update[0], "error")
            self.assertIn("unknown structural layout", update[1])
            self.assertEqual(registry.active_dll, first.resolve())
            self.assertEqual(len(registry.plans_by_dll), 1)

    def test_module_match_accepts_original_or_patched_writes(self):
        write = SimpleNamespace(
            rva=0x30,
            original=b"original",
            patched=b"patched!",
        )
        plan = SimpleNamespace(
            checks=[("signature", 0x10, b"check")],
            writes=[write],
        )
        base = 0x1000
        memory = {
            base + 0x10: b"check",
            base + 0x30: b"patched!",
        }

        with mock.patch.object(
            hot,
            "read_memory",
            side_effect=lambda _process, address, _size: memory[address],
        ):
            self.assertTrue(hot.module_matches_plan(object(), base, plan))
            memory[base + 0x30] = b"unknown!"
            self.assertFalse(hot.module_matches_plan(object(), base, plan))


class TrayInterfaceTests(unittest.TestCase):
    def test_about_metadata_is_present(self):
        self.assertEqual(tray.APP_NAME, "Gamma22Tray")
        self.assertEqual(tray.APP_VERSION, "0.4.0-beta.2")
        self.assertEqual(tray.APP_AUTHOR, "Jaroslav Safar")
        self.assertEqual(tray.APP_EMAIL, "jaroslav.safar.91@gmail.com")

    def test_enable_autostart_writes_current_executable_to_hkcu(self):
        key = object()
        context = mock.MagicMock()
        context.__enter__.return_value = key
        with mock.patch.object(
            tray, "autostart_command", return_value='"C:\\Tools\\Gamma22Tray.exe"'
        ), mock.patch.object(
            tray.winreg, "CreateKeyEx", return_value=context
        ) as create_key, mock.patch.object(tray.winreg, "SetValueEx") as set_value:
            tray.set_autostart(True)

        create_key.assert_called_once_with(
            tray.winreg.HKEY_CURRENT_USER,
            tray.RUN_KEY,
            0,
            tray.winreg.KEY_SET_VALUE,
        )
        set_value.assert_called_once_with(
            key,
            tray.RUN_VALUE_NAME,
            0,
            tray.winreg.REG_SZ,
            '"C:\\Tools\\Gamma22Tray.exe"',
        )

    def test_disable_autostart_removes_only_its_own_run_value(self):
        key = object()
        context = mock.MagicMock()
        context.__enter__.return_value = key
        with mock.patch.object(
            tray, "autostart_command", return_value='"C:\\Tools\\Gamma22Tray.exe"'
        ), mock.patch.object(
            tray.winreg, "OpenKey", return_value=context
        ), mock.patch.object(tray.winreg, "DeleteValue") as delete_value:
            tray.set_autostart(False)

        delete_value.assert_called_once_with(key, tray.RUN_VALUE_NAME)


if __name__ == "__main__":
    unittest.main()
