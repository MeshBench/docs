# Getting started

This page gets MeshBench installed and open. From there,
[your first simulation](first-simulation.html) is fifteen minutes to a real
network relaying real packets, and
[the concepts page](concepts.html) explains what is real and what is
modelled.

## What you need

Linux is the only platform with a build today (the others are tracked
[below](#other-platforms)).

- **glibc 2.35 or newer**: Ubuntu 22.04, Debian 12, RHEL 9, or anything more
  recent.
- **A display and a GPU.** The CPU path gives the same answers more slowly,
  so a machine without a usable GPU loses time rather than features.
- **RAM**: about 500 MB for the application, plus roughly 10 MB per simulated
  node. The 378-node network wants about 4 GB free.
- **Disk**: 200 MB for the bundle, and a cache under `~/.cache/meshbench`
  that grows with the firmware builds and map tiles you use.

## Install and launch

1. Download `meshbench-linux-x86_64.tar.gz` from the
   [releases page](https://github.com/MeshBench/meshbench/releases).
2. Unpack it anywhere you can write to.
   ```console
   tar xzf meshbench-linux-x86_64.tar.gz
   cd meshbench
   ```
3. Run it.
   ```console
   ./meshbench workbench
   ```

There is no installer, no root, and nothing to configure. Firmware builds and
map tiles download on first use; the emulators, if the bundle carries them,
sit beside the binary and are found automatically.

The workbench opens on the Plan view with a map. You are ready for
[your first simulation](first-simulation.html).

## Next

- [Your first simulation](first-simulation.html): load a real network, boot
  the firmware, watch a flood.
- [What is real, and what is modelled](concepts.html): the mental model, and
  the project's terminology.
- [Shipped networks](fixtures.html) if you want a bigger or more realistic
  mesh.
- The [CLI reference](reference-cli.html) for everything the binary does
  without a window, and [Settings](settings.html) for what the application
  remembers.
- [External tools](tools.html) for what MeshBench looks for on the machine:
  Wireshark, SDR++, the emulators, and what happens when one is missing.

## If it will not start

| symptom | cause |
|---|---|
| `version GLIBC_2.35 not found` | the distribution is older than the floor above |
| `Cannot set swap interval` | harmless, printed when the compositor declines vsync |
| a window opens and stays black | no usable GL driver; install your vendor's Mesa or driver package |

One bundle oddity worth knowing before rearranging files:
`qemu-system-xtensa` (the board emulator, used later by
[emulation](emulation.html)) is a symlink on purpose. QEMU resolves its own
path to find its data files, so a bare copy of the binary will not run.

## Building from source, any platform

```console
git clone https://github.com/MeshBench/meshbench
cd meshbench
go build ./cmd/meshbench
```

That produces a binary called `meshbench`, the same program the release
ships.

Needs Go 1.25 and a C toolchain with GL and X11 development headers, because
the UI is cgo. On Debian and Ubuntu:

```console
sudo apt install gcc pkg-config libgl1-mesa-dev xorg-dev
```

## Other platforms

### macOS

**Not built yet.** What it needs, in order:

1. **A Darwin runner in the packaging workflow.** The application itself is
   Go and cgo against a cross-platform UI library, so this part is expected
   to be straightforward.
2. **The QEMU fork built on Darwin.** MeshBench's QEMU carries an SX1262
   device upstream does not have. It has never been compiled on macOS, and
   that is the real unknown.
3. **A separate Apple Silicon build.** An x86_64 build under Rosetta would
   run the simulator acceptably and the emulated firmware badly, so arm64
   needs its own row rather than a translation layer.

The intended shape is a signed `.app` in a `.dmg`, with the same
`~/Library/Caches/meshbench` behaviour the Linux build has under `~/.cache`.
Emulation would be optional on first release: the native firmware path, which
is what every study and every CI gate uses, has no platform-specific parts.

### Windows

**Not built yet**, and blocked on one specific thing:

1. **`radioserver` speaks Unix domain sockets on the QEMU path.** It already
   has a TCP path, used for Renode, and that is what the QEMU path needs
   before anything else can be tried. This is the single item on the critical
   path.
2. **A Windows runner in the packaging workflow**, once the above is done.
3. **Driver expectations.** The virtual serial device the Companion bench
   offers is a pty on Unix. On Windows the equivalent is a named pipe or a
   com0com-style pair, so the Companion bench would offer TCP first and
   serial second there.

The intended shape is a plain `.zip` you unpack and run, matching Linux,
rather than an installer: nothing in the application writes outside its own
cache directory.
