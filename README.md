# Chromium HDR SDR Gamma 2.2 patcher

Experimental, fail-closed patcher for **64-bit Chrome for Testing on Windows**.
It keeps Chromium's native HDR / wide-gamut pipeline, but changes ordinary
BT.709+sRGB SDR content to a pure gamma 2.2 interpretation while Windows HDR
is enabled.

The repository contains **no Chrome or Edge binaries**. Download Chrome for
Testing from Google and patch only your own extracted copy.

## Supported build

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
patched BT.709+sRGB construction pattern.

## Usage

Requirements: Windows 11 x64, Windows HDR enabled, and Python 3.9 or newer.
Prebuilt releases can use `Gamma22Patcher.exe` in place of
`python .\gamma22_patcher.py`.

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

The Chrome for Testing `151.0.7922.138` recipe and the equivalent Edge patch
were visually verified on Windows 11 with Windows HDR enabled for:

- SDR black-level and grayscale tests matching a pure gamma 2.2 reference;
- Display-P3 remaining wide gamut;
- native HDR video and HDR black matching an unmodified Chromium browser;
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
