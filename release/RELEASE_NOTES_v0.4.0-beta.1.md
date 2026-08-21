## Gamma22Tray v0.4.0-beta.1 — runtime tray test

This is an experimental preview of the new non-destructive runtime mode for the
normally installed 64-bit Google Chrome and Microsoft Edge on Windows 11.

### What is new

- Attaches to an already running Chrome or Edge and changes only process memory.
- Watches future browser/GPU processes so new windows and tabs stay corrected.
- Supports Chrome and Edge simultaneously from one notification-area app.
- Provides a true runtime ON/OFF switch without restarting the browser.
- Uses a colored tray icon while enabled and a gray icon while disabled.
- Leaves browser files on disk and normal Chrome/Edge updates untouched.
- Preserves the original Display-P3, PQ, HLG and native HDR video paths.
- Uses strict structural verification and fails closed on an unfamiliar layout.

### Tested versions

- Google Chrome `151.0.7922.138`, x64
- Microsoft Edge `151.0.4129.86`, x64
- Windows 11 x64 with Windows HDR enabled

Structural discovery may also recognize later Chromium versions, but this beta
does not promise universal forward compatibility. Please report the browser
version and attach `%LOCALAPPDATA%\ChromiumGamma22\Gamma22HotAttach.log` when an
updated build is rejected.

### Usage

1. Download `Gamma22Tray.exe` below.
2. Run it normally, not as administrator.
3. Start or continue using installed Chrome or Edge.
4. Right-click the tray icon for status, ON/OFF and the diagnostic log.

Disable the fix before exiting if you want to restore the currently running
browser immediately. Otherwise, all changes disappear when the browser exits.

### Antivirus warning

The EXE is currently unsigned and uses debugger attachment plus process-memory
writes. Defender or VirusTotal engines may flag those behaviors heuristically.
The complete source and build script are included in this repository. Do not
disable antivirus protection; verify the SHA-256 and build from source if in
doubt.

SHA-256 (`Gamma22Tray.exe`):

`7A85A76B70F800DB1C241781727DECD1E2BE42316C67B7945AAFCB586BE638F6`
