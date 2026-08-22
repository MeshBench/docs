# The waveform

MeshBench has two reception models. In **calculated** mode a link is decided by
arithmetic: a signal-to-noise ratio against the demodulator's floor, with
concurrent transmissions summed into the noise. In **waveform** mode there is
no such decision. The channel produces a sampled signal, a receiver front end
looks for a preamble in it, and a demodulator either recovers the frame or does
not.

The rule the whole design serves:

> The RF channel produces signals, never verdicts. The receiver produces
> observations, never packets. The demodulator produces packets, and only a
> valid PHY decode may enter MeshCore.

Calculated mode is the default and is the right choice for large scenarios.
Waveform mode is slower by a factor of tens and answers questions arithmetic
cannot: whether two overlapping transmissions capture or collide, what a
partial overlap actually costs, and what a receiver would hear.

## Choosing a mode

The mode is set in **Configuration → RF Simulation**, or through the `rf.mode`
verb. It applies on a whole-transmission boundary, so a run can be switched
while it plays without cutting a frame in half. The choice is persisted, and it
is stamped into every saved run — a result carries the physics that produced
it, because two runs under different models are not comparable.

The status bar names the active mode while a run plays.

## A packet's life in waveform mode

### Transmit

MeshCore firmware writes a frame to its virtual radio. The bridge surfaces it,
and the engine prices its airtime with the same formula RadioLib uses in
`getTimeOnAir` — the one MeshCore's own CSMA is built on. When the airtime
elapses the transmission is collected for delivery together with everything
that shared the air: transmissions still in flight, others that ended in the
same tick, and transmissions that ended earlier but overlapped something still
up.

That last category matters. A short interferer that has already stopped still
damaged the frame it overlapped, and a model that forgets it the moment it ends
under-reports collisions in both modes.

### Synthesis

The frame is rendered as an SX126x would send it. The coding chain
(`internal/rf/lora`) runs an explicit header with its checksum, payload
whitening, a CRC16, Hamming forward error correction at the frame's coding
rate, the diagonal interleaver, and Gray mapping. The result is wrapped
(`internal/rf/dsp/sync.go`) in MeshCore's own preamble length — 32 upchirps at
spreading factor 8 and below, 16 above — the `0x12` sync word, and the
2.25-symbol downchirp that marks the start of frame.

That 2.25 is not a rounding. It is RadioLib's `sfCoeff1 = 4.25` expressed as
samples, and a test holds the sample stream and the airtime formula to
describing the same frame. If they disagreed, the channel and the firmware's
CSMA would drift apart silently.

The coding chain accepts spreading factors 7 to 12. SF5 and SF6 use a different
frame arrangement on the SX126x — a 6.25-symbol delimiter rather than 2.25 —
and are rejected rather than approximated.

Samples are synthesised once per packet per delivery batch and shared across
receivers, because unit-amplitude baseband does not depend on who is listening.

### The channel

For each transmission and each receiver (`internal/sim/engine/baseband.go`) the
engine applies transmit power, antenna gain in the true direction to the far
end, path loss, the timing offset into the receive window, and the oscillator
disagreement between the two nodes as a per-sample phase ramp.

Path loss is free-space plus ITU-R P.526 terrain diffraction, plus buildings
when an environment is loaded, plus a calibration term.

With multipath enabled, one geometric echo is added per path: deterministic
excess delay and carrier phase, drifted by the configured fading rate.

`internal/rf/channel` then sums every contribution coherently — fractional
delay carried as phase — and adds counter-based Gaussian noise at the
receiver's own noise floor. The same synthesis feeds the decode verdicts, the
waterfall, the carrier-sense detector and the SDR observers. Rendering those
from different signals would let the pictures disagree with the physics.

### Receive

The receiver front end runs in parallel across candidate receivers, with serial
bookkeeping so that ledgers stay byte-identical between runs.

1. Saturate the front end, if a level is configured.
2. Measure signal-to-noise from the window. This is telemetry only; nothing
   downstream reads it to decide anything.
3. Find the preamble, by looking for dechirped bins that hold still.
4. Find the frame boundary from the start-of-frame delimiter, using the
   calibrated relations between the up-chirp and down-chirp bins.
5. Resolve whole-symbol aliasing with a three-candidate contest, judged by what
   precedes each candidate: a true start is preceded by delimiter mush, a late
   one by a clean symbol.
6. Refine to ±2 samples, because a one-sample slip shifts every bin.

No lock, no packet. "No preamble lock" is its own entry in the ledger rather
than being folded into a general failure.

What follows is carrier-frequency correction, a per-symbol FFT demodulation,
and the coding chain in reverse: Gray, deinterleave, Hamming, dewhiten, header
parse, CRC. The 4/7 and 4/8 coding rates correct one bit per codeword; 4/5 and
4/6 only detect. That split is the chip's, not a simplification.

The decoder consumes only the frame its header declares, so the tail of a
streaming window is the channel's business rather than damage to the packet.

### The verdict

What reaches MeshCore is **the decoded bytes, not the transmitted frame**. With
a valid CRC those are the same bytes. On the day a corrupted frame passes CRC by
chance, the firmware sees the corruption — which is what the chip would hand it
too.

Misses say why: no preamble lock, header unreadable, or a count of codewords
beyond repair alongside the number the forward error correction did repair.
Signal-to-noise and RSSI ride along as telemetry.

### Carrier sense

In waveform mode, channel-busy is decided by the same detector the chip uses.
One symbol of summed IQ per listening node per tick is dechirped and its peak
compared against the mean. That detector fires below the decode floor, which is
why listen-before-talk works at all.

The busy verdict is handed to the firmware over the bridge, so MeshCore's CSMA
and backoff respond to actual radio conditions with no engine rule in between.

## The SDR observer

Any node's antenna can be rendered over a span of simulated time and served to
real SDR software. The stream is built from the same synthesis as the decode
path, never from packet events.

`internal/world/sdr` speaks rtl-sdr's own network protocol, so a stock SDR++
client connects to it: the RTL0 header, five-byte tuning commands, and unsigned
8-bit interleaved IQ. That format has a dynamic range ceiling of roughly 48 dB,
which is a real limit of what an observer can show.

The design is shaped by being judged next to a real dongle:

- A producer goroutine renders signal-only IQ a quarter of a second behind the
  engine's clock into a ring buffer, so delivery never touches the engine and a
  heavy judgement cannot stall the stream.
- Delivery is paced against wall-clock deficit, served from the ring.
- Windowed-sinc resampling follows the client's own rate menu, so a burst stays
  exactly as wide as its bandwidth.
- The noise floor is painted server-side across the whole client span at the
  receiver's own noise density. A paused run streams that floor rather than
  inventing future air or replaying a block on repeat.
- Level control is anchored to that floor and drops instantly rather than let a
  strong burst clip, because a clipped chirp is broadband splatter smeared
  across the span.
- The stream position only ever moves forward. Rewinding to chase a slow
  simulation re-serves overlapping windows and stripes the waterfall.

One client at a time, as with the real server. Verbs are `sdr.serve` and
`sdr.stop`.

Moving a node on the map forgets its cached path losses, so dragging an
observer changes what an attached client hears on the next window.

An observer has its own node window (`internal/ui/workbench/nodewindowobserver.go`)
with no console and no Radio tab — it runs no firmware and has no chip — but an
SDR pane that serves the antenna, shows the address and the client's exact
sample rate, and says whether a client is connected.

## Buildings

`internal/rf/environ` holds what physically stands in the path: footprints,
heights, and a material taxonomy, with every derived value carrying its source
and its confidence.

Tiles are gzipped JSON lines per zoom-14 slippy tile, produced offline by
`tools/envgen` from Microsoft Global ML Building Footprints or OSM GeoJSON,
loaded on demand and cached. **Missing tiles are counted, never mistaken for
empty ground** — the difference between "no buildings here" and "no data here"
changes what a coverage raster means.

Each crossed building is priced as a P.526 knife edge at its rooftop, plus one
wall of material loss when the direct ray passes through. Both reception modes
pay it, because buildings change the gain along a path and never the verdict
directly. A test holds the waveform chain to this: a thin-margin link that
decodes cleanly over bare earth must fail with a concrete building across it.

Verdicts, carrier sense and the SDR observer all price through the same path,
so a loaded environment reaches all three. Loading or dropping an environment
forgets the link cache, because two sets of physics must not share one matrix.

Footprints can also be pulled at runtime from OpenStreetMap over Overpass, from
Microsoft's footprints by quadkey, or — the default — the two merged. Microsoft
provides existence and height; an OSM building whose centroid falls inside a
detected footprint contributes its explicit type, levels and materials, with
explicit overriding inferred. OSM-only buildings survive on their own.

Pulls are scoped to patches around the nodes and merged where those overlap, so
a town is requested once and a national network's empty middle is never
requested at all. A pull that is still too large refuses and points at
`tools/envgen`.

## Determinism

Same seed, same scenario, same ledger, in both modes. What makes that true:

- Counter-based noise, keyed by packet and receiver rather than drawn from a
  shared stream.
- Crystal offsets and echo geometry derived from node names by hash.
- Parallel signal processing with serial bookkeeping.
- Map iteration in node order.

The known exception is emulated firmware, which runs on wall-clock time.

## What it costs

Measured on a Ryzen 5 3600XT with 12 threads and an RDNA2 GPU.

| Workload | Time |
|---|---|
| 300-node, 20-sender flood burst (~5 s simulated), calculated | 46 ms |
| Same burst, waveform, symbol-level verdicts | 1.04 s |
| Same burst, full coding chain | 1.89 s |
| Same burst, with the receiver front end in the path | 2.29 s |
| GPU demodulation, SF9 × 512 symbols | 4.53 ms CPU, 1.11 ms GPU |

The heaviest burst runs about 2.2× faster than real time on the CPU alone.
Roughly half the remaining time is Gaussian noise synthesis and a fifth is FFT.

Waveform mode is between 20× and 50× the cost of calculated mode. That is the
trade: it is the mode to reach for when the question is about a specific
collision, a specific link, or what a receiver would actually hear — not the
mode to sweep a national network in.
