# Python client reference

The Python client is `pkg/client-python/meshbench` in the
[meshbench repository](https://github.com/MeshBench/meshbench) - one dependency,
the standard library, and a control socket. Install it with
`pip install -e pkg/client-python`, then `from meshbench import Workbench`.

This page is the whole exported surface. It is generated from the client's own
docstrings and type annotations, so it says exactly what the code says and no
less; where a note reads like an argument with itself, that is the docstring
earning its place. For how a session is opened and what a verb is, read
[Scripting a session](scripting.html) first; for whole programs, the
[cookbook](cookbook.html).

## The surface

<!-- BEGIN GENERATED API -->

Every class the client exports, its methods, and the shape of each call - generated from the docstrings and type annotations in `pkg/client-python/meshbench`, so it cannot drift from the code it documents. Start at [Scripting a session](scripting.html) for how a session is opened, and the [cookbook](cookbook.html) for whole programs.

**The workbench** · [Workbench](#workbench)

**The parts** · [Project](#project) · [Nodes](#nodes) · [Node](#node) · [Sim](#sim) · [Firmware](#firmware) · [Console](#console) · [Events](#events) · [Boundary](#boundary) · [Live](#live) · [Assertions](#assertions) · [Schedule](#schedule) · [Device](#device) · [Subscription](#subscription) · [Job](#job)

**Enumerations** · [Board](#board) · [Class](#class) · [Kind](#kind) · [Preset](#preset) · [Role](#role) · [Strategy](#strategy) · [Tab](#tab) · [Transport](#transport)

**Values** · [Event](#event) · [Build](#build) · [BuildDetails](#builddetails) · [CardSlot](#cardslot) · [Check](#check) · [Hello](#hello) · [ImportPreview](#importpreview) · [JobInfo](#jobinfo) · [NameMatch](#namematch) · [NodeInfo](#nodeinfo) · [NodeStat](#nodestat) · [Notification](#notification) · [Provenance](#provenance) · [Report](#report) · [Screen](#screen) · [Shot](#shot) · [SimState](#simstate)

**Errors** · [BadParams](#badparams) · [Closing](#closing) · [Conflict](#conflict) · [MeshbenchError](#meshbencherror) · [NotFound](#notfound) · [ProtocolMismatch](#protocolmismatch) · [Refused](#refused) · [Timeout](#timeout) · [Unavailable](#unavailable) · [UnknownVerb](#unknownverb)

**Module functions** · [default_address](#default-address) · [subscribe](#subscribe)

## Workbench

A running session.

Use it as a context manager. `launch` and `headless` own the process they
started and stop it on the way out; `attach` never does - a script must not
be able to close the workbench somebody is looking at by falling off the
end of a `with`.

### `classmethod Workbench.attach(cls, socket: str | None = None, timeout: float = 300.0) -> Workbench`

Connect to a workbench that is already running.

### `classmethod Workbench.headless(cls, fixture: str | None = None, seed: int | None = None, socket: str | None = None, binary: str | None = None, extra: list[str] | None = None, start_timeout: float = 90.0, stderr: Any = None) -> Workbench`

Start a session with no window, and own it.

The one to use from a test or from CI: no display, no GPU, no toolkit.

### `classmethod Workbench.launch(cls, **kw) -> Workbench`

Open the desktop workbench and own it. Needs a display.

### `classmethod Workbench.attach_or_headless(cls, **kw) -> Workbench`

Use the session that is running, or start one with no window.

For a script somebody runs repeatedly by hand: the second run should
carry on from the first rather than clearing everything down.

Note which half you get. Attaching does not own the process and leaves
it running at the end; starting one does own it and stops it. A script
that wants the session to survive should attach to a session started
separately.

### `classmethod Workbench.attach_or_launch(cls, **kw) -> Workbench`

Use the session that is running, or open the desktop workbench.

The windowed half of the pair, so a re-run can put something back on
screen. Needs a display.

### `Workbench.close() -> None`

Hang up, and stop the process if this client started it.

### `property Workbench.owns_process() -> bool`

Whether closing this will stop the workbench.

### `property Workbench.is_headless() -> bool`

### `Workbench.call(verb: str, params: Any = None) -> Any`

Run one verb and return its result.

Public and documented, not an escape hatch to be ashamed of: the shaped
API will never cover all 213 verbs, and a verb added tomorrow should be
usable today.

### `Workbench.subscribe(*topics: str) -> Subscription`

Stream server-pushed notifications for the given topics, rather than
polling. Opens a second connection to this same workbench, so closing
the returned Subscription hangs up only that stream.

Topics today: "status" (a new console line) and "snapshot" (a compact
summary after each publish, coalesced by the server so a busy run cannot
flood a slow reader).

### `Workbench.checkpoint(name: str) -> dict[str, Any]`

Freeze the whole session under a name - the network, how it is being
run, and where the clock had got to - so it can be taken back here.

### `Workbench.restore(name: str) -> dict[str, Any]`

Rebuild a checkpoint and replay to the moment it was taken. Returns
as soon as the replay is under way; the sim reaching target_ms is when
it has actually arrived. Deterministic, so it comes back to exactly
where it was - at the cost of the replay taking the run's own time.

### `Workbench.checkpoints() -> list[str]`

What can be restored, by name.

### `Workbench.snapshot() -> dict[str, Any]`

The whole session as the socket summarises it.

### `Workbench.describe() -> dict[str, Any]`

The cheap summary: nodes, seed, time, whether it is playing.

### `Workbench.journal() -> dict[str, Any]`

Every command this workbench has been driven with, newest last, and
when the process started - so a session picked up cold can be told how
the world got here, and whether it has been restarted.

### `Workbench.verbs() -> list[str]`

Every method this build answers.

### `Workbench.say(text: str) -> None`

Leave a line in the session's log, for whoever is watching.

### `Workbench.keep_above(on: bool | None = None) -> bool`

Whether a panel opened in its own window stays above the main one.

Reads the preference when called with nothing, sets it when given a
value, and returns what it now is.

The preference exists for Linux under Wayland, where no client may ask
a normal window to stay above others. What can be asked for is a
layer-shell surface, and that is a different kind of window: the
compositor gives it no title bar, no taskbar entry and no minimise, so
the window draws its own bar and its close button returns the panel to
the main window. Somebody who would rather have the compositor's own
windows turns this off. On macOS and Windows always-on-top costs
nothing and the preference does not apply.

### `Workbench.window(node: str | Node, tab: Tab | str = '') -> str`

Open a node's own window, on a named tab.

Windowed sessions only, and it says so here rather than appearing to
work: a headless run has nothing to open, and a script that "opened the
Hardware tab" in CI and saw no error will be written to assume it did.

Tabs are named as they are on the strip - Console, Companion, SDR,
Settings, Radio, Stats, Activity, Connect, Hardware. Returns the one it
opened on.

### `property Workbench.nodes() -> Nodes`

### `Workbench.node(name: str) -> Node`

A handle, without checking it exists - so one can be named before
it is placed. Every method on it will say so if it does not.

### `property Workbench.schedule() -> Schedule`

### `property Workbench.assertions() -> Assertions`

### `property Workbench.sim() -> Sim`

### `property Workbench.project() -> Project`

### `property Workbench.firmware() -> Firmware`

### `property Workbench.events() -> Events`

### `property Workbench.boundary() -> Boundary`

The study area: which nodes are in the question being asked. Set it
before importing, because the import filters at fetch time.

### `property Workbench.live() -> Live`

A live deployment feed - CoreScope and the rest - and the import
chain that brings one in.

### `Workbench.console(node: str) -> Console`

### `Workbench.job(job_id: str) -> Job`

### `Workbench.jobs() -> list[dict[str, Any]]`

Everything long-running that is in flight.

### `Workbench.wait_for_nodes(timeout: timedelta = JOB_WAIT) -> None`

Wait until the session has a network in it.

For a fixture opened at startup, which happens on a worker: the socket
answers first, so everything asked before the open lands describes an
empty session and is believed.

### `Workbench.wait_idle(timeout: timedelta = JOB_WAIT) -> None`

Wait for every job to finish.

The honest way to wait out a warm, which is what most of them are.

Finished jobs are ignored rather than waited for: some are removed when
they end and some are only marked - infer.run's is marked - so waiting
for the list to empty waits forever on half of them. That is a
difference between the verbs, not something a caller should know.

### `Workbench.node_stats() -> list[NodeStat]`

Sample every node and return what it found.

A sample, not a read: it costs a /proc read per node, which is why the
window only does it while somebody is looking at the panel.

### `Workbench.provenance() -> Provenance`

What this session's measurements are being made under.

Read from the session rather than carried on each result, for now: the
verbs do not return it yet, and inventing it here would be a claim this
client is not entitled to make.

## Project

Opening, saving, and starting over. Live.

### `Project.new(place: str | None = None) -> None`

An empty network.

With a place it becomes the study area and the map is framed on it,
because those are the same wish - and because a blank network with no
place is a map in the middle of the Atlantic.

### `Project.open(path: str) -> None`

### `Project.save(name: str) -> str`

Write it out.

Worth doing before anything that might restart the process: the
scenario lives in the process, not on disk.

### `Project.list() -> list[str]`

## Nodes

The collection. Live: every call reads the session.

### `Nodes.list() -> list[NodeInfo]`

### `Nodes.info(name: str) -> NodeInfo`

### `Nodes.search(query: str, limit: int = 10) -> list[NameMatch]`

Find nodes by name, best first, when you cannot type the name.

Imported names carry emoji and accents - "🏔️ West Lomond 📡" is one
real node - so matching is done on letters and digits alone, with
accents folded and word order ignored. The ranking happens at the
workbench rather than here, so this client and the Go one agree about
which result is the top one.

Returns an empty list rather than raising: "nothing matched" is an
answer, and the caller usually wants to widen the query rather than
handle an exception.

### `Nodes.find(query: str, least: float = 0.5) -> Node`

The one node a search meant, or a refusal naming what it did find.

`least` is the score below which the top answer is not good enough to
act on. Taking the top result unconditionally is how a script ends up
sending an advert from a node that merely shared a word with what was
asked for, and it does that silently.

### `Nodes.near(node: Node | str, count: int = 0) -> list[Node]`

The nodes closest to this one, nearest first.

Trimming an imported deployment to a neighbourhood is the first thing
anybody does with one, and the distance is the workbench's own - the
same great circle its path losses use.

### `Nodes.of_kind(kind: str) -> list[Node]`

### `Nodes.place(name: str, kind: Kind | str = Kind.SIMPLE_REPEATER, lat: float = 0.0, lon: float = 0.0, height_m: float | None = None, tx_dbm: float | None = None, board: Board | str | None = None) -> Node`

Put one node down.

It inherits its neighbours' regions and their firmware, because
somebody dropping a repeater on a map is adding a repeater to this
network, not choosing a firmware strategy.

### `Nodes.place_many(placements: list[dict]) -> list[Node]`

Put several down, then measure the links once.

One warm at the end rather than one per node: nodes.place re-measures
the matrix each time, and on a national network that is minutes
repeated.

### `Nodes.delete(*nodes: Node | str) -> None`

Remove them, in one rebuild.

All or none: a name that is not there refuses and removes nothing,
because half a deletion leaves a scenario nobody described and no way
to tell which half survived without asking again.

### `Nodes.keep(*nodes: Node | str) -> None`

Delete everything these do not name.

The complement is worked out at the workbench rather than here, so it
cannot be computed against a list that changed in between.

### `Nodes.select(*nodes: Node | str, add: bool = False) -> None`

### `Nodes.selected() -> list[str]`

### `Nodes.stats() -> list[NodeStat]`

## Node

One node. Live: a handle, not a copy - it holds a name and asks.

### `property Node.info() -> NodeInfo`

### `property Node.stat() -> NodeStat | None`

### `property Node.running() -> bool`

### `property Node.state() -> str`

### `Node.start() -> None`

### `Node.stop() -> None`

### `Node.delete() -> None`

### `Node.output(source: str = 'serial', lines: int = 200) -> list[str]`

What this node printed, from one of four voices.

`serial` is the board's own port - a native node's standard error;
`boot` is the ROM's, on a board whose application talks over USB;
`emulator` is what QEMU or Renode said about running it; `radio` is
the radio model's log.

The lines, not a count of them: a board that has gone quiet is read
by looking at what it last said.

### `property Node.device() -> Device`

This node as a device to drive: its screen, buttons and panel. All
of it works headless - the display is the framebuffer the controller
holds, not a picture of the desktop. Distinct from `board`, which is
the model name this hardware is.

### `Node.radio() -> dict[str, Any]`

What this node's radio is set to - the same thing the workbench
shows under Radio. What the model assumes, and, for a node that is
running, what it reports back and where the two differ. Left as a dict
because a repeater and a companion answer it differently.

### `Node.wipe() -> None`

Put this board back to factory: its flash, its card, its files.

A board keeps what it was told between runs, as hardware does, so a
node configured into a corner stays there until this is called. Refused
while it is running, rather than rewriting a flash underneath the
emulator holding it.

### `Node.card(*, fitted: bool | None = None, file: str | None = None, wipe: bool = False) -> CardSlot`

What is in this node's card slot, and changing it.

A slot is not a fitted card: the board says the slot exists, this says
whether it is filled. Two of the same handheld in one network, one with
storage and one without, is an ordinary thing to want.

`file` hands the node a card of your own - shared between runs, or
prepared in advance; an empty string returns it to its own, named after
it and kept beside its flash. `wipe` erases it, which is what
reformatting one is, and is refused while the node is running.

A firmware marked as needing a card fills the slot whatever this says,
because a build that keeps its settings there boots into nothing
without one.

### `Node.output_window(source: str = 'serial') -> None`

Open one of this node's logs in a window of its own.

A tab is one pane. What people do while a board is misbehaving is watch
its screen and two of its logs together - what the board printed beside
what the emulator said about running it - and that needs windows.

### `Node.move(lat: float, lon: float) -> None`

Put it somewhere else. The physics moves with it: cached losses for
this node are forgotten.

### `Node.set_regions(*regions: str) -> None`

### `Node.set_firmware(build: Build | str, apply: bool = True) -> None`

Change what it runs.

Applied by default, which means stop, provision, start: firmware is
chosen when a node launches, so recording it and leaving the node on
its old build is the control somebody presses twice and then distrusts.
Pass apply=False to record it for the next start instead - and know
that is what you have done.

### `property Node.build() -> Build | None`

The build this node runs, or None if it is pinned to nothing.

The whole row rather than the version string, because deleting a build
or comparing two needs its path and its board, and reassembling those
from a version is the kind of guesswork that deletes the wrong file.

### `property Node.firmware() -> str`

### `Node.firmware(build: Build | str) -> None`

### `property Node.board() -> str`

What this node is, by board profile name.

From the network rather than from the statistics: a stopped node has
hardware just as surely as a running one.

### `Node.board(name: Board | str) -> None`

What hardware this node is.

A change to the physics rather than a label, so it rebuilds and
re-warms - and it clears a firmware pin made for a different board,
because that image cannot run on this one and a pin nobody can honour
reads as a configured node right up until it refuses to start.

### `Node.set_true_rf(on: bool = True) -> None`

Take waveform verdicts whatever the run's mode - the hybrid flag,
for measuring one node honestly inside a cheap run.

### `Node.inject() -> None`

Originate a packet without firmware.

It exercises the radio model and the channel; what it does not exercise
is relaying, which is a firmware behaviour and needs a firmware.

### `Node.provisioning() -> list[str]`

What this node is told at boot, in the console's own words.

### `Node.serve(over: Transport = Transport.TCP) -> str`

Hand this companion to a real client, and say where to point it.

### `Node.unserve() -> None`

### `property Node.console() -> Console`

### `Node.wait_running(timeout: timedelta = FIRMWARE_WAIT) -> None`

Wait for its firmware process to be up.

`timeout` is wall clock - how long you are prepared to sit here - not
simulated time. Starting a process is real work on the real machine.

## Sim

The clock, and the run. Live.

### `Sim.state() -> SimState`

### `property Sim.playing() -> bool`

### `property Sim.now_ms() -> int`

### `Sim.start(firmware_wait: timedelta = FIRMWARE_WAIT, wait: timedelta = JOB_WAIT) -> None`

Bring the run up: wait out the warm, start every node, and play.

Deliberately not one call to `sim.start`. That verb is the play
button's own handler and answers four ways - it *pauses* if already
playing, declines while links are being measured, or starts firmware
and does not play - so a script pressing it once gets whichever of
those the moment happens to be in.

Worse, it only starts firmware when **no** node is running. Pin a
build onto two nodes of a fifty-eight node fixture and it considers
the mesh started, plays with fifty-six of them down, and says nothing.

So this asks for the three things it actually wants, in order, and
checks each one.

### `Sim.play() -> None`

### `Sim.pause() -> None`

### `Sim.step() -> None`

### `Sim.reset() -> None`

### `Sim.settle(steps: int = 60) -> None`

Step a paused run, which is how a command gets the time it needs to
be answered without starting the clock.

### `property Sim.seed() -> int`

### `Sim.seed(value: int) -> None`

Fix the run. Same seed, same scenario, same result - which is what
makes a *changed* result mean something.

### `property Sim.step_ms() -> int`

### `Sim.step_ms(value: int) -> None`

### `Sim.set_real_firmware(on: bool = True) -> None`

### `Sim.run(simulated: timedelta, wait: timedelta = RUN_WAIT) -> None`

Advance the mesh's own clock by this much, and wait for it.

Two clocks, one call, and they are not the same one:

- `simulated` is the mesh's. `timedelta(minutes=5)` is five minutes
  of its time.
- `wait` is yours: how long you are prepared to sit here before
  giving up. On 155 emulated nodes five simulated minutes is a great
  deal more than five of yours, which is why it is separate and
  generous.

### `Sim.wait_stopped(timeout: timedelta = RUN_WAIT) -> None`

Wait for a run to end. `timeout` is wall clock.

### `Sim.wait_until(at: timedelta, timeout: timedelta = RUN_WAIT) -> None`

Wait for the mesh's clock to reach a moment.

`at` is simulated time; `timeout` is yours.

## Firmware

What this machine can run, and what it is running. Live.

### `Firmware.library() -> list[Build]`

### `Firmware.on_disk() -> list[Build]`

Only the ones this machine holds, which is the only thing that
decides what a node can run. A build that failed to download and one in
daily use look identical from anywhere else.

### `Firmware.find(version: str, board: Board | str = '') -> Build`

One build, by version and - where the version alone is ambiguous,
which it is for every board image - by board.

### `Firmware.scan() -> None`

Ask the catalogue what is published, which is how a build nobody has
downloaded becomes offerable.

### `Firmware.download(role: str, version: str, board: Board | str = '') -> None`

Fetch a published build.

`role` is a plain string here and a Role everywhere else,
deliberately: this one names a published release asset, and the
catalogue's own spellings are not always the application names the
verbs are keyed on.

### `Firmware.import_(path: str, role: str, board: str = '', label: str = '') -> Build`

Take a build from a path - the one way a locally built image gets
into the library.

`label` is what the library will know it by and what a node pins.
Left out it is a timestamp, so importing twice gives two builds rather
than one that quietly replaced the other - which matters the moment you
want to put the new one on a node and delete the old.

### `Firmware.delete(build: Build) -> str`

Remove a build from the cache, and say what was removed.

By path, and the workbench refuses any path outside the firmware
cache. A build nodes are still pinned to will go: they keep the pin,
which then cannot be honoured and fails at start - so move them onto
the replacement first.

### `Firmware.details(build: Build | str, board: Board | str = '', role: Role | str = '') -> BuildDetails`

Everything known about one build: where it is, what it is, and what
has been decided about it.

Takes a Build or a bare label. A label alone is refused when it names
more than one build - the same image imported for two boards, say -
because acting on the wrong one is a rename of somebody else's image.

### `Firmware.update(build: Build | str, *, board: Board | str = '', role: Role | str = '', label: str | None = None, new_role: Role | str | None = None, new_board: Board | str | None = None, coproc_at_reset: bool | None = None, card_required: bool | None = None, notes: str | None = None) -> BuildDetails`

Rename a build, move it to another board or role, or change how it
is run.

Renaming moves the file, because the name is the identity: a board
image is stored as `<board>/<role>@<label>.bin` and nothing else
records what it is. Nodes pinned to the old name are repointed, or they
would fail at their next start with "no image in the cache" about a
build sitting in the library under its new name.

Every argument left out is left alone, which is why they default to
None rather than to "" or False: "leave this setting" and "turn it
off" are different answers.

### `Firmware.window(build: Build | str, board: Board | str = '', role: Role | str = '') -> None`

Open the build's own window - what a click on a library row does.

### `Firmware.build(checkout: str, role: Role | str = '', label: str = '', wait: timedelta = JOB_WAIT) -> list[Build]`

Compile a MeshCore checkout and put the results in the library.

Both roles unless one is named, deliberately. A locally built repeater
compiled against a stale shim once answered console output with 0x06
where the host expects 0x07: it connected, misbehaved and exited. Two
arms of a comparison built at different moments from different trees
measure the build process rather than the firmware, so the easy thing
here is the thing that builds them together.

Blocks until it is done - a MeshCore build is a minute or two per
role - and returns what the library now holds that was built locally.

### `Firmware.use_what_is_here() -> dict[Role, Build]`

Pin every role that needs one to the newest build on this machine.

What a script wants almost every time: this mesh, whatever this machine
holds, rather than a version typed into the script that goes stale. A
run refuses to start until every role is answered, so the alternative
is the same loop written out in each one.

Refuses by name when a role has nothing, because "no companion build"
is a thing to go and fix rather than a reason to start a mesh with a
silent hole in it.

### `Firmware.use_for_role(role: Role, build: Build | str) -> None`

### `Firmware.start() -> None`

Bring up firmware on every node.

Asynchronous, and always has been: it answers with what it has begun,
not with what is up. It was synchronous once, and on 155 nodes that
froze the window and the socket together for as long as it was left -
which read as a crash and was reported as one.

### `Firmware.state() -> dict[str, Any]`

### `Firmware.needed() -> list[dict[str, Any]]`

The roles with nodes and no build pinned, with what could be. A run
refuses to start until every one is answered.

### `Firmware.wait_started(timeout: timedelta = FIRMWARE_WAIT) -> None`

Wait for every node's firmware to be up. `timeout` is wall clock.

`nodes` here is the nodes that *run* firmware, which is not every
node - an SDR observer and an emitter never boot one. It used to be
every node, so a fixture holding either reported "56 of 58" until the
timeout and there was no way to see which two.

Which is why the wait names the stragglers rather than counting them.
Ten minutes of "56 of 58" tells you nothing; two node names tell you
whether a build is missing or a board is wedged.

## Console

One node's firmware console. Live.

Two consoles, not one, and which you get depends on what the node is.

A repeater has a text CLI and reads typed bytes. A companion does not: it
speaks the framed companion protocol, and its command line is
meshcore-cli's vocabulary - `advert`, `public <msg>`, `chan <n>
<msg>`. Typing text at a companion goes nowhere, is echoed locally, and
reads exactly like a command that ran and did nothing.

So this picks the right one from the node's kind. A caller should not have
to know, and every caller that did know got it wrong at least once.

### `Console.send(line: str) -> None`

### `Console.read() -> list[str]`

The scrollback, newest last.

The lines come back under "tail" and "lines" is how many there are in
total - so reading "lines" hands you an integer where you asked for
text, and every use of it fails somewhere further along. The tail is
the last 200; a node up for an hour has thousands and nobody reads the
first one.

### `Console.ask(line: str, steps: int = 100) -> str`

Send a line and wait for the node to answer it.

The important one. A node reads its serial input on its next loop and
its loop only runs when the engine steps, so reading straight after
sending reads the moment *before* the command was sent - every script
that has done this by hand got an empty reply and concluded the console
was broken. This gives the mesh its own time first.

## Events

What the engine has done. Live.

### `Events.recent(limit: int = 50) -> list[Event]`

The tail.

A tail, and only a tail: the store keeps a bounded one because a long
run has millions. A script that needs all of them dumps per round -
reading only the tail after a busy flood samples the most congested
moment of it, which is a mistake already made once here.

### `Events.total() -> int`

### `Events.dump(path: str) -> int`

Write every event held to a file, one JSON object per line.

### `Events.wait(kind: str = '', from_: str = '', to: str = '', timeout: timedelta = EVENT_WAIT) -> Event`

Wait for an event to match, and return it.

## Boundary

The study area, however you have it. Live.

### `Boundary.use(area: str | Path, name: str = '') -> list[str]`

Take a study area from a place name or from GeoJSON.

The one to call. A path to a .geojson file is loaded; anything else is
searched for by name and the best match accepted. Both end with the
area in the study, which is the only thing the caller wanted to say.

`name` renames a single loaded polygon, so a file called
`export(3).geojson` can still join the study as "Tay catchment".

### `Boundary.search(query: str) -> list[str]`

Places matching a name, best first. Needs the network.

Returns names rather than geometry: the geometry stays at the
workbench, and the name is what accept takes.

### `Boundary.accept(name: str) -> str`

Take one of the search results into the study area.

Areas union rather than replace: a study is often two council areas
rather than one.

### `Boundary.load(source: str | Path | dict, name: str = '') -> list[str]`

Take a study area from GeoJSON: a path, a document, or a dict.

A Polygon, a MultiPolygon, a Feature or a FeatureCollection. Each
polygon becomes an area named from its `name` property, or from
`name`, or from the file.

The one way to study an area nothing has an administrative name for -
a catchment, a valley, the bit north of the river - and the only one
that works with no network at all.

### `Boundary.list() -> list[str]`

What the study area is made of.

### `Boundary.remove(name: str) -> None`

Take one area back out.

Changes what is measured, never what is loaded: the nodes stay until
something prunes them.

### `Boundary.prune(margin_km: float | None = None) -> int`

Delete the nodes outside the study area, and say how many went.

For a mesh that was imported before the boundary was set. The margin is
kept on purpose: a node just outside still interferes with one just
inside, and dropping it makes the inside look quieter than it is.

## Live

A live feed, and the deployment it describes. Live in both senses.

### `Live.pull(url: str, strategy: Strategy = Strategy.REPLACE, window: timedelta = DEFAULT_WINDOW, wait: timedelta = JOB_WAIT) -> ImportPreview`

Fetch, commit, read the traffic, and apply what it implies.

The whole chain, in the order that works. `window` is how far back
into the feed's history to read - the mesh's own past, not your
patience; `wait` is yours.

Returns what the fetch found. Link measurement is still running when
this returns on anything but a small mesh, so follow it with
`wb.wait_idle()` before starting a run.

### `Live.set_source(url: str) -> str`

Point at a feed without reading it, and say how it was tidied.

A method rather than a property, because a property implies something
to read back and the session offers no way to ask what its source
currently is. One that answered from a value this object happened to
remember would be right until anything else set it.

### `Live.fetch(url: str = '') -> ImportPreview`

Read the deployment and say what would change, changing nothing.

### `Live.commit(strategy: Strategy = Strategy.REPLACE) -> int`

Apply the fetched nodes to the scenario.

`"replace-all"` is what the shipped fixtures were built with;
`"add"` keeps what is already here and skips names that clash.

Measuring the links afterwards is a job rather than part of this call -
676 nodes is 228,000 terrain paths over real ground - so this returns
while that is still running.

### `Live.infer(window: timedelta = DEFAULT_WINDOW, wait: timedelta = JOB_WAIT) -> None`

Read the feed's recent traffic to work out what each node holds.

This is the step that decides whether anything relays. A node whose
regions are unknown forwards nothing, and nothing says so.

`window` is the feed's own past; `wait` is how long you will sit
here for it. A week of ScotMesh is around 150,000 packets and several
minutes of paging.

### `Live.apply_regions() -> int`

Put the inferred regions onto the nodes, and say how many took one.

The forgotten step. Everything above can succeed and the mesh still be
silent until this runs.

## Assertions

What has to be true for a run to have passed. Live.

### `Assertions.delivered(at_least: int, within: timedelta | None = None) -> None`

At least this many nodes received something.

### `Assertions.sent(node: str | Node = '', at_least: int = 0, at_most: int = 0, within: timedelta | None = None) -> None`

This node - or the whole mesh - transmitted within these bounds.

at_most is the interesting one: it is how a relay-suppression change is
held to not having made the mesh chattier.

### `Assertions.add(kind: str, node: str | Node = '', at_least: int = 0, at_most: int = 0, max_pct: float = 0.0, within: timedelta | None = None) -> int`

The general form, for a kind this package has no name for yet.

### `Assertions.check() -> Report`

Measure every assertion against the run so far.

The provenance travels with the verdict, because a delivery figure
without what the model assumed is the number this project exists not to
publish.

## Schedule

What the mesh is told to send, and when. Live.

### `Schedule.add(node: str | Node, command: str, at: timedelta | None = None, every: timedelta | None = None) -> int`

Have a node send something, once or repeatedly.

`at` and `every` are **simulated** time - the mesh's own clock,
not yours. The verb underneath takes milliseconds; nobody writing a
script should have to.

Repeating traffic has worked all along and nothing said so, which to
somebody writing a script is the same as it not existing.

### `Schedule.clear() -> int`

Forget all of them.

## Device

One running node's board, as a device to drive.

A handle, not a copy: it holds a name and asks.

### `Device.screen() -> Screen`

What the display is showing, as numbers. Works headless - it reads
the framebuffer the controller holds, not the desktop.

### `Device.screenshot() -> Shot`

Write the display to a PNG and return where it landed. The frame is
exactly what the controller holds, at the size it holds it.

### `Device.press(pin: int, down: bool = True) -> None`

Hold a button pin down, or release it. Held rather than clicked
because the firmware cares: MeshCore wakes a sleeping display on a
press and powers off on a long one, so time the release yourself - or
use tap, which does not hold.

### `Device.tap(pin: int) -> None`

Press a button and let go - the ordinary click.

### `Device.type(text: str) -> None`

Enter text at the board's own keyboard, a character at a time -
which is what the keyboard sends and what the firmware polls for.

### `Device.touch(x: int, y: int, down: bool = True) -> None`

Put a finger on the panel at a point, or lift it off.

### `Device.tap_at(x: int, y: int) -> None`

Touch a point and lift off - a tap on the panel.

### `Device.wait_screen(timeout: timedelta = DEFAULT_SCREEN_WAIT) -> Screen`

Wait until the display changes from what it shows now, and return the
new frame; raise with what it was still showing if the timeout runs out.

This is the honest way to check an input. Half duplex eats stimuli - a
board handed a packet while transmitting never hears it - so a tap
followed by an immediate screen read will intermittently read the frame
from before the tap landed. Change is by digest, so a redraw that keeps
the same number of lit pixels still counts.

## Subscription

A live stream of notifications on a connection of its own.

Iterate it for events; it blocks until the next one arrives and ends when
the workbench hangs up. Use it as a context manager, or call close, so the
extra connection does not outlive the interest.

### `Subscription.close() -> None`

## Job

A long operation the workbench is doing. Live: a handle to an id.

### `Job.info() -> JobInfo | None`

### `Job.cancel() -> None`

Stop it, where whoever started it left a way to.

A job with no cancel refuses by name rather than silently doing
nothing: an operator who asked deserves to be told, not left watching a
bar that carries on.

### `Job.wait(timeout: timedelta = JOB_WAIT) -> None`

Wait for it to finish, and raise if it finished badly.

`timeout` is wall clock. Ended is not the same as worked: a read that
failed used to finish the job with the reason in its title and nothing
else, so every caller either carried on as though it had succeeded or
matched on the wording.

## Enumerations

### Board

A hardware profile this build knows about.

A node's board decides its transmit ceiling, its receive chain's noise
figure and the battery the energy model uses, so naming one that does not
exist is refused rather than defaulted.

- `EBYTE_EORA_S3` - `'Ebyte_EoRa-S3'`
- `GENERIC_E22_SX1262` - `'Generic_E22_sx1262'`
- `HELTEC_E213` - `'Heltec_E213'`
- `HELTEC_E290` - `'Heltec_E290'`
- `HELTEC_WSL3` - `'Heltec_WSL3'`
- `HELTEC_WIRELESS_PAPER` - `'Heltec_Wireless_Paper'`
- `HELTEC_WIRELESS_TRACKER` - `'Heltec_Wireless_Tracker'`
- `HELTEC_MESH_SOLAR` - `'Heltec_mesh_solar'`
- `HELTEC_T096` - `'Heltec_t096'`
- `HELTEC_T114` - `'Heltec_t114'`
- `HELTEC_V2` - `'Heltec_v2'`
- `HELTEC_V3` - `'Heltec_v3'`
- `LILYGO_T3S3_SX1262` - `'LilyGo_T3S3_sx1262'`
- `LILYGO_TBEAM_1W` - `'LilyGo_TBeam_1W'`
- `LILYGO_TDECK` - `'LilyGo_TDeck'`
- `RAK_3112` - `'RAK_3112'`
- `RAK_4631` - `'RAK_4631'`
- `STATION_G2` - `'Station_G2'`
- `STATION_G3_ESP32` - `'Station_G3_ESP32'`
- `TBEAM_SX1262` - `'Tbeam_SX1262'`
- `XIAO_S3` - `'Xiao_S3'`
- `XIAO_S3_WIO` - `'Xiao_S3_WIO'`
- `XIAO_NRF52` - `'Xiao_nrf52'`
- `HELTEC_TRACKER_V2` - `'heltec_tracker_v2'`
- `HELTEC_V4` - `'heltec_v4'`

### Class

What happened to an event.

- `SENT` - `'sent'`
- `RECEIVED` - `'received'`
- `HALF_DUPLEX` - `'half-duplex'`
- `INTERFERENCE` - `'interference'`
- `FLOOR` - `'floor'`

### Kind

What a node is.

- `SIMPLE_REPEATER` - `'simple-repeater'`
- `ADVANCED_REPEATER` - `'advanced-repeater'`
- `COMPANION` - `'companion'`
- `ROOM_SERVER` - `'room-server'`
- `SDR_OBSERVER` - `'sdr-observer'`
- `EMITTER` - `'emitter'`

### Preset

A named set of LoRa parameters for a territory.

An agreement between operators rather than a configuration, which is why
the list is baked in rather than fetched.

- `AUSTRALIA` - `'Australia'`
- `AUSTRALIA_NARROW` - `'Australia (Narrow)'`
- `AUSTRALIA_MID` - `'Australia (Mid)'`
- `AUSTRALIA_SA_WA` - `'Australia: SA, WA'`
- `AUSTRALIA_QLD` - `'Australia: QLD'`
- `BRAZIL` - `'Brazil'`
- `EU_UK_NARROW` - `'EU/UK (Narrow)'`
- `EU_UK_DEPRECATED` - `'EU/UK (Deprecated)'`
- `CZECH_REPUBLIC_NARROW` - `'Czech Republic (Narrow)'`
- `EU_433MHZ_LONG_RANGE` - `'EU 433MHz (Long Range)'`
- `EU_433MHZ_NARROW` - `'EU 433MHz (Narrow)'`
- `NETHERLANDS` - `'Netherlands'`
- `NEW_ZEALAND` - `'New Zealand'`
- `NEW_ZEALAND_NARROW` - `'New Zealand (Narrow)'`
- `PORTUGAL_433` - `'Portugal 433'`
- `PORTUGAL_868` - `'Portugal 868'`
- `SWITZERLAND` - `'Switzerland'`
- `USA_CANADA_RECOMMENDED` - `'USA/Canada (Recommended)'`
- `VIETNAM_NARROW` - `'Vietnam (Narrow)'`
- `VIETNAM_DEPRECATED` - `'Vietnam (Deprecated)'`

### Role

The MeshCore application a node runs, named as upstream names
its example directory.

The string every firmware verb is keyed on. The published catalogue spells
some of the same things differently - "repeater", "room-server" - and those
belong to the release assets; typing one at a verb pins nothing, and the run
then refuses to start with no clue as to why.

- `SIMPLE_REPEATER` - `'simple_repeater'`
- `COMPANION_RADIO` - `'companion_radio'`
- `SIMPLE_ROOM_SERVER` - `'simple_room_server'`
- `COMPANION_RADIO_USB` - `'companion_radio_usb'`
- `COMPANION_RADIO_BLE` - `'companion_radio_ble'`

### Strategy

How an imported deployment meets what is already loaded.

- `REPLACE` - `'replace-all'`
- `ADD` - `'add'`

### Tab

A pane of a node's own window.

- `CONSOLE` - `'Console'`
- `COMPANION` - `'Companion'`
- `SDR` - `'SDR'`
- `SETTINGS` - `'Settings'`
- `RADIO` - `'Radio'`
- `STATS` - `'Stats'`
- `ACTIVITY` - `'Activity'`
- `CONNECT` - `'Connect'`
- `HARDWARE` - `'Hardware'`
- `OUTPUT` - `'Output'`

### Transport

How a served companion is reached.

- `TCP` - `'tcp'`
- `SERIAL` - `'serial'`

## Values

### Event

One thing the engine did.

The frame bytes are deliberately absent: a long run has millions of these,
and the one packet somebody wants is asked for by id.

- `at_ms: int`
- `kind: Kind | str`
- `from_: str`
- `to: str`
- `message_id: int`
- `packet_id: int`
- `snr_db: float | None`
- `detail: str`
- `class_: Class | str`

### Build

One firmware image, as the library sees it.

Version, board and role travel together because a board image is not a
build on its own: "wadamesh" means nothing until it is wadamesh for a
LilyGo_TDeck, built as a companion.

- `role: Role | str`
- `version: str`
- `board: str`
- `bytes: int`
- `on_disk: bool`
- `path: str`
- `in_use: int`
- `unavailable: bool`

### BuildDetails

One build, in full: what a row cannot hold.

Separate from :class:`Build` because the library is deliberately a list -
role, version, size, a tick. Where the file actually is, whether it is a
whole flash image or half of one, and what has been decided about how it
runs are the questions somebody has once a build does not do what they
expected.

- `role: Role | str`
- `version: str`
- `board: str`
- `native: bool`
- `on_disk: bool`
- `path: str`
- `settings_path: str`
- `bytes: int`
- `modified: str`
- `in_use: int`
- `kind: str`
- `bootable: bool`
- `flash_mb: int`
- `coproc_at_reset: bool`
- `card_required: bool`
- `notes: str`

### CardSlot

What is in one node's card slot.

A slot is not a fitted card: the board says the slot exists, the node says
whether it is filled, and a firmware that keeps its settings on a card
fills it regardless.

- `node: str`
- `slot: str`
- `fitted: bool`
- `file: str`
- `own_file: str`
- `bytes: int`
- `required_by_firmware: bool`
- `board_has_slot: bool`
- `wiped: bool`

### Check

One assertion, and what the run made of it.

- `kind: str`
- `node: str`
- `passed: bool`
- `got: str`
- `want: str`

### Hello

What a connection is talking to. Read once, at connect.

- `protocol: int`
- `version: str`
- `mode: str`
- `socket: str`
- `verbs: int`
- `pid: int`
- `started_at: str`
- `headless() -> bool`

### ImportPreview

What a fetch found, before anything has been changed.

`skipped_no_position` and `uncertain` are the two numbers worth reading
before committing. A node with no position cannot be simulated at all, and
an uncertain one is being placed to within kilometres - the answer it gives
is that vague too, however confident the rest of the output looks.

- `records: int`
- `nodes: int`
- `skipped_no_position: int`
- `uncertain: int`

### JobInfo

A long operation in flight.

- `id: str`
- `what: str`
- `done: int`
- `total: int`
- `finished: bool`
- `failed: bool`

### NameMatch

One answer from a name search, and how sure it is.

`score` runs 0 to 1, ranked best first by the workbench. It exists so a
script can tell "found it" from "found something that shares a word": a top
result at 0.3 is a prompt to look at the list, not a node to start talking
to.

- `name: str`
- `score: float`
- `kind: Kind | str`
- `lat: float`
- `lon: float`

### NodeInfo

What the network is, per node.

What a node is *doing* is NodeStat: the two change on completely different
timescales, and the store publishes them apart.

- `name: str`
- `kind: Kind | str`
- `lat: float`
- `lon: float`
- `height_m: float`
- `tx_dbm: float`
- `regions: list[str]`
- `firmware: str`
- `board: str`
- `firmware_board: str`
- `sent: int`
- `heard: int`
- `selected: bool`

### NodeStat

What one node is costing and doing right now.

- `name: str`
- `backend: str`
- `firmware: str`
- `running: bool`
- `state: str`
- `board: str`
- `pid: int`
- `rss_bytes: int`
- `cpu_ms: int`
- `cpu_pct: float`
- `sent: int`
- `heard: int`
- `last_sent_ms: int`
- `last_heard_ms: int`
- `last_sent_to: str`
- `last_heard_from: str`
- `irq_reads: int`
- `busy_reads: int`
- `busy_ms: int`
- `spurious: int`

### Notification

One server-pushed event. `dropped` is how many snapshot notifications
the server coalesced away before this one - zero for every other topic.

- `topic: str`
- `data: Any`
- `dropped: int`

### Provenance

What a measurement was measured under.

Printed above any number a script emits. Not decoration: a scripted number
gets pasted into a report with the caveats stripped, so the caveats have to
be in the value.

- `rf_mode: str`
- `excess_loss_db: float`
- `calibrated: bool`
- `seed: int`

### Report

What a run passed and failed, with what it was measured under.

- `passed: int`
- `total: int`
- `checks: list[Check]`
- `provenance: Provenance | None`
- `ok() -> bool` - Whether every assertion held.
- `failures() -> list[Check]`
- `write_junit(path: str, suite: str = 'meshbench') -> None` - Write a JUnit file, with the caveats inside it.

### Screen

What a board's display is showing, as numbers rather than a picture.

Enough to answer "did anything change" after a press or a touch, which is
the question every check of an input comes down to; for the picture itself
ask for a screenshot.

- `node: str`
- `has_screen: bool`
- `width: int`
- `height: int`
- `bpp: int`
- `on: bool`
- `lit: int`
- `digest: str`

### Shot

A captured display: a PNG under the node's own work directory, and the
frame's dimensions. The frame is exactly what the controller holds.

- `node: str`
- `path: str`
- `width: int`
- `height: int`
- `bpp: int`
- `on: bool`

### SimState

The clock.

- `playing: bool`
- `now_ms: int`
- `until_ms: int`
- `events: int`
- `step_ms: int`
- `seed: int`

## Errors

### BadParams

The verb refused what it was given.

### Closing

The workbench is shutting down. Retry against a new session.

### Conflict

The right request in the wrong state.

Nothing loaded, nothing running to send to, no import preview to commit.

### MeshbenchError

Anything this client raises.

### NotFound

No node, build, area or job of that name.

### ProtocolMismatch

A client and a workbench that cannot speak to each other.

Raised at connect rather than discovered on the fortieth call, because a
mismatch found halfway through a script looks like the simulation
misbehaving - and in a CI run that reads as a firmware regression.

### Refused

A verb the workbench declined, with its own words kept.

### Timeout

A wait that ran out, saying what it wanted and what it last saw.

Not a bare deadline: "timeout" in a CI log tells whoever reads it nothing,
and the state at the moment it gave up is the only thing that does.

### Unavailable

A request this session cannot serve at all.

A window verb with no window, or hardware that is not here.

### UnknownVerb

Not a method this build has.

Nearly always a client older or newer than the workbench - which connecting
is supposed to have caught first, so seeing this is worth looking into.

## Module functions

### `default_address`

```python
default_address() -> str
```

Where a workbench answers on this operating system unless told otherwise.

### `subscribe`

```python
subscribe(*topics: str, address: str | None = None) -> Subscription
```

Open a subscription to the given topics - "status", "snapshot", and
whatever else the workbench publishes.

<!-- END GENERATED API -->
