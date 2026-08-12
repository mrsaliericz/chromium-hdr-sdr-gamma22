#!/usr/bin/env python3
"""Fail-closed binary patcher for Chromium HDR SDR gamma experiments.

The patcher never downloads or redistributes a browser binary.  A recipe is
bound to one exact original DLL SHA-256 and contains enough structural checks
to reject an unexpected build before writing anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
from typing import BinaryIO, Iterable


ROOT = Path(__file__).resolve().parent
DEFAULT_RECIPES = ROOT / "recipes"
BACKUP_SUFFIX = ".gamma22-original"

SRGB_TRANSFER_FUNCTION = bytes.fromhex(
    "9A 99 19 40 6E A7 72 3F 19 89 55 3D 91 83 9E 3D "
    "E6 AE 25 3D 00 00 00 00 00 00 00 00"
)
GAMMA22_TRANSFER_FUNCTION = bytes.fromhex(
    "CD CC 0C 40 00 00 80 3F 00 00 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 00 00"
)
SRGB_GAMUT = bytes.fromhex(
    "00 44 DF 3E 00 32 C5 3E 00 80 12 3E "
    "00 D4 63 3E 00 85 37 3F 00 40 78 3D "
    "00 00 64 3C 00 D0 C6 3D 00 CF 36 3F"
)

INSTALLED_BROWSER_ROOTS = (
    Path(r"C:\Program Files\Google\Chrome\Application"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application"),
    Path(r"C:\Program Files\Microsoft\Edge\Application"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application"),
)


class PatchError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_hex(value: str) -> bytes:
    return bytes.fromhex(value.replace("_", " "))


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def reject_installed_browser(path: Path) -> None:
    resolved = path.resolve()
    for root in INSTALLED_BROWSER_ROOTS:
        if root.exists() and is_relative_to(resolved, root.resolve()):
            raise PatchError(
                f"Refusing to modify an installed browser: {resolved}\n"
                "Use an extracted Chrome for Testing / portable copy instead."
            )


def read_pe_sections(path: Path) -> list[tuple[str, int, int, int, int]]:
    with path.open("rb") as stream:
        dos = stream.read(0x1000)
        if dos[:2] != b"MZ":
            raise PatchError("Not a PE file (missing MZ header)")
        pe_offset = struct.unpack_from("<I", dos, 0x3C)[0]
        stream.seek(pe_offset)
        header = stream.read(24)
        if header[:4] != b"PE\0\0":
            raise PatchError("Not a PE file (missing PE signature)")
        machine = struct.unpack_from("<H", header, 4)[0]
        if machine != 0x8664:
            raise PatchError(f"Only Windows x64 is supported (PE machine 0x{machine:04X})")
        section_count = struct.unpack_from("<H", header, 6)[0]
        optional_size = struct.unpack_from("<H", header, 20)[0]
        stream.seek(pe_offset + 24 + optional_size)
        sections = []
        for _ in range(section_count):
            entry = stream.read(40)
            name = entry[:8].rstrip(b"\0").decode("ascii", "replace")
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", entry, 8
            )
            sections.append((name, virtual_address, virtual_size, raw_offset, raw_size))
        return sections


def rva_to_offset(
    sections: list[tuple[str, int, int, int, int]], rva: int
) -> int:
    for _name, virtual_address, virtual_size, raw_offset, raw_size in sections:
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_offset + rva - virtual_address
    raise PatchError(f"RVA 0x{rva:X} is outside all PE sections")


def read_at(stream: BinaryIO, offset: int, size: int) -> bytes:
    stream.seek(offset)
    data = stream.read(size)
    if len(data) != size:
        raise PatchError(f"Short read at file offset 0x{offset:X}")
    return data


def write_at(stream: BinaryIO, offset: int, data: bytes) -> None:
    stream.seek(offset)
    stream.write(data)


def rel32(instruction_rva: int, instruction_size: int, target_rva: int) -> bytes:
    displacement = target_rva - (instruction_rva + instruction_size)
    if not -(2**31) <= displacement < 2**31:
        raise PatchError("Relative branch target is outside rel32 range")
    return struct.pack("<i", displacement)


def branch(opcode: int, instruction_rva: int, target_rva: int) -> bytes:
    return bytes((opcode,)) + rel32(instruction_rva, 5, target_rva)


def load_recipes(directory: Path) -> list[dict]:
    recipes = []
    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as stream:
            recipe = json.load(stream)
        if recipe.get("schema_version") != 1:
            raise PatchError(f"Unsupported recipe schema in {path}")
        recipe["_path"] = str(path)
        recipes.append(recipe)
    if not recipes:
        raise PatchError(f"No recipes found in {directory}")
    return recipes


def choose_recipe(path: Path, recipes: Iterable[dict], allow_backup: bool = False) -> dict:
    actual = sha256(path)
    candidates = [
        recipe
        for recipe in recipes
        if actual
        in {
            recipe["original_sha256"].upper(),
            recipe.get("patched_sha256", "").upper(),
        }
    ]
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise PatchError("More than one recipe matches this DLL hash")

    if allow_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.is_file():
            backup_hash = sha256(backup)
            backup_candidates = [
                recipe
                for recipe in recipes
                if backup_hash == recipe["original_sha256"].upper()
            ]
            if len(backup_candidates) == 1:
                return backup_candidates[0]
            if len(backup_candidates) > 1:
                raise PatchError("More than one recipe matches the recovery copy")

    # A patched file may have been produced by an older recipe without a known
    # patched hash.  Try every same-named recipe structurally and require one.
    structural = []
    for recipe in recipes:
        if path.name.lower() != recipe["dll_name"].lower():
            continue
        try:
            state, _details = patch_state(path, recipe)
            if state == "patched":
                structural.append(recipe)
        except (PatchError, OSError, struct.error):
            pass
    if len(structural) == 1:
        return structural[0]

    supported = "\n".join(
        f"  {item['product']} {item['version']} ({item['architecture']})"
        for item in recipes
    )
    raise PatchError(
        f"No recipe matches SHA-256 {actual}.\nSupported builds:\n{supported}"
    )


def find_rip_movups_refs(text: bytes, text_rva: int, target_rva: int) -> list[int]:
    """Find `movups xmm?, [rip+disp32]` instructions targeting one RVA."""
    result = []
    position = 0
    valid_modrm = {0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D}
    while True:
        position = text.find(b"\x0F\x10", position)
        if position < 0:
            break
        if position + 7 <= len(text) and text[position + 2] in valid_modrm:
            displacement = struct.unpack_from("<i", text, position + 3)[0]
            target = text_rva + position + 7 + displacement
            if target == target_rva:
                result.append(text_rva + position)
        position += 1
    return result


def find_initializer_loads(
    path: Path,
    sections: list[tuple[str, int, int, int, int]],
    transfer_rva: int,
    gamut_rva: int,
    expected_count: int,
) -> list[tuple[int, int]]:
    try:
        _name, text_rva, _virtual_size, text_offset, text_size = next(
            section for section in sections if section[0] == ".text"
        )
    except StopIteration as error:
        raise PatchError("PE file has no .text section") from error
    with path.open("rb") as stream:
        stream.seek(text_offset)
        text = stream.read(text_size)

    first_refs = find_rip_movups_refs(text, text_rva, transfer_rva)
    second_refs = set(find_rip_movups_refs(text, text_rva, transfer_rva + 12))
    gamut_refs = set(find_rip_movups_refs(text, text_rva, gamut_rva))
    pairs: list[tuple[int, int]] = []
    for first in first_refs:
        seconds = [rva for rva in second_refs if first < rva < first + 48]
        gamuts = [rva for rva in gamut_refs if first < rva < first + 48]
        if len(seconds) == 1 and len(gamuts) == 1 and seconds[0] < gamuts[0]:
            pairs.append((first, seconds[0]))
    if len(pairs) != expected_count:
        raise PatchError(
            "Unexpected number of strict sRGB+BT.709 initializers: "
            f"{len(pairs)} (expected {expected_count})"
        )
    return pairs


def transfer_load(instruction_rva: int, target_rva: int, original: bytes) -> bytes:
    if len(original) != 7 or original[:2] != b"\x0F\x10":
        raise PatchError(f"Unexpected movups instruction at RVA 0x{instruction_rva:X}")
    return original[:3] + rel32(instruction_rva, 7, target_rva)


def make_trampoline(recipe: dict) -> bytes:
    hdr = recipe["hdr_output"]
    cave = int(hdr["cave_rva"], 0)
    call_target = int(hdr["set_output_call_rva"], 0)
    resume = int(hdr["resume_rva"], 0)
    code = bytearray()

    def emit(data: bytes) -> None:
        code.extend(data)

    def emit_call(target: int) -> None:
        rva = cave + len(code)
        emit(branch(0xE8, rva, target))

    # The verified target does not write to its Win64 shadow space, so the
    # existing RCX/R9 arguments can be preserved there without changing RSP.
    emit(bytes.fromhex("48 89 0C 24"))        # mov [rsp], rcx
    emit(bytes.fromhex("4C 89 4C 24 08"))     # mov [rsp+8], r9
    emit(bytes.fromhex("31 D2"))              # xor edx, edx (usage = SDR)
    emit(bytes.fromhex("45 31 C0"))           # xor r8d, r8d (opaque)
    emit_call(call_target)
    emit(bytes.fromhex("48 8B 0C 24"))        # mov rcx, [rsp]
    emit(bytes.fromhex("4C 8B 4C 24 08"))     # mov r9, [rsp+8]
    emit(bytes.fromhex("31 D2"))              # usage = SDR
    emit(bytes.fromhex("41 B0 01"))           # r8b = 1 (alpha)
    emit_call(call_target)
    emit(bytes.fromhex("48 8B 0C 24"))        # restore original args
    emit(bytes.fromhex("4C 8B 4C 24 08"))
    emit(bytes.fromhex("B2 01"))              # original usage = WCG
    emit(bytes.fromhex("45 31 C0"))           # original opaque flag
    rva = cave + len(code)
    emit(branch(0xE9, rva, resume))
    if len(code) > int(hdr["cave_size"]):
        raise PatchError("Generated trampoline does not fit in the recipe code cave")
    return bytes(code)


def validate_constants(stream: BinaryIO, sections, recipe: dict) -> None:
    color = recipe["color_space"]
    checks = (
        (int(color["srgb_gamut_rva"], 0), SRGB_GAMUT, "sRGB gamut"),
        (int(color["srgb_transfer_rva"], 0), SRGB_TRANSFER_FUNCTION, "sRGB transfer"),
        (int(color["gamma22_transfer_rva"], 0), GAMMA22_TRANSFER_FUNCTION, "gamma 2.2 transfer"),
    )
    for rva, expected, name in checks:
        actual = read_at(stream, rva_to_offset(sections, rva), len(expected))
        if actual != expected:
            raise PatchError(f"Unexpected {name} constant at RVA 0x{rva:X}")


def patch_state(path: Path, recipe: dict) -> tuple[str, list[str]]:
    sections = read_pe_sections(path)
    color = recipe["color_space"]
    hdr = recipe["hdr_output"]
    srgb_rva = int(color["srgb_transfer_rva"], 0)
    gamma_rva = int(color["gamma22_transfer_rva"], 0)
    gamut_rva = int(color["srgb_gamut_rva"], 0)
    expected_count = int(color["expected_initializer_count"])

    with path.open("rb") as stream:
        validate_constants(stream, sections, recipe)

    original_pairs = []
    patched_pairs = []
    try:
        original_pairs = find_initializer_loads(
            path, sections, srgb_rva, gamut_rva, expected_count
        )
    except PatchError:
        pass
    try:
        patched_pairs = find_initializer_loads(
            path, sections, gamma_rva, gamut_rva, expected_count
        )
    except PatchError:
        pass

    hook_rva = int(hdr["hook_rva"], 0)
    cave_rva = int(hdr["cave_rva"], 0)
    cave_size = int(hdr["cave_size"])
    original_hook = parse_hex(hdr["hook_original"])
    patched_hook = branch(0xE9, hook_rva, cave_rva)
    trampoline = make_trampoline(recipe)
    pristine_cave = bytes((int(hdr["cave_fill"], 0),)) * cave_size

    with path.open("rb") as stream:
        hook = read_at(stream, rva_to_offset(sections, hook_rva), len(original_hook))
        cave = read_at(stream, rva_to_offset(sections, cave_rva), cave_size)
        callee_rva = int(hdr["set_output_call_rva"], 0)
        callee_expected = parse_hex(hdr["set_output_callee_bytes"])
        callee = read_at(
            stream, rva_to_offset(sections, callee_rva), len(callee_expected)
        )
        if callee != callee_expected:
            raise PatchError("HDR output helper no longer matches the verified recipe")

    color_state = (
        "original" if original_pairs and not patched_pairs
        else "patched" if patched_pairs and not original_pairs
        else "unexpected"
    )
    hdr_state = (
        "original" if hook == original_hook and cave == pristine_cave
        else "patched"
        if hook == patched_hook
        and cave[: len(trampoline)] == trampoline
        and cave[len(trampoline) :] == pristine_cave[len(trampoline) :]
        else "unexpected"
    )
    details = [
        f"sRGB+BT.709 gamma loads: {color_state} "
        f"({expected_count} initializers / {expected_count * 2} RIP loads)",
        f"SDR scRGB/F16 output trampoline: {hdr_state}",
    ]
    if color_state == hdr_state == "original":
        return "original", details
    if color_state == hdr_state == "patched":
        return "patched", details
    return "mixed-or-unknown", details


def apply_recipe(path: Path, recipe: dict) -> None:
    reject_installed_browser(path)
    if not path.is_file():
        raise PatchError(f"DLL does not exist: {path}")
    state, details = patch_state(path, recipe)
    print("Before:")
    for detail in details:
        print(f"  {detail}")
    if state == "patched":
        print("Already patched; no changes made.")
        return
    if state != "original":
        raise PatchError("DLL is neither pristine nor consistently patched")
    actual_hash = sha256(path)
    expected_hash = recipe["original_sha256"].upper()
    if actual_hash != expected_hash:
        raise PatchError(
            f"Unexpected pristine DLL SHA-256: {actual_hash}\nExpected: {expected_hash}"
        )

    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if not backup.exists():
        print(f"Creating recovery copy: {backup}")
        shutil.copy2(path, backup)
    elif sha256(backup) != expected_hash:
        raise PatchError(f"Existing recovery copy has the wrong hash: {backup}")

    sections = read_pe_sections(path)
    color = recipe["color_space"]
    srgb_rva = int(color["srgb_transfer_rva"], 0)
    gamma_rva = int(color["gamma22_transfer_rva"], 0)
    gamut_rva = int(color["srgb_gamut_rva"], 0)
    pairs = find_initializer_loads(
        path,
        sections,
        srgb_rva,
        gamut_rva,
        int(color["expected_initializer_count"]),
    )
    hdr = recipe["hdr_output"]
    hook_rva = int(hdr["hook_rva"], 0)
    cave_rva = int(hdr["cave_rva"], 0)
    trampoline = make_trampoline(recipe)

    with path.open("r+b", buffering=0) as stream:
        for first, second in pairs:
            for instruction_rva, target in (
                (first, gamma_rva),
                (second, gamma_rva + 12),
            ):
                offset = rva_to_offset(sections, instruction_rva)
                original = read_at(stream, offset, 7)
                write_at(
                    stream,
                    offset,
                    transfer_load(instruction_rva, target, original),
                )
        write_at(
            stream,
            rva_to_offset(sections, cave_rva),
            trampoline,
        )
        write_at(
            stream,
            rva_to_offset(sections, hook_rva),
            branch(0xE9, hook_rva, cave_rva),
        )
        stream.flush()
        os.fsync(stream.fileno())

    state, details = patch_state(path, recipe)
    print("After:")
    for detail in details:
        print(f"  {detail}")
    if state != "patched":
        raise PatchError("Post-write verification failed")
    patched_hash = sha256(path)
    expected_patched = recipe.get("patched_sha256", "").upper()
    if expected_patched and patched_hash != expected_patched:
        raise PatchError(
            f"Patched hash mismatch: {patched_hash} (expected {expected_patched})"
        )
    print(f"Patched SHA-256: {patched_hash}")


def restore(path: Path, recipe: dict) -> None:
    reject_installed_browser(path)
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if not backup.is_file():
        raise PatchError(f"Recovery copy does not exist: {backup}")
    expected = recipe["original_sha256"].upper()
    if sha256(backup) != expected:
        raise PatchError(f"Recovery copy has the wrong hash: {backup}")
    shutil.copy2(backup, path)
    if sha256(path) != expected:
        raise PatchError("Restore verification failed")
    print(f"Restored pristine DLL: {path}")


def verify(path: Path, recipe: dict) -> None:
    state, details = patch_state(path, recipe)
    print(f"Recipe: {recipe['id']}")
    print(f"State: {state}")
    for detail in details:
        print(f"  {detail}")
    print(f"SHA-256: {sha256(path)}")


def resolve_dll(path: Path) -> Path:
    path = path.expanduser()
    if path.is_file():
        return path
    direct = path / "chrome.dll"
    if direct.is_file():
        return direct
    matches = list(path.glob("**/chrome.dll"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise PatchError(f"No chrome.dll found under: {path}")
    raise PatchError(f"More than one chrome.dll found under: {path}")


def write_launcher(dll: Path) -> Path:
    chrome = dll.with_name("chrome.exe")
    if not chrome.is_file():
        raise PatchError(f"chrome.exe was not found beside the patched DLL: {chrome}")
    launcher = dll.with_name("Start Chrome Gamma22.cmd")
    content = (
        "@echo off\r\n"
        'set "GAMMA22_PROFILE=%PUBLIC%\\ChromeGamma22PortableProfile"\r\n'
        'start "Chrome Gamma22" "%~dp0chrome.exe" '
        '--user-data-dir="%GAMMA22_PROFILE%" --no-first-run '
        '--disable-default-apps\r\n'
    )
    with launcher.open("w", encoding="utf-8", newline="") as stream:
        stream.write(content)
    return launcher


def interactive_main(recipes: list[dict]) -> int:
    print("Chromium HDR SDR Gamma 2.2 patcher")
    print("====================================")
    print("This tool supports only exact, audited Chrome for Testing builds.")
    print("Installed Chrome/Edge under Program Files is always refused.\n")

    search_roots = [Path.cwd()]
    if getattr(sys, "frozen", False):
        search_roots.insert(0, Path(sys.executable).resolve().parent)
    candidates: list[Path] = []
    for root in search_roots:
        try:
            candidate = resolve_dll(root)
        except PatchError:
            continue
        if candidate.resolve() not in [item.resolve() for item in candidates]:
            candidates.append(candidate)

    if len(candidates) == 1:
        dll = candidates[0]
    else:
        print("Place Gamma22Patcher.exe beside chrome.exe, or paste the path")
        print("to the extracted chrome-win64 folder / chrome.dll below.")
        entered = input("Chrome path: ").strip().strip('"')
        if not entered:
            print("Cancelled.")
            return 0
        dll = resolve_dll(Path(entered))

    recipe = choose_recipe(dll, recipes, allow_backup=True)
    state, details = patch_state(dll, recipe)
    print(f"\nSupported build: {recipe['product']} {recipe['version']}")
    print(f"Target: {dll}")
    print(f"State: {state}")
    for detail in details:
        print(f"  {detail}")

    print("\n[A] Apply gamma 2.2 patch")
    print("[V] Verify only")
    print("[R] Restore original DLL")
    print("[Q] Quit")
    choice = input("Choose: ").strip().lower()
    if choice == "q" or not choice:
        print("Cancelled; no changes made.")
        return 0
    if choice == "v":
        verify(dll, recipe)
        return 0
    if choice == "r":
        confirm = input("Type RESTORE to replace chrome.dll from its backup: ").strip()
        if confirm != "RESTORE":
            print("Cancelled; no changes made.")
            return 0
        restore(dll, recipe)
        return 0
    if choice != "a":
        raise PatchError(f"Unknown choice: {choice!r}")
    confirm = input("Type APPLY to patch this portable Chrome copy: ").strip()
    if confirm != "APPLY":
        print("Cancelled; no changes made.")
        return 0
    apply_recipe(dll, recipe)
    launcher = write_launcher(dll)
    print(f"Launcher created: {launcher}")
    print("Use that launcher so regular installed Chrome cannot capture the launch.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch a supported portable Chrome DLL for SDR gamma 2.2 in Windows HDR."
    )
    parser.add_argument("action", nargs="?", choices=("apply", "verify", "restore", "list"))
    parser.add_argument("path", nargs="?", type=Path, help="chrome.dll or extracted Chrome directory")
    parser.add_argument("--recipes", type=Path, default=DEFAULT_RECIPES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        recipes = load_recipes(args.recipes)
        if args.action is None:
            result = interactive_main(recipes)
            if sys.stdin.isatty():
                input("\nPress Enter to close...")
            return result
        if args.action == "list":
            for recipe in recipes:
                print(
                    f"{recipe['id']}: {recipe['product']} {recipe['version']} "
                    f"({recipe['architecture']})"
                )
            return 0
        if args.path is None:
            raise PatchError("A chrome.dll or extracted Chrome directory is required")
        dll = resolve_dll(args.path)
        recipe = choose_recipe(dll, recipes, allow_backup=args.action == "restore")
        print(f"Using recipe: {recipe['id']}")
        print(f"Target: {dll}")
        if args.action == "apply":
            apply_recipe(dll, recipe)
        elif args.action == "restore":
            restore(dll, recipe)
        else:
            verify(dll, recipe)
        return 0
    except (PatchError, OSError, ValueError, KeyError, struct.error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
