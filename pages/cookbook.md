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

Pick one below. Each opens into the steps it is made of, one at a time, with the
reason for each; and every example carries a button to switch the language — the
same task in Python and Go, and Node where it exists, side by side so the shape
shows through the syntax. The first three — a board on show, a local build on
two nodes, and a small mesh with traffic — are the ones to start from.

{{app}}

## What a scripted result still is

Everything on the [limits page](what-it-does-not-do.html) applies to a script's
output exactly as it does to the application's: a simulated result is a best
case, kinder than the air. A number a script prints is worth no more than the
same number read off the screen, and the caveats travel with it. The
[Scripting a session](scripting.html) page ends on the two limits that belong to
scripting itself — reproducibility, and what a script cannot see.
