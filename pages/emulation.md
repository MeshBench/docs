# Emulating a board

Running the **published firmware image**, unmodified, the same file somebody
flashes onto hardware, against MeshBench's radio channel.

This is a different thing from the native path. A native build compiles MeshCore
for your host and links a shim in place of the radio driver: fast, deterministic,
and what every study and every CI gate uses. Emulation runs the real binary on a
model of the real chip, which is slow and not deterministic, and answers a
question the native path cannot: **does this release actually come up and talk on
this board?**

<figure>
<svg viewBox="0 0 760 400" role="img" aria-label="The emulation stack, with a real and simulated divide">
  <text x="150" y="18" class="svg-dim" font-size="12" text-anchor="middle" letter-spacing="1.5">REAL</text>
  <text x="530" y="18" class="svg-dim" font-size="12" text-anchor="middle" letter-spacing="1.5">SIMULATED</text>
  <line x1="300" y1="28" x2="300" y2="390" class="svg-real" stroke-width="2"/>
  <rect x="30" y="40" width="240" height="54" rx="7" class="svg-panel"/>
  <text x="150" y="63" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">Published firmware image</text>
  <text x="150" y="82" class="svg-dim" font-size="11.5" text-anchor="middle">Heltec_v3_repeater-v1.17.0.bin</text>
  <rect x="30" y="112" width="240" height="54" rx="7" class="svg-panel"/>
  <text x="150" y="135" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">MeshCore, unmodified</text>
  <text x="150" y="154" class="svg-dim" font-size="11.5" text-anchor="middle">same code, same compiler, same flags</text>
  <rect x="30" y="184" width="240" height="70" rx="7" class="svg-panel"/>
  <text x="150" y="206" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">CPU and peripherals</text>
  <text x="150" y="224" class="svg-dim" font-size="11.5" text-anchor="middle">QEMU (Xtensa) or Renode (Cortex-M4)</text>
  <text x="150" y="241" class="svg-dim" font-size="11.5" text-anchor="middle">SPIM, GPIO, RTC, TWIM, SAADC</text>
  <rect x="30" y="272" width="240" height="54" rx="7" class="svg-panel"/>
  <text x="150" y="294" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">SPI bus</text>
  <text x="150" y="313" class="svg-dim" font-size="11.5" text-anchor="middle">commands, registers, IRQ line, NSS</text>
  <path d="M270 299 L 420 299" class="svg-accent" stroke-width="2" marker-end="url(#a)"/>
  <defs><marker id="a" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
    <polygon points="0 0, 9 3.5, 0 7" fill="currentColor" class="svg-ink"/></marker></defs>
  <rect x="420" y="272" width="290" height="54" rx="7" class="svg-panel"/>
  <text x="565" y="294" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">radioserver</text>
  <text x="565" y="313" class="svg-dim" font-size="11.5" text-anchor="middle">the SX1262 chip model, out of process</text>
  <rect x="420" y="184" width="290" height="70" rx="7" class="svg-panel"/>
  <text x="565" y="206" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">MeshBench channel</text>
  <text x="565" y="224" class="svg-dim" font-size="11.5" text-anchor="middle">sum, delay, path loss, terrain, noise</text>
  <text x="565" y="241" class="svg-dim" font-size="11.5" text-anchor="middle">sample accurate, decides nothing</text>
  <rect x="420" y="112" width="290" height="54" rx="7" class="svg-panel"/>
  <text x="565" y="135" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">Every other node</text>
  <text x="565" y="154" class="svg-dim" font-size="11.5" text-anchor="middle">native, emulated, or an SDR observer</text>
  <line x1="565" y1="272" x2="565" y2="258" class="svg-line" stroke-width="2"/>
  <line x1="565" y1="184" x2="565" y2="170" class="svg-line" stroke-width="2"/>
  <line x1="150" y1="94" x2="150" y2="108" class="svg-line" stroke-width="2"/>
  <line x1="150" y1="166" x2="150" y2="180" class="svg-line" stroke-width="2"/>
  <line x1="150" y1="254" x2="150" y2="268" class="svg-line" stroke-width="2"/>
  <text x="380" y="365" class="svg-dim" font-size="11.5" text-anchor="middle">the boundary is the SPI bus</text>
</svg>
<figcaption>Everything left of the dashed line is the artefact people flash onto
hardware. The boundary is the SPI bus, which is where a real SX1262 would be, so
nothing above it has to be told it is being simulated.</figcaption>
</figure>

## Why the boundary is the SPI bus

MeshCore talks to its radio over SPI: command opcodes, register reads and
writes, a busy line and an interrupt line. Put the model there and the firmware
above it needs no modification at all. Put it any higher, at the driver or the
packet layer, and you are no longer testing the thing that ships.

That choice is what makes the answer meaningful. When an emulated Heltec v3 sent
an advert and thirty-eight other nodes decoded it, what was verified was the
published binary's SPI conversation with a chip model, not a re-implementation
of what that conversation should look like.

## radioserver: one chip model, three consumers

`radioserver` is a small C++17 program that presents the SX1262 interface and
turns transmit commands into waveforms. It runs **out of process** and is shared
by all three ways of running firmware:

| consumer | how it connects |
|---|---|
| native builds | in-process shim, no socket |
| QEMU | Unix domain socket |
| Renode | TCP |

The TCP path exists even though Linux does not need it, because Windows will:
the Unix socket path is the single item on the critical path for a Windows
build.

One model rather than three means a bug in the chip's behaviour is a bug
everywhere, which is much easier to find than three subtly different radios.

## QEMU, for ESP32 (Xtensa)

**The fork adds `hw/ssi/sx1262.c`**, an SX1262 device upstream does not have.
The packaging workflow asserts that file is in the tree it built, because a
checkout that silently resolved to upstream produces a QEMU that runs perfectly
and reports no chip present, which looks like our bug.

**It must be configured with `--enable-gcrypt`.** Without it the `esp32` machine
will not instantiate at all, and the error does not mention crypto.

## Renode, for nRF52 (Cortex-M4)

The nRF52840 path took considerably more work, and every piece of it is a
detail that produced a silent failure first.

### SPIM3 lives at 0x4002F000

The nRF52840 has four SPI master instances. The one MeshCore uses on these
boards is **SPIM3 at `0x4002F000`**, which was initially mis-identified as
CryptoCell. The register offsets settle it: `0x118` is `EVENTS_END`, `0x304` and
`0x308` are `INTENSET` and `INTENCLR`. Those are SPIM's, not CryptoCell's.

### EasyDMA, not a data register

SPIM does not have a byte-at-a-time data register. The firmware writes a pointer
and a length into `TXD.PTR` and `TXD.MAXCNT`, the same for `RXD`, and triggers
`TASKS_START`. The peripheral model has to read the transmit buffer out of guest
memory, run the transaction, write the reply back into the receive buffer, and
then raise `EVENTS_END`. A model that ignores EasyDMA sees no bytes at all and
the firmware waits forever for a chip that never answers.

### Chip select is a GPIO, and Renode never releases it

An SX1262 transaction is delimited by NSS going low and then high again. Renode's
SPI infrastructure never calls `FinishTransmission()`, so from the chip model's
point of view the transaction never ends and every subsequent command is read as
a continuation of the first one.

The fix is to stop treating NSS as the SPI controller's business and wire it as
what it actually is on the board: a GPIO. For the RAK4631 that is `gpio1` pin
10, with DIO1, the interrupt line, on `gpio1` pin 15. Those numbers are recorded
per board in `internal/scenario/boards.go` as `RenodeWiring`, because they are a
property of the board rather than of the emulator.

### The SEVONPEND fix, and why the fix looked absent

Published nRF52 firmware sets **SEVONPEND** and then executes `WFE`, expecting to
be woken when an interrupt becomes pending, whether or not it is enabled to fire.

Renode's CPU core, tlib, was checking whether any interrupt was pending in a way
that did not match the ARM semantics the firmware relies on, so the core slept
and never woke. The mesh looked alive and completely silent.

The fix has three parts, and missing any one of them looks identical from
outside:

1. tlib gains `tlib_nvic_get_pending_masked_irq()` and the wake check uses it.
2. `renode_arm_callbacks.c` needs the binding
   `EXTERNAL_AS(int32_t, PendingIRQ, tlib_nvic_get_pending_irq)`. Without this
   the new function exists and is never called, and the whole change appears to
   do nothing.
3. The managed side calls `sleeper.Interrupt()` so the sleeping thread actually
   wakes.

> **A fix that is absent and a fix that is wrong look identical from outside.**
> The first attempt at this had the tlib change and not the binding, and the
> conclusion drawn was "SEVONPEND is not the problem", which was wrong.

### Peripherals the firmware touches on the way up

MeshCore does not only talk to the radio. Boot touches several peripherals, and
each missing one stops the firmware somewhere earlier and less obviously:

| peripheral | why the firmware needs it |
|---|---|
| `NRF52840_Temp` | the temperature sensor read at start-up |
| `NRF52840_Clock` | HFCLK and LFCLK start, waited on before anything proceeds |
| `NRF52840_SAADC` | battery voltage |
| `NRF52840_TWIM` | I2C, for the display and sensors on some boards |
| `RadioServerSX1262` | the radio, bridged to radioserver |

These live in `tools/renode/peripherals/` as C# files loaded by the platform
description.

## Forks, and why they are not upstream builds

Neither emulator can be a distribution build:

- Our **QEMU** carries the SX1262 device. A stock build runs and reports no chip.
- Our **Renode** carries the SEVONPEND fix. A stock build boots the firmware and
  it sleeps for ever.

Both are built in CI from MeshBench's forks. A bundle that shipped a stock build
of either would fail in a way that looks like MeshBench's fault.

## What it costs, and the ceiling

**Each emulated node is its own emulator process, running in real time**, and
costs roughly one core and 150 MB.

> **Never run more than eight at once on a twelve-core machine, and never let
> free memory fall below 3 GB.** Past the ceiling nothing reports an error.
> Boots stretch, simulated time falls behind the wall clock, and the symptom is
> a mesh that has gone quiet: exactly what a genuine RF problem looks like.

The firmware library says how many nodes a board image would land on before you
press the button, for this reason.

## Emulation is a conformance tool, not a measurement tool

Emulated nodes run on wall time. Two runs of the same seed do not agree, so:

- **every CI gate is native**
- **every study arm is native**
- emulation answers "does this published build come up, configure itself, and
  put a correctly formed packet on the air"

Both architectures have been taken to that point. The ESP32 path produced an
advert decoded by thirty-eight other nodes; the nRF52 path produced a 127-byte
advert after 5,240 SPI transactions.
