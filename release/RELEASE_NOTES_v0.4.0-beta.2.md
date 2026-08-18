## Gamma22Tray v0.4.0-beta.2 — automatic browser-update handoff

This remains an experimental pre-release for normally installed 64-bit Google
Chrome and Microsoft Edge on Windows 11 HDR.

### What is new

- Checks the installed Chrome and Edge DLL generation every five seconds.
- Structurally analyzes a newly installed DLL without restarting Gamma22Tray.
- Retains verified old and new runtime plans simultaneously while processes
  from both browser generations coexist during an update.
- Detects a replacement DLL even when an updater reuses the same file path.
- Fails closed on an unfamiliar layout and retries safely later.
- Adds **Start with Windows**, stored per user under the standard HKCU Run key.
- Adds an **About Gamma22Tray** dialog with version, project and author contact.
- Keeps the runtime ON/OFF switch and colored/gray tray status introduced in
  beta 1.

### Important beta limitation

The automatic handoff has passed simulated tests for:

- a newly installed version-directory DLL,
- an in-place DLL replacement,
- old and new in-memory generations coexisting,
- an unsupported update preserving the last verified plan.

It has **not yet been observed through a real Chrome or Edge update that arrived
while this exact beta was already running**. Please treat that as the main beta
test. After the next update, confirm that the fix remains active without
restarting Gamma22Tray and look for this diagnostic-log message:

```text
Edge: browser update detected: old_version -> new_version
```

Please report the browser version and attach
`%LOCALAPPDATA%\ChromiumGamma22\Gamma22HotAttach.log` if the handoff fails.

### Tested versions

- Google Chrome `151.0.7922.138`, x64
- Microsoft Edge `151.0.4129.93`, x64
- Windows 11 x64 with Windows HDR enabled

### Usage

1. Download `Gamma22Tray.exe` below.
2. Run it normally, not as administrator.
3. Start or continue using installed Chrome or Edge.
4. Right-click the tray icon for ON/OFF, **Start with Windows**, About and the
   diagnostic log.

### Antivirus warning

The EXE is unsigned and uses debugger attachment plus process-memory writes.
Defender or VirusTotal engines may flag those behaviors heuristically. Do not
disable antivirus protection; verify the SHA-256 and build from the published
source if in doubt.

The release SHA-256 and exact source commit are appended automatically by the
GitHub Actions build that creates the downloadable EXE.

- Author: Jaroslav Safar
- Contact: `jaroslav.safar.91@gmail.com`
