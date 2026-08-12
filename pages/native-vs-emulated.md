# Native and emulated firmware

MeshBench runs the real MeshCore application on every node. There are two ways
it can do that, and choosing between them is the first decision in any piece of
work.

<figure>
<svg viewBox="0 0 760 330" role="img" aria-label="Native and emulated firmware compared">
  <defs>
    <linearGradient id="ng" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="var(--accent)" stop-opacity=".22"/>
      <stop offset="1" stop-color="var(--accent)" stop-opacity=".04"/>
    </linearGradient>
    <linearGradient id="eg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="var(--warn)" stop-opacity=".22"/>
      <stop offset="1" stop-color="var(--warn)" stop-opacity=".04"/>
    </linearGradient>
  </defs>

  <text x="180" y="20" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">Native</text>
  <text x="180" y="38" font-size="11.5" fill="var(--dim)" text-anchor="middle">MeshCore compiled for your computer</text>
  <rect x="40" y="50" width="280" height="230" rx="10" fill="url(#ng)" stroke="var(--accent)" stroke-opacity=".5"/>
  <rect x="62" y="70" width="236" height="40" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="180" y="95" font-size="12" fill="var(--ink)" text-anchor="middle">MeshCore application</text>
  <rect x="62" y="118" width="236" height="40" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="180" y="143" font-size="12" fill="var(--ink)" text-anchor="middle">MeshCore radio driver</text>
  <rect x="62" y="166" width="236" height="46" rx="6" fill="var(--card)" stroke="var(--accent)" stroke-dasharray="4 3"/>
  <text x="180" y="186" font-size="12" fill="var(--ink)" text-anchor="middle">radio shim, linked in</text>
  <text x="180" y="203" font-size="10.5" fill="var(--dim)" text-anchor="middle">in place of the SPI transport</text>
  <text x="180" y="238" font-size="11.5" fill="var(--ink)" text-anchor="middle" font-weight="600">deterministic - faster than real time</text>
  <text x="180" y="257" font-size="11" fill="var(--dim)" text-anchor="middle">a few MB and a fraction of a core per node</text>

  <text x="580" y="20" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">Emulated</text>
  <text x="580" y="38" font-size="11.5" fill="var(--dim)" text-anchor="middle">the published image for a real board</text>
  <rect x="440" y="50" width="280" height="230" rx="10" fill="url(#eg)" stroke="var(--warn)" stroke-opacity=".5"/>
  <rect x="462" y="70" width="236" height="40" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="580" y="95" font-size="12" fill="var(--ink)" text-anchor="middle">MeshCore application</text>
  <rect x="462" y="118" width="236" height="40" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="580" y="143" font-size="12" fill="var(--ink)" text-anchor="middle">MeshCore radio driver</text>
  <rect x="462" y="166" width="236" height="46" rx="6" fill="var(--card)" stroke="var(--warn)" stroke-dasharray="4 3"/>
  <text x="580" y="186" font-size="12" fill="var(--ink)" text-anchor="middle">emulated CPU, SPI and GPIO</text>
  <text x="580" y="203" font-size="10.5" fill="var(--dim)" text-anchor="middle">talking to a modelled SX1262</text>
  <text x="580" y="238" font-size="11.5" fill="var(--ink)" text-anchor="middle" font-weight="600">wall time - not reproducible</text>
  <text x="580" y="257" font-size="11" fill="var(--dim)" text-anchor="middle">about 150 MB and a core per node</text>

  <path d="M330 165 C 370 165, 390 165, 430 165" stroke="var(--rule)" stroke-width="2" fill="none"/>
  <text x="380" y="158" font-size="11" fill="var(--faint)" text-anchor="middle">same</text>
  <text x="380" y="300" font-size="11.5" fill="var(--dim)" text-anchor="middle">Both feed the same channel model, so a native node and an emulated one can share a mesh.</text>
</svg>
<figcaption>The application and its radio driver are identical in both. They
differ only in what sits under the driver: a linked shim, or a modelled chip
reached over an emulated SPI bus.</figcaption>
</figure>

## Which to use

| | native | emulated |
|---|---|---|
| what is compiled | MeshCore, for your computer | nothing; the released `.bin` runs as published |
| the radio | a shim linked where the SPI transport would be | an SX1262 model over an emulated SPI bus |
| speed | faster than real time on a small network | wall time, always |
| same seed, same result | yes | no |
| cost per node | a few MB, a fraction of a core | about 150 MB and a core |
| how many nodes | hundreds | eight, on a twelve core machine |
| answers | how does this change behave on a network | does this release work on this board |

**Use native for anything you intend to measure.** Comparisons, regression
gates, protocol studies, coverage questions. Repeatability is the point: the
same seed and the same scenario give the same answer, so a difference between
two runs is a difference between the two firmwares.

**Use emulation to check a release.** It runs the artefact people flash, on a
model of the chip they flash it to, so it answers whether that build comes up,
configures itself and puts a correctly formed packet on the air.

## Why emulation cannot be measured

An emulated node executes instructions at the emulator's pace, so simulated time
is tied to the wall clock. Two runs of the same seed interleave differently and
produce different numbers. That is a property of the approach, not a defect to
be tuned out.

It also has a hard ceiling. Each emulated node is a separate emulator process
running in real time. Beyond roughly eight on a twelve core machine, nothing
reports an error: boot times stretch, simulated time falls behind, and the
result looks like a mesh that has gone quiet.

## Mixing them

A scenario can hold both. A single emulated node in a native mesh is a common
and useful arrangement: the network around it is fast and repeatable, and the
node under test is the real image.

Firmware is assigned per role or per node, so making one node emulated is a
matter of giving it a board image while the rest keep a native build.
