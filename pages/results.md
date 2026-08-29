# Reading a result

A MeshBench result is a measurement made under stated conditions. This page is
what the numbers mean, and how far to trust them.

## Every event carries a cause

The event log records why, not just whether. A reception that failed says
what happened: below the demodulator floor, corrupted by overlap, the radio
was transmitting, nothing relayed it. The full cause table and the workflow
for chasing one packet are in
[Debugging packet delivery](debugging.html).

## Every result carries its provenance

The RF mode (calculated or waveform), the seed, the realism switches and the
fixture's strictness are stamped into every saved run, and the status bar
shows them while it plays. Two runs under different provenance are not
comparable, and the application will not quietly pretend they are.

## The one rule: kinder than the air

The model has no multipath, no body loss, no oscillator drift, and bare-earth
terrain unless buildings are loaded. Nearly every known bias makes simulated
links *better* than real ones, and that direction is what makes results
usable:

- **A link that fails in MeshBench fails in reality.** Believe the failure.
- **A link that works marginally may not survive the air.** Go and measure.
- **Absolute numbers are a best case.** Delivery counts, margins and coverage
  edges are upper bounds, not predictions.

[Accuracy and limits](what-it-does-not-do.html) is the full account, kept
current with the code.

## Comparisons survive what absolutes do not

Both arms of a comparison are flattered by the same biases, so the
*difference* between two runs is far more trustworthy than either run alone.
This is why the serious workflow is an [experiment](experiments.html): a
control arm, one changed variable, several seeds, and a delta read against
the control's own spread.

A single run of a single seed is one draw. Treat a difference found that way
as a hypothesis, not a finding.

## When to validate against hardware

- **Marginal links that matter.** If a plan depends on a link the model gives
  a few dB of margin, measure it on air before trusting it.
- **The model itself.** The **Validate** view fetches what a real network
  actually heard and compares it with the model's prediction, and can fit an
  excess-loss calibration from the residual.
- **The physics.** The waveform chain is held to real silicon by captured
  [golden vectors](golden-vectors.html): frames from a real SX1262, decoded
  end to end by MeshBench's receiver.
