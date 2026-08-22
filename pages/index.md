# MeshBench

An RF-accurate MeshCore network simulator. It runs **real MeshCore firmware**
against a modelled radio channel, so the question it answers is not "would a
packet get through" but "what actually arrived at the antenna, and why".

Reception is decided one of two ways. **Calculated** is the default: a link
budget against the demodulator's floor, fast enough for a national network.
**Waveform** synthesises the actual chirps and runs a real demodulator over
them, so capture and collision emerge from the physics rather than from a rule.
Both price the same path; see [RF simulation](rf-simulation.html).

One binary on your machine. No service to deploy, no account, nothing to
configure before the first run.

<figure>
<svg viewBox="0 0 780 340" role="img" aria-label="Who uses MeshBench, what it gives them, and which parts are real">
  <defs>
    <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="var(--dim)"/>
    </marker>
  </defs>

  <text x="86" y="18" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">You</text>

  <rect x="12" y="34" width="148" height="52" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="86" y="55" font-size="12" fill="var(--ink)" text-anchor="middle">Planning a network</text>
  <text x="86" y="72" font-size="10.5" fill="var(--faint)" text-anchor="middle">where does the next node go</text>

  <rect x="12" y="98" width="148" height="52" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="86" y="119" font-size="12" fill="var(--ink)" text-anchor="middle">Writing firmware</text>
  <text x="86" y="136" font-size="10.5" fill="var(--faint)" text-anchor="middle">did my branch relay more</text>

  <rect x="12" y="162" width="148" height="52" rx="8" fill="var(--card)" stroke="var(--rule)"/>
  <text x="86" y="183" font-size="12" fill="var(--ink)" text-anchor="middle">Writing an app</text>
  <text x="86" y="200" font-size="10.5" fill="var(--faint)" text-anchor="middle">how does it cope with a bad link</text>

  <path d="M164 60 H210" stroke="var(--dim)" fill="none" marker-end="url(#ar)"/>
  <path d="M164 124 H210" stroke="var(--dim)" fill="none" marker-end="url(#ar)"/>
  <path d="M164 188 H210" stroke="var(--dim)" fill="none" marker-end="url(#ar)"/>

  <rect x="214" y="26" width="196" height="196" rx="10" fill="var(--panel)" stroke="var(--accent)" stroke-opacity=".45"/>
  <text x="312" y="48" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">One binary</text>
  <rect x="234" y="60" width="156" height="34" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="312" y="81" font-size="11.5" fill="var(--ink)" text-anchor="middle">the workbench</text>
  <rect x="234" y="102" width="156" height="34" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="312" y="123" font-size="11.5" fill="var(--ink)" text-anchor="middle">the command line</text>
  <rect x="234" y="144" width="156" height="34" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="312" y="165" font-size="11.5" fill="var(--ink)" text-anchor="middle">meshtest, in your tests</text>
  <text x="312" y="202" font-size="10.5" fill="var(--faint)" text-anchor="middle">no service, no account,</text>
  <text x="312" y="215" font-size="10.5" fill="var(--faint)" text-anchor="middle">nothing to configure first</text>

  <path d="M414 124 H460" stroke="var(--dim)" fill="none" marker-end="url(#ar)"/>

  <rect x="464" y="26" width="300" height="196" rx="10" fill="none" stroke="var(--good)" stroke-dasharray="5 4"/>
  <text x="614" y="48" font-size="12.5" font-weight="600" fill="var(--good)" text-anchor="middle">Real, not modelled</text>

  <rect x="484" y="60" width="260" height="46" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="614" y="79" font-size="11.5" fill="var(--ink)" text-anchor="middle">MeshCore&#8217;s own firmware</text>
  <text x="614" y="95" font-size="10.5" fill="var(--faint)" text-anchor="middle">routing, flood suppression, CSMA timing</text>

  <rect x="484" y="114" width="260" height="46" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="614" y="133" font-size="11.5" fill="var(--ink)" text-anchor="middle">a sample-accurate LoRa channel</text>
  <text x="614" y="149" font-size="10.5" fill="var(--faint)" text-anchor="middle">waveforms summed, noise added</text>

  <rect x="484" y="168" width="260" height="40" rx="6" fill="var(--card)" stroke="var(--rule)"/>
  <text x="614" y="185" font-size="11.5" fill="var(--ink)" text-anchor="middle">real terrain</text>
  <text x="614" y="200" font-size="10.5" fill="var(--faint)" text-anchor="middle">and, if you load them, buildings</text>

  <rect x="12" y="248" width="752" height="72" rx="8" fill="var(--sunk)" stroke="var(--rule)"/>
  <text x="32" y="272" font-size="12" font-weight="600" fill="var(--ink)">The channel decides nothing.</text>
  <text x="32" y="292" font-size="11.5" fill="var(--dim)">It sums waveforms, applies path loss and adds noise. Whether a packet decodes is the demodulator&#8217;s business,</text>
  <text x="32" y="308" font-size="11.5" fill="var(--dim)">so capture effect and partial collisions emerge from the physics instead of from a rule somebody wrote down.</text>
</svg>
<figcaption>Three questions, one binary, and the parts that are not a model of the
thing but the thing itself.</figcaption>
</figure>

## What it is for

- **Network operators.** Will this repeater help? What does the mesh look like
  if that site goes down? Import a real network from CoreScope and ask.
- **Firmware developers.** Does my branch relay more or less than `dev`? Build
  it, hand it to MeshBench, run both against the same 311-node network, and
  read the difference.
- **Application developers.** Point your client at a simulated mesh over TCP or
  a virtual serial port, and break it on purpose to see how your app copes.

## Start here

| if you want to | read |
|---|---|
| run it for the first time | [Getting started](getting-started.html) |
| use a ready-made network | [Shipped networks](fixtures.html) |
| bring in a real network | [Importing a network](importing.html) |
| find out why a packet failed | [Why a packet failed](debugging.html) |
| test a firmware change | [Firmware development](firmware-development.html) |
| write a client against it | [App development](app-development.html) |
| test your own firmware or app | [Testing your own code](testing.html) |
| compare two configurations | [Experiments](experiments.html) |
| drive it from a script | [Control socket](reference-control.html) |
| know how it works inside | [Architecture](architecture.html) |
| understand how reception is decided | [RF simulation](rf-simulation.html) |
| know what the build refuses | [What the build enforces](quality-gates.html) |

## What it does not do

The simulator is **kinder than the air**. There is no multipath, no body loss,
no oscillator drift. The measured biases nearly all run one way, which is what
makes a result usable: treat every absolute number as a best case, and trust the
*comparison* between two runs far more than either run alone.

It is a desktop application, not a web service. "On the GPU" always means the
GPU in the machine running it, and every GPU path has a CPU path that produces
the same answer more slowly.
