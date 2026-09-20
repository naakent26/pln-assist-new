# LLVM Requirement Analysis for PLN Assist

## The Problem
LLVM is failing because `bindgen` needs `libclang.dll` to generate Rust bindings from C headers.

## Crates That Need LLVM:
1. `magnum-opus` - Opus audio codec
2. `kcp-sys` - KCP reliable UDP protocol
3. `scrap` - Screen capture (VPX bindings)

All three use `bindgen` in their `build.rs`!

## Solution Options:

### Option A: Pre-built LLVM (Fastest ~10 min)
Download installer from GitHub releases instead of compiling:
- URL: https://github.com/llvm/llvm-project/releases/download/llvmorg-18.1.8/LLVM-18.1.8-win64.exe
- Size: ~300MB (vs compiling 2-3 hours)
- Install to `C:\Program Files\LLVM`
- Sets `LIBCLANG_PATH` automatically

### Option B: Wait for vcpkg Build (2-3 hours)
Currently compiling LLVM from source in background.

### Option C: Chocolatey (If available)
```powershell
choco install llvm -y
```

### Option D: Winget
```powershell
winget install LLVM.LLVM
```
