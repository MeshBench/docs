# Studies

A study is a question about the protocol, answered by changing MeshCore, running
both versions against the same real network, and publishing what came out
including the parts that did not work.

They live in the [meshbench-reports](https://github.com/MeshBench/meshbench-reports)
repository, one directory per report, each a self-contained page.

## How one is run here

1. **Read the firmware at a pinned tag** and take the ideas from the code. An
   idea that cannot point at a line is a guess.
2. **Pre-register**: mechanism, hypothesis, the metric that would show it, and
   the cost it adds, written down *before* running anything, so a result cannot
   be fished out of twelve columns afterwards.
3. **One local branch per idea** on a local MeshCore clone. Nothing is pushed.
4. **Build each arm** with `meshcore-native/build.sh`, and copy in the roles the
   arm does not change so exactly one thing differs.
5. **Import each build into MeshBench** and run it against a control in the same
   sweep, on the same network and the same seeds.
6. **Export the report** and write it up against what was predicted.

## The control arm is the whole game

Two arms the firmware guarantees are identical are a free reproducibility check.
Build the same source from two branches, label them differently, run both.

In the eight-idea series the control produced **573 transmissions and 4,830
receptions in every single sweep**, across seven separate sweeps run over three
hours. That is what makes each arm's difference attributable to the firmware.
Had it wandered, the honest thing would have been to stop and say so rather than
publish seven deltas measured against a moving baseline.

## What gets published

Everything that was run, not everything that worked. A change that made the
network worse is a result; a change that did nothing is a result, and usually a
more interesting one, because it says the mechanism you believed in is not
reachable in the shipped configuration.

Three of the eight ideas in the first series changed nothing measurable, and one
of those three turned out to be dead code in the shipped default rather than a
bad idea.

## Reading one honestly

- A delta smaller than the control's own spread is not a finding.
- A delta in one metric with no story in the others deserves suspicion.
- Absolute numbers are a best case, because [the model is kinder than the
  air](what-it-does-not-do.html). The comparison survives that; the absolute value does not.
