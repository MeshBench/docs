# Known limits

Kept honest deliberately. A simulator whose shortcomings are undocumented is a
simulator whose results cannot be trusted, and the ones below are the reason a
comparison is worth more than a single number.

## The model is kinder than the air

| absent | which way it biases |
|---|---|
| multipath and fading | links look more stable |
| body loss and orientation | handhelds look better |
| oscillator error and drift | timing looks tighter |
| interference from outside the scenario | the band looks quieter |
| antenna pattern imperfection | siting looks more forgiving |

The biases run almost entirely one way. **Treat every absolute number as a best
case.** A link that fails here fails in reality; a link that works here may not.

## Measurement floors depend on the metric

The often-quoted ±20% is the spread of **reach under contention from around
eight simultaneous senders**, measured by running one configuration repeatedly.
It is a property of that contention, not of the simulator, and it does not
transfer to every measurement.

A one-originator flood on a 58-node network has produced an identical
transmission count across eight seeds, while receptions on the very same runs
varied by ±17%. Measure the control's own spread on the metric you care about,
and quote that.

## Emulation is not deterministic

Emulated nodes run at the speed of the emulator, so simulated time is pinned to
the wall clock. Two runs of one seed do not agree. Every CI gate and every study
arm is native for this reason.

Beyond about eight emulated nodes on a twelve-core machine, nothing reports an
error: boots stretch, simulated time falls behind, and the symptom is a mesh
gone quiet, which is exactly what a genuine RF problem looks like.

## Things that fail silently

Each of these has produced a confident wrong answer here at least once.

**Regions that were inferred and never applied.** Every node transmits, no node
relays, and nothing reports an error. It reads as a mesh with no propagation.

**A scope written without its `#`.** The key on the wire is `sha256("#sco")`;
`sha256("sco")` matches no repeater in existence. Every repeater receives the
packet, derives a different key, and declines to forward. No error anywhere.

**Saved node state overriding a compiled default.** Both arms of a comparison
return identical numbers and the change looks inert.

**A bare version tag.** MeshCore tags one role at a time, so `v1.17.0` resolves
nothing while `repeater-v1.17.0` resolves.

**A permissive fixture.** More generous than the real network. It says so on
screen and in the test runner's first line of output, every time, because a
quiet one would produce exactly the flattering-but-wrong answer this simulator
exists to avoid.

## Currently unproven

**Whether the permissive fixtures relay more than the strict ones.** The
firmware accepts `region allowf *` and answers OK, but a controlled run gave the
same answer twice. Either the wildcard needs `region put *` first, or the
experiment could not see the difference. Until that is settled, treat
`-permissive` as declared rather than demonstrated.

## Not built yet

- macOS and Windows builds. See [Getting started](getting-started.html) for what
  each is blocked on.
- Emulator releases for the two forks, without which a bundle ships the
  application alone.
- Offered-load and per-region airtime metrics in the study harness, which is
  what two of the eight protocol ideas need before they can be measured at all.
