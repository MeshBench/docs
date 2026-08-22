# RF simulation: the two models

Everything about a run that involves the air passes through one layer, and that
layer can decide reception two different ways. Which one is active changes what
a result means, so it is stamped into every saved run.

<figure>
<svg viewBox="0 0 760 400" role="img" aria-label="Calculated and waveform reception compared">
  <defs>
    <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="var(--accent)" stop-opacity=".22"/>
      <stop offset="1" stop-color="var(--accent)" stop-opacity=".04"/>
    </linearGradient>
    <linearGradient id="wg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="var(--good)" stop-opacity=".22"/>
      <stop offset="1" stop-color="var(--good)" stop-opacity=".04"/>
    </linearGradient>
  </defs>

  <rect x="40" y="16" width="680" height="58" rx="8" fill="var(--sunk)" stroke="var(--rule)"/>
  <text x="380" y="40" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">Shared by both: transmit power, antenna gain in the true direction,</text>
  <text x="380" y="60" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">free space + terrain diffraction + buildings, the receiver's noise floor</text>

  <path d="M240 74 L 200 104" stroke="var(--rule)" stroke-width="2" fill="none"/>
  <path d="M520 74 L 560 104" stroke="var(--rule)" stroke-width="2" fill="none"/>
  <text x="380" y="96" font-size="11" fill="var(--faint)" text-anchor="middle">then the verdict is reached two ways</text>

  <text x="180" y="126" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">Calculated</text>
  <text x="180" y="144" font-size="11.5" fill="var(--dim)" text-anchor="middle">the default</text>
  <rect x="40" y="156" width="280" height="196" rx="10" fill="url(#cg)" stroke="var(--accent)" stroke-opacity=".5"/>
  <rect x="62" y="176" width="236" height="38" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="180" y="200" font-size="12" fill="var(--ink)" text-anchor="middle">signal, in dBm</text>
  <rect x="62" y="222" width="236" height="38" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="180" y="246" font-size="12" fill="var(--ink)" text-anchor="middle">overlaps summed into the noise</text>
  <rect x="62" y="268" width="236" height="42" rx="6" fill="var(--card)" stroke="var(--accent)" stroke-dasharray="4 3"/>
  <text x="180" y="288" font-size="12" fill="var(--ink)" text-anchor="middle">SNR vs the demodulator floor</text>
  <text x="180" y="304" font-size="10.5" fill="var(--dim)" text-anchor="middle">above it decodes, below it does not</text>
  <text x="180" y="334" font-size="11.5" font-weight="600" fill="var(--ink)" text-anchor="middle">no capture effect</text>

  <text x="580" y="126" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">Waveform</text>
  <text x="580" y="144" font-size="11.5" fill="var(--dim)" text-anchor="middle">20 to 50 times the cost</text>
  <rect x="440" y="156" width="280" height="196" rx="10" fill="url(#wg)" stroke="var(--good)" stroke-opacity=".5"/>
  <rect x="462" y="176" width="236" height="38" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="580" y="200" font-size="12" fill="var(--ink)" text-anchor="middle">IQ samples, chirp by chirp</text>
  <rect x="462" y="222" width="236" height="38" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="580" y="246" font-size="12" fill="var(--ink)" text-anchor="middle">overlaps summed coherently</text>
  <rect x="462" y="268" width="236" height="42" rx="6" fill="var(--card)" stroke="var(--good)" stroke-dasharray="4 3"/>
  <text x="580" y="288" font-size="12" fill="var(--ink)" text-anchor="middle">the real receive chain</text>
  <text x="580" y="304" font-size="10.5" fill="var(--dim)" text-anchor="middle">preamble, header, FEC, CRC</text>
  <text x="580" y="334" font-size="11.5" font-weight="600" fill="var(--ink)" text-anchor="middle">capture emerges, it is not a rule</text>

  <text x="380" y="378" font-size="11.5" fill="var(--dim)" text-anchor="middle">The channel never decides anything in either mode. It produces a signal; what reads it differs.</text>
</svg>
<figcaption>Both modes price the same path. They differ only in what happens
at the receiver: arithmetic against a floor, or a demodulator given samples.</figcaption>
</figure>

## Which to use

**Calculated** is the default and the right choice for anything large — a
national network, a coverage raster, a sweep across seeds. It is the mode most
questions should be asked in.

**Waveform** answers what arithmetic cannot: whether two overlapping
transmissions capture or collide, what a partial overlap actually costs, and
what a receiver would hear if you attached an SDR to it.

| | Calculated | Waveform |
|---|---|---|
| verdict from | link-budget SNR | a decoded frame |
| concurrent transmissions | summed into the noise, in dBm | summed coherently, as samples |
| capture effect | none | emerges from the physics |
| partial overlap | counted as full-length interference | costs what it actually costs |
| cost, 300-node burst | 46 ms | 1.0 to 2.3 s |

## What calculated gets wrong, and in which direction

Two known biases, and they pull opposite ways:

- **Any overlap counts as full-length interference**, however briefly it clipped
  the packet. Pessimistic under partial collisions.
- **There is no capture.** A strong signal is destroyed by a weak overlap that a
  real chip would ignore.

Measured against waveform mode on a dense 60-node burst with six simultaneous
senders: roughly **half the collision-affected pairs decode under the waveform
that calculated calls lost**. In a contended scenario, calculated understates
delivery.

That is a reason to compare two runs in the same mode rather than to distrust
the mode. It is also why the mode is stamped into every saved run — two runs
under different models are not comparable.

## Switching

Configuration → **RF Simulation**, or the `rf.mode` verb. It applies on a
whole-transmission boundary, so a run can be switched while it plays without
cutting a frame in half. The status bar names the active mode.

## Where to go next

- [The RF chain](rf-chain.html) — the physics both modes share: path loss,
  terrain, summation, noise.
- [The waveform](waveform.html) — the sample-accurate path in full, including
  the SDR observer and the carrier-sense detector.
- [What it does not do](what-it-does-not-do.html) — the error budget for each
  mode.
