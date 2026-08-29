# Settings

Everything that changes what a run does, grouped by what it affects.

![The Configuration window's overview: scope, links, randomness, and the run profile](images/settings-overview.png)

## Radio presets

A preset is an agreed set of LoRa parameters for a territory, taken from the
MeshCore community's own list. It is baked in rather than fetched, so the
workbench works offline and a saved scenario keeps the table it was built with.

| preset | MHz | kHz | SF | CR |
|---|---|---|---|---|
| Australia | 915.8 | 250 | 10 | 4/5 |
| Australia (Narrow) | 916.575 | 62.5 | 7 | 4/8 |
| Australia (Mid) | 915.075 | 125 | 9 | 4/5 |
| Australia: SA, WA | 923.125 | 62.5 | 8 | 4/8 |
| Australia: QLD | 923.125 | 62.5 | 8 | 4/5 |
| Brazil | 923.125 | 62.5 | 8 | 4/8 |
| **EU/UK (Narrow)** | 869.618 | 62.5 | 8 | 4/8 |
| EU/UK (Deprecated) | 869.525 | 250 | 11 | 4/5 |
| Czech Republic (Narrow) | 869.432 | 62.5 | 7 | 4/5 |
| EU 433MHz (Long Range) | 433.65 | 250 | 11 | 4/5 |
| EU 433MHz (Narrow) | 433.65 | 62.5 | 8 | 4/8 |
| Netherlands | 869.618 | 62.5 | 7 | 4/5 |
| New Zealand | 917.375 | 250 | 11 | 4/5 |
| New Zealand (Narrow) | 917.375 | 62.5 | 7 | 4/5 |
| Portugal 433 | 433.375 | 62.5 | 9 | 4/6 |
| Portugal 868 | 869.618 | 62.5 | 7 | 4/6 |
| Switzerland | 869.618 | 62.5 | 8 | 4/8 |
| USA/Canada (Recommended) | 910.525 | 62.5 | 7 | 4/5 |
| Vietnam (Narrow) | 920.25 | 62.5 | 8 | 4/5 |
| Vietnam (Deprecated) | 920.25 | 250 | 11 | 4/5 |

**EU/UK (Narrow) is the default.** Set one with `radio.preset`, or per node in
the Inspector.

Spreading factor is the dominant setting: each step up roughly doubles airtime
and buys about 2.5 dB of link budget. A network on SF11 is slower and reaches
further than the same network on SF8, and the two are not interoperable.

## Provisioning

What each node is told when its firmware starts. These are workbench settings
rather than firmware settings: they decide which CLI lines are issued at boot.

| setting | what it issues | default |
|---|---|---|
| set name to the node's name on the map | `set name <name>` | on |
| set the node's position | `set lat` / `set lon` | on |
| set the clock, the same on every node | `time <epoch>` | on |
| define a transport region from the study area | `region put` / `allowf` / `save` | off |
| and make it this node's default scope | `region default <name>` | off |
| cap advert hops | `set flood.max.advert <n>` | on, 32 |
| stagger node start times | spreads boot across a window | on |

**The clock comes from the scenario, not the host.** MeshCore timestamps
messages and judges freshness by them, so a mesh whose nodes disagree about the
time behaves differently. Taking it from the scenario keeps runs reproducible.

**Regions are off by default** because they change which packets a node relays,
and therefore change results. A node that already carries observed regions is
always configured with them regardless of this switch.

## Per node

| field | notes |
|---|---|
| kind | repeater, advanced repeater, companion, room server, SDR observer, emitter |
| position | latitude and longitude; uncertainty is carried from an import |
| height above ground | matters more than power on most links |
| transmit power | capped by the board profile; a scenario asking for more is reported |
| board | sets antenna gain, feedline loss, noise figure, battery and panel |
| radio | frequency, bandwidth, spreading factor, coding rate |
| firmware role and version | which application, and which build |
| regions and default scope | what it relays, and what it scopes its own traffic to |
| forward flood traffic for any region | `region allowf *`; more permissive than any real network |
| emitter duty | for interferers only: what share of the time it is keyed |

## Simulation

| setting | effect |
|---|---|
| seed | the run's randomness. Same seed, same scenario, same result |
| speed | how fast simulated time advances relative to the wall clock |
| step | the engine's tick, 10 ms by default |
| real firmware | whether nodes run MeshCore or inject traffic directly |
| excess path loss | a flat dB penalty, for calibrating against a known-bad reality |

## Experiments

| setting | effect |
|---|---|
| arms | what varies: firmware version, loop detection, path hash size, CAD mode |
| seeds | how many times each arm runs |
| senders | who originates; `spread` picks separated nodes rather than neighbours |
| scope | the transport scope the burst is sent on, written `#sco` |
| run for | simulated milliseconds per run |
| message size | payload bytes; 0 means a short label |

## Energy

Off by default, and **not fully implemented yet**: when on, a battery and
panel are sketched from the board profile, but the numbers have not been
validated against anything real. Do not use them for siting decisions.

## Automation

| setting | effect |
|---|---|
| let agents drive this workbench | opens the control socket at `$XDG_RUNTIME_DIR/meshbench.sock` |
| compute the link matrix in the background | keeps reachability current while editing |
| `MESHBENCH_CARTO_KEY` in the environment | unlocks the CARTO basemaps and makes the dark map the first-run default; without it they answer every tile with an API-key watermark |

The control socket is how every scripted run, the test runner and the MCP server
drive the application. See the [control socket reference](reference-control.html).
