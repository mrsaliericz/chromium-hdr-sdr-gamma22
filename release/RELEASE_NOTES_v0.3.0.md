## Gamma22Patcher v0.3.0 — Microsoft Edge support

This release adds the visually verified **Microsoft Edge 151.0.4129.78 win64**
recipe. Microsoft does not publish a genuine portable edition, so the patcher
supports a user-created isolated copy of Edge's complete `Application` folder.
It always refuses the installed browser under `Program Files` and creates an
isolated-profile `Start Edge Gamma22.cmd` launcher.

### Verified Edge patch

- verifies all 98 exact sRGB singleton initializer sites;
- extends Edge's audited output-usage setup to SDR + WCG + HDR;
- ordinary BT.709/sRGB SDR uses pure gamma 2.2;
- Display-P3 remains wide gamut;
- native HDR video, PQ/HLG, black levels and highlights remain unchanged;
- exact original and patched DLL hashes are required.

The release still supports normally branded Google Chrome Portable
`150.0.7871.187` and Chrome for Testing `151.0.7922.138`.

The project is MIT-licensed, free to use and modify, and will remain free. If
it helps you, optional support is welcome at
[Buy Me a Coffee](https://buymeacoffee.com/mrsaliericze).

This experimental EXE is not code-signed. Do not disable Windows security;
verify `SHA256SUMS.txt` if in doubt.

SHA-256: `934F4A4535513460F041576449F1AD1EB6FF4BFEAC0E053444E1F1B4540A3DE1`
