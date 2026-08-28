# Getting started

Fifteen minutes from nothing to a real 378-node network relaying real packets
through real firmware.

## Install

Linux is the only platform with a build today. macOS and Windows are described
below with what is actually blocking each, because a plan you can read beats a
blank space you have to ask about.

### Linux

**Requirements**

- **glibc 2.35 or newer**: Ubuntu 22.04, Debian 12, RHEL 9, or anything more
  recent. The floor is the build machine's own glibc rather than a choice, and
  on an older distribution the application will not start.
- **A display and a GPU.** The CPU path gives the same answers more slowly, so a
  machine without a usable GPU loses time rather than features.
- **RAM**: about 500 MB for the application, plus roughly 10 MB per simulated
  node running real firmware. The 378-node network wants about 4 GB free.
- **Disk**: 200 MB for the bundle, and a cache under `~/.cache/meshbench` that
  grows with the firmware builds and map tiles you use.

**Steps**

1. Download `meshbench-linux-x86_64.tar.gz` from the releases page.
2. Unpack it anywhere you can write to.
   ```
   tar xzf meshbench-linux-x86_64.tar.gz
   cd meshbench
   ```
3. Run it.
   ```
   ./meshbench workbench
   ```

There is no installer, no root, and nothing to configure. Firmware builds and
map tiles download on first use. The emulators, if the bundle carries them, sit
beside the binary and are found automatically.

`qemu-system-xtensa` in the bundle is a symlink on purpose: QEMU resolves its
own path to find its data files, so a bare copy of the binary will not run.

**If it will not start**

| symptom | cause |
|---|---|
| `version GLIBC_2.35 not found` | the distribution is older than the floor above |
| `Cannot set swap interval` | harmless, printed when the compositor declines vsync |
| a window opens and stays black | no usable GL driver; install your vendor's Mesa or driver package |

### macOS

**Not built yet.** What it needs, in order:

1. **A Darwin runner in the packaging workflow.** The application itself is Go
   and cgo against a cross-platform UI library, so this part is expected to be
   straightforward.
2. **The QEMU fork built on Darwin.** MeshBench's QEMU carries an SX1262 device
   upstream does not have. It has never been compiled on macOS, and that is the
   real unknown.
3. **A separate Apple Silicon build.** An x86_64 build under Rosetta would run
   the simulator acceptably and the emulated firmware badly, so arm64 needs its
   own row rather than a translation layer.

The intended shape is a signed `.app` in a `.dmg`, with the same
`~/Library/Caches/meshbench` behaviour the Linux build has under
`~/.cache`. Emulation would be optional on first release: the native firmware
path, which is what every study and every CI gate uses, has no platform-specific
parts.

### Windows

**Not built yet**, and blocked on one specific thing:

1. **`radioserver` speaks Unix domain sockets on the QEMU path.** It already has
   a TCP path, used for Renode, and that is what the QEMU path needs before
   anything else can be tried. This is the single item on the critical path.
2. **A Windows runner in the packaging workflow**, once the above is done.
3. **Driver expectations.** The virtual serial device the Companion bench offers
   is a pty on Unix. On Windows the equivalent is a named pipe or a com0com-style
   pair, so the Companion bench would offer TCP first and serial second there.

The intended shape is a plain `.zip` you unpack and run, matching Linux, rather
than an installer: nothing in the application writes outside its own cache
directory.

### Building from source, any platform

```
git clone https://github.com/MeshBench/meshbench
cd meshbench
go build ./cmd/meshbench
```

That produces a binary called `meshbench`, the same program the release
ships.

Needs Go 1.25 and a C toolchain with GL and X11 development headers, because the
UI is cgo. On Debian and Ubuntu:

```
sudo apt install gcc pkg-config libgl1-mesa-dev xorg-dev
```

## Your first network

1. **Load a shipped network.** `File` then `Open project`, and choose
   `fixture-fife-strict`. Fifty-eight real nodes from the Fife area of ScotMesh,
   with the transport regions the real nodes actually hold.
2. **Start the firmware.** `Simulation` then `Start firmware`. Every node
   launches a real MeshCore build and is told its name, position, clock and
   regions. Watch the count in the status bar reach the node total.
3. **Press play.** The transport symbol on the toolbar. Simulated time starts
   moving and the map fills with links as nodes hear each other.
4. **Watch something happen.** Open the `Events` panel. Every transmission,
   reception and miss is listed with a cause, which is the difference between
   "it did not arrive" and "it arrived 3 dB under the demodulator floor".

> If the mesh looks dead, the usual cause is regions rather than radio. A
> repeater only forwards flood traffic for regions it has been told about, and
> reports no error when it declines. See [Shipped networks](fixtures.html).

## Where things are

The view switcher along the top is the main navigation. Each view is a saved
arrangement of panels for one kind of work:

| view | for |
|---|---|
| **Plan** | build and site: import, place, drag, boundary, coverage |
| **Run** | exercise it and watch: play, schedule traffic, consoles, live feed |
| **Debug** | ask why one thing happened: packets, waterfall, consoles, budgets |
| **Verify** | check it is still true: baselines, A/B bisect, residuals |
| **Bench** | compare configurations: sweep a parameter, read what differed |
| **App** | write a client against it: an endpoint, the protocol, faults |

Panels can be dragged out, docked elsewhere, or popped into their own window on
a second monitor. Each view remembers its own arrangement.

## Next

- [Shipped networks](fixtures.html) if you want a bigger or more realistic mesh.
- The [CLI reference](reference-cli.html) for everything the binary does without
  a window, and [Settings](settings.html) for what the application remembers.
- [External tools](tools.html) for what MeshBench looks for on the machine —
  Wireshark, SDR++, the emulators — and what happens when one is missing.
- [Firmware development](firmware-development.html) if you are changing MeshCore
  itself.
- [Companion bench](companion-bench.html) if you are writing a client.
