<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/meshbench-logo-white-800.png">
  <img alt="MeshBench" src="brand/meshbench-logo-staged-800.png" width="800">
</picture>

The source of the **[MeshBench documentation site](https://meshbench.github.io/docs/)**.

## What this is

Markdown in `pages/`, one page per file, built into a static site by
`gen.py`: shared navigation, search, the method tabs, syntax highlighting and
a link checker, with no framework and nothing to install. Every push to
`main` deploys.

```console
python3 gen.py
```

The build refuses to ship a broken internal link, a dead anchor, or a
duplicate heading id.

## What is generated, and from where

Some pages are written by tools rather than by hand, so they cannot drift
from the code they describe. `gen.py` fails the build if a reachable
MeshBench checkout disagrees with what is committed.

| page | source | regenerate with |
|---|---|---|
| `what-it-does-not-do.md` | `docs/shortcomings.md` in the main repository | `tools/sync-limits.py` |
| `reference-cli.md` | `docs/cli-reference.md` in the main repository, itself generated from the flag declarations | `tools/sync-cli.py` |
| `reference-control.md` (verb list) | `internal/app/session` | `tools/sync-verbs.py` |
| `reference-python.md` | the Python client's docstrings | `tools/sync-api-python.py` |
| `reference-go.md` | `go doc` over the Go client | `tools/sync-api-go.py` |
| `reference-js.md` | the Node client's JSDoc | `tools/sync-api-js.py` |

Point them at a checkout with `MESHBENCH_REPO=/path/to/meshbench`.

## Writing rules

[`CLAUDE.md`](CLAUDE.md) holds the register: present tense, third person,
British English, no em-dashes, no selling, the limits admitted in the same
breath as the claim. Screenshots are window-only captures from the running
application, reviewed before commit; instructional marks are drawn by
`tools/annotate.py`.

Every how-to leads with the workbench. The control socket, Python and Go are
tabs on the same block, so a reader picks a method once and the whole site
follows.

## Related

[`MeshBench/meshbench`](https://github.com/MeshBench/meshbench) is the
application this site documents;
[`MeshBench/meshbench-reports`](https://github.com/MeshBench/meshbench-reports)
publishes the studies run with it.
