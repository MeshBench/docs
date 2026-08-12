# Architecture

MeshBench is one binary on one machine. There is no service, no worker, no
backend. The only things that cross the network are *data*: terrain tiles, map
tiles, and the optional CoreScope, Beacon and MQTT feeds. Nothing in the
simulation depends on anything remote.

<figure>
<svg viewBox="0 0 780 430" role="img" aria-label="How a packet gets from one node's firmware to another's">
  <rect x="20" y="30" width="180" height="150" rx="8" class="svg-panel"/>
  <text x="110" y="52" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">Node A</text>
  <text x="110" y="74" class="svg-dim" font-size="11.5" text-anchor="middle">real MeshCore firmware</text>
  <text x="110" y="92" class="svg-dim" font-size="11.5" text-anchor="middle">its own process</text>
  <text x="110" y="110" class="svg-dim" font-size="11.5" text-anchor="middle">its own storage and identity</text>
  <rect x="40" y="126" width="140" height="38" rx="6" class="svg-panel"/>
  <text x="110" y="150" class="svg-ink" font-size="12" text-anchor="middle">Radio shim / SPI</text>
  <path d="M200 145 L 275 145" class="svg-accent" stroke-width="2" marker-end="url(#b)"/>
  <defs><marker id="b" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
    <polygon points="0 0, 9 3.5, 0 7" class="svg-ink"/></marker></defs>
  <text x="237" y="136" class="svg-dim" font-size="11" text-anchor="middle">bytes</text>
  <rect x="275" y="30" width="230" height="220" rx="8" class="svg-panel"/>
  <text x="390" y="52" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">The channel</text>
  <text x="390" y="76" class="svg-dim" font-size="11.5" text-anchor="middle">modulate to complex samples</text>
  <text x="390" y="96" class="svg-dim" font-size="11.5" text-anchor="middle">delay by distance / c</text>
  <text x="390" y="116" class="svg-dim" font-size="11.5" text-anchor="middle">path loss, terrain diffraction</text>
  <text x="390" y="136" class="svg-dim" font-size="11.5" text-anchor="middle">antenna gain, per direction</text>
  <text x="390" y="156" class="svg-dim" font-size="11.5" text-anchor="middle">sum every transmission in flight</text>
  <text x="390" y="176" class="svg-dim" font-size="11.5" text-anchor="middle">add thermal noise</text>
  <text x="390" y="206" class="svg-ink" font-size="12" text-anchor="middle" font-weight="600">It decides nothing.</text>
  <text x="390" y="226" class="svg-dim" font-size="11.5" text-anchor="middle">No rule says "these two collide".</text>
  <path d="M505 145 L 580 145" class="svg-accent" stroke-width="2" marker-end="url(#b)"/>
  <text x="542" y="136" class="svg-dim" font-size="11" text-anchor="middle">samples</text>
  <rect x="580" y="30" width="180" height="220" rx="8" class="svg-panel"/>
  <text x="670" y="52" class="svg-ink" font-size="13" text-anchor="middle" font-weight="600">Node B</text>
  <rect x="596" y="66" width="148" height="60" rx="6" class="svg-panel"/>
  <text x="670" y="88" class="svg-ink" font-size="12" text-anchor="middle">Demodulator</text>
  <text x="670" y="106" class="svg-dim" font-size="11" text-anchor="middle">decides what decodes</text>
  <text x="670" y="150" class="svg-dim" font-size="11.5" text-anchor="middle">capture effect emerges</text>
  <text x="670" y="170" class="svg-dim" font-size="11.5" text-anchor="middle">from the arithmetic,</text>
  <text x="670" y="190" class="svg-dim" font-size="11.5" text-anchor="middle">not from a rule</text>
  <text x="670" y="222" class="svg-dim" font-size="11.5" text-anchor="middle">real firmware, again</text>
  <text x="390" y="300" class="svg-ink" font-size="12.5" text-anchor="middle" font-weight="600">Every GPU kernel has a CPU twin, and they are tested against each other.</text>
  <text x="390" y="322" class="svg-dim" font-size="11.5" text-anchor="middle">A wrong FFT does not crash. It produces a plausible waterfall and slightly wrong</text>
  <text x="390" y="340" class="svg-dim" font-size="11.5" text-anchor="middle">sensitivity, and nobody notices for months.</text>
</svg>
<figcaption>The channel sums waveforms and adds noise. Whether a packet decodes
is the demodulator's business, which is why capture effect emerges rather than
being coded as a rule.</figcaption>
</figure>

## The rules that keep it honest

These are enforced by review and by tests, and each one exists because the
alternative produces a plausible answer that is wrong.

**The channel does not decide anything.** It sums waveforms and adds noise.
Never add a rule like "if two transmissions overlap, both fail": capture effect
must *emerge*, or the simulator is a packet model with extra steps.

**Every GPU kernel has a CPU twin**, and the two are tested against each other.

**Reachability is asymmetric.** A can hear B while B cannot hear A: different
antennas, heights, powers and noise figures. Every result states which
direction, because one that does not is wrong even when the arithmetic is right.

**Antenna gain is directional.** The pattern is evaluated in the true direction
to the far end, per direction. A scalar gain field is a bug.

**Position uncertainty propagates.** A node imported at ±5 km does not get a
confident answer.

**Airtime must match the firmware's own `getEstAirtimeFor()`.** The firmware's
CSMA timing is built on it. If the channel disagrees, the two desynchronise
silently and every timing result is quietly wrong.

**Determinism is a feature.** Same seed, same scenario, same result. Counter-based
RNG, never a stateful stream shared across goroutines.

## Where the code is

```
cmd/meshcoresim/     the binary: workbench plus the headless commands
internal/rf/         channel: sum, delay, noise
internal/dsp/        modulation, demodulation, FFT; CPU reference and GPU
internal/antenna/    patterns, orientation, polarisation
internal/terrain/    DEM tiles, profiles, diffraction
internal/firmware/   host builds of MeshCore, the Radio shim, per-node runtime
internal/scenario/   nodes, import, persistence, seeds
internal/fixture/    the shipped fixture format, shared with the test runner
internal/engine/     the simulation loop, events, assertions
internal/capture/    pcapng, event log
internal/sdr/        IQ export, SigMF, streaming
internal/companion/  TCP and pty companion transports
internal/ui/         panels
shaders/             WGSL compute shaders
tools/dissector/     Wireshark Lua dissector
```

## The engine loop

The engine steps in fixed increments, 10 ms by default. On each step it advances
every node's firmware, collects whatever those nodes handed to their radios,
places the resulting transmissions in flight, and delivers to each receiver the
sum of everything audible at its antenna.

**Simulated time is not wall time.** A native run can go faster than real time
on a small network and slower on a large one, and neither changes the result.
This is exactly what emulation gives up: an emulated node runs at the speed of
the emulator, so simulated time is pinned to the wall clock and two runs of one
seed do not agree.

## The control socket

The application listens on `$XDG_RUNTIME_DIR/meshcoresim.sock`, newline
delimited JSON. Every verb drives the same code path a person clicks, so a
driven session opens the same panels and shows the operator what happened.
See the [control socket reference](reference-control.html).

**Verbs are serviced on the frame thread.** That is a real constraint rather
than an implementation detail: it is why a headless mode is a separate mode
rather than the application running without a window.
