## Gamma22Tray v0.4.0 — installed Chrome and Edge runtime release

Gamma22Tray v0.4.0 brings the SDR gamma 2.2 correction to normally installed
64-bit Google Chrome and Microsoft Edge on Windows 11 HDR. Portable or isolated
browser copies are no longer required, and browser files are never modified on
disk.

### Highlights

- Watches installed Chrome and Edge simultaneously from the notification area.
- Attaches to already running browsers and follows new browser/GPU processes.
- Preserves Chromium's native Display-P3, PQ, HLG and HDR video paths.
- Provides a true runtime ON/OFF switch and colored/gray tray status.
- Includes optional per-user **Start with Windows**, About and diagnostic log.
- Structurally discovers compatible Chromium layouts and fails closed on an
  unknown version before writing process memory.

### Browser updates

Gamma22Tray checks the installed DLL generation every five seconds. After a
compatible Chrome or Edge update is detected, it stops new runtime writes,
waits 15 seconds for the update to settle and restarts itself before attaching
to the current generation. Repeated or incompatible processes are bounded to
prevent debugger-attachment retry storms.

This handoff was verified during real Chrome and Edge updates: in both cases
the correction resumed after several seconds without manual intervention.

### Download and usage

1. Download `Gamma22Tray-win64.zip` below.
2. Extract the complete `Gamma22Tray` folder to a permanent location.
3. Keep `Gamma22Tray.exe` beside its `_internal` folder. Copying only the EXE
   will produce a missing Python DLL error.
4. Run `Gamma22Tray.exe` normally, not as administrator.
5. Use the tray menu for ON/OFF, optional Start with Windows, About and logs.

### Antivirus and packaging

The earlier one-file PyInstaller beta triggered Windows Defender's behavioral
heuristics. The stable release therefore uses an unpacked onedir package and
also eliminates aggressive repeated debugger-attachment attempts. This layout
survived real Chrome and Edge updates without a Defender detection during
testing.

The program is still unsigned and necessarily attaches as a debugger and
writes to browser process memory. Antivirus false positives remain possible.
Do not disable security software; verify the SHA-256, inspect the source, and
build it yourself if in doubt.

### Validation

- 19 automated tests cover patch recipes, update generations, safe restart,
  bounded attach attempts, tray metadata and per-user autostart.
- Tested on Windows 11 x64 with Windows HDR enabled.
- Final package verified with Google Chrome `151.0.7922.174` and Microsoft Edge
  `151.0.4129.101` after real browser updates.
- Real update handoff verified with installed Google Chrome and Microsoft Edge.
- Native HDR video, HDR black levels, PQ/HLG and Display-P3 remained unchanged.

- Author: Jaroslav Safar
- Contact: `jaroslav.safar.91@gmail.com`
