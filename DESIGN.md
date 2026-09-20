# DESIGN.md - PLN Assist

## Product Direction

PLN Assist memakai UI Flutter PLN Assist 1.4.9 sebagai fondasi. Fase awal tidak mengganti navigasi utama: Home untuk ID/password, daftar perangkat untuk Recent/Favorites/Groups, dan remote workspace untuk sesi bertab.

## Identity

- Display name: `PLN Assist`
- Internal process/service slug: `pln-assist`
- Primary language: Indonesia
- Existing PLN Assist icon remains temporary until an approved PLN Assist asset is supplied.
- Do not publish with PLN marks before written authorization.

## Navigation

Desktop:

- Home: ID perangkat, password, status service.
- Devices: Recent, Favorites, Discovered, Address Book, Device Groups.
- Sessions: tab remote, chat, file transfer, invite technician, reconnect.
- Operations: health, updates, SLA, audit.
- Admin: users, roles, policy, allowlist/blocklist, emergency revoke.

Mobile:

- Home, Devices, Sessions, Settings.
- Admin/Operations use responsive drill-down pages, not dense desktop tables.

## Role Defaults

- Admin: semua perangkat, role, policy, update, audit, emergency revoke.
- SPV: perangkat dan sesi dalam area tanggung jawab; invite, audit area, emergency disconnect area.
- PBM: remote perangkat dalam group yang ditugaskan; chat, transfer, WOL, reboot/reconnect, health read.
- Biller: remote perangkat billing yang ditugaskan; chat, transfer, reconnect, health read.
- Umum: perangkat sendiri/yang ditugaskan; meminta bantuan, menyetujui sesi, chat, emergency disconnect.

Server tetap menjadi sumber kebenaran. Client hanya menyembunyikan aksi untuk UX; API wajib memvalidasi izin setiap operasi.

## Interaction Rules

- Local mouse/keyboard activity blocks remote input for 5 seconds.
- Every new local event restarts the 5-second window.
- Remote video and chat remain active while input is blocked.
- Remote toolbar shows `Pengguna lokal sedang aktif` and remaining time.
- Local emergency disconnect is always available.
- Timeout dialog provides `Reconnect` and `Akhiri sesi`.
- Destructive admin actions require confirmation and audit entry.

## Technical Boundaries

- Keep PLN Assist protocol/capture/input components unless behavior requires a focused patch.
- Reuse upstream chat, favorites, WOL, multi-window, file transfer, and reconnect paths.
- Device groups currently call Server Pro-compatible APIs; replace through a PLN management API adapter, not UI duplication.
- Cloudflare handles HTTP control-plane only.
- A Linux VPS runs `hbbs` and `hbbr`; ordinary Cloudflare proxy cannot host them.
- R2 object keys must never expose passwords or raw access tokens.
- Recording and file-download URLs use short-lived signed access.

## Build Targets

1. Windows x64 client.
2. Android universal/arm64 client.
3. macOS, Linux, iOS after signing and target-specific verification.

Pinned upstream toolchain:

- Rust `1.75`
- Flutter `3.24.5`
- LLVM `15.0.6`
- vcpkg commit `120deac3062162151622ca4860575a33844ba10b`

Source: `.github/workflows/flutter-build.yml`.
