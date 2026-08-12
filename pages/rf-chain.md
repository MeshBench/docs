# The RF chain

What happens to a packet between one node's antenna and another's, in the order
it happens.

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

This is also why comparisons are worth far more than single runs. Both arms of
an A/B are equally flattered, so the difference between them survives.
