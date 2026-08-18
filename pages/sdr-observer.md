# Listening with SDR++

An SDR observer is a node that transmits nothing and runs no firmware: it is
an antenna on the map, and its window can serve that antenna to real SDR
software over the `rtl_tcp` protocol. SDR++'s stock client connects to it as
if it were a dongle, and what it draws is the simulation's actual air — the
same summed IQ the verdicts are judged from, never a picture generated from
packet events. If two transmissions collide, the waterfall shows the
collision because the samples contain it, and for no other reason.

<svg viewBox="0 0 760 200" role="img" aria-label="The observer serving SDR++">
  <rect x="14" y="52" width="200" height="92" rx="10" fill="var(--panel)" stroke="var(--accent)"/>
  <text x="114" y="78" font-size="12.5" fill="var(--ink)" text-anchor="middle" font-weight="600">SDR observer</text>
  <text x="114" y="96" font-size="10.5" fill="var(--dim)" text-anchor="middle">a node on the map</text>
  <text x="114" y="112" font-size="10.5" fill="var(--dim)" text-anchor="middle">transmits nothing, hears everything</text>
  <text x="114" y="128" font-size="10.5" fill="var(--dim)" text-anchor="middle">drag it and the physics follows</text>
  <path d="M218 98 L 288 98" stroke="var(--accent)" stroke-width="2"/>
  <text x="253" y="88" font-size="10" fill="var(--dim)" text-anchor="middle">shared synthesis</text>
  <rect x="292" y="52" width="200" height="92" rx="10" fill="var(--panel)" stroke="var(--line)"/>
  <text x="392" y="78" font-size="12.5" fill="var(--ink)" text-anchor="middle" font-weight="600">rtl_tcp server</text>
  <text x="392" y="96" font-size="10.5" fill="var(--dim)" text-anchor="middle">RTL0 header, 8-bit IQ</text>
  <text x="392" y="112" font-size="10.5" fill="var(--dim)" text-anchor="middle">follows the client's rate menu</text>
  <text x="392" y="128" font-size="10.5" fill="var(--dim)" text-anchor="middle">one client, like the real one</text>
  <path d="M496 98 L 566 98" stroke="var(--accent)" stroke-width="2"/>
  <text x="531" y="88" font-size="10" fill="var(--dim)" text-anchor="middle">TCP</text>
  <rect x="570" y="52" width="176" height="92" rx="10" fill="var(--panel)" stroke="var(--good)"/>
  <text x="658" y="78" font-size="12.5" fill="var(--ink)" text-anchor="middle" font-weight="600">SDR++</text>
  <text x="658" y="96" font-size="10.5" fill="var(--dim)" text-anchor="middle">stock RTL-TCP source</text>
  <text x="658" y="112" font-size="10.5" fill="var(--good)" text-anchor="middle">the simulated spectrum,</text>
  <text x="658" y="128" font-size="10.5" fill="var(--good)" text-anchor="middle">live</text>
  <text x="380" y="180" font-size="11" fill="var(--dim)" text-anchor="middle">Nothing on this path reads packet metadata: a collision is on the screen because the summed air contains it.</text>
</svg>

## Serving the antenna

1. Place an SDR observer on the map, or import a scenario that has one. Any
   position works, and its height and antenna matter exactly as much as any
   other node's.
2. Open its node window. An observer's window is its own: no console and no
   Radio tab — it runs no firmware and has no chip to read — but an **SDR**
   pane in front.
3. Press **serve rtl_tcp**. The pane shows the address and port the server
   picked, and a status line that flips to "client connected" when something
   is on the other end.

The same serve/stop control sits in the window's head, and the verb behind
both is `sdr.serve` with `sdr.stop`, so a script can do it too.

## Connecting SDR++

In SDR++, choose the **RTL-TCP** source and give it the address and port
from the observer's window. Then:

- **Sample rate**: any rate in the menu works — the server resamples its
  stream to whatever the client asks for. 250 kHz is the sensible choice:
  the lowest offered, the lightest to draw, and the tightest view of a LoRa
  channel.
- **Tuned frequency**: tune to the observer's centre frequency so the axis
  labels are truthful. The server streams the observer's channel wherever
  the client tunes; the frequency command is recorded, not obeyed, because
  a simulated observer has exactly one channel to give.
- **Direct Sampling** disabled, **Offset Tuning** off, **RTL AGC** and
  **Tuner AGC** off. **Gain** is accepted and ignored — there is no front
  end to drive.
- **IQ Correction** off. It exists to fight a real tuner's DC spike and
  image imbalance; pointed at mathematically clean synthetic IQ it slowly
  invents a correction for a fault that is not there.
- To look at LoRa bursts, **RAW** mode with the bandwidth set to the
  channel (62500 for the UK/EU narrow preset) beats any demodulator mode —
  there is no FM here for WFM to find.

Start the simulation playing, and transmissions appear as chirp bursts at
the channel's width. Drag the observer across the map while it serves: the
engine forgets its cached path losses on the spot, and the next window
prices the new geometry — walking an observer away from a transmitter sinks
it into the noise floor in real time.

## What the stream honestly is

- **Simulated time, continuously.** The stream position only moves forward.
  If the simulation runs slower than the wall — a heavy waveform judgement,
  a busy machine — the stream waits for it rather than rewinding or
  repeating windows; a client sees a slower waterfall, never a striped one.
  If the simulation runs much faster than real time, the stream jumps
  forward rather than falling minutes behind, exactly as a real dongle
  drops samples on overflow.
- **A paused run streams its noise floor.** Frozen time cannot honestly
  produce signal, so a paused observer serves fresh noise-floor windows at
  the pause point until the run moves again.
- **8-bit IQ**, as the rtl_tcp format demands: about 48 dB of visible
  dynamic range, the same ceiling a real RTL-SDR has.
- **One channel, honestly.** The stream is band-limited interpolation from
  the observer's native rate (one sample per hertz of bandwidth) up to the
  client's rate, so a transmission is exactly as wide as its bandwidth and
  the span either side of the channel is silent - the observer hears one
  channel, and the resampler does not invent air around it.
- **One client at a time**, exactly as the real `rtl_tcp` behaves — a
  second connection is refused rather than fed interleaved samples.

This is the same instrument the golden-vector experiment used from the
other side: there a real dongle fed captured air into MeshBench's receiver;
here MeshBench feeds simulated air into a real client. Both directions
exist so neither half of the chain has to be taken on trust.
