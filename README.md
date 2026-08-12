# Chromium HDR SDR Gamma 2.2 patcher

Experimental, fail-closed patcher for supported **64-bit Google Chrome builds
on Windows**, including normally branded Google Chrome Portable.
It keeps Chromium's native HDR / wide-gamut pipeline, but changes ordinary
BT.709+sRGB SDR content to a pure gamma 2.2 interpretation while Windows HDR
is enabled.

> **HDR content is displayed correctly and without any modification.** The
> patch changes only ordinary SDR BT.709/sRGB interpretation. Native HDR video,
> PQ, HLG, HDR black levels and highlights remain on Chromium's original HDR
> path and visually match the unpatched browser.

The repository contains **no Chrome or Edge binaries**. Download Chrome for
Testing from Google and patch only your own extracted copy.

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

Every recipe is tied to an exact original hash. Unknown or updated builds are
rejected before any write.

## What the patch changes

1. Adds ordinary SDR (`ContentColorUsage::kSRGB`) to Chromium's existing
   scRGB/F16 HDR output setup, alongside WCG and HDR.
2. Redirects only the 49 verified inline constructions combining the canonical
   sRGB transfer function with the BT.709/sRGB gamut to Skia's adjacent pure
   gamma 2.2 transfer function.

The shared sRGB transfer constant is **not** overwritten. That distinction is
important because Display-P3 commonly uses the sRGB transfer curve with P3
primaries. PQ, HLG, P3 primaries and HDR video paths are not selected by the
patched BT.709+sRGB construction pattern. **HDR rendering is therefore neither
tone-mapped nor gamma-adjusted by this patch; it remains unchanged.**

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

The EXE refuses unknown Chrome versions and installed browsers. It creates a
verified original-DLL backup before changing anything. Windows may show a
SmartScreen warning because this community-built EXE is not code-signed; do
not disable Windows security, and compare the release SHA-256 if in doubt.

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

The patcher creates `chrome.dll.gamma22-original` beside the DLL before the
first write. Restore it with:

```powershell
python .\gamma22_patcher.py restore C:\path\to\chrome-win64\chrome.dll
```

## Safety model

- Refuses Chrome/Edge DLLs under `Program Files`.
- Requires an exact original SHA-256 for `apply`.
- Verifies PE architecture, Skia constants, initializer count, hook bytes,
  trampoline padding, and the complete target helper body.
- Writes a recovery copy and performs structural post-write verification.
- Refuses mixed, ambiguous, already-modified, and unknown versions.

Modifying `chrome.dll` invalidates its Authenticode signature. Browser updates
replace the DLL and require a new audited recipe. Security software may also
object to modified browser code. Use only an isolated portable/test copy and
never for high-risk browsing.

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

The patcher source and recipes are MIT-licensed. Google Chrome, Chromium,
Skia, Windows and Microsoft Edge retain their respective licenses and marks.
