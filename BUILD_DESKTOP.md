# PLN Assist Desktop Build Guide

## Target Platform
Windows Desktop (x64)

## Build Status
- Rust toolchain: ✅ Installed (1.75.0)
- vcpkg: ✅ Installed & Bootstrapped
- LLVM build: ⏳ In progress (via vcpkg)
- Build blockers: Bindgen needs libclang

## Quick Start (After LLVM Build Completes)

### 1. Verify LLVM is Ready
```powershell
Test-Path 'D:/vcpkg/installed/x64-windows/bin/libclang.dll'
# Should return True
```

### 2. Set Environment Variables
```powershell
$env:PATH += ";D:\vcpkg\installed\x64-windows\bin"
$env:VCPKG_ROOT = "D:\vcpkg"
$env:LIBCLANG_PATH = "D:\vcpkg\installed\x64-windows\bin"
```

### 3. Build Debug (Faster, for development)
```powershell
cd "D:\Tugas Indra\project pkl\pln-assist"
cargo build
# Output: target\debug\plnassist.exe
```

### 4. Build Release (Smaller, optimized)
```powershell
cargo build --release
# Output: target\release\plnassist.exe
```

### 5. Test the Build
```powershell
.\target\debug\plnassist.exe --version
# Should show: PLN Assist 1.4.9
```

## Build Options

### Skip Audio (Faster Build, No VCPKG Needed)
```powershell
cargo build --no-default-features --features flutter
```

### Full Build with All Features
```powershell
cargo build
# Requires: LLVM (libclang), vcpkg packages (opus, ffmpeg)
```

## Output Locations

| Config | Location |
|--------|----------|
| Debug exe | `target\debug\plnassist.exe` |
| Release exe | `target\release\plnassist.exe` |
| DLL library | `target\debug\libplnassist.dll` |
| DLL library (release) | `target\release\libplnassist.dll` |

## Windows Package Options

### Option A: Portable EXE (Recommended for testing)
Just copy the executable to any folder and run.

```powershell
copy target\release\plnassist.exe D:\pln-assist-portable\
D:\pln-assist-portable\plnassist.exe
```

### Option B: Installer (Requires NSIS)
```powershell
# Install NSIS first
choco install nsis -y

# Then build installer
cargo build --release
make_installer.bat
```

### Option C: MSIX Package (Modern Windows)
```powershell
# Requires Windows SDK
# See https://docs.microsoft.com/en-us/windows/uwp/packaging/create-app-package
```

## Dependencies Summary

### Required (Already Installed)
- Rust 1.75.0+ (via rustup)
- cargo + fmt
- VS 2022 Build Tools (already at C:\Program Files\Microsoft Visual Studio\18\Community)

### Building Now
- LLVM (via vcpkg) - ~2-3 hours from start

### Optional (For Full Features)
- vcpkg opus package (audio)
- vcpkg ffmpeg package (video codecs)
- winpty (Unix compatibility)

## Troubleshooting

### Error: "Unable to find libclang"
**Cause**: LLVM build not complete yet  
**Solution**: Wait for vcpkg to finish building LLVM

### Error: "Couldn't find VCPKG_ROOT"
**Cause**: vcpkg not in PATH or wrong location  
**Solution**:
```powershell
$env:VCPKG_ROOT = "D:\vcpkg"
```

### Error: "magnum-opus build failed"
**Cause**: Missing audio dependencies  
**Solution**: Skip audio feature:
```powershell
cargo build --no-default-features --features flutter
```

## Next Steps After Build

1. **Test locally**: Run `plnassist.exe` and connect to a peer
2. **Configure server**: Point to your hbbs/hbbr server
3. **Package for distribution**: Create installer or portable package
4. **Deploy to clients**: Copy to all user machines

## Documentation Files

- `PROJECT_SUMMARY.md` - Executive overview
- `FINAL_REPORT.md` - Complete implementation details
- `BUILD_APK_MOBILE.md` - Android mobile build guide
- `AUDIT.md` - Feature audit results
- `DESIGN.md` - Design system documentation
- `PRODUCT.md` - Product requirements
