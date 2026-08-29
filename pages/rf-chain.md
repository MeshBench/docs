# The RF chain

This is the physics both reception models share. Which model reads the result - 
a link budget, or a real demodulator over synthesised samples - is
[RF simulation](rf-simulation.html).

What happens to a packet between one node's antenna and another's, in the order
it happens.

<figure>
<svg viewBox="0 0 780 320" role="img" aria-label="The six stages between one antenna and another">
  <defs><marker id="rc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="var(--accent-mark)"/></marker></defs>
  <rect x="12" y="30" width="228" height="86" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="126" y="54" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">1 · Modulation</text>
  <text x="126" y="74" font-size="10.5" fill="var(--dim)" text-anchor="middle">bytes become chirps; airtime is</text>
  <text x="126" y="90" font-size="10.5" fill="var(--dim)" text-anchor="middle">the firmware&#8217;s own getEstAirtimeFor()</text>
  <rect x="276" y="30" width="228" height="86" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="390" y="54" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">2 · Delay</text>
  <text x="390" y="74" font-size="10.5" fill="var(--dim)" text-anchor="middle">distance over c - the difference</text>
  <text x="390" y="90" font-size="10.5" fill="var(--dim)" text-anchor="middle">between aligned and half-symbol overlap</text>
  <rect x="540" y="30" width="228" height="86" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="654" y="54" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">3 · Path loss</text>
  <text x="654" y="74" font-size="10.5" fill="var(--dim)" text-anchor="middle">free space, terrain, diffraction,</text>
  <text x="654" y="90" font-size="10.5" fill="var(--dim)" text-anchor="middle">antenna gain in the true direction</text>
  <path d="M240 73 H272" stroke="var(--accent-mark)" stroke-width="2" fill="none" marker-end="url(#rc)"/>
  <path d="M504 73 H536" stroke="var(--accent-mark)" stroke-width="2" fill="none" marker-end="url(#rc)"/>
  <path d="M654 116 V150" stroke="var(--accent-mark)" stroke-width="2" fill="none" marker-end="url(#rc)"/>
  <rect x="540" y="154" width="228" height="86" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="654" y="178" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">4 · Summation</text>
  <text x="654" y="198" font-size="10.5" fill="var(--dim)" text-anchor="middle">every transmission in flight, summed</text>
  <text x="654" y="214" font-size="10.5" fill="var(--dim)" text-anchor="middle">as samples - no collision rule exists</text>
  <rect x="276" y="154" width="228" height="86" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="390" y="178" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">5 · Noise</text>
  <text x="390" y="198" font-size="10.5" fill="var(--dim)" text-anchor="middle">thermal, at the board&#8217;s noise figure,</text>
  <text x="390" y="214" font-size="10.5" fill="var(--dim)" text-anchor="middle">plus any emitter in the scenario</text>
  <rect x="12" y="154" width="228" height="86" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="126" y="178" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">6 · Demodulation</text>
  <text x="126" y="198" font-size="10.5" fill="var(--dim)" text-anchor="middle">de-chirp, FFT, error correction -</text>
  <text x="126" y="214" font-size="10.5" fill="var(--dim)" text-anchor="middle">it decodes, or the cause is recorded</text>
  <path d="M536 197 H508" stroke="var(--accent-mark)" stroke-width="2" fill="none" marker-end="url(#rc)"/>
  <path d="M272 197 H244" stroke="var(--accent-mark)" stroke-width="2" fill="none" marker-end="url(#rc)"/>
  <rect x="12" y="264" width="756" height="40" rx="8" fill="var(--sunk)" stroke="var(--rule)"/>
  <text x="390" y="289" font-size="11.5" fill="var(--dim)" text-anchor="middle">Capture effect emerges at stage 4: what survives an overlap is decided by the arithmetic at stage 6, not by a rule.</text>
</svg>
<figcaption>The chain both reception models share, in the order it happens.
Orange is the signal&#8217;s own path.</figcaption>
</figure>

## 1. Modulation

The bytes the firmware handed its radio are turned into complex baseband samples
using LoRa's chirp spread spectrum: a symbol is a chirp whose starting frequency
encodes the value, and the spreading factor sets how many samples that chirp
occupies.

**Airtime must agree with the firmware.** MeshCore computes its own estimate
with `getEstAirtimeFor()` and builds its CSMA timing on it. The simulator matches
that calculation rather than deriving its own, because a discrepancy makes the
two desynchronise silently.

## 2. Delay

Distance over the speed of light. At mesh distances this is tens of
microseconds, which sounds negligible and is not: it is the difference between
two transmissions overlapping symbol-aligned and overlapping half a symbol out,
and the demodulator treats those very differently.

## 3. Path loss and terrain

The link budget between two points, in both directions:

- free space loss at the carrier frequency
- terrain profile sampled from DEM tiles, cached permanently, with an offline
  mode that fails loudly rather than quietly returning flat earth
- diffraction over obstructions
- feedline loss and antenna gain, evaluated in the true direction to the far end

**Both directions, always.** A hilltop repeater with a big antenna and a
handheld with a rubber duck have an asymmetric link, and a result that reports
one number for "the link" is hiding half the answer.

## 4. Summation

Every transmission in flight is summed at the receiver's antenna, as complex
samples, with its own delay and its own attenuation.

This is the step that makes the simulator worth running. There is no rule about
collisions anywhere in the code. Two overlapping transmissions produce a sum, and
what the demodulator recovers from that sum depends on their relative power,
their relative timing, and their spreading factors. **Capture effect emerges**:
a strong signal is recovered despite a weak overlapping one, exactly as real
hardware does it.

## 5. Noise

Thermal noise at the receiver's noise figure, from the board profile. Plus any
emitters in the scenario, which is what an interferer node is.

## 6. Demodulation

De-chirp, FFT, pick the peak per symbol, then the LoRa forward error correction
at the configured coding rate. The packet either decodes or it does not, and if
it does not the engine records *why*: below the demodulator floor, corrupted by
overlap, radio was elsewhere, or the receiver was mid-transmission.

That distinction is the reason the event log records a cause rather than a
boolean. "It did not arrive" and "it arrived 3 dB under the floor" lead to
completely different fixes.

## What is missing, and which way it biases

The simulator is **kinder than the air**:

| absent | effect on results |
|---|---|
| multipath and fading | links look more stable than they are |
| body loss and orientation | handhelds look better than they are |
| oscillator error and drift | timing looks tighter than it is |
| interference from outside the scenario | the band looks quieter than it is |
| antenna pattern imperfection | siting looks more forgiving than it is |

The biases run almost entirely one way, which is what makes the output usable:
**treat every absolute number as a best case**. A link that fails here fails in
reality; a link that works here may not.

Comparisons are therefore worth more than single runs. Both arms of
an A/B are equally flattered, so the difference between them survives.
