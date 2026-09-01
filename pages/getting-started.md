# Getting started

Fifteen minutes from nothing to a real 311-node network relaying real packets
through real firmware.

## Install

Every release carries a Linux archive, a macOS disk image for Apple Silicon, and
a Windows zip. They are not equal: Linux is the platform everything is developed
and tested on, and the other two carry the caveats set out under each heading.

| platform | download | emulated boards |
|---|---|---|
| Linux x86_64 | `.tar.gz`, `.AppImage` or `.deb` | yes, emulators in the bundle |
| macOS, Apple Silicon | `.dmg`, unsigned | yes, emulators in the bundle |
| Windows x86_64 | `.zip` | only when the emulator builds are published for Windows |

Native firmware, the path every study and every CI gate uses, works on all
three. Emulated boards are the part that varies.

### Linux

**Requirements**

- **glibc 2.38 or newer**: Ubuntu 24.04, Debian 13, Fedora 39, or anything more
  recent. The floor is set by a prebuilt library MeshBench links against rather
  than by choice, and on an older distribution the application will not start.
- **A display and a GPU.** The CPU path gives the same answers more slowly, so a
  machine without a usable GPU loses time rather than features.
- **RAM**: about 500 MB for the application, plus roughly 10 MB per simulated
  node running real firmware. The 311-node network wants about 4 GB free.
- **Disk**: 200 MB for the bundle, and a cache under `~/.cache/meshbench`. Budget
  about **1 GB for a first session**: the network the workbench opens with covers
  Scotland and Ireland, and the ground under its links is roughly 500 MB of
  terrain that arrives on first launch. After that the cache grows only with the
  firmware builds and map tiles you actually use.
- **Bandwidth on the first run.** That terrain is fetched before you have done
  anything, so a metered connection is worth knowing about in advance. Opening a
  smaller network first, or running with `-fixture ""`, avoids it.

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

There is no installer, no root, and nothing to configure. The emulators, if the
bundle carries them, sit beside the binary and are found automatically.

The first launch is the slow one. The workbench opens on a network spanning
Scotland and Ireland and measures every link in it, which means fetching the
terrain underneath: about 500 MB, before you have clicked anything. The status
line reads `measuring every link` while that happens, so a percentage that
barely moves early on is the download rather than a stall. Firmware builds are
fetched separately, on first use.

`qemu-system-xtensa` in the bundle is a symlink on purpose: QEMU resolves its
own path to find its data files, so a bare copy of the binary will not run.

**If it will not start**

| symptom | cause |
|---|---|
| `version GLIBC_2.38 not found` | the distribution is older than the floor above |
| `Cannot set swap interval` | harmless, printed when the compositor declines vsync |
| a window opens and stays black | no usable GL driver; install your vendor's Mesa or driver package |

### macOS

Apple Silicon only. An x86_64 build under Rosetta would run the simulator
acceptably and the emulated firmware badly, so there is an arm64 build rather
than a translation layer.

**Steps**

1. Download `MeshBench-<version>-arm64.dmg` from the releases page and open it.
2. Drag the application out of the disk image.
3. **The disk image is unsigned.** Double-clicking it is refused by Gatekeeper.
   Right-click the application and choose Open, then confirm, which is needed
   once.

The bundle carries the QEMU and Renode builds beside the application, so
emulated boards work as they do on Linux. The cache lives under
`~/Library/Caches` rather than `~/.cache`.

### Windows

**Steps**

1. Download `meshbench-<version>-windows-x86_64.zip` from the releases page.
2. Unzip it anywhere you can write to.
3. Run `meshbench.exe`.

**SmartScreen warns**, because the executable is unsigned: choose More info and
then Run anyway.

The workbench and native firmware work. Emulated boards need QEMU and Renode
builds for Windows, and the bundle carries them only when those have been
published. A release built without them still runs, and emulated boards are
simply unavailable. The Companion bench offers TCP rather than a virtual serial
device, because the pty it uses elsewhere has no direct Windows equivalent.

### Building from source, any platform

Every release carries `meshbench-<version>-source.tar.gz` beside the binaries.
That archive is the source for exactly that build, which is what to use if the
question is how a particular release behaves.

```
tar xzf meshbench-<version>-source.tar.gz
cd meshbench-<version>
go build ./cmd/meshbench
```

To build the current tree instead, clone
[the repository](https://github.com/MeshBench/meshbench) and
`go build ./cmd/meshbench` in it.

That produces a binary called `meshbench`. It calls itself whichever name it was
run as, so a copy under another name behaves the same way.

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
- [Firmware development](firmware-development.html) if you are changing MeshCore
  itself.
- [Companion bench](companion-bench.html) if you are writing a client.
