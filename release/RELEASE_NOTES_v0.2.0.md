## Gamma22Patcher v0.2.0 — normally branded Portable Chrome

This release adds the beginner-friendly **Google Chrome Portable by
PortableApps.com 150.0.7871.187 win64**. It has the normal Google Chrome name
and icon, with no "Chrome for Testing" branding.

### Easy installation

1. Install
   [Google Chrome Portable 64-bit](https://portableapps.com/apps/internet/google-chrome-portable-64)
   version `150.0.7871.187` into a new folder.
2. Download `Gamma22Patcher.exe` below and put it beside
   `GoogleChromePortable.exe`.
3. Double-click the patcher, choose `A`, and type `APPLY`.
4. Launch normally with `GoogleChromePortable.exe`.

The patcher automatically finds the nested `chrome.dll`, creates a verified
backup, and reuses the PortableApps launcher and portable profile.

### Verified result

- ordinary BT.709/sRGB SDR uses pure gamma 2.2;
- Display-P3 remains wide gamut;
- mixed SDR + P3/HDR content does not change SDR appearance;
- **native HDR video, PQ/HLG, HDR black levels and highlights remain fully
  correct and completely unchanged, matching unpatched Chrome.**

It works well in parallel with
[`dwm_eotf`](https://github.com/ledoge/dwm_eotf). The browser remains on its
scRGB/F16 HDR presentation path, so `dwm_eotf` does not double-correct it.

Chrome for Testing `151.0.7922.138` remains supported as a second recipe.

This experimental EXE is not code-signed. Do not disable Windows security;
verify `SHA256SUMS.txt` if in doubt.

SHA-256: `4AAE83765376B12D82196C4FC47715A300566C387B655D81854BEE2207EFD953`
