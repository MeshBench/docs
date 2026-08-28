# Validated on the air

How MeshBench's LoRa coding chain was checked against a real SX1262 — not
against a paper, not against another simulator, but against what an actual
chip put on the air. This is the experiment behind the golden vectors in
`internal/rf/lora/testdata/`, run on 18 August 2026, and the method is
repeatable whenever the chain changes.

The problem it solves: the LoRa PHY's bit-level details — the sync word, the
parity equations, the whitening sequence, the CRC — are not published by
Semtech. Everything anyone implements comes from reverse-engineering
literature, and the implementations in the wild disagree with each other on
several of them. A simulator that is merely *self-consistent* decodes its
own transmissions perfectly and proves nothing. The only referee is silicon.

## The rig

Two pieces of ordinary MeshCore hardware, neither modified:

- **A KISS modem** — MeshCore's own `kiss_modem` firmware on an SX1262
  board, plugged into the dev machine over USB. Its SetHardware extensions
  let MeshBench set the radio (frequency, bandwidth, SF, coding rate) and
  transmit an arbitrary raw payload, and it reports `TxDone` when the frame
  has left the antenna.
- **An RTL-SDR on a mast**, about ten metres away, exposed over the network
  as a standard `rtl_tcp` server. Its antenna is not even tuned for
  868 MHz; at ten metres that does not matter.

A repeater that normally lives next to the mast was put in monitor-only
mode for the runs, so the test frames would not be relayed back over
themselves.

<svg viewBox="0 0 760 240" role="img" aria-label="The golden-vector rig">
  <rect x="14" y="58" width="170" height="96" rx="10" fill="var(--panel)" stroke="var(--accent)"/>
  <text x="99" y="84" font-size="12.5" fill="var(--ink)" text-anchor="middle" font-weight="600">KISS modem</text>
  <text x="99" y="102" font-size="10.5" fill="var(--dim)" text-anchor="middle">SX1262, MeshCore firmware</text>
  <text x="99" y="118" font-size="10.5" fill="var(--dim)" text-anchor="middle">known payload, known radio</text>
  <text x="99" y="134" font-size="10.5" fill="var(--dim)" text-anchor="middle">USB serial, KISS framing</text>
  <path d="M196 92 q 24 -26 48 0 q 24 26 48 0" stroke="var(--accent)" stroke-width="1.8" fill="none" opacity=".85"/>
  <path d="M204 116 q 20 -20 40 0 q 20 20 40 0" stroke="var(--accent)" stroke-width="1.4" fill="none" opacity=".5"/>
  <text x="244" y="70" font-size="10" fill="var(--dim)" text-anchor="middle">869.618&#8201;MHz, ~10&#8201;m</text>
  <rect x="306" y="58" width="150" height="96" rx="10" fill="var(--panel)" stroke="var(--line)"/>
  <text x="381" y="84" font-size="12.5" fill="var(--ink)" text-anchor="middle" font-weight="600">RTL-SDR on a mast</text>
  <text x="381" y="102" font-size="10.5" fill="var(--dim)" text-anchor="middle">rtl_tcp over the network</text>
  <text x="381" y="118" font-size="10.5" fill="var(--dim)" text-anchor="middle">1&#8201;MS/s raw 8-bit IQ</text>
  <text x="381" y="134" font-size="10.5" fill="var(--dim)" text-anchor="middle">offset-tuned &#8722;150&#8201;kHz</text>
  <path d="M460 106 L 516 106" stroke="var(--accent)" stroke-width="2"/>
  <text x="488" y="98" font-size="10" fill="var(--dim)" text-anchor="middle">TCP</text>
  <rect x="520" y="42" width="226" height="128" rx="10" fill="var(--panel)" stroke="var(--good)"/>
  <text x="633" y="68" font-size="12.5" fill="var(--ink)" text-anchor="middle" font-weight="600">tools/goldencap</text>
  <text x="633" y="88" font-size="10.5" fill="var(--dim)" text-anchor="middle">channelize to one sample per chip</text>
  <text x="633" y="104" font-size="10.5" fill="var(--dim)" text-anchor="middle">MeshBench's own receiver front end</text>
  <text x="633" y="120" font-size="10.5" fill="var(--dim)" text-anchor="middle">demodulate every symbol</text>
  <text x="633" y="140" font-size="11" fill="var(--good)" text-anchor="middle" font-weight="600">diff against internal/rf/lora's encoding</text>
  <text x="381" y="206" font-size="11.5" fill="var(--dim)" text-anchor="middle">The command path and the capture path never touch: what arrives is judged only by the air.</text>
</svg>

## The method

One run is one commanded transmission:

1. `goldencap` programs the modem's radio — the UK/EU narrow preset,
   869.618 MHz, 62.5 kHz, SF8, CR 4/8 — and confirms the settings took by
   reading them back.
2. It opens the `rtl_tcp` stream, tuned 150 kHz below the channel so the
   dongle's DC spike stays out of the signal, and starts buffering IQ.
3. It transmits a known payload and waits for the modem's `TxDone`.
4. It finds the burst in the capture, mixes it to baseband, decimates to one
   sample per chip — the rate every piece of MeshBench's DSP speaks — and
   runs the simulator's own receiver over it: preamble search, SFD lock,
   CFO correction, per-symbol FFT.
5. Every demodulated symbol is compared against what `internal/rf/lora` says
   that payload should encode to. Any difference is a place where the
   simulator and the chip disagree about LoRa itself.

The receiver being MeshBench's own is the point. The experiment does not ask
"can something decode this" — it asks whether *MeshBench's* transmit chain and *MeshBench's*
receive chain, pointed at real silicon, agree with it bit for bit.

## What the air showed

The first capture's raw structure, read window by window off the dechirped
spectrum, confirmed the frame's shape exactly as modelled — and corrected
one value:

<svg viewBox="0 0 760 168" role="img" aria-label="The captured frame's structure">
  <rect x="14" y="46" width="238" height="52" rx="6" fill="var(--panel)" stroke="var(--line)"/>
  <text x="133" y="68" font-size="11.5" fill="var(--ink)" text-anchor="middle">32 preamble upchirps</text>
  <text x="133" y="86" font-size="10" fill="var(--dim)" text-anchor="middle">constant bin, exactly MeshCore's length</text>
  <rect x="256" y="46" width="120" height="52" rx="6" fill="var(--panel)" stroke="var(--warn)"/>
  <text x="316" y="68" font-size="11.5" fill="var(--ink)" text-anchor="middle">sync word</text>
  <text x="316" y="86" font-size="10" fill="var(--warn)" text-anchor="middle">shifts +8, +16</text>
  <rect x="380" y="46" width="120" height="52" rx="6" fill="var(--panel)" stroke="var(--line)"/>
  <text x="440" y="68" font-size="11.5" fill="var(--ink)" text-anchor="middle">2.25 downchirps</text>
  <text x="440" y="86" font-size="10" fill="var(--dim)" text-anchor="middle">the SFD, as modelled</text>
  <rect x="504" y="46" width="242" height="52" rx="6" fill="var(--panel)" stroke="var(--line)"/>
  <text x="625" y="68" font-size="11.5" fill="var(--ink)" text-anchor="middle">data symbols</text>
  <text x="625" y="86" font-size="10" fill="var(--dim)" text-anchor="middle">header block at SF&#8722;2, then payload blocks</text>
  <text x="316" y="128" font-size="10.5" fill="var(--warn)" text-anchor="middle">nibble &#215; 8, whatever the SF &#8212;</text>
  <text x="316" y="143" font-size="10.5" fill="var(--warn)" text-anchor="middle">not the SF-scaled value the literature suggested</text>
</svg>

Then the symbol diff did something better than pass or fail: it *localised*
the disagreement. Within every eight-symbol interleaver block, the first
four symbols matched the simulator exactly and the last four did not. In
LoRa's diagonal interleaver, the first four columns carry the data bits of
every codeword and the last four carry the parity bits — so the diff itself
said: whitening, Gray coding, the interleaver and the header layout are all
exactly right, and only the parity equations are wrong.

<svg viewBox="0 0 760 190" role="img" aria-label="The diff localises the disagreement to the parity columns">
  <text x="14" y="30" font-size="11.5" fill="var(--dim)">one interleaver block, eight symbols:</text>
  <rect x="14" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--good)"/>
  <rect x="106" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--good)"/>
  <rect x="198" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--good)"/>
  <rect x="290" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--good)"/>
  <rect x="382" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--warn)" stroke-dasharray="5 4"/>
  <rect x="474" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--warn)" stroke-dasharray="5 4"/>
  <rect x="566" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--warn)" stroke-dasharray="5 4"/>
  <rect x="658" y="46" width="88" height="44" rx="5" fill="var(--panel)" stroke="var(--warn)" stroke-dasharray="5 4"/>
  <text x="58" y="72" font-size="11" fill="var(--good)" text-anchor="middle">match</text>
  <text x="150" y="72" font-size="11" fill="var(--good)" text-anchor="middle">match</text>
  <text x="242" y="72" font-size="11" fill="var(--good)" text-anchor="middle">match</text>
  <text x="334" y="72" font-size="11" fill="var(--good)" text-anchor="middle">match</text>
  <text x="426" y="72" font-size="11" fill="var(--warn)" text-anchor="middle">differ</text>
  <text x="518" y="72" font-size="11" fill="var(--warn)" text-anchor="middle">differ</text>
  <text x="610" y="72" font-size="11" fill="var(--warn)" text-anchor="middle">differ</text>
  <text x="702" y="72" font-size="11" fill="var(--warn)" text-anchor="middle">differ</text>
  <text x="196" y="118" font-size="10.5" fill="var(--dim)" text-anchor="middle">columns 0&#8211;3: the data bits of every codeword</text>
  <text x="196" y="134" font-size="10.5" fill="var(--good)" text-anchor="middle">whitening, Gray, interleaver, header: confirmed exact</text>
  <text x="564" y="118" font-size="10.5" fill="var(--dim)" text-anchor="middle">columns 4&#8211;7: the parity bits</text>
  <text x="564" y="134" font-size="10.5" fill="var(--warn)" text-anchor="middle">the Hamming equations differed from the literature</text>
  <text x="380" y="170" font-size="11" fill="var(--dim)" text-anchor="middle">Seventy captured codewords then over-determine the real equations, and linear algebra solves them.</text>
</svg>

With the known data nibbles on one side and the captured parity bits on the
other, each parity bit is an unknown XOR of data bits — sixteen possible
masks, checked against seventy observations. The chip's answer:

```
p0 = d0 ^ d1 ^ d2        p1 = d1 ^ d2 ^ d3
p2 = d0 ^ d1 ^ d3        p3 = d0 ^ d2 ^ d3
```

Four three-input XORs — not the textbook Hamming-plus-overall-parity a
first implementation reaches for. The same technique, applied to the frame's own
CRC field against the known payload, settled the last convention: the
payload CRC is CCITT from a zero seed over all but the final two bytes,
with those two bytes then XORed straight into the result.

After those three corrections — sync word, parity matrix, CRC — a real
SX1262 frame decodes end to end through MeshBench's receive chain: sync
lock, frequency correction, demodulation, error correction, dewhitening,
header, CRC, and the exact payload out the far side.

## What the capture tooling defends against

A live capture can mislead in four specific ways, and the tooling defends
against each:

- **A DC spike beats a chirp in a naive spectrum search.** A chirp's
  spectrum is a plateau, not a peak, so "find the strongest bin" lands
  anywhere in the occupied band — or on the dongle's DC offset. The search now takes the
  midpoint of the occupied band, away from DC.
- **Half a chip of timing smears every bin.** The decimator's sampling
  phase relative to symbol boundaries is luck; near a half-sample, every
  bin reads as a smear between neighbours. The tool
  now tries every decimation phase and keeps the one whose frame decodes
  best — sub-chip timing recovery by exhaustive search.
- **A live channel damages frames.** A single flipped bit — a collision
  or a fade, on a frequency other repeaters genuinely use — is enough. A
  reference vector carrying channel damage would teach the
  test the wrong bits, so the tool refuses to write a vector from any frame
  the error correction had to repair. Recapture instead.
- **The chip pads with garbage.** The final interleaver block's padding
  nibbles decode to nothing deterministic — uninitialised buffer contents
  no receiver ever reads. Golden comparison stops at the last block made
  entirely of meaningful nibbles, and requires the whole air frame to
  decode instead.

## What stands afterwards

Two clean captured frames, at different payload lengths and therefore
different block layouts, are checked into `internal/rf/lora/testdata/` as
golden vectors. The test suite holds the encoder to them symbol by symbol —
at each symbol's own coded rate, since reduced-rate symbols only carry
their top bits — and requires each captured frame to decode to its payload
with a valid CRC. The chain cannot drift from silicon without a test
saying so.

To repeat the experiment after a chain change, or to add vectors at other
spreading factors:

```
go run ./tools/goldencap -probe
go run ./tools/goldencap -run -payload "a known payload" \
    -out capture.iq -golden internal/rf/lora/testdata/golden-sfX-crY.json
```

`-probe` says who is on the serial port and how its radio is set; `-run`
does a full transmit-capture-diff; `-analyze` re-runs the analysis on a
saved capture without transmitting anything.
