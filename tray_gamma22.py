#!/usr/bin/env python3
"""Native Win32 notification-area frontend for Gamma22 hot attach."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
import threading

import hot_attach_gamma22 as hot


WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_CONTEXTMENU = 0x007B
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONUP = 0x0205
WM_APP = 0x8000
WM_TRAY = WM_APP + 1
WM_STATUS_CHANGED = WM_APP + 2
NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIM_SETVERSION = 4
NOTIFYICON_VERSION_4 = 4
NIF_MESSAGE = 0x01
NIF_ICON = 0x02
NIF_TIP = 0x04
MF_STRING = 0
MF_GRAYED = 0x01
MF_SEPARATOR = 0x0800
TPM_RIGHTBUTTON = 0x0002
TPM_RETURNCMD = 0x0100
SW_SHOWNORMAL = 1
IDI_APPLICATION = 32512
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x0010
CMD_STATUS = 100
CMD_LOG = 101
CMD_EXIT = 102
CMD_TOGGLE = 103

user32 = ctypes.WinDLL("user32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(
    LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", GUID),
        ("hBalloonIcon", wintypes.HICON),
    ]


kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.RegisterClassW.restype = wintypes.ATOM
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    ctypes.c_void_p,
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.DefWindowProcW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.DefWindowProcW.restype = LRESULT
user32.LoadIconW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
user32.LoadIconW.restype = wintypes.HICON
user32.LoadImageW.argtypes = [
    wintypes.HINSTANCE,
    wintypes.LPCWSTR,
    wintypes.UINT,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.LoadImageW.restype = wintypes.HANDLE
user32.DestroyIcon.argtypes = [wintypes.HICON]
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    ctypes.c_size_t,
    wintypes.LPCWSTR,
]
user32.TrackPopupMenu.argtypes = [
    wintypes.HMENU,
    wintypes.UINT,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    ctypes.c_void_p,
]
user32.TrackPopupMenu.restype = wintypes.UINT
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.PostMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.GetMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
]
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL
shell32.ExtractIconExW.argtypes = [
    wintypes.LPCWSTR,
    ctypes.c_int,
    ctypes.POINTER(wintypes.HICON),
    ctypes.POINTER(wintypes.HICON),
    wintypes.UINT,
]
shell32.ExtractIconExW.restype = wintypes.UINT
shell32.ShellExecuteW.argtypes = [
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    ctypes.c_int,
]

stop_event = threading.Event()
status_lock = threading.Lock()
fix_lock = threading.Lock()
current_status = "Starting"
fix_enabled = True
switch_in_progress = False
window_handle = None
notify_data = None
active_icon = None
inactive_icon = None
owned_icons: set[int] = set()
log_path = None


def set_status(value: str) -> None:
    global current_status
    with status_lock:
        current_status = value
    if window_handle:
        user32.PostMessageW(window_handle, WM_STATUS_CHANGED, 0, 0)


def status_text() -> str:
    with status_lock:
        return current_status


def fix_mode() -> tuple[bool, bool]:
    with fix_lock:
        return fix_enabled, switch_in_progress


def request_fix_toggle() -> None:
    global fix_enabled, switch_in_progress
    with fix_lock:
        if switch_in_progress:
            return
        fix_enabled = not fix_enabled
        switch_in_progress = True
        destination = "ON" if fix_enabled else "OFF"
    set_status(f"Switching Gamma 2.2 fix {destination}…")


def finish_fix_toggle() -> None:
    global switch_in_progress
    with fix_lock:
        switch_in_progress = False


def update_tray_state() -> None:
    if notify_data is None:
        return
    enabled, _switching = fix_mode()
    notify_data.uFlags = NIF_ICON | NIF_TIP
    notify_data.hIcon = active_icon if enabled else inactive_icon
    notify_data.szTip = f"Chromium Gamma 2.2 — {status_text()}"[:127]
    shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(notify_data))


def open_log() -> None:
    if log_path is not None:
        shell32.ShellExecuteW(None, "open", str(log_path), None, None, SW_SHOWNORMAL)


def show_menu(hwnd) -> None:
    menu = user32.CreatePopupMenu()
    if not menu:
        return
    try:
        user32.AppendMenuW(menu, MF_STRING | MF_GRAYED, CMD_STATUS, status_text()[:80])
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        enabled, switching = fix_mode()
        toggle_label = (
            "Switching…"
            if switching
            else "Disable Gamma 2.2 fix"
            if enabled
            else "Enable Gamma 2.2 fix"
        )
        toggle_flags = MF_STRING | (MF_GRAYED if switching else 0)
        user32.AppendMenuW(menu, toggle_flags, CMD_TOGGLE, toggle_label)
        user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(menu, MF_STRING, CMD_LOG, "Open diagnostic log")
        user32.AppendMenuW(menu, MF_STRING, CMD_EXIT, "Exit")
        point = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))
        user32.SetForegroundWindow(hwnd)
        command = user32.TrackPopupMenu(
            menu,
            TPM_RIGHTBUTTON | TPM_RETURNCMD,
            point.x,
            point.y,
            0,
            hwnd,
            None,
        )
        if command == CMD_TOGGLE:
            request_fix_toggle()
        elif command == CMD_LOG:
            open_log()
        elif command == CMD_EXIT:
            stop_event.set()
            user32.DestroyWindow(hwnd)
    finally:
        user32.DestroyMenu(menu)


@WNDPROC
def window_proc(hwnd, message, wparam, lparam):
    if message == WM_TRAY:
        event = int(lparam) & 0xFFFF
        if event in (WM_RBUTTONUP, WM_CONTEXTMENU):
            show_menu(hwnd)
        elif event == WM_LBUTTONDBLCLK:
            open_log()
        return 0
    if message == WM_STATUS_CHANGED:
        update_tray_state()
        return 0
    if message == WM_CLOSE:
        stop_event.set()
        user32.DestroyWindow(hwnd)
        return 0
    if message == WM_DESTROY:
        if notify_data is not None:
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(notify_data))
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, message, wparam, lparam)


def load_icon_file(resource_root: Path, filename: str) -> int | None:
    icon_path = resource_root / "assets" / filename
    if not icon_path.is_file():
        return None
    icon = user32.LoadImageW(
        None, str(icon_path), IMAGE_ICON, 16, 16, LR_LOADFROMFILE
    )
    return int(icon) if icon else None


def load_app_icons() -> tuple[int, int, set[int]]:
    resource_root = Path(
        getattr(hot.sys, "_MEIPASS", Path(__file__).resolve().parent)
    )
    active = load_icon_file(resource_root, "gamma22.ico")
    inactive = load_icon_file(resource_root, "gamma22-disabled.ico")
    loaded = {icon for icon in (active, inactive) if icon is not None}
    if active is not None:
        return active, inactive or active, loaded
    try:
        large = wintypes.HICON()
        small = wintypes.HICON()
        if shell32.ExtractIconExW(
            hot.sys.executable, 0, ctypes.byref(large), ctypes.byref(small), 1
        ):
            if large:
                user32.DestroyIcon(large)
            if small:
                fallback = int(small)
                return fallback, fallback, {fallback}
    except Exception:
        pass
    fallback = int(
        user32.LoadIconW(None, ctypes.cast(IDI_APPLICATION, wintypes.LPCWSTR))
    )
    return fallback, fallback, set()


def worker() -> None:
    browser_locations = (
        (
            "Chrome",
            (
                Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
                Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            ),
        ),
        (
            "Edge",
            (
                Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
                Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            ),
        ),
    )
    targets = []
    states = {}

    def publish_status() -> None:
        if not states:
            set_status("No supported browser installed")
            return
        set_status(" | ".join(f"{name}: {states[name]}" for name in states))

    for name, candidates in browser_locations:
        installed = [candidate.resolve() for candidate in candidates if candidate.is_file()]
        if not installed:
            continue
        if len(installed) > 1:
            states[name] = "multiple installations"
            publish_status()
            print(f"{name}: multiple installed executables found; skipping")
            continue
        browser = installed[0]
        states[name] = "analyzing"
        publish_status()
        try:
            dll = hot.locate_chrome_dll(browser, None)
            plan = hot.make_runtime_plan(dll)
            expected_dll = hot.normalized_path(dll)
            current = set(hot.running_processes_for_executable(browser))
            completed: set[int] = set()
            enabled, _switching = fix_mode()
            if current:
                patched, already_debugged = hot.attach_and_patch(
                    browser, dll, enabled=enabled
                )
                completed = patched | already_debugged
                hot.refresh_display_state(current)
                states[name] = "active" if enabled else "off"
            else:
                states[name] = "waiting" if enabled else "off"
            targets.append(
                {
                    "name": name,
                    "browser": browser,
                    "dll": dll,
                    "plan": plan,
                    "expected_dll": expected_dll,
                    "completed": completed,
                    "failures": {},
                }
            )
            print(f"{name}: watching {browser} ({dll.name}, {plan.dll_hash[:12]})")
        except Exception as error:
            states[name] = "unsupported/error"
            print(f"{name}: ERROR: {error}")
        publish_status()

    last_enabled, initial_switching = fix_mode()
    if initial_switching:
        finish_fix_toggle()
    while not stop_event.is_set():
        enabled, _switching = fix_mode()
        mode_changed = enabled != last_enabled
        if mode_changed:
            destination = "on" if enabled else "off"
            print(f"Switching Gamma 2.2 fix {destination} for all running browsers")
            for target in targets:
                target["completed"].clear()
                states[target["name"]] = f"switching {destination}"
            publish_status()
        for target in targets:
            name = target["name"]
            browser = target["browser"]
            try:
                current = set(hot.running_processes_for_executable(browser))
                target["completed"].intersection_update(current)
                states[name] = (
                    "active" if enabled and current
                    else "waiting" if enabled
                    else "off"
                )
                for pid in sorted(current - target["completed"]):
                    try:
                        command_line = hot.process_command_line(pid)
                    except (OSError, hot.PatchError):
                        target["failures"][pid] = target["failures"].get(pid, 0) + 1
                        continue
                    if "--type=crashpad-handler" in command_line:
                        target["completed"].add(pid)
                        continue
                    if "--type=gpu-process" in command_line:
                        role = "gpu"
                    elif "--type=" not in command_line:
                        role = "browser"
                    else:
                        # Renderer and utility processes intentionally retain
                        # their pristine upstream gamma behavior.
                        target["completed"].add(pid)
                        continue
                    success, detail = hot.attach_one(
                        pid,
                        target["plan"],
                        target["expected_dll"],
                        role=role,
                        enabled=enabled,
                    )
                    if success:
                        target["completed"].add(pid)
                        target["failures"].pop(pid, None)
                        print(f"{name}: new {role} PID {pid}: {detail}")
                        hot.refresh_display_state(current)
                    else:
                        attempts = target["failures"].get(pid, 0) + 1
                        target["failures"][pid] = attempts
                        if attempts == 1 or attempts % 10 == 0:
                            print(
                                f"{name}: PID {pid} attach attempt {attempts} "
                                f"deferred ({detail})"
                            )
            except Exception as error:
                states[name] = "error"
                print(f"{name} watcher ERROR: {error}")
            publish_status()
        if mode_changed:
            last_enabled = enabled
            finish_fix_toggle()
            publish_status()
        stop_event.wait(0.5)


def main() -> int:
    global active_icon, inactive_icon, log_path, notify_data, owned_icons, window_handle
    log_path = hot.configure_background_process()
    if getattr(hot.sys, "frozen", False) and hot._instance_mutex is None:
        return 0
    hot.set_status_callback(set_status)

    instance = kernel32.GetModuleHandleW(None)
    class_name = "ChromiumGamma22TrayWindow"
    window_class = WNDCLASSW()
    window_class.lpfnWndProc = window_proc
    window_class.hInstance = instance
    window_class.lpszClassName = class_name
    if not user32.RegisterClassW(ctypes.byref(window_class)):
        raise ctypes.WinError(ctypes.get_last_error())
    window_handle = user32.CreateWindowExW(
        0, class_name, class_name, 0, 0, 0, 0, 0, None, None, instance, None
    )
    if not window_handle:
        raise ctypes.WinError(ctypes.get_last_error())

    active_icon, inactive_icon, owned_icons = load_app_icons()
    notify_data = NOTIFYICONDATAW()
    notify_data.cbSize = ctypes.sizeof(notify_data)
    notify_data.hWnd = window_handle
    notify_data.uID = 1
    notify_data.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
    notify_data.uCallbackMessage = WM_TRAY
    notify_data.hIcon = active_icon
    notify_data.szTip = "Chromium Gamma 2.2 — Starting"
    if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(notify_data)):
        raise ctypes.WinError(ctypes.get_last_error())
    notify_data.uVersion = NOTIFYICON_VERSION_4
    shell32.Shell_NotifyIconW(NIM_SETVERSION, ctypes.byref(notify_data))

    threading.Thread(target=worker, name="Gamma22Watcher", daemon=True).start()
    message = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(message))
        user32.DispatchMessageW(ctypes.byref(message))
    stop_event.set()
    for icon in owned_icons:
        user32.DestroyIcon(icon)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
