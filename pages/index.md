# MeshBench

An RF-accurate MeshCore network simulator. It runs **real MeshCore firmware**
against a **sample-accurate LoRa baseband channel** with real noise, so the
question it answers is not "would a packet get through" but "what actually
arrived at the antenna, and why".

One binary on your machine. No service to deploy, no account, nothing to
configure before the first run.

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
| test a firmware change | [Firmware development](firmware-development.html) |
| write a client against it | [Companion bench](companion-bench.html) |
| use a ready-made network | [Shipped networks](fixtures.html) |
| compare two configurations | [Experiments](experiments.html) |
| drive it from a script | [Control socket](reference-control.html) |
| know how it works inside | [Architecture](architecture.html) |

## What it does not do

The simulator is **kinder than the air**. There is no multipath, no body loss,
no oscillator drift. The measured biases nearly all run one way, which is what
makes a result usable: treat every absolute number as a best case, and trust the
*comparison* between two runs far more than either run alone.

It is a desktop application, not a web service. "On the GPU" always means the
GPU in the machine running it, and every GPU path has a CPU path that produces
the same answer more slowly.
