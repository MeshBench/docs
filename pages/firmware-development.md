# Firmware development

The loop this page describes is the reason MeshBench exists in its current
shape: change MeshCore, and find out what your change does to a real network of
three hundred nodes before it reaches anybody's hardware.

![The firmware library](images/firmware-library-annotated.png)

## The loop, end to end

1. **Change the firmware.** Any local clone of MeshCore, on a branch. Nothing
   about MeshBench needs to know what you changed.
   ```
   cd ~/src/MeshCore
   git checkout -b fix/relay-suppression
   $EDITOR src/Dispatcher.cpp
   ```
2. **Build it for this machine.** MeshBench runs the firmware natively, so this
   is a host build rather than a board image.
   ```
   meshcore-native/build.sh simple_repeater ~/builds/my-arm
   ```
   The build produces `meshcore-simple_repeater-linux-amd64`.
3. **Hand it to MeshBench.** With the workbench running:
   ```
   msim firmware import ~/builds/my-arm/meshcore-simple_repeater-linux-amd64 \
     --role simple_repeater --version my-arm
   ```
   It appears in the firmware library immediately, labelled
   `simple_repeater my-arm (native)`.
4. **Assign it.** In the firmware library, find the row and press **`use for
   role`**. Every node of that role now runs your build. The button is scoped to
   the role because a companion asked to run a repeater build would be a
   different kind of node, not a different version.
5. **Run it against a control.** See [Experiments](experiments.html): two arms,
   one naming `my-arm` and one naming the release you forked from, the same
   seeds, the same network.
6. **Export the report.** `experiment.export` writes an HTML report with both
   arms side by side.

## From PlatformIO, in one keypress

If you build with PlatformIO, `tools/platformio/meshbench.py` removes steps 2
and 3 entirely. Add it to an environment:

```
extra_scripts = post:meshbench.py
```

After a successful build the image is handed to the running workbench over its
control socket. The environment name supplies the board and the role:

| environment | board | role |
|---|---|---|
| `Tbeam_SX1262_repeater` | Tbeam_SX1262 | simple_repeater |
| `Heltec_v3_companion_radio_usb` | Heltec_v3 | companion_radio |

The build is named after the git branch it came from, so two local builds appear
separately in the library rather than overwriting each other. If the workbench
is not running the hand-over is skipped and the build still succeeds: a build
should not fail because a simulator is closed.

## Three things that quietly ruin a comparison

These are not hypothetical. Each one has produced a confidently wrong answer
here, and each one fails silently in *both* arms, which is the worst way for a
comparison to fail.

### Saved node state beats a compiled default

A node keeps its preferences between runs, exactly as hardware does. A node that
has run before loads its old value at boot and never reaches your changed
default. Both arms then return identical numbers and your change looks inert.

**Wipe between arms.** The firmware library has a `wipe every node's memory`
button; the verb is `firmware.wipe`. Identities regenerate from the run seed, so
a wipe costs nothing but the next boot.

### An arm needs every role, not just the one you changed

If you point MeshBench at a directory of builds, it needs one per role. A
network with companions or a room server fails to resolve otherwise, with an
error about firmware on 0 of N nodes. Copy the roles you did not change in from
the release cache so exactly one thing differs.

### Versions are per role

Upstream tags one role at a time, so `companion-v1.17.0` and `repeater-v1.17.0`
are different releases. Asking for a bare `v1.17.0` resolves nothing and reports
"no native builds published", which points at the release rather than at the
string that caused it.

## A worked example

The protocol study on this simulator used exactly this loop. One arm restored
`rx_delay_base` to 10.0 in `MyMesh::begin()`; the control was the same source
built from a second branch. On the 311-node Scotland and Ireland network:

| arm | transmissions | collisions | airtime |
|---|---|---|---|
| control, v1.17.0 | 159 | 1345 | 127.1 s |
| rx delay plus relay suppression | 106.7 | 1040 | 102.3 s |

Delivery was unchanged. The full reports are in the reports repository.

**Run the control twice.** Two builds of identical source must produce identical
numbers. If they do not, nothing else you measure that day means anything, and
the cheapest way to find that out is a second control arm rather than a
surprising result three hours later.
