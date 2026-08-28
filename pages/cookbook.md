# The scripting cookbook

Seven runnable programs, the same seven in each client, that do a whole task
end to end rather than showing one call. They are the worked answers behind
[Scripting a session](scripting.html): read that for how a session is opened
and what a verb is, then come here for a shape close to what you want and change
it.

They live beside the clients they use, in the
[meshbench repository](https://github.com/MeshBench/meshbench):

```
pkg/client-go/examples/          pkg/client-python/examples/
```

The two sets match one for one, done idiomatically in each language rather than
one reading as a translation of the other — where one is awkward, that is a
fault in the client, not the language.

## Why they are programs, not snippets

An example pasted into a page goes stale the first time the API moves, and
nobody notices until they try it. These do not, because the build compiles
them:

- **`go build ./...` compiles every Go example.** One that stops compiling is a
  red build, found by CI, not by you.
- **`headless-regression` is run by CI** — no display, no GPU, no toolkit — so
  the one example a pipeline depends on is exercised on every change, not just
  compiled.

That is the rule the cookbook is designed around: a broken example should break
a build, never a study.

## Running one

Each Go example is a program in its own directory; each Python example is a
file. Both need `meshbench` on `PATH`, or `MESHBENCH_BINARY` naming one.

```
go run ./pkg/client-go/examples/small-mesh-with-traffic
python3 pkg/client-python/examples/03_small_mesh_with_traffic.py
```

Most open the workbench and are meant to be watched. `headless-regression` is
the exception — it opens no window and exits non-zero on a regression, which is
what makes it the one for CI:

```
go run ./pkg/client-go/examples/headless-regression fife-strict results.xml
```

Two of them — `two-nodes-on-a-local-build` and `replace-a-board-build` — attach
to a session already open at the default address rather than starting another,
so running one a second time carries on from where it left off instead of
building the scenario again.

## The seven

| Go directory · Python file | What it does | Needs |
|---|---|---|
| `blank-setup-with-a-board` · `01_blank_setup_with_a_board.py` | A blank setup, a companion set to a LilyGo T-Deck running wadamesh, its window open on Hardware. | a display |
| `two-nodes-on-a-local-build` · `02_two_nodes_on_a_local_build.py` | A fixture trimmed to two companions in Scotland, both on a build made from a MeshCore checkout; re-runnable, so a rebuilt firmware swaps in without rebuilding the scenario. | a display, a checkout |
| `small-mesh-with-traffic` · `03_small_mesh_with_traffic.py` | Two repeaters and two companions, one a T-Deck; a message to the public channel every twenty seconds, with a node window open to watch it arrive. | a display |
| `headless-regression` · `04_headless_regression.py` | The one CI runs: assertions over a shipped network, JUnit output, a non-zero exit on regression. No display. | — |
| `two-builds-in-one-scenario` · `05_two_builds_in_one_scenario.py` | The A/B: two firmware builds on two nodes under one seed, so a behaviour change is the build and not the luck of the draw. | a display, two builds |
| `live-import-and-advert` · `06_live_import_and_advert.py` | A real mesh pulled from its live feed into a study area, one node found by name, an advert sent from it. | a display, the network |
| `replace-a-board-build` · `07_replace_a_board_build.py` | Build a board image from its own repository, put the new image on a node, delete the old one; re-runnable. | a display, a checkout |

The first three are the examples asked for when scripting was
specified — a board on show, a local build on two nodes, and a small mesh with
traffic — and they are the ones to start from.

## What a scripted result still is

Everything on the [limits page](what-it-does-not-do.html) applies to a script's
output exactly as it does to the application's: a simulated result is a best
case, kinder than the air. A number a script prints is worth no more than the
same number read off the screen, and the caveats travel with it. The
[Scripting a session](scripting.html) page ends on the two limits that belong to
scripting itself — reproducibility, and what a script cannot see.
