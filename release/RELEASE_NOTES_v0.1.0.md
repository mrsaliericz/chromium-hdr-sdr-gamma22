## Chromium HDR SDR Gamma 2.2 patcher v0.1.0

First public experimental release for **Google Chrome for Testing
151.0.7922.138 win64**.

> **HDR content remains fully correct and completely unchanged.** This patch
> affects only ordinary SDR BT.709/sRGB. Native HDR video, PQ, HLG, HDR black
> levels and highlights continue through Chromium's original HDR path and
> visually match the unpatched browser.

### Easy installation

1. Download and extract the exact official
   [Chrome for Testing win64 ZIP](https://storage.googleapis.com/chrome-for-testing-public/151.0.7922.138/win64/chrome-win64.zip).
2. Download `Gamma22Patcher.exe` below and place it beside the extracted
   `chrome.exe`.
3. Double-click the patcher, choose `A`, and type `APPLY`.
4. Start Chrome using the generated `Start Chrome Gamma22.cmd`.

The launcher uses an isolated profile so an already-running installed Chrome
cannot capture the launch.

### Verified result

- ordinary BT.709/sRGB SDR uses pure gamma 2.2;
- Display-P3 remains wide gamut;
- **native HDR video, PQ/HLG, HDR black levels and highlights remain correct
  and unchanged, matching unpatched Chrome;**
- SDR appearance stays stable on mixed SDR + P3/HDR pages.

### dwm_eotf compatibility

The patch works well alongside
[`dwm_eotf`](https://github.com/ledoge/dwm_eotf), and using both concurrently
is recommended when other Windows applications need its SDR correction. The
patched browser stays on the scRGB/F16 HDR presentation path, so its presented
output is always HDR/scRGB. Its gamma 2.2 browser image is therefore not
altered or double-corrected by `dwm_eotf`.

### Important

This release is tied to one exact Chrome DLL SHA-256 and refuses unknown
versions. It never modifies installed Chrome/Edge under Program Files and
creates a verified original-DLL backup before patching. The executable is not
code-signed, so Windows may display a SmartScreen warning. Do not disable
Windows security; verify the SHA-256 asset instead.

`Gamma22Patcher.exe` SHA-256:
`7F6500FAFB5D72BCCBFD54564488BC8D93F7E1A0CC5EBFCF7D8829D4A117A38C`
