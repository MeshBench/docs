# Your first simulation

Fifteen minutes from an empty workbench to a real 378-node network relaying
real packets through real firmware. You will load a shipped snapshot of
ScotMesh, boot MeshCore on every node, and watch a message flood across
Scotland.

## Run it

1. **Load a shipped network.** **File**, then **Open a saved network**, and
   choose `fixture-fife-strict` for a quick start (58 nodes) or
   `fixture-scotland-ireland-strict` for the full map (378 nodes).
2. **Start the firmware.** **Simulation**, then **Start firmware on every
   node**. Each node launches a real MeshCore build and is told its name,
   position, clock and regions. Watch the count in the status bar reach the
   node total; the big fixture takes about a minute and 4 GB.
3. **Press play.** The transport control on the toolbar, or the space bar.
   Simulated time starts moving.
4. **Make something happen.** Open the **Schedule** panel, type `advert` with
   a node selected, and press **add send**. Watch the flood spread: the
   Events panel lists every transmission, reception and miss with a cause.

![The Run view playing: the schedule and scoreboard beside the map, firmware running](images/view-run.png)

> If the mesh looks dead, the usual cause is regions rather than radio. A
> repeater only forwards flood traffic for regions it has been told about, and
> reports no error when it declines. The `-strict` fixtures carry the real
> regions, so they relay. See [Shipped networks](fixtures.html).

## What you are looking at

- **The map** draws nodes coloured by kind, and links weighted by the weaker
  direction's margin. The layer key toggles links, coverage, terrain and more.
- **The Events panel** is the ground truth. Every reception and every failure
  carries a cause, which is the difference between "it did not arrive" and
  "it arrived 3 dB under the demodulator floor".
- **The status bar** carries the honesty line: results are a best case. That
  is a property of the model, explained in
  [Reading a result](results.html).
- **The clock** is simulated time, not wall time. On a small network it runs
  faster than your watch; nothing about the result changes either way. See
  [Time and determinism](timing.html).

## Where things are

The view switcher along the top is the main navigation. Each view is a saved
arrangement of panels for one kind of work:

![The menu bar, and the view switcher under it](images/crop-viewbar.png)

| view | for |
|---|---|
| **Plan** | build and site: import, place, drag, boundary, coverage |
| **Run** | exercise it and watch: play, schedule traffic, consoles, live feed |
| **Debug** | ask why one thing happened: packets, waterfall, consoles, budgets |
| **Validate** | check the model against what a real network heard |
| **Bench** | compare configurations: sweep a parameter, read what differed |
| **App** | write a client against it: an endpoint, the protocol, faults |

Panels can be dragged out, docked elsewhere, or popped into their own window
on a second monitor. Each view remembers its own arrangement.

## What to try next

- **Open a node's console.** Double-click any repeater and type `get name` on
  its Console tab. The reply is the firmware's own.
- **Break a link.** Drag a hilltop repeater into a valley and watch its links
  thin as the terrain model reprices every path.
- **Ask why a packet failed.** Pick a miss in the Events panel and follow
  [Debugging packet delivery](debugging.html).
- **Compare two settings.** When one run stops being enough,
  [run an experiment](experiments.html).
