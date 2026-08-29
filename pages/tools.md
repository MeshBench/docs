# External tools

MeshBench runs real MeshCore firmware. Native builds run as ordinary processes;
emulated boards need an emulator and a radio server beside them. This is what it
looks for, where, and why each version is pinned.

## Where tools are looked for

In this order:

1. The environment variable, if set
2. **Beside the MeshBench binary**
3. `~/.cache/meshbench/tools/`
4. `PATH`

`PATH` is last, and on a desktop it is nearly useless. **A desktop application
is not launched from a shell**, so it inherits neither a useful `PATH` nor any
environment variables set in a shell profile. Emulation that works from a
terminal and fails when launched from the desktop is this ordering being wrong.

Beside-the-binary is what an installed bundle uses. The cache directory is what
a development checkout uses, and is where the installer puts anything it
downloads after the fact.

## The tools

| Tool | Environment variable | Needed for |
|---|---|---|
| `qemu-system-xtensa` | `MESHBENCH_QEMU` | emulated ESP32 nodes |
| `renode` | `MESHBENCH_RENODE` | emulated nRF52 nodes |
| `radioserver` | `MESHBENCH_RADIO_SERVER` | both, and nothing else |
| native firmware | `MESHBENCH_NATIVE` | every native node |

`radioserver` is the one **every** emulated node needs, ESP32 or nRF52, and it
is looked up before either emulator.

`MESHBENCH_NATIVE` may name a **directory** holding one build per role, which
is what a scenario mixing roles needs. Naming a single binary overrides every
node regardless of role, so a mesh of repeaters and room servers quietly
becomes a mesh of one application.

## Why the versions are pinned

**QEMU** must carry MeshBench's SX1262 device and a working GPIO
implementation. Upstream's GPIO write handler is empty, and RadioLib drives chip
select as an ordinary GPIO rather than through the SPI controller, so a
distribution build produces a driver that reports no chip present. It must also
be configured with `--enable-gcrypt`, or the `esp32` machine will not
instantiate at all.

**Renode** must carry the SEVONPEND fix. Stock Renode asks whether a pending
interrupt could be *taken*, which a disabled interrupt never can, so published
nRF52 firmware sleeps for ever with its wake condition already true. A stock
Renode will start, load, run, and then hang in exactly the place the fix
addresses.

**Native firmware versions are per-role release tags**, not bare versions:
`repeater-v1.17.0`, `companion-v1.17.0`, `room-server-v1.17.0`. Asking for
`v1.17.0` resolves nothing and reports that no native builds were published,
which points at the release rather than at the string.

**Board images are not pinned here.** They are fetched from MeshCore's own
releases at run time and cached, because they change every release and bundling
them dates the installer.

## What a release bundle ships

```
meshbench                     the application
qemu-system-xtensa            beside it, or symlinked
renode                        beside it, or symlinked
radioserver                   beside it
```

A **symlink** is correct for QEMU and a copy is not: it resolves its own path to
find its data files, so a bare copy of the binary will not run. The Windows zip
cannot carry a symlink at all, so nothing is linked there and the lookup
searches the emulators' own unpacked layouts - `qemu/bin/` and the versioned
`renode_*-portable/` - instead.

The AppImage and the `.deb` carry the application and `radioserver` but not the
emulators: those are 110 MB against a 26 MB AppImage. The tarball is the
batteries-included download for anyone who wants them.

## What is checked, and when

A missing tool is reported **before** a run rather than during one, and the
error names all four search locations. "`qemu-system-xtensa` not found" on its
own sends people to their package manager for a build that will not work.

The firmware library only offers boards with verified emulation wiring, so a
board that appears in the picker is one whose image has been watched booting.
That list is deliberately short.
