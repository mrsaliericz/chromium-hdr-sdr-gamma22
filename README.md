# Chromium HDR SDR Gamma 2.2 patcher

> **Free and open source, forever.** You may use, share, modify and redistribute
> this MIT-licensed solution at no cost. If it improves your Windows HDR setup
> and you would like to support the work, I will be very happy if you
> [buy me a coffee ☕](https://buymeacoffee.com/mrsaliericze) — but donating is
> entirely optional and the patcher is and always will be free.

Experimental, fail-closed patcher for supported **64-bit Google Chrome and
Microsoft Edge builds on Windows**, including normally branded Google Chrome
Portable and an isolated copy of Microsoft Edge.
It keeps Chromium's native HDR / wide-gamut pipeline, but changes ordinary
BT.709+sRGB SDR content to a pure gamma 2.2 interpretation while Windows HDR
is enabled.

> **HDR content is displayed correctly and without any modification.** The
> patch changes only ordinary SDR BT.709/sRGB interpretation. Native HDR video,
> PQ, HLG, HDR black levels and highlights remain on Chromium's original HDR
> path and visually match the unpatched browser.

The repository contains **no Chrome or Edge binaries**. Obtain the browser from
Google or Microsoft and patch only your own extracted/isolated copy.

## Supported build

- Google Chrome Portable by PortableApps.com `150.0.7871.187`, win64
  - Normal Google Chrome name and icon; no "Chrome for Testing" branding.
  - Original `chrome.dll` SHA-256:
    `577D16A963D3283960140C23521F5AEB5459D3127267D8076E71E1CF94403A79`
- Google Chrome for Testing `151.0.7922.138`, win64
  - Exact official archive: [chrome-win64.zip](https://storage.googleapis.com/chrome-for-testing-public/151.0.7922.138/win64/chrome-win64.zip)
  - Archive SHA-256:
    `864A03252382FCFAF0475A1D7CAD30B99CB54883060DCB5526249F4CA08AA03A`
  - Original `chrome.dll` SHA-256:
    `660E66FFC2F622E57506E373DBB33F7CDA4005D38D4CDAB2BFEB3F9A274FDAFC`
- Microsoft Edge isolated portable copy `151.0.4129.78`, win64
  - Built by copying your own Microsoft-signed Edge `Application` directory
    outside `Program Files`; this is not an official Microsoft portable edition.
  - Original Microsoft-signed `msedge.dll` SHA-256:
    `29B191751916DBFE5ED4206022A0D7AB45BD79966D9074ED872112D1865DCEC6`

Every recipe is tied to an exact original hash. Unknown or updated builds are
rejected before any write.

## What the patch changes

1. Adds ordinary SDR (`ContentColorUsage::kSRGB`) to Chromium's existing
   scRGB/F16 HDR output setup, alongside WCG and HDR. Chrome recipes use an
   audited output trampoline; the Edge recipe extends its audited SDR/WCG/HDR
   usage table.
2. Redirects only the version-specific, structurally verified constructions
   combining the canonical sRGB transfer function with the BT.709/sRGB gamut
   to Skia's adjacent pure gamma 2.2 transfer function. Depending on the build,
   the recipe verifies 47, 49 or 98 exact initializer sites.

The shared sRGB transfer constant is **not** overwritten. That distinction is
important because Display-P3 commonly uses the sRGB transfer curve with P3
primaries. PQ, HLG, P3 primaries and HDR video paths are not selected by the
patched BT.709+sRGB construction pattern. **HDR rendering is therefore neither
tone-mapped nor gamma-adjusted by this patch; it remains unchanged.**

### HDR photos, iPhone and Google Photos

The patch intentionally does not modify Display-P3 images or HDR gain-map
photos. An HDR photo can use a Display-P3 or sRGB SDR base plus a gain map;
Chromium reconstructs its HDR rendition separately from the ordinary
BT.709+sRGB SDR path corrected by this patch.

Google Photos may serve or export an iPhone photo as a converted Adobe Ultra
HDR JPEG. Such a rendition can contain a Display-P3 SDR base with the
piecewise-sRGB transfer curve and a separate HDR gain map. Its shadows and
midtones may consequently look lighter than the same photo in Apple Photos or
iCloud even while its HDR highlights and wide gamut remain active. This is a
difference in the supplied image rendition and gain-map tone mapping, not a
failure of the SDR gamma patch. Google documents its
[Ultra HDR support](https://support.google.com/photos/answer/14159275) but does
not promise pixel-identical tone mapping across the Apple and Google display
pipelines.

For the most faithful rendering of iPhone HDR photos, prefer iCloud or the
original Apple media. If Google Photos is used for backup, select
[Original quality](https://support.google.com/photos/answer/6220791), avoid
unnecessary web edits and retain the original HEIC/JPEG files separately; a
Google Photos web preview can still be a transformed rendition. Applying gamma
2.2 globally to Display-P3 or gain-map paths is not recommended, because that
would alter legitimate wide-gamut/HDR content and its creator-authored HDR
appearance.

## Usage

Requirements: Windows 11 x64 and Windows HDR enabled.

### Easy EXE method

1. Download and install
   [Google Chrome Portable 64-bit from PortableApps.com](https://portableapps.com/apps/internet/google-chrome-portable-64)
   into a new folder. Version `150.0.7871.187` is supported.
2. Download `Gamma22Patcher.exe` from the
   [latest GitHub Release](https://github.com/mrsaliericz/chromium-hdr-sdr-gamma22/releases/latest).
3. Put `Gamma22Patcher.exe` beside `GoogleChromePortable.exe` and double-click it.
4. Choose `A`, then type `APPLY` when asked.
5. Start the browser normally using `GoogleChromePortable.exe`.

This is the recommended beginner-friendly option: it has the normal Google
Chrome icon and name, keeps its profile inside the portable folder, and does
not display the "Chrome for Testing" label.

Alternatively, the exact official Chrome for Testing `151.0.7922.138` win64
ZIP remains supported. For that build, put the patcher beside `chrome.exe`; it
will create `Start Chrome Gamma22.cmd` after applying the patch.

### Microsoft Edge isolated-copy method

Microsoft currently distributes Edge as an installer/offline enterprise
package, not as an official portable browser. The patcher therefore supports a
user-created isolated copy of the exact Edge `151.0.4129.78` build:

1. Close every Microsoft Edge window and process.
2. Locate the installed version directory, normally under
   `C:\Program Files (x86)\Microsoft\Edge\Application\151.0.4129.78`.
3. Copy the **entire `Application` directory** to a new writable folder, for
   example `C:\Users\Public\EdgeGamma22Portable\Application`. Never patch the
   original directory under `Program Files`.
4. Put `Gamma22Patcher.exe` in `C:\Users\Public\EdgeGamma22Portable` and
   double-click it. Choose `A`, then type `APPLY`.
5. Start Edge only through the generated `Start Edge Gamma22.cmd`. It uses an
   isolated `EdgeGamma22Profile` inside the copied folder.

#### Desktop shortcut and taskbar pin

Windows does not reliably pin the generated `.cmd` launcher. You can instead
create a normal desktop shortcut that launches the copied `msedge.exe` with
the same isolated profile. This procedure has been verified to keep the
running portable window grouped under its pinned taskbar icon.

> **Create a completely new shortcut.** Do not copy or edit the shortcut from
> the normally installed Microsoft Edge. Existing Edge shortcuts can retain a
> hidden Windows `AppUserModelID` even after their visible target and arguments
> are changed. That stale identity can make the portable window open under a
> second taskbar icon.

1. Right-click the desktop and select **New → Shortcut**.
2. For a copy stored in `C:\Users\Public\EdgeGamma22Portable`, enter:

   ```text
   "C:\Users\Public\EdgeGamma22Portable\Application\msedge.exe" --user-data-dir="C:\Users\Public\EdgeGamma22Portable\EdgeGamma22Profile" --no-first-run --no-default-browser-check
   ```

   Replace both root paths if you placed the portable copy elsewhere.
3. Name the shortcut `Edge Gamma 2.2`.
4. In its **Properties**, set **Start in** to:

   ```text
   C:\Users\Public\EdgeGamma22Portable\Application
   ```

5. Right-click the finished shortcut (use **Show more options** on Windows 11)
   and select **Pin to taskbar**. If that option is unavailable, press
   `Win+R`, open `shell:programs`, copy the shortcut there, then find
   `Edge Gamma 2.2` in Start and pin it from the search result.

Alternatively, this PowerShell snippet creates a fresh shortcut without
inheriting metadata from an installed Edge shortcut. Change only
`$edgeGammaRoot` if your portable folder is elsewhere:

```powershell
$edgeGammaRoot = 'C:\Users\Public\EdgeGamma22Portable'
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Edge Gamma 2.2.lnk'
$edgeExe = Join-Path $edgeGammaRoot 'Application\msedge.exe'
$edgeProfile = Join-Path $edgeGammaRoot 'EdgeGamma22Profile'

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $edgeExe
$shortcut.Arguments = "--user-data-dir=`"$edgeProfile`" --no-first-run --no-default-browser-check"
$shortcut.WorkingDirectory = Join-Path $edgeGammaRoot 'Application'
$shortcut.IconLocation = "$edgeExe,0"
$shortcut.Description = 'Microsoft Edge Gamma 2.2'
$shortcut.Save()
```

Do not pin an already-running Edge window: Windows may create a new shortcut
without `--user-data-dir`, allowing the installed Edge session to capture the
launch. After starting the pinned shortcut, open `edge://version` and verify
both values:

```text
Executable Path: C:\Users\Public\EdgeGamma22Portable\Application\msedge.exe
Profile Path:    C:\Users\Public\EdgeGamma22Portable\EdgeGamma22Profile\Default
```

Both paths matter. The executable must come from the patched copy and the
profile must remain inside its isolated portable folder.

If the window still appears under a second icon, unpin the old custom icon,
close the isolated Edge copy, delete only the custom shortcut that was copied
or edited from normal Edge, and create a fresh shortcut using the steps or
PowerShell snippet above. Do not change or remove the normal installed Edge
shortcut. Windows may need a restart of Explorer or a sign-out/sign-in to
discard an already cached taskbar identity.

If your installed Edge has already updated to a different version, the patcher
will safely refuse it. Do not download an old `msedge.dll` from third-party DLL
sites. Microsoft publishes official installers on the
[Edge for Business download page](https://www.microsoft.com/en-us/edge/business/download),
but every new Edge build still requires a separately audited recipe.

The EXE refuses unknown browser versions and installed browsers. It creates a
verified original-DLL backup before changing anything. Windows may show a
SmartScreen warning because this community-built EXE is not code-signed; do
not disable Windows security, and compare the release SHA-256 if in doubt.

### Make the patched Chrome or Edge your default browser

Windows 11 will not offer an arbitrary portable EXE as a default browser until
it has been registered. The included
[`tools/register_default_browser.ps1`](tools/register_default_browser.ps1)
creates a separate, per-user registration named **Chrome Gamma 2.2** or
**Edge Gamma 2.2**. It does not modify Chrome's `ChromeHTML`, Edge's
`MSEdgeHTM`, the installed browser, or machine-wide registry keys. Administrator
rights are not required. It follows Microsoft's documented
[Default Programs registration](https://learn.microsoft.com/en-us/windows/win32/shell/default-programs)
and [per-user Default Apps deep link](https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-default-apps-settings).

Download the script (or run it from a cloned repository), then use the example
that matches your browser. Change the paths to your actual portable folder.

For an isolated Edge copy:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\register_default_browser.ps1 `
  -Browser Edge `
  -ExecutablePath 'C:\Users\Public\EdgeGamma22Portable\Application\msedge.exe' `
  -ProfileDirectory 'C:\Users\Public\EdgeGamma22Portable\EdgeGamma22Profile'
```

For Google Chrome Portable by PortableApps.com, register its launcher. Do not
add `-ProfileDirectory`; the PortableApps launcher already selects its portable
profile:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\register_default_browser.ps1 `
  -Browser Chrome `
  -ExecutablePath 'C:\PortableApps\GoogleChromePortable\GoogleChromePortable.exe'
```

For a raw extracted Chrome or Chrome for Testing copy, register `chrome.exe`
and provide its isolated profile explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\register_default_browser.ps1 `
  -Browser Chrome `
  -ExecutablePath 'C:\Browsers\chrome-win64\chrome.exe' `
  -ProfileDirectory 'C:\Browsers\ChromeGamma22Profile'
```

The script opens **Settings → Apps → Default apps** on the new browser's page.
Clear the optional **Pin to Start** and **Pin to taskbar** checkboxes if you
already have a working portable shortcut, then click **Set default**. Windows
protects the final user choice, so the script deliberately does not try to
write or bypass the protected `UserChoice` hash.

This sets `HTTP`, `HTTPS`, `.htm`, `.html` and `.shtml`. PDF is intentionally
left unchanged. Verify `edge://version` or `chrome://version` after opening an
external link: both **Executable Path** and **Profile Path** must point to the
patched portable copy. Links using the Windows-specific `microsoft-edge:`
protocol may still open the normally installed Edge; ordinary web links use
the selected default browser.

The registration keeps working while the executable and profile stay at the
same paths. Keep the portable browser patched to a currently supported,
security-updated build before using it for all external links.

To undo the change, first select another default browser in Windows Settings.
Then remove only the custom per-user registration:

```powershell
# Choose Chrome here if that is the copy you registered.
powershell -ExecutionPolicy Bypass -File .\tools\register_default_browser.ps1 `
  -Browser Edge -Unregister
```

The script refuses to unregister while its custom ProgID is still selected,
preventing a broken default association.

### Python / command-line method

Python 3.9 or newer is required for this method. The prebuilt release can use
`Gamma22Patcher.exe` in place of `python .\gamma22_patcher.py`.

1. Download and extract the official
   [Chrome for Testing win64 ZIP](https://googlechromelabs.github.io/chrome-for-testing/).
2. Close every process belonging to that extracted Chrome copy.
3. Verify and apply:

```powershell
python .\gamma22_patcher.py verify C:\path\to\chrome-win64\chrome.dll
python .\gamma22_patcher.py apply  C:\path\to\chrome-win64\chrome.dll
```

4. Launch with a separate test profile:

```powershell
C:\path\to\chrome-win64\chrome.exe `
  --user-data-dir=C:\Users\Public\ChromeGamma22Profile
```

The separate profile is mandatory when regular Chrome is already running.
Without it, Chrome's process singleton can forward the launch to the installed,
unpatched browser even though a different `chrome.exe` path was requested.
For convenience, copy
[`launcher/Start Chrome Gamma22.cmd`](launcher/Start%20Chrome%20Gamma22.cmd)
beside the extracted `chrome.exe` and run that launcher.

### Using it with dwm_eotf

This patch works well alongside
[`dwm_eotf`](https://github.com/ledoge/dwm_eotf), and running both at the same
time is recommended when `dwm_eotf` is needed to correct SDR output from other
Windows applications. The patched browser deliberately stays on Chromium's
scRGB/F16 HDR presentation path, so its presented output is always HDR/scRGB.
Its SDR content therefore remains gamma 2.2 and is not altered by `dwm_eotf`'s
SDR-through-DWM correction.

In short: leave `dwm_eotf` enabled for other applications; it can coexist with
this browser patch without double-correcting the browser image.

### SDR browser video and NVIDIA RTX Video HDR

Ordinary web-page SDR and SDR video are not always rendered through exactly
the same Chromium path. SDR video is commonly decoded as limited-range YUV
with BT.709 primaries, transfer and matrix, and it may use a dedicated hardware
video surface. The patch guarantees its audited ordinary BT.709+sRGB RGB path;
it should not be described as a universal gamma override for every SDR video
decoder, codec or presentation path.

If **NVIDIA RTX Video HDR** is enabled, the distinction is especially
important. NVIDIA documents that RTX Video HDR converts supported SDR browser
video into HDR10 in real time in current Chrome and Edge. In that configuration:

- this patch keeps the surrounding SDR web page at gamma 2.2;
- RTX Video HDR handles the SDR video's separate SDR-to-HDR tone mapping;
- native HDR video is not processed by RTX Video HDR and remains on Chromium's
  unchanged native HDR path.

This combination has been visually verified with SDR and native-HDR YouTube
playback. It is a useful optional setup, but RTX-processed SDR video is
**synthetic HDR**, not creator-authored native HDR and not a pure gamma 2.2 SDR
reference.

When showing or hiding player controls, a brief gamma/brightness transition of
only a few frames may occasionally be visible. Testing showed this transition
only with RTX Video HDR active, consistent with a short video-surface or filter
reconfiguration; it is not a persistent page-gamma switch. NVIDIA also states
that enabling RTX Video automatically disables Multiplane Overlay (MPO), so the
exact internal transition should not be assumed to be a normal MPO promotion.

To determine whether the browser patch itself affects a particular SDR video
path, disable **RTX Video HDR**, restart the browser, confirm `Color: bt709` in
YouTube's **Stats for nerds**, and compare again. NVIDIA App can display a
real-time RTX Video status indicator. On Edge, NVIDIA recommends disabling
Edge's own **Enhance videos** option when using NVIDIA RTX Video.

See NVIDIA's official
[RTX Video FAQ](https://nvidia.custhelp.com/app/answers/detail/a_id/5448/~/rtx-video-faq)
for current compatibility, exclusions and status-indicator instructions.

The patcher creates `chrome.dll.gamma22-original` or
`msedge.dll.gamma22-original` beside the DLL before the first write. Restore it
with:

```powershell
python .\gamma22_patcher.py restore C:\path\to\chrome-win64\chrome.dll
# Edge: python .\gamma22_patcher.py restore C:\path\to\msedge.dll
```

## Safety model

- Refuses Chrome/Edge DLLs under `Program Files`.
- Requires an exact original SHA-256 for `apply`.
- Verifies PE architecture, Skia constants, initializer count, hook bytes,
  trampoline padding, and the complete target helper body.
- Writes a recovery copy and performs structural post-write verification.
- Refuses mixed, ambiguous, already-modified, and unknown versions.

Modifying `chrome.dll` or `msedge.dll` invalidates that DLL's Authenticode
signature. Browser updates replace the DLL and require a new audited recipe.
Security software may also object to modified browser code. Use only an
isolated portable/test copy and never for high-risk browsing.

## Verification status

The PortableApps Chrome `150.0.7871.187`, Chrome for Testing `151.0.7922.138`,
and the equivalent Edge patch were visually verified on Windows 11 with
Windows HDR enabled for:

- SDR black-level and grayscale tests matching a pure gamma 2.2 reference;
- Display-P3 remaining wide gamut;
- **native HDR video, PQ/HLG, HDR black levels and highlights remaining fully
  correct and unchanged, matching an unmodified Chromium browser;**
- stable SDR appearance on mixed SDR + P3/HDR pages.

The Chrome mixed-content test remained stable when P3/HDR content appeared or
disappeared, while native HDR video and wide-gamut content retained the same
appearance as an unmodified Chromium browser. The patch remains experimental
because it modifies a signed browser DLL and is tied to one exact build hash.

Open [`tests/gamma22_test.html`](tests/gamma22_test.html) in both patched and
unmodified Chrome for a quick SDR, P3 and mixed-content comparison. The rows
inside one patched window are not fully independent references because all of
them ultimately traverse the patched canonical sRGB space; screenshots from
patched and unmodified runs provide the stronger comparison.

## Adding another recipe

Do not copy RVAs from a different release. A new recipe needs an exact DLL
hash and a fresh structural audit. At minimum, verify:

- the unique adjacent BT.709 gamut, kSRGB and k2Dot2 Skia constants;
- every inline sRGB+BT.709 construction and its exact count;
- the Windows HDR `DisplayColorSpaces` setup for SDR, WCG and HDR;
- the output helper ABI and any trampoline/code-cave assumptions;
- unmodified P3, PQ and HLG paths.

Pull requests for reviewed recipes and for replacing binary hooks with a clean
upstream Chromium feature are welcome.

## Building the standalone EXE

Install PyInstaller and run:

```powershell
python -m pip install pyinstaller
.\build_exe.ps1
```

The result is `dist\Gamma22Patcher.exe`. The EXE embeds only this patcher and
its JSON recipes; it does not contain Chrome.

## License

The patcher source and recipes are MIT-licensed: they are free to use, copy,
modify, publish and redistribute, including in derivative projects, subject
only to the short terms in [`LICENSE`](LICENSE). The patcher is and will remain
free; donations never unlock features or recipes.

If the project helped you and you voluntarily want to support continued recipe
research, you can [buy me a coffee](https://buymeacoffee.com/mrsaliericze).
Google Chrome, Chromium, Skia, Windows and Microsoft Edge retain their
respective licenses and marks.
