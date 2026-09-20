#!/usr/bin/env bash
# Quick build script for PLN Assist Desktop (Windows)
# Run this after LLVM build completes

set -e

echo "=== PLN Assist Desktop Build ==="
echo ""

cd "/d/Tugas Indra/project pkl/pln-assist"

# Check LLVM status
if [ -f "D:/vcpkg/installed/x64-windows/bin/libclang.dll" ]; then
    echo "LLVM: Ready"
else
    echo "WARNING: LLVM not ready yet, using no-audio build"
fi

# Set environment
export VCPKG_ROOT="D:/vcpkg"
export LIBCLANG_PATH="D:/vcpkg/installed/x64-windows/bin"

# Build options
if [ -f "D:/vcpkg/installed/x64-windows/bin/libclang.dll" ]; then
    echo "Building with audio support..."
    cargo build --release
else
    echo "Building without audio (skip magnum-opus)..."
    cargo build --release --no-default-features --features flutter
fi

echo ""
echo "Build complete!"
echo "Debug: target/debug/rustdesk.exe"
echo "Release: target/release/rustdesk.exe"
