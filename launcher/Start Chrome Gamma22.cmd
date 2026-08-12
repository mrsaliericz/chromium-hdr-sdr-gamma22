@echo off
set "GAMMA22_PROFILE=C:\Users\Public\ChromeGamma22PortableProfile"
start "Chrome Gamma22" "%~dp0chrome.exe" --user-data-dir="%GAMMA22_PROFILE%" --no-first-run --disable-default-apps
