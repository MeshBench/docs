# What is real, and what is modelled

**MeshBench runs real MeshCore firmware. MeshBench models the air.**

That one sentence is the whole design. MeshBench does not simulate the
firmware's behaviour: every node is the actual MeshCore application, compiled
and running as its own process, keeping its own state, making its own routing
decisions. What MeshBench provides is everything the firmware cannot bring
with it: the radio spectrum, the terrain, the distances, the noise, and a
clock all the nodes share.

<figure>
<svg viewBox="0 0 780 300" role="img" aria-label="Real firmware above the radio boundary, modelled air below it">
  <rect x="20" y="20" width="740" height="108" rx="10" fill="var(--good)" fill-opacity=".07" stroke="var(--good)" stroke-opacity=".45"/>
  <text x="46" y="44" font-size="12.5" font-weight="700" fill="var(--good)">REAL</text>
  <rect x="46" y="58" width="210" height="52" rx="7" fill="var(--card)" stroke="var(--rule)"/>
  <text x="151" y="80" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">MeshCore firmware</text>
  <text x="151" y="98" font-size="10.5" fill="var(--dim)" text-anchor="middle">one process per node</text>
  <rect x="276" y="58" width="210" height="52" rx="7" fill="var(--card)" stroke="var(--rule)"/>
  <text x="381" y="80" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">its routing and timing</text>
  <text x="381" y="98" font-size="10.5" fill="var(--dim)" text-anchor="middle">flood suppression, CSMA, regions</text>
  <rect x="506" y="58" width="228" height="52" rx="7" fill="var(--card)" stroke="var(--rule)"/>
  <text x="620" y="80" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">the bytes it transmits</text>
  <text x="620" y="98" font-size="10.5" fill="var(--dim)" text-anchor="middle">and its own serial protocol</text>

  <rect x="20" y="140" width="740" height="30" rx="7" fill="var(--panel)" stroke="var(--accent-mark)" stroke-dasharray="5 4"/>
  <text x="390" y="160" font-size="11.5" font-weight="600" fill="var(--accent)" text-anchor="middle">the radio interface: a linked shim (native) or a modelled SX1262 chip (emulated)</text>

  <rect x="20" y="182" width="740" height="96" rx="10" fill="var(--relay)" fill-opacity=".06" stroke="var(--relay)" stroke-opacity=".4"/>
  <text x="46" y="206" font-size="12.5" font-weight="700" fill="var(--relay)">MODELLED</text>
  <rect x="140" y="216" width="184" height="48" rx="7" fill="var(--card)" stroke="var(--rule)"/>
  <text x="232" y="236" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">the channel</text>
  <text x="232" y="253" font-size="10.5" fill="var(--dim)" text-anchor="middle">path loss, terrain, noise, overlap</text>
  <rect x="344" y="216" width="184" height="48" rx="7" fill="var(--card)" stroke="var(--rule)"/>
  <text x="436" y="236" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">the clock</text>
  <text x="436" y="253" font-size="10.5" fill="var(--dim)" text-anchor="middle">simulated time, one tick for all</text>
  <rect x="548" y="216" width="184" height="48" rx="7" fill="var(--card)" stroke="var(--rule)"/>
  <text x="640" y="236" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">the world</text>
  <text x="640" y="253" font-size="10.5" fill="var(--dim)" text-anchor="middle">positions, antennas, buildings</text>
</svg>
<figcaption>Everything above the dashed line is MeshCore's own code, unmodified.
Everything below it is MeshBench's model. The boundary sits exactly where a real
radio chip sits.</figcaption>
</figure>

## Why the interface sits there

A simulator that re-implements the protocol tests the re-implementation. By
running the real firmware and substituting only the radio, what MeshBench
measures is MeshCore's actual behaviour: its flood suppression, its CSMA
timing, its region filtering, exactly as they ship. When a packet is not
relayed, it is because the real code decided not to relay it.

The interface has two placements, described in
[Native and emulated](native-vs-emulated.html):

- **Native**: MeshCore compiled for this machine, with a radio shim linked in
  where the SPI driver would be. Deterministic, hundreds of nodes, the mode
  every measurement uses.
- **Emulated**: the published board image, unmodified, on an emulated CPU
  talking to a modelled SX1262 over emulated SPI. Wall-clock time, about eight
  nodes, the mode for checking a release boots and transmits.

## What happens to a transmission

The firmware hands bytes to its radio. The channel prices the path to every
listener: transmit power, antenna gain in the true direction, free-space loss,
terrain diffraction, buildings if loaded, then noise at each receiver. Whether
each listener decodes is judged one of two ways:

- **Calculated RF** (the default): signal-to-noise arithmetic against the
  demodulator's floor. Fast enough for a national network.
- **Waveform RF**: the actual chirps are synthesised as IQ samples, overlaps
  sum coherently, and a real demodulator recovers the frame or does not.
  Capture and collision emerge from the physics. 20 to 50 times the cost.

[RF simulation](rf-simulation.html) compares them; the
[RF chain](rf-chain.html) walks the stages both share. Either way, the verdict
and its cause land in the event log, which is what every result is read from.

## The words, in one place

The terms below are the project's own, used consistently by the application,
the fixtures and the clients.

| term | meaning |
|---|---|
| network | the nodes on the map and the links between them |
| scenario | a network plus everything that makes a run repeatable: seed, radio settings, schedule |
| fixture | a scenario shipped as JSON, with assertions; the runnable, testable form |
| run | one execution of a scenario; `run.save` keeps its results for comparison |
| seed | the run's randomness; same seed, same scenario, same result (native firmware) |
| arm | one variant in an experiment: a firmware version or setting under comparison |
| region | a transport region a repeater forwards flood traffic for, e.g. `sco` |
| scope | the region a packet is sent on; written `#sco` on the wire, and hashed |
| kind | what a node is: simple-repeater, companion, room-server, sdr-observer, emitter |
| role | the MeshCore application a node runs: `simple_repeater`, `companion_radio`, `simple_room_server` |
| native | MeshCore compiled for this machine, radio shim linked in; deterministic |
| emulated | the published board image on an emulated chip; wall-clock time |
| calculated RF | reception decided by link-budget arithmetic against the demodulator floor |
| waveform RF | reception decided by a real demodulator over synthesised samples |
| boundary | the study area; nodes outside it (plus a margin) are not simulated |
| demodulator floor | the weakest signal the radio can still decode; everything quieter is noise |
| margin | how many dB a link clears the demodulator floor by |
| cause | why a reception failed, recorded per event: below the floor, corrupted by overlap, radio elsewhere |
| provenance | the caveats stamped into a result: RF mode, realism switches, seed |

Two pairs are worth keeping apart because both words appear in the interface:
a **region** is held by a node and decides what it relays; a **scope** is
carried by a packet and decides who relays it. A **kind** is what a node is on
the map; a **role** is which MeshCore application it boots.

## Where to go next

- [Getting started](getting-started.html): install and launch.
- [Your first simulation](first-simulation.html): a real network relaying real
  packets, in about fifteen minutes.
- [Reading a result](results.html): what the numbers mean, and how much to
  trust them.
