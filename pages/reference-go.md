# Go client reference

The Go client is `pkg/client-go/meshbench` in the
[meshbench repository](https://github.com/MeshBench/meshbench):
`import "github.com/MeshBench/meshbench/pkg/client-go/meshbench"`. It is a peer
of the Python client, not a wrapper — both speak the control socket, and
anything either can do the other can.

This page is the whole exported surface, taken from the package's own `go doc`.
`Call` is the entire API; everything else is a typed shape over it, so a verb the
façade has not reached is still one line away. For how a session is opened read
[Scripting a session](scripting.html); for whole programs, the
[cookbook](cookbook.html).

## The surface

<!-- BEGIN GENERATED API -->

Every exported type in the Go client, its methods, and the shape of each call - taken straight from `go doc` over `pkg/client-go/meshbench`, so it matches the package a program imports. Read [Scripting a session](scripting.html) for the two layers - `Call` and the façade over it - and the [cookbook](cookbook.html) for whole programs.

**The workbench** · [Workbench](#workbench)

**The parts** · [Project](#project) · [Nodes](#nodes) · [Node](#node) · [Sim](#sim) · [Firmware](#firmware) · [Console](#console) · [Events](#events) · [Boundary](#boundary) · [Live](#live) · [Assertions](#assertions) · [Schedule](#schedule) · [Device](#device) · [Job](#job)

**Enumerations** · [Board](#board) · [Class](#class) · [Kind](#kind) · [Preset](#preset) · [Role](#role) · [Strategy](#strategy) · [Tab](#tab) · [Transport](#transport)

**Errors** · [ProtocolMismatch](#protocolmismatch) · [Refused](#refused) · [Timeout](#timeout)

**Values** · [Assertion](#assertion) · [Build](#build) · [BuildChange](#buildchange) · [BuildDetails](#builddetails) · [BuildID](#buildid) · [CardChange](#cardchange) · [CardSlot](#cardslot) · [Check](#check) · [Checkpoint](#checkpoint) · [Describe](#describe) · [Event](#event) · [FirmwareState](#firmwarestate) · [Hello](#hello) · [ImportPreview](#importpreview) · [JobInfo](#jobinfo) · [Journal](#journal) · [JournalEntry](#journalentry) · [Match](#match) · [NameMatch](#namematch) · [Neighbour](#neighbour) · [NodeInfo](#nodeinfo) · [NodeStat](#nodestat) · [Notification](#notification) · [Placement](#placement) · [Provenance](#provenance) · [Report](#report) · [Restored](#restored) · [RoleNeed](#roleneed) · [Screen](#screen) · [Send](#send) · [Shot](#shot) · [SimState](#simstate) · [Subscription](#subscription)

**Options and functions** · [Option](#option) · [CodeOf](#codeof)

## Workbench

Workbench is a connection to a running session.

Safe from several goroutines: the socket serialises calls, which is what the control package already guarantees.

### `Attach(ctx context.Context, options ...Option) (*Workbench, error)`

Attach connects to a workbench that is already running.

It never owns the process: Close hangs up, and whatever was on screen stays on screen.

### `AttachOrHeadless(ctx context.Context, options ...Option) (*Workbench, error)`

AttachOrHeadless is AttachOrLaunch without a window, for a machine with no display.

### `AttachOrLaunch(ctx context.Context, options ...Option) (*Workbench, error)`

AttachOrLaunch uses the session that is already running, or opens one.

For a script somebody runs repeatedly by hand: the second run carries on from the first rather than clearing everything down and starting again.

Note which half you got, because they differ in one important way. Attaching does not own the process and Close leaves it running; launching owns it and Close stops it. Owned reports which happened, so a script that must not take the session down with it can say so.

### `Headless(ctx context.Context, options ...Option) (*Workbench, error)`

Headless starts a session with no window and owns it.

The one to use from a test or from CI: no display, no GPU, no toolkit.

### `Launch(ctx context.Context, options ...Option) (*Workbench, error)`

Launch opens the desktop workbench and owns it. Needs a display.

### `(w *Workbench) Assertions() Assertions`

Assertions reaches them.

### `(w *Workbench) Boundary() Boundary`

Boundary reaches the study area.

### `(w *Workbench) Call(ctx context.Context, verb string, params any) (json.RawMessage, error)`

Call runs one verb and returns its result as raw JSON.

Public and documented, not an escape hatch to be ashamed of: the façade will never cover all 213 verbs, and a verb added tomorrow is usable today.

### `(w *Workbench) CallInto(ctx context.Context, verb string, params, into any) error`

CallInto runs a verb and decodes its result.

### `(w *Workbench) Checkpoint(ctx context.Context, name string) (Checkpoint, error)`

Checkpoint freezes the session under a name, so it can be taken back here.

### `(w *Workbench) Checkpoints(ctx context.Context) ([]string, error)`

Checkpoints is what can be restored, by name.

### `(w *Workbench) Close() error`

Close hangs up, and stops the process if this client started it.

### `(w *Workbench) Describe(ctx context.Context) (Describe, error)`

Describe is the cheap summary: how many nodes, what time it is, whether it is playing.

### `(w *Workbench) Do(ctx context.Context, verb string, params any) error`

Do runs a verb and discards its result, for the ones whose answer is only an acknowledgement.

### `(w *Workbench) Events() Events`

Events reaches the log.

### `(w *Workbench) Firmware() Firmware`

Firmware reaches the builds.

### `(w *Workbench) Headless() bool`

Headless reports whether this session has no interface, so a caller can check once rather than learn it from a dozen refusals.

### `(w *Workbench) Hello() Hello`

Hello is what this connection is talking to, read once at connect.

### `(w *Workbench) Job(id string) Job`

Job makes a handle to one by id.

### `(w *Workbench) Jobs(ctx context.Context) ([]JobInfo, error)`

Jobs is everything in flight.

### `(w *Workbench) Journal(ctx context.Context) (Journal, error)`

Journal is the command history, for picking up a session cold: how the world got here, and whether the process has been restarted since it was built.

### `(w *Workbench) KeepAbove(ctx context.Context) (bool, error)`

Window opens a node's own window, on a named tab.

Windowed sessions only, and it says so here rather than appearing to work: a headless run has nothing to open, and a script that "opened the Hardware tab" in CI and saw no error will be written to assume it did.

The tab names are the ones on the strip - Console, Companion, SDR, Settings, Radio, Stats, Activity, Connect, Hardware - and an empty one takes the default. It returns the tab it opened on. KeepAbove reads whether a panel opened in its own window stays above the main one.

The preference exists for Linux under Wayland, where no client may ask a normal window to stay above others. What can be asked for is a layer-shell surface, and that is a different kind of window: the compositor gives it no title bar, no taskbar entry and no minimise, so the window draws its own bar and its close button returns the panel to the main window. On macOS and Windows always-on-top costs nothing and the preference does not apply.

### `(w *Workbench) Live() Live`

Live reaches the import chain.

### `(w *Workbench) Node(name string) Node`

Node makes a handle without checking it exists, so a caller can name one before placing it. Every method on it will say so if it does not.

### `(w *Workbench) NodeStats(ctx context.Context) ([]NodeStat, error)`

NodeStats samples every node and returns what it found.

A sample, not a read: it costs a /proc read per node, which is why the window only does it while somebody is looking at the panel.

### `(w *Workbench) Nodes() Nodes`

Nodes reaches the network.

### `(w *Workbench) Owned() bool`

Owned reports whether Close will stop the session or only hang up on it.

Worth asking after AttachOrLaunch, where either is possible and the difference is whether the workbench is still there afterwards.

### `(w *Workbench) Project() Project`

Project reaches the network as a whole.

### `(w *Workbench) Provenance(ctx context.Context) (Provenance, error)`

Provenance is what this session's measurements are being made under.

Read from the snapshot rather than carried on each result, for now: the verbs do not return it yet, and inventing it client-side would be a claim this client is not entitled to make. What it does guarantee is that the numbers here are the session's actual settings at the moment of asking.

### `(w *Workbench) Restore(ctx context.Context, name string) (Restored, error)`

Restore rebuilds a checkpoint and replays to the moment it was taken. It returns as soon as the replay is under way; the sim reaching TargetMs is when it has actually arrived.

### `(w *Workbench) Say(ctx context.Context, text string) error`

Say puts a line in the session's log, which is how a script leaves a note for whoever is watching the window or reading the run's stderr.

### `(w *Workbench) Schedule() Schedule`

Schedule reaches the fixture's traffic.

### `(w *Workbench) SetKeepAbove(ctx context.Context, on bool) (bool, error)`

SetKeepAbove sets it, and reports what it now is.

### `(w *Workbench) Sim() Sim`

Sim reaches the clock.

### `(w *Workbench) Snapshot(ctx context.Context) (map[string]any, error)`

Snapshot is the whole session as the socket summarises it - counts, jobs, endpoints, the status line. Decoded loosely on purpose: it grows, and a client that failed on a field it had not heard of would break on every release.

### `(w *Workbench) Stop() error`

Stop ends a workbench this client started. Attach's connection has nothing to stop, and says so rather than quietly doing nothing.

### `(w *Workbench) Subscribe(topics ...string) (*Subscription, error)`

Subscribe streams the given topics - status, snapshot, and whichever else the server publishes - without polling. It opens a second connection to the same workbench, so Close on the returned Subscription hangs up only that stream.

Topics known today: "status" (a new console line) and "snapshot" (a compact summary after each publish, coalesced by the server so a busy run cannot flood a slow reader).

### `(w *Workbench) Verbs(ctx context.Context) ([]string, error)`

Verbs is every method this build answers.

### `(w *Workbench) WaitIdle(ctx context.Context, timeout time.Duration) error`

WaitIdle waits for every job to finish - the honest way to wait out a warm, which is what most of them are.

Finished jobs are ignored rather than waited for. Some are removed when they end and some are only marked - infer.run's is marked - so waiting for the list to empty waits forever on half of them. That is a difference between the verbs, and not a caller's to know about.

### `(w *Workbench) Window(ctx context.Context, node string, tab Tab) (Tab, error)`

## Project

Project is opening, saving and starting over. Live.

### `(p Project) List(ctx context.Context) ([]string, error)`

List is what has been saved.

### `(p Project) New(ctx context.Context, place string) error`

New is an empty network.

With a place, it becomes the study area and the map is framed on it, because those are the same wish - and because a blank network with no place is a map in the middle of the Atlantic.

### `(p Project) Open(ctx context.Context, path string) error`

Open loads a fixture or a saved project.

### `(p Project) Save(ctx context.Context, name string) (string, error)`

Save writes the current one out. Worth doing before anything that might restart the process: the scenario lives in the process, not on disk.

## Nodes

Nodes is the collection. Live: every call reads the session.

### `(n Nodes) Delete(ctx context.Context, names ...string) error`

Delete removes them, in one rebuild.

All or none: a name that is not there refuses and removes nothing, because half a deletion leaves a scenario nobody described and no way to tell which half survived without asking again.

### `(n Nodes) Find(ctx context.Context, query string) (Node, error)`

Find is the one node a search meant, or a refusal naming what it did find.

### `(n Nodes) Get(ctx context.Context, name string) (NodeInfo, error)`

Get is one by name.

### `(n Nodes) Keep(ctx context.Context, names ...string) error`

Keep deletes everything these do not name.

The complement is worked out at the workbench rather than here, so it cannot be computed against a list that changed in between.

### `(n Nodes) List(ctx context.Context) ([]NodeInfo, error)`

List is every node, as the network currently has them.

### `(n Nodes) Near(ctx context.Context, name string, count int) ([]Neighbour, error)`

Near is the nodes closest to this one, nearest first, at most count of them (all of them when count is zero).

Trimming an imported deployment to a neighbourhood is the first thing anybody does with one, and the distance is the workbench's own - the same great circle its path losses use.

### `(n Nodes) OfKind(ctx context.Context, kind Kind) ([]NodeInfo, error)`

OfKind filters. Evaluated here rather than at the workbench: it is a question about a list somebody already has.

### `(n Nodes) Place(ctx context.Context, p Placement) (Node, error)`

Place puts one node down and hands back a handle to it.

It inherits its neighbours' regions and their firmware, because somebody dropping a repeater on a map is adding a repeater to this network, not choosing a firmware strategy.

### `(n Nodes) PlaceMany(ctx context.Context, ps []Placement) ([]Node, error)`

PlaceMany puts several down, then measures the links once.

One warm at the end rather than one per node: nodes.place re-measures the matrix each time, and on a national network that is minutes repeated.

### `(n Nodes) RefreshStats(ctx context.Context) error`

RefreshStats samples what every node is costing, rather than waiting for the window to ask.

### `(n Nodes) Search(ctx context.Context, query string, limit int) ([]NameMatch, error)`

Search finds nodes by name, best first, when you cannot type the name.

Imported names carry emoji and accents - "\U0001F3D4\uFE0F West Lomond \U0001F4E1" is one real node - so matching is done on letters and digits alone, with accents folded and word order ignored. The ranking happens at the workbench rather than here, so this client and the Python one agree about which result is the top one.

An empty result is not an error: "nothing matched" is an answer, and the caller usually wants to widen the query rather than handle a refusal.

### `(n Nodes) Select(ctx context.Context, names []string, add bool) error`

Select replaces the selection, or adds to it.

### `(n Nodes) Selected(ctx context.Context) ([]string, error)`

Selected is who is selected now.

## Node

Node is one node. Live: a handle, not a copy - it holds a name, and asks.

### `(n Node) Build(ctx context.Context) (Build, bool, error)`

SetFirmware changes what it runs.

Applied by default, which means stop, provision, start: firmware is chosen when a node launches, so recording it and leaving the node on its old build is the control somebody presses twice and then distrusts. Pass false to record it for the next start instead - and know that is what you have done. Build is the build this node runs, and false when it is pinned to nothing.

The whole row rather than the version string, because deleting a build or comparing two needs its path and its board, and reassembling those from a version is the kind of guesswork that deletes the wrong file.

### `(n Node) Card(ctx context.Context, c CardChange) (CardSlot, error)`

Card is what is in this node's card slot, and changing it.

A slot is not a fitted card: the board says the slot exists, this says whether it is filled. A firmware marked as needing a card fills the slot whatever this says, because a build that keeps its settings there boots into nothing without one.

### `(n Node) Console() Console`

Console reaches a node's console.

### `(n Node) Delete(ctx context.Context) error`

Delete removes it from the scenario, and re-measures what is left.

### `(n Node) Device() Device`

Device is this node as a device to drive: its screen, buttons and panel.

### `(n Node) Info(ctx context.Context) (NodeInfo, error)`

Info is what the network says about it, now.

### `(n Node) Inject(ctx context.Context) error`

Inject originates a packet without firmware.

It exercises the radio model and the channel; what it does not exercise is relaying, which is a firmware behaviour and needs a firmware.

### `(n Node) Move(ctx context.Context, lat, lon float64) error`

Move puts it somewhere else. The physics moves with it: cached losses for this node are forgotten.

### `(n Node) Name() string`

Name is what it is called, which is also its identity everywhere.

### `(n Node) Output(ctx context.Context, source string, lines int) ([]string, error)`

Output is what this node printed, from one of four voices: "serial" is the board's own port (a native node's standard error), "boot" is the ROM's on a board whose application talks over USB, "emulator" is what QEMU or Renode said about running it, and "radio" is the radio model's log.

The lines, not a count of them. A board that has gone quiet is read by looking at what it last said.

### `(n Node) OutputWindow(ctx context.Context, source string) error`

OutputWindow opens one of this node's logs in a window of its own.

A tab is one pane. What people do while a board is misbehaving is watch its screen and two of its logs together - what the board printed beside what the emulator said about running it - and that needs windows.

### `(n Node) Provisioning(ctx context.Context) ([]string, error)`

Provisioning is what this node is told at boot, in the console's own words.

### `(n Node) Radio(ctx context.Context) (map[string]any, error)`

Radio is what this node's radio is set to - the same thing the workbench shows under Radio: the frequency, spreading factor, bandwidth and the rest the model assumes, and, for a node that is running, what it reports back and where the two differ. The shape is left open because a repeater and a companion answer it differently, and both are worth having whole.

### `(n Node) Running(ctx context.Context) (bool, error)`

Running reports whether its firmware process is up.

### `(n Node) Serve(ctx context.Context, over Transport) (string, error)`

Serve hands this companion to a real client - meshcore-cli, or an app over a bridge - and returns where to point it.

### `(n Node) SetBoard(ctx context.Context, board Board) error`

SetBoard changes what hardware this node is.

A change to the physics rather than a label, so it rebuilds and re-warms - and it clears a firmware pin made for a different board, because that image cannot run on this one and a pin nobody can honour reads as a configured node right up until it refuses to start.

### `(n Node) SetFirmware(ctx context.Context, b Build, apply bool) error`

### `(n Node) SetRegions(ctx context.Context, regions ...string) error`

SetRegions is what it relays for.

### `(n Node) SetTrueRF(ctx context.Context, on bool) error`

SetTrueRF makes this receiver take waveform verdicts whatever the run's mode - the hybrid flag, for measuring one node honestly inside a cheap run.

### `(n Node) Start(ctx context.Context) error`

Start and Stop are its firmware process.

### `(n Node) Stop(ctx context.Context) error`

### `(n Node) Unserve(ctx context.Context) error`

Unserve takes it back.

### `(n Node) WaitRunning(ctx context.Context, timeout time.Duration) error`

WaitRunning waits for its firmware to come up.

Polling, for now. When the socket learns to push this switches underneath and no caller changes - which is why the clients are built before the events rather than after.

### `(n Node) Wipe(ctx context.Context) error`

Wipe puts this board back to factory: its flash, its card, its files.

A board keeps what it was told between runs, as hardware does, so a node configured into a corner stays there until this is called. Refused while it is running, rather than rewriting a flash underneath the emulator holding it.

## Sim

Sim is the run. Live.

### `(s Sim) Pause(ctx context.Context) error`

### `(s Sim) Play(ctx context.Context) error`

Play, Pause and Toggle are the clock itself.

### `(s Sim) Reset(ctx context.Context) error`

Reset puts the clock and the counters back to the start of the run.

### `(s Sim) Run(ctx context.Context, simulated, wait time.Duration) error`

Run advances the mesh's own clock by this much and waits for it to finish.

Simulated time, not yours. Five minutes here is five minutes of the mesh's clock; on 155 emulated nodes that is a great deal longer than five of yours, which is why the wait's own timeout is separate and generous.

### `(s Sim) SetRealFirmware(ctx context.Context, on bool) error`

SetRealFirmware chooses whether play starts MeshCore on every node, or runs the channel with nothing behind it.

### `(s Sim) SetSeed(ctx context.Context, seed uint64) error`

SetSeed fixes the run. Same seed, same scenario, same result - which is what makes a *changed* result mean something.

### `(s Sim) SetStepMs(ctx context.Context, ms uint32) error`

SetStepMs is how much simulated time one tick advances.

### `(s Sim) Settle(ctx context.Context, steps int) error`

Settle steps the engine on a paused run, which is how a command gets the time it needs to be answered without starting the clock.

### `(s Sim) Start(ctx context.Context) error`

Start brings the run up: waits out the warm, starts every node, and plays.

Deliberately not one call to sim.start. That verb is the play button's own handler and answers four ways - it pauses if already playing, declines while links are being measured, or starts firmware and does not play - so a script pressing it once gets whichever of those the moment happens to be in.

Worse, it only starts firmware when *no* node is running. Pin a build onto two nodes of a fifty-eight node fixture and it considers the mesh started, plays with fifty-six of them down, and says nothing.

So this asks for the three things it actually wants, in order, and checks each one. Zero timeouts mean the usual ones.

### `(s Sim) StartWithin(ctx context.Context, warm, firmware time.Duration) error`

StartWithin is Start with the two waits named: how long to give the link measurement, and how long to give the firmware.

### `(s Sim) State(ctx context.Context) (SimState, error)`

State is what the clock is doing.

### `(s Sim) Step(ctx context.Context) error`

Step advances one tick, which is StepMs of simulated time.

### `(s Sim) Toggle(ctx context.Context) error`

### `(s Sim) WaitStopped(ctx context.Context, timeout time.Duration) error`

WaitStopped waits for a run to end.

### `(s Sim) WaitUntil(ctx context.Context, atMs uint32, timeout time.Duration) error`

WaitUntil waits for the mesh's clock to reach a moment.

## Firmware

Firmware is the library. Live.

### `(f Firmware) Build(ctx context.Context, checkout, role, label string) (Job, error)`

Build compiles a MeshCore checkout and puts the results in the library.

Both roles from one call unless one is named, deliberately. A locally built repeater compiled against a stale shim once answered console output with 0x06 where the host expects 0x07: it connected, misbehaved and exited. Two arms of a comparison built at different moments from different trees measure the build process rather than the firmware, so the easy thing to do here is the thing that builds them together.

It returns once the work has started. Wait on it: a MeshCore build is a minute or two per role.

### `(f Firmware) BuildAndWait(ctx context.Context, checkout string, timeout time.Duration) ([]Build, error)`

BuildAndWait is the same, blocking, for a caller with nothing else to do - which is most of them.

### `(f Firmware) Delete(ctx context.Context, b Build) (string, error)`

Delete removes a build from the cache, and says what it removed.

By path, and the workbench refuses any path outside the firmware cache. A build nodes are still pinned to will go: they keep the pin, which then cannot be honoured and fails at start - so move them onto the replacement first.

### `(f Firmware) Details(ctx context.Context, id BuildID) (BuildDetails, error)`

Details is everything known about one build: where it is, what it is, and what has been decided about it.

### `(f Firmware) Download(ctx context.Context, role, version string, board Board) error`

Download fetches one. It returns once the download has been asked for, not once it has landed: wait on the job. role is a plain string here and a Role everywhere else, deliberately: this one names a published release asset, and the catalogue's own spellings are not always the application names the verbs are keyed on. Typing it as Role would have the compiler vouch for something nobody has checked.

### `(f Firmware) Find(ctx context.Context, version string, board Board) (Build, error)`

Find is one build by version, and by board where the version alone is ambiguous - which it is for every board image, because "wadamesh" is not a build until it is wadamesh for a particular piece of hardware.

### `(f Firmware) Import(ctx context.Context, path string, role Role, board Board, label string) (Build, error)`

Import takes a build from a path - the one way a locally built image gets into the library.

label is what the library will know it by and what a node pins. Left empty it is a timestamp, so importing twice gives two builds rather than one that quietly replaced the other - which matters the moment you want to put the new one on a node and delete the old.

### `(f Firmware) Library(ctx context.Context) ([]Build, error)`

Library is every build, published or on disk, with what runs it.

### `(f Firmware) Needed(ctx context.Context) ([]RoleNeed, error)`

Needed is the roles this scenario has nodes for and no build pinned to, with what could be pinned. A run refuses to start until every one is answered.

### `(f Firmware) OnDisk(ctx context.Context) ([]Build, error)`

OnDisk is only the ones this machine actually holds, which is the only thing that decides what a node can run. A build that failed to download and one in daily use look identical from anywhere else.

### `(f Firmware) Scan(ctx context.Context) error`

Scan asks the catalogue what is published, which is how a build nobody has downloaded becomes offerable.

### `(f Firmware) Start(ctx context.Context) error`

Start brings up firmware on every node.

Asynchronous, and always has been: it answers with what it has begun, not with what is up. It was synchronous once, and on 155 nodes that froze the window and the socket together for as long as it was left - which read as a crash and was reported as one. Wait with WaitStarted.

### `(f Firmware) State(ctx context.Context) (FirmwareState, error)`

State is how far a start has got.

### `(f Firmware) Update(ctx context.Context, id BuildID, c BuildChange) (BuildDetails, error)`

Update renames a build, moves it to another board or role, or changes how it is run, and reports it as it now stands.

### `(f Firmware) UseForRole(ctx context.Context, role Role, b Build) error`

UseForRole pins every node of a role to one build.

### `(f Firmware) UseWhatIsHere(ctx context.Context) (map[Role]Build, error)`

UseWhatIsHere pins every role that needs one to the newest build on this machine, and reports what it chose.

What a script wants almost every time: this mesh, whatever this machine holds, rather than a version typed into the script that goes stale. A run refuses to start until every role is answered, so the alternative is the same loop written out in every caller.

It refuses by name when a role has nothing, because "no companion build" is a thing to go and fix rather than a reason to start a mesh with a silent hole in it.

### `(f Firmware) WaitStarted(ctx context.Context, timeout time.Duration) error`

WaitStarted waits for every node's firmware to be up.

Generous by default where a caller passes nothing: real firmware on a large network is minutes, and on emulated boards it is longer. WaitStarted waits for every node's firmware to be up.

Nodes here is the nodes that run firmware, which is not every node: an SDR observer and an emitter never boot one. It used to be every node, so a fixture holding either reported "56 of 58" until the timeout with no way to see which two.

Which is why this names the stragglers rather than counting them. Ten minutes of "56 of 58" tells you nothing; two node names tell you whether a build is missing or a board is wedged.

### `(f Firmware) Window(ctx context.Context, id BuildID) error`

Window opens the build's own window, which is what a click on a library row does. Refused by a workbench with no interface.

## Console

Console is one node's firmware console. Live.

### `(c Console) Ask(ctx context.Context, line string, steps int) (string, error)`

Ask sends a line and waits for the node to answer it.

The important one. A node reads its serial input on its next loop and its loop only runs when the engine steps, so reading straight after sending reads the moment *before* the command was sent - every script that has done this by hand got an empty reply and concluded the console was broken. This gives the mesh its own time first, by stepping when the run is paused.

### `(c Console) Read(ctx context.Context) ([]string, error)`

Read is the scrollback. Read is the scrollback, newest last.

The lines come back under "tail" and "lines" is how many there are in total, so reading "lines" hands you a number where you asked for text. The tail is the last 200; a node up for an hour has thousands and nobody reads the first one.

### `(c Console) Send(ctx context.Context, line string) error`

Send types a line at it.

## Events

Events is what the engine has done. Live.

### `(e Events) Dump(ctx context.Context, path string) (int, error)`

Dump writes every event held to a file, one JSON object per line.

### `(e Events) Recent(ctx context.Context, limit int) ([]Event, error)`

Recent is the tail.

A tail, and only a tail: the store keeps a bounded one because a long run has millions, so a script that needs all of them dumps per round rather than polling this. Reading only the tail after a busy flood samples the most congested moment of it, which is a mistake already made once here.

### `(e Events) Total(ctx context.Context) (int, error)`

Total is how many there have been, which is the cheap question.

### `(e Events) Wait(ctx context.Context, m Match, timeout time.Duration) (Event, error)`

Wait blocks until an event matches, and returns it.

## Boundary

Boundary is the study area, however you have it. Live.

### `(b Boundary) Accept(ctx context.Context, name string) (string, error)`

Accept takes one of the search results into the study area.

Areas union rather than replace: a study is often two council areas rather than one.

### `(b Boundary) List(ctx context.Context) ([]string, error)`

List is what the study area is made of.

### `(b Boundary) Load(ctx context.Context, source, name string) ([]string, error)`

Load takes a study area from GeoJSON: a path, or the document itself.

A Polygon, a MultiPolygon, a Feature or a FeatureCollection. Each polygon becomes an area named from its "name" property, or from name, or from the file.

The one way to study an area nothing has an administrative name for - a catchment, a valley, the bit north of the river - and the only one that works with no network at all.

### `(b Boundary) Prune(ctx context.Context, marginKm float64) (int, error)`

Prune deletes the nodes outside the study area, and says how many went.

For a mesh that was imported before the boundary was set. marginKm is kept on purpose and zero means the session's own: a node just outside still interferes with one just inside, and dropping it makes the inside look quieter than it is.

### `(b Boundary) Remove(ctx context.Context, name string) error`

Remove takes one area back out.

Changes what is measured, never what is loaded: the nodes stay until something prunes them.

### `(b Boundary) Search(ctx context.Context, query string) ([]string, error)`

Search finds places matching a name, best first. Needs the network.

Names rather than geometry: the geometry stays at the workbench, and the name is what Accept takes.

### `(b Boundary) Use(ctx context.Context, area string) ([]string, error)`

Use takes a study area from a place name or from GeoJSON.

The one to call. A path to a .geojson file is loaded; anything else is searched for by name and the best match accepted. Both end with the area in the study, which is the only thing the caller wanted to say.

## Live

Live is a live feed, and the deployment it describes. Live in both senses.

### `(l Live) ApplyRegions(ctx context.Context) (int, error)`

ApplyRegions puts the inferred regions onto the nodes, and says how many took one.

The forgotten step. Everything above can succeed and the mesh still be silent until this runs.

### `(l Live) Commit(ctx context.Context, strategy Strategy) (int, error)`

Commit applies the fetched nodes to the scenario and says how many it now holds.

"replace-all" is the default and is what the shipped fixtures were built with; "add" keeps what is already here and skips names that clash.

Measuring the links afterwards is a job rather than part of this call - 676 nodes is 228,000 terrain paths over real ground - so this returns while that is still running.

### `(l Live) Fetch(ctx context.Context, url string) (ImportPreview, error)`

Fetch reads the deployment and says what would change, changing nothing.

### `(l Live) Infer(ctx context.Context, window, wait time.Duration) error`

Infer reads the feed's recent traffic to work out what each node holds.

This is the step that decides whether anything relays. A node whose regions are unknown forwards nothing, and nothing says so.

window is the feed's own past and zero means DefaultWindow; wait is how long you will sit here for it. A week of ScotMesh is around 150,000 packets and several minutes of paging.

### `(l Live) Pull(ctx context.Context, url string, window, wait time.Duration) (ImportPreview, error)`

Pull fetches, commits, reads the traffic and applies what it implies.

The whole chain, in the order that works. window is how far back into the feed's own history to read - the mesh's past, not your patience - and zero means DefaultWindow. wait is yours.

Link measurement is still running when this returns on anything but a small mesh, so follow it with WaitIdle before starting a run.

### `(l Live) SetSource(ctx context.Context, url string) (string, error)`

SetSource points at a feed without reading it, and reports the URL as the workbench tidied it.

## Assertions

Assertions are what has to be true for a run to have passed. Live.

### `(a Assertions) Add(ctx context.Context, want Assertion) error`

Add records one.

### `(a Assertions) Check(ctx context.Context) (Report, error)`

Check measures every assertion against the run so far.

### `(a Assertions) Delivered(ctx context.Context, atLeast int) error`

Delivered is the common one: at least this many nodes received something.

### `(a Assertions) Sent(ctx context.Context, node string, atLeast, atMost int) error`

Sent bounds what a node - or the whole mesh - transmitted.

AtMost is the interesting one: it is how a relay-suppression change is held to not having made the mesh chattier.

## Schedule

Schedule is what the mesh is told to send, and when. Live.

### `(s Schedule) Add(ctx context.Context, send Send) error`

Add schedules one.

Repeating traffic has worked all along and nothing said so, which to somebody writing a script is the same as it not existing.

### `(s Schedule) Clear(ctx context.Context) error`

Clear forgets all of them.

## Device

Device is a running board a script can look at and prod: read what its display is showing, capture it as an image, press its buttons, type at its keyboard, and touch its panel. All of it works headless - the display is the framebuffer the controller holds, not a picture of anybody's desktop - which is the point: a board test that needs a screen in front of it does not run in CI.

### `(b Device) Press(ctx context.Context, pin int, down bool) error`

Press holds a button pin down, or releases it. Held rather than clicked because the firmware cares: MeshCore wakes a sleeping display on a press and powers the board off on a long one, so a caller times the release itself.

### `(b Device) Screen(ctx context.Context) (Screen, error)`

Screen reads what this board's display is currently showing.

### `(b Device) Screenshot(ctx context.Context) (Shot, error)`

Screenshot writes the board's display to a PNG and returns where it landed. The frame is exactly what the controller holds, at the size it holds it.

### `(b Device) Tap(ctx context.Context, pin int) error`

Tap presses a button and lets go - the ordinary click, for when the hold does not matter.

### `(b Device) TapAt(ctx context.Context, x, y int) error`

TapAt touches a point and lifts off - a tap on the panel.

### `(b Device) Touch(ctx context.Context, x, y int, down bool) error`

Touch puts a finger on the panel at a point (down true) or lifts it off (down false).

### `(b Device) Type(ctx context.Context, text string) error`

Type enters text at the board's own keyboard, one character at a time - which is what the keyboard sends, and what the firmware polls for.

### `(b Device) WaitScreen(ctx context.Context, timeout time.Duration) (Screen, error)`

WaitScreen waits until the display changes from what it shows now and returns the new frame, or fails with what it was still showing when the timeout ran out. This is the honest way to check an input: half duplex eats stimuli - a board handed a packet while transmitting never hears it - so a tap followed by an immediate screen read will intermittently read the frame from before the tap landed. Change is by Digest, so a redraw that keeps the same number of lit pixels still counts.

## Job

Job is a long operation the workbench is doing. Live: a handle to an id.

### `(j Job) Cancel(ctx context.Context) error`

Cancel stops it, where whoever started it left a way to.

A job with no cancel refuses by name rather than silently doing nothing: an operator who asked deserves to be told, not left watching a bar that carries on.

### `(j Job) Info(ctx context.Context) (JobInfo, bool, error)`

Info is where this job has got to, or false when it is no longer listed - which means finished, because a job that has ended is removed.

### `(j Job) Wait(ctx context.Context, timeout time.Duration) error`

Wait blocks until it is gone from the list.

## Enumerations

### Board

Board is a hardware profile this build knows about.

- `BoardEbyteEoRaS3` — `"Ebyte_EoRa-S3"` · Ebyte_EoRa-S3: ESP32-S3, SX1262, by Ebyte.
- `BoardGenericE22Sx1262` — `"Generic_E22_sx1262"` · Generic_E22_sx1262: ESP32, SX1262, by Ebyte.
- `BoardHeltecE213` — `"Heltec_E213"` · Heltec_E213: ESP32-S3, SX1262, by Heltec.
- `BoardHeltecE290` — `"Heltec_E290"` · Heltec_E290: ESP32-S3, SX1262, by Heltec.
- `BoardHeltecWSL3` — `"Heltec_WSL3"` · Heltec_WSL3: ESP32-S3, SX1262, by Heltec.
- `BoardHeltecWirelessPaper` — `"Heltec_Wireless_Paper"` · Heltec_Wireless_Paper: ESP32-S3, SX1262, by Heltec.
- `BoardHeltecWirelessTracker` — `"Heltec_Wireless_Tracker"` · Heltec_Wireless_Tracker: ESP32-S3, SX1262, by Heltec.
- `BoardHeltecMeshSolar` — `"Heltec_mesh_solar"` · Heltec_mesh_solar: nRF52840, SX1262, by Heltec.
- `BoardHeltecT096` — `"Heltec_t096"` · Heltec_t096: nRF52840, SX1262, by Heltec.
- `BoardHeltecT114` — `"Heltec_t114"` · Heltec_t114: nRF52840, SX1262, by Heltec.
- `BoardHeltecV2` — `"Heltec_v2"` · Heltec_v2: ESP32, SX1276, by Heltec.
- `BoardHeltecV3` — `"Heltec_v3"` · Heltec_v3: ESP32-S3, SX1262, by Heltec.
- `BoardLilyGoT3S3Sx1262` — `"LilyGo_T3S3_sx1262"` · LilyGo_T3S3_sx1262: ESP32-S3, SX1262, by LILYGO.
- `BoardLilyGoTBeam1W` — `"LilyGo_TBeam_1W"` · LilyGo_TBeam_1W: ESP32-S3, SX1262, by LILYGO.
- `BoardLilyGoTDeck` — `"LilyGo_TDeck"` · LilyGo_TDeck: ESP32-S3, SX1262, by LILYGO.
- `BoardRAK3112` — `"RAK_3112"` · RAK_3112: ESP32-S3, SX1262, by RAKwireless.
- `BoardRAK4631` — `"RAK_4631"` · RAK_4631: nRF52840, SX1262, by RAKwireless.
- `BoardStationG2` — `"Station_G2"` · Station_G2: ESP32-S3, SX1262, by LILYGO.
- `BoardStationG3ESP32` — `"Station_G3_ESP32"` · Station_G3_ESP32: ESP32-S3, SX1262, by LILYGO.
- `BoardTbeamSX1262` — `"Tbeam_SX1262"` · Tbeam_SX1262: ESP32, SX1262, by LILYGO.
- `BoardXiaoS3` — `"Xiao_S3"` · Xiao_S3: ESP32-S3, SX1262, by Seeed.
- `BoardXiaoS3WIO` — `"Xiao_S3_WIO"` · Xiao_S3_WIO: ESP32-S3, SX1262, by Seeed.
- `BoardXiaoNrf52` — `"Xiao_nrf52"` · Xiao_nrf52: nRF52840, SX1262, by Seeed.
- `BoardHeltecTrackerV2` — `"heltec_tracker_v2"` · heltec_tracker_v2: ESP32-S3, SX1262, by Heltec.
- `BoardHeltecV4` — `"heltec_v4"` · heltec_v4: ESP32-S3, SX1262, by Heltec.

### Class

Class is what happened to an event.

- `ClassSent` — `"sent"` · ClassSent is this node transmitted it.
- `ClassReceived` — `"received"` · ClassReceived is this node decoded it, for the first time.
- `ClassHalfDuplex` — `"half-duplex"` · keyed; LoRa is half duplex.
- `ClassInterference` — `"interference"` · ClassInterference is would have decoded, but a stronger signal took it.
- `ClassFloor` — `"floor"` · spreading factor.

### Kind

Kind is what a node is.

- `SimpleRepeater` — `"simple-repeater"` · SimpleRepeater forwards, and nothing else.
- `AdvancedRepeater` — `"advanced-repeater"` · AdvancedRepeater forwards, serves clients, holds state.
- `Companion` — `"companion"` · Companion a user's device - the thing a phone connects to.
- `RoomServer` — `"room-server"` · mesh that treats one as a repeater overstates its own reach.
- `SDRObserver` — `"sdr-observer"` · field at its antenna and hands back IQ.
- `Emitter` — `"emitter"` · terrain as everything else.

### Preset

Preset is a named set of LoRa parameters for a territory.

- `PresetAustralia` — `"Australia"` · Australia: 915.800 MHz, 250.0 kHz, SF10, CR 4/5.
- `PresetAustraliaNarrow` — `"Australia (Narrow)"` · Australia (Narrow): 916.575 MHz, 62.5 kHz, SF7, CR 4/8.
- `PresetAustraliaMid` — `"Australia (Mid)"` · Australia (Mid): 915.075 MHz, 125.0 kHz, SF9, CR 4/5.
- `PresetAustraliaSAWA` — `"Australia: SA, WA"` · Australia: SA, WA: 923.125 MHz, 62.5 kHz, SF8, CR 4/8.
- `PresetAustraliaQLD` — `"Australia: QLD"` · Australia: QLD: 923.125 MHz, 62.5 kHz, SF8, CR 4/5.
- `PresetBrazil` — `"Brazil"` · Brazil: 923.125 MHz, 62.5 kHz, SF8, CR 4/8.
- `PresetEUUKNarrow` — `"EU/UK (Narrow)"` · EU/UK (Narrow): 869.618 MHz, 62.5 kHz, SF8, CR 4/8.
- `PresetEUUKDeprecated` — `"EU/UK (Deprecated)"` · EU/UK (Deprecated): 869.525 MHz, 250.0 kHz, SF11, CR 4/5.
- `PresetCzechRepublicNarrow` — `"Czech Republic (Narrow)"` · Czech Republic (Narrow): 869.432 MHz, 62.5 kHz, SF7, CR 4/5.
- `PresetEU433MHzLongRange` — `"EU 433MHz (Long Range)"` · EU 433MHz (Long Range): 433.650 MHz, 250.0 kHz, SF11, CR 4/5.
- `PresetEU433MHzNarrow` — `"EU 433MHz (Narrow)"` · EU 433MHz (Narrow): 433.650 MHz, 62.5 kHz, SF8, CR 4/8.
- `PresetNetherlands` — `"Netherlands"` · Netherlands: 869.618 MHz, 62.5 kHz, SF7, CR 4/5.
- `PresetNewZealand` — `"New Zealand"` · New Zealand: 917.375 MHz, 250.0 kHz, SF11, CR 4/5.
- `PresetNewZealandNarrow` — `"New Zealand (Narrow)"` · New Zealand (Narrow): 917.375 MHz, 62.5 kHz, SF7, CR 4/5.
- `PresetPortugal433` — `"Portugal 433"` · Portugal 433: 433.375 MHz, 62.5 kHz, SF9, CR 4/6.
- `PresetPortugal868` — `"Portugal 868"` · Portugal 868: 869.618 MHz, 62.5 kHz, SF7, CR 4/6.
- `PresetSwitzerland` — `"Switzerland"` · Switzerland: 869.618 MHz, 62.5 kHz, SF8, CR 4/8.
- `PresetUSACanadaRecommended` — `"USA/Canada (Recommended)"` · USA/Canada (Recommended): 910.525 MHz, 62.5 kHz, SF7, CR 4/5.
- `PresetVietnamNarrow` — `"Vietnam (Narrow)"` · Vietnam (Narrow): 920.250 MHz, 62.5 kHz, SF8, CR 4/5.
- `PresetVietnamDeprecated` — `"Vietnam (Deprecated)"` · Vietnam (Deprecated): 920.250 MHz, 250.0 kHz, SF11, CR 4/5.

### Role

Role is the MeshCore application a node runs, named as upstream names its example directory. The string every firmware verb is keyed on. The published catalogue spells some of the same things differently - "repeater", "room-server" - and those belong to the release assets; typing one at a verb pins nothing and the run refuses to start with no clue as to why.

- `RoleSimpleRepeater` — `"simple_repeater"` · only in configuration.
- `RoleCompanionRadio` — `"companion_radio"` · RoleCompanionRadio is a user's device - the thing a phone connects to.
- `RoleSimpleRoomServer` — `"simple_room_server"` · not forward.
- `RoleCompanionRadioUSB` — `"companion_radio_usb"` · where a board publishes both transports at one version.
- `RoleCompanionRadioBLE` — `"companion_radio_ble"` · only.

### Strategy

Strategy is how an imported deployment meets what is already loaded.

- `Replace` — `"replace-all"` · shipped fixtures were built with.
- `Add` — `"add"` · Add is keep what is loaded and add the names it has not got.

### Tab

Tab is a pane of a node's own window.

- `TabConsole` — `"Console"` · TabConsole is the firmware's text console, which only a repeater has.
- `TabCompanion` — `"Companion"` · TabCompanion is channels, contacts and the companion command line.
- `TabSDR` — `"SDR"` · TabSDR is an observer's antenna: serve it, read the address.
- `TabSettings` — `"Settings"` · TabSettings is what this node is: identity, radio, regions, firmware.
- `TabRadio` — `"Radio"` · TabRadio is what the chip is really doing.
- `TabStats` — `"Stats"` · TabStats is what it has cost and what it has carried.
- `TabActivity` — `"Activity"` · TabActivity is what it has heard and sent, in order.
- `TabConnect` — `"Connect"` · TabConnect is hand this companion to a real client.
- `TabHardware` — `"Hardware"` · grows it.
- `TabOutput` — `"Output"` · running it, or the radio model beside it.

### Transport

Transport is how a served companion is reached.

- `OverTCP` — `"tcp"` · one to point a phone or another machine at.
- `OverSerial` — `"serial"` · OverSerial is a pseudo-terminal, for a client that wants a serial port.

## Errors

### ProtocolMismatch

ProtocolMismatch is a client and a workbench that cannot speak to each other, reported at connect rather than discovered later.

```
Client    int
Workbench Hello
```

### Refused

Refused is one verb's refusal: what was asked, what came back, and its kind.

```
Verb string
Code control.Code
// Message is the workbench's own words, unaltered.
Message string
// Has unexported fields.
```

### Timeout

Timeout is a wait that ran out, saying what it was waiting for and what the state actually was.

Not a bare deadline error: "timeout" in a CI log tells whoever reads it nothing, and the state at the moment it gave up is the only thing that does.

```
What  string
After time.Duration
// Last is what the final check saw.
Last string
```

## Values

### Assertion

Assertion is one claim, in the general form.

```
// Kind is what is being counted. AssertDelivered and AssertSent are the
// ones this build understands; one it does not is a failure rather than a
// pass, because a green run that checked nothing is the worst outcome
// available here.
Kind    string
Node    string
AtLeast int
AtMost  int
MaxPct  float64
Within  time.Duration
```

### Build

Build is one firmware image, as the library sees it. Snapshot.

Version, board and role travel together because a board image is not a build on its own: "wadamesh" means nothing until it is wadamesh for a LilyGo_TDeck, built as a companion. A host build carries neither of the other two.

```
Role    Role   `json:"role"`
Version string `json:"version"`
Board   Board  `json:"board"`
Bytes   int64  `json:"bytes"`
OnDisk  bool   `json:"on_disk"`
Path    string `json:"path"`
InUse   int    `json:"in_use"`
// Unavailable marks a build that exists only because nodes are pinned to
// it: nothing on disk, nothing published. Pinning to one succeeds and then
// fails at start, which reads as the library losing builds rather than as
// a pin nobody can honour.
Unavailable bool `json:"unavailable"`
```

- `(b Build) Describe() string` — Describe is how this build is named where a person will read it.

- `(b Build) ID() BuildID` — ID is the identity of a build already in hand.

### BuildChange

BuildChange is what to change about a build. Every field left at its zero value is left alone, which is why the settings are pointers: "leave this setting" and "turn it off" are different answers, and a bool cannot say both.

```
// Label, NewRole and NewBoard rename the build, which moves the file: the
// name is the identity, because a board image is stored as
// <board>/<role>@<label>.bin and nothing else records what it is. Nodes
// pinned to the old name are repointed, or they would fail at their next
// start with "no image in the cache" about a build sitting in the library
// under its new name.
Label    string
NewRole  Role
NewBoard Board
CoprocAtReset *bool
CardRequired  *bool
Notes         *string
```

### BuildDetails

BuildDetails is one build in full: what a library row cannot hold.

Separate from Build because the library is deliberately a list - role, version, size, a tick. Where the file actually is, whether it is a whole flash image or half of one, and what has been decided about how it runs are the questions somebody has once a build does not do what they expected.

```
Role    Role   `json:"role"`
Version string `json:"version"`
Board   Board  `json:"board"`
// Native marks a build for this machine rather than an image for a board.
// The two are not interchangeable and only one of them can be renamed.
Native bool   `json:"native"`
OnDisk bool   `json:"on_disk"`
Path   string `json:"path"`
// SettingsPath is where the settings below are written, named whether or
// not any exist: "where does this live" is asked of a build that has none
// as often as of one that has.
SettingsPath string `json:"settings_path"`
Bytes        int64  `json:"bytes"`
Modified     string `json:"modified"`
InUse        int    `json:"in_use"`
// Kind is what reading the front of the image says it is, and Bootable
// whether a board could start from it. An application-only image imports,
// lists and pins exactly like a whole one and then starts nothing.
Kind     string `json:"kind"`
Bootable bool   `json:"bootable"`
FlashMB  int    `json:"flash_mb"`
// CoprocAtReset, CardRequired and Notes are kept beside the image, so
// they follow this build rather than the board it runs on.
CoprocAtReset bool `json:"coproc_at_reset"`
// CardRequired says this firmware will not get far without storage in the
// board's slot, so every node running it is given a card whatever its own
// slot was set to.
CardRequired bool   `json:"card_required"`
Notes        string `json:"notes"`
```

- `(b BuildDetails) Describe() string` — Describe is how this build is named where a person will read it.

### BuildID

BuildID says which build a call means.

All three names travel together where they are known, so a call cannot land on a different build that happens to share a label. Version alone is accepted and the workbench refuses it when it is ambiguous, rather than guessing - acting on the wrong build is a rename of somebody else's image.

```
Version string
Role    Role
Board   Board
```

### CardChange

CardChange is what to change about a node's card. Nil leaves a field alone, which is why the two that can be turned off are pointers: "leave this" and "take the card out" are different answers and a bool cannot say both.

```
Fitted *bool
// File hands the node a card of its own - shared between runs, or
// prepared in advance. A pointer to the empty string returns it to its
// own, named after it and kept beside its flash.
File *string
Wipe bool
```

### CardSlot

CardSlot is what is in one node's card slot.

A slot is not a fitted card: the board says the slot exists, the node says whether it is filled, and a firmware that keeps its settings on a card fills it regardless.

```
Node string `json:"node"`
// Slot is "" for the board's own answer, "fitted" or "empty" for a
// decision somebody made about this node.
Slot   string `json:"slot"`
Fitted bool   `json:"fitted"`
// File is the card this node uses, and OwnFile the one it would use if it
// had been handed none.
File    string `json:"file"`
OwnFile string `json:"own_file"`
Bytes   int64  `json:"bytes"`
// RequiredByFirmware says the build fills the slot whatever the node
// asked for; BoardHasSlot that there is a slot at all.
RequiredByFirmware bool `json:"required_by_firmware"`
BoardHasSlot       bool `json:"board_has_slot"`
Wiped              bool `json:"wiped"`
```

### Check

Check is one assertion, and what the run made of it.

```
Kind   string `json:"kind"`
Node   string `json:"node"`
Passed bool   `json:"pass"`
Got    string `json:"got"`
Want   string `json:"want"`
```

- `(c Check) String() string`

### Checkpoint

Checkpoint is what a save reports back.

```
Name  string `json:"checkpoint"`
Path  string `json:"path"`
NowMs uint32 `json:"now_ms"`
Nodes int    `json:"nodes"`
```

### Describe

Describe is the cheap summary. Snapshot.

```
Nodes   int    `json:"nodes"`
Seed    uint64 `json:"seed"`
NowMs   uint32 `json:"now_ms"`
Playing bool   `json:"playing"`
```

### Event

Event is one thing the engine did. Snapshot.

The frame bytes are deliberately absent: a long run has millions of these, and the one packet somebody wants is asked for by id.

```
AtMs      uint32 `json:"at_ms"`
Kind      string `json:"kind"`
From      string `json:"from"`
To        string `json:"to"`
MessageID uint64 `json:"message_id"`
PacketID  uint64 `json:"packet_id"`
// SNRdB is null on the wire for an infinite ratio - a reception with no
// noise at all - so it is a pointer here. Absent is not zero.
SNRdB  *float64 `json:"snr_db"`
Detail string   `json:"detail"`
Class  Class    `json:"class"`
```

### FirmwareState

FirmwareState is how far a start has got. Snapshot.

```
Running int `json:"running"`
// Nodes is the nodes that run firmware, which is not every node: an SDR
// observer and an emitter never boot one. Comparing Running against the
// scenario's size is how a wait ends up asking for 58 of 58 on a mesh
// where only 56 can ever start.
Nodes    int  `json:"nodes"`
Total    int  `json:"total"`
Starting bool `json:"starting"`
```

### Hello

Hello is what a connection is talking to. Snapshot, read once at connect.

```
Protocol int    `json:"protocol"`
Version  string `json:"version"`
// Mode is "workbench" or "headless".
Mode   string `json:"mode"`
Socket string `json:"socket"`
Verbs  int    `json:"verbs"`
// PID and StartedAt tell a restart from a reconnect. The scenario does
// not survive a restart, so a script picking up a session it did not
// start has to be able to ask.
PID       int       `json:"pid"`
StartedAt time.Time `json:"started_at"`
```

### ImportPreview

ImportPreview is what a fetch found, before anything has been changed.

SkippedNoPosition and Uncertain are the two worth reading before committing. A node with no position cannot be simulated at all, and an uncertain one is being placed to within kilometres - the answer it gives is that vague too, however confident the rest of the output looks.

```
Records           int `json:"records"`
Nodes             int `json:"nodes"`
SkippedNoPosition int `json:"skipped_no_position"`
Uncertain         int `json:"uncertain"`
```

- `(p ImportPreview) String() string`

### JobInfo

JobInfo is a long operation in flight. Snapshot; ask again for progress, or use Job.Wait.

```
ID       string `json:"id"`
What     string `json:"what"`
Done     int    `json:"done"`
Total    int    `json:"total"`
Finished bool   `json:"finished"`
// Failed marks a job that ended without doing what it was for. Separate
// from Finished because a waiter needs both: "stop waiting" and "this did
// not work" are different answers, and telling them apart by reading What
// means matching on prose.
Failed bool `json:"failed"`
```

### Journal

Journal is the command history: when the process started, and the commands since, newest last. Polls and the workers' own progress reports are left out, so this is how the world got here, not everything that touched the socket.

```
StartedMs int64          `json:"started_ms"`
Count     int            `json:"count"`
Entries   []JournalEntry `json:"entries"`
```

### JournalEntry

JournalEntry is one command the workbench was driven with: its sequence, the wall-clock time it ran, the verb, and a compact rendering of its argument.

```
Seq   uint64 `json:"seq"`
AtMs  int64  `json:"at_ms"`
Verb  string `json:"verb"`
Nodes int    `json:"nodes"`
Err   string `json:"err,omitempty"`
Arg   string `json:"arg,omitempty"`
```

### Match

Match is what an event has to be for Wait to stop.

Empty fields match anything, so waiting for "any reception at Glenrothes" is Match{Kind: "rx", To: "Glenrothes"} and not a predicate somebody has to write.

```
Kind string
From string
To   string
```

### NameMatch

NameMatch is one answer from a name search, and how sure it is.

Score runs 0 to 1, ranked best first by the workbench. It exists so a script can tell "found it" from "found something that shares a word": a top result at 0.3 is a prompt to look at the list, not a node to start talking to.

```
Name     string  `json:"name"`
Score    float64 `json:"score"`
Kind     Kind    `json:"kind"`
Lat, Lon float64 `json:"-"`
```

- `(m NameMatch) String() string`

### Neighbour

Neighbour is one node near another, with how far away it is.

```
Name     string  `json:"name"`
Km       float64 `json:"km"`
Kind     Kind    `json:"kind"`
Lat, Lon float64 `json:"-"`
```

- `(n Neighbour) String() string`

### NodeInfo

NodeInfo is what a network is, per node. Snapshot: take another with Nodes.List when something has changed it.

What a node is *doing* - running, its memory, its counters - is NodeStat, because the two change on completely different timescales and the store publishes them separately.

```
Name     string   `json:"name"`
Kind     Kind     `json:"kind"`
Lat      float64  `json:"lat"`
Lon      float64  `json:"lon"`
HeightM  float64  `json:"height_m"`
TxDBm    float64  `json:"tx_dbm"`
Regions  []string `json:"regions"`
Firmware string   `json:"firmware"`
// Board is what the node is; FirmwareBoard is what its image was built
// for. They agree most of the time and come apart the moment a host build
// is pointed at a T-Deck, which is an ordinary thing to do.
Board         Board  `json:"board"`
FirmwareBoard string `json:"firmware_board"`
Sent          int    `json:"sent"`
Heard         int    `json:"heard"`
Selected      bool   `json:"selected"`
```

### NodeStat

NodeStats is what every node is costing and doing. Snapshot.

Separate from NodeInfo because one is what the network *is* and the other is what it is *doing*: they change on different timescales and the store publishes them apart.

```
Name     string `json:"name"`
Backend  string `json:"backend"`
Firmware string `json:"firmware"`
Running  bool   `json:"running"`
State    string `json:"state"`
Board    string `json:"board"`
PID      int    `json:"pid"`
RSSBytes int64  `json:"rss_bytes"`
CPUms    int64  `json:"cpu_ms"`
Sent     int    `json:"sent"`
Heard    int    `json:"heard"`
```

### Notification

Notification is one server-pushed event on a Subscription. Named apart from the log's Event, which is a different thing entirely: an Event is a record of something that happened in the simulation, a Notification is the socket telling this connection about a change as it lands.

### Placement

Placement is a node to put down.

```
Name     string
Kind     Kind
Lat, Lon float64
// HeightM and TxDBm default to the scenario's own defaults when zero -
// ten metres and 22 dBm - rather than to nothing.
HeightM float64
TxDBm   float64
// Board is the hardware this node is, by profile name. Empty is a host
// build. A name nothing matches is refused rather than ignored: the board
// decides the transmit ceiling, the noise figure and the battery, so a
// silent fallback would be a different node answering the question.
Board Board
```

### Provenance

Provenance is what a measurement was measured under.

Carried with any result that is a number about the world, because a scripted number gets pasted into a report with the caveats stripped. The caveats have to be in the value.

```
// RFMode is "calculated" or "waveform".
RFMode string `json:"rf_mode"`
// ExcessLossDB is the calibration term in force, and Calibrated says it
// was fitted against real receptions rather than left at the default.
ExcessLossDB float64 `json:"excess_loss_db"`
Calibrated   bool    `json:"calibrated"`
Seed         uint64  `json:"seed"`
```

- `(p Provenance) String() string` — String is one line, meant to be printed above any number a script emits.

### Report

Report is what a run passed and failed, with what it was measured under.

```
Passed int     `json:"passed"`
Total  int     `json:"total"`
Checks []Check `json:"results"`
// Provenance is what the numbers were measured under, carried with the
// verdict because a delivery figure without it is the number this project
// exists not to publish.
Provenance Provenance `json:"-"`
```

- `(r Report) Failures() []Check` — Failures are the ones that did not hold.

- `(r Report) OK() bool` — OK reports whether every assertion held.

- `(r Report) String() string`

- `(r Report) WriteJUnit(path, suite string) error` — WriteJUnit writes a JUnit file, with the caveats inside it.

### Restored

Restored is what a restore reports: where it landed, and whether it is still replaying to get there.

```
Name     string `json:"restored"`
Nodes    int    `json:"nodes"`
NowMs    uint32 `json:"now_ms"`
TargetMs uint32 `json:"target_ms"`
// Replaying is true while the run is stepping forward to the checkpoint's
// time; wait on the sim reaching TargetMs to know it has arrived.
Replaying bool `json:"replaying"`
```

### RoleNeed

RoleNeed is one role with nothing to run. Snapshot.

```
Role    Role     `json:"role"`
Nodes   int      `json:"nodes"`
Choices []string `json:"choices"`
```

### Screen

Screen is what a board's display is showing, as numbers rather than a picture. Enough to answer "did anything change" after a press or a touch; for the picture itself, use Screenshot.

```
// HasScreen is false when the board has drawn nothing yet, or has no
// display at all - the other fields are meaningless then.
HasScreen bool `json:"has_screen"`
Width     int  `json:"width"`
Height    int  `json:"height"`
BPP       int  `json:"bpp"`
On        bool `json:"on"`
// Lit is how many framebuffer bytes are non-zero - how much is lit.
Lit int `json:"lit"`
// Digest identifies the frame: two screens with the same Digest are the
// same picture, which Lit cannot promise. It is what WaitScreen watches.
Digest string `json:"digest"`
```

### Send

Send is one scheduled line at a node.

At and Every are durations of the mesh's own clock, not yours. The verb underneath takes milliseconds; nobody writing a script should have to.

```
Node    string
Command string
At      time.Duration
// Every repeats it. Zero sends once.
Every time.Duration
```

### Shot

Shot is a captured display: a PNG written under the node's own work directory, with the frame's dimensions.

```
Path   string `json:"path"`
Width  int    `json:"width"`
Height int    `json:"height"`
BPP    int    `json:"bpp"`
On     bool   `json:"on"`
```

### SimState

SimState is the clock. Snapshot.

```
Playing bool   `json:"playing"`
NowMs   uint32 `json:"now_ms"`
UntilMs uint32 `json:"until_ms"`
Events  int    `json:"events"`
StepMs  uint32 `json:"step_ms"`
Seed    uint64 `json:"seed"`
```

### Subscription

Subscription is a live stream of notifications, on a connection of its own so it never interleaves with this workbench's request/response calls.

## Options and functions

### Option

Option configures a connection.

- `Args(a ...string) Option` — Args passes extra flags to a launched process.

- `Binary(path string) Option` — Binary names the meshbench executable to launch. The default is whatever "meshbench" resolves to on PATH.

- `Fixture(name string) Option` — Fixture opens a network as the session starts.

- `LogTo(f *os.File) Option` — LogTo sends a launched process's stderr somewhere. The default is this process's own, because a scripted run that fails silently is the worst of both worlds.

- `Seed(n uint64) Option` — Seed fixes the run's seed. Same seed, same scenario, same result - which is what makes a changed result mean something.

- `Socket(path string) Option` — Socket chooses which socket to use, rather than the per-user default.

- `StartTimeout(d time.Duration) Option` — StartTimeout bounds how long Launch and Headless wait for the socket.

### `CodeOf(err error) control.Code`

CodeOf reads the workbench's classification off an error, for a caller that wants the code rather than the sentinel.

<!-- END GENERATED API -->
