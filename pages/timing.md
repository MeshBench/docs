# Time and determinism

MeshBench has two clocks, and every confusing result that is not about radio
turns out to be about which clock a number was measured in.

## Simulated time

The engine advances the world in fixed steps, 10 ms of simulated time per
tick. On each tick it runs every node's firmware, collects what they handed
their radios, places transmissions in flight with their true airtime, and
delivers the summed signal at every antenna. The
[engine loop](architecture.html#the-engine-loop) is the whole story.

Simulated time is the mesh's own time. A message that takes two seconds to
cross four hops takes two simulated seconds, because airtime is computed with
the firmware's own formula. How long that takes *you* depends on the machine:
a small native network runs faster than the wall clock, a large one slower,
and neither changes the result.

## Wall time

Timeouts, waits and your patience are wall time. The clients keep the two
apart deliberately: a run length is simulated time, a timeout is yours, and
nothing that means simulated time is ever called "timeout". Five simulated
minutes on a large network can be much more than five minutes of waiting.

## Determinism

**Same seed, same scenario, same result.** For native firmware this is exact:
the ledger of events is byte-identical between runs. It holds because nothing
in the pipeline draws from shared randomness:

- noise is counter-based, keyed by packet and receiver
- crystal offsets and echo geometry derive from node names by hash
- signal processing runs in parallel, bookkeeping stays serial
- iteration follows node order, never map order

Determinism is what makes [experiments](experiments.html) meaningful: run the
same seed under two firmwares and the difference is the firmware. It is also
what makes a failure shareable: a fixture and a seed reproduce the bug on
another machine.

## The exception: emulated firmware

An emulated node executes at the emulator's pace, so its timing is tied to
the wall clock, and two runs of one seed interleave differently. That is a
property of emulation, not a defect. Measure with
[native firmware](native-vs-emulated.html); use emulation to check that a
release boots and transmits.

An nRF52 board under Renode can be run in
[lockstep with the engine](emulation.html#lockstep-under-renode), which steps
its CPU and radio chip with the engine's clock. Console input still arrives on
the wall clock, so a run with an emulated node is reported as not reproducible
either way.

## Speed control

The toolbar's speed control scales how fast simulated time is chased. It
never changes what happens, only how long you wait to see it.

The control is how much simulated time each tick covers, shown beside it as
**ms/tick**. A tick is ten milliseconds of wall time, so 10 ms/tick is real time,
20 is twice as fast and 5 is half. The engine always steps in its own 10 ms,
whatever the setting, so nothing is skipped or coarsened: a larger setting just
runs more steps in each tick. Past what the machine can step in a tick the run
goes as fast as the machine allows, up to 1000 ms/tick. The status bar's
**realtime** figure is the measured answer, not the setting.

Native firmware reads the simulator's clock rather than the wall's, so it
cannot tell the difference. An emulated node can, and a mesh with one in it is
held near real time by the emulator whatever the setting.

![The Fife fixture at 1000 ms/tick: the status bar reads about fourteen times real time](images/speed-control-realtime.png)

From a script, `sim.speed {"step_ms": 1000}` sets the same control. Pausing freezes
the mesh mid-thought: an [SDR observer](sdr-observer.html) streams its bare
noise floor while paused, because frozen time cannot honestly produce signal.
