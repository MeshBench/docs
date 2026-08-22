# What the build enforces

MeshBench's limits are mechanical rather than advisory, because taste does not
survive scale. This is what actually fails a build, what only reports, and why
each one exists.

## On every pull request

| gate | what it refuses |
|---|---|
| `gofmt -l` | any file not formatted |
| `go vet` | the compiler's own suspicions |
| `golangci-lint` + ratchet | any *increase* in findings — see below |
| `go test ./...` | a failing test, across four parallel shards |
| conflict markers | `<<<<<<<`, `=======` or `>>>>>>>` committed in source |
| file length | over 500 lines without an exemption naming its reason |
| tracked build artifacts | a compiled binary or coverage profile in the index |
| the layout map | a package with no entry, or an entry with no package |
| the licence inventory | a dependency change that has not regenerated it |

The last three are recent, and each was added after the thing it checks had
already gone wrong once.

## The lint ratchet

Twenty linters run, not the eight that ran historically and not all 104. The
enabled set is those whose findings are worth acting on here, each with its
reason recorded in `.golangci.yml`.

Running the bug-class linters for the first time produced 477 findings. Turning
that into a red build would have meant 477 unreviewed changes at once, so the
count is held at a baseline instead:

```
tools/lint-ratchet.sh            compare against the baseline
tools/lint-ratchet.sh --update   rewrite it, after clearing something
```

A **new** finding fails the pull request that introduces it. The backlog is
cleared deliberately, one class at a time, and each clearing tightens
`.golangci-baseline.txt` in the same commit as the fix that earned it.

Four `gosec` rules are excluded with the reason stated in the file. `G115`,
integer overflow on conversion, is the notable one: in the RF packages those
need auditing by hand rather than by rule, because a truncated sample index
produces a plausible waterfall and slightly wrong sensitivity, which no
automatic check distinguishes from a safe cast.

**The linter version matters.** Different versions disagree about this tree by
tens of findings, so the baseline is only meaningful against the version
`ci.yml` pins. Use that one.

## The race detector

Not on every push — it multiplies an already slow suite by enough that the wait
becomes the thing people notice about the pipeline, and a check nobody waits for
is a check that gets worked around.

It runs when a `v*` tag is pushed, which is the moment it matters and the moment
nobody is waiting on the answer, and on request from the Actions tab. It has
earned that: a GPU-probe race crashed every startup, and nothing else was going
to find it.

## SonarQube

Run on demand rather than in CI, because a second gate to satisfy before a merge
is a second thing to work around. This one is for reading.

It covers what a per-file linter cannot measure: cognitive complexity per
function, duplication found across the whole tree rather than thresholded, and
coverage readable per package instead of as one number. It found a duplicated
`switch` case that twenty Go linters had not.

## What only reports

Some limits are stated but not enforced, and it is worth knowing which.

Function length is a **soft** 50 lines and 256 functions exceed it; enforcing
that would be inventing a rule rather than mechanising one. Nesting depth has
partial cover from the linter set. One type per panel file has four known
violations and wants those fixed before it can be a gate.

## The release pipeline is checked separately, and less

`package.yml` runs only on a tag push or a manual dispatch. **Nothing in a pull
request exercises it**, which is worth stating plainly because it has bitten:
two independent breakages sat in it for days behind eleven days of green checks,
and both were found only by dispatching it deliberately.

If a change touches the release pipeline, dispatch it and read the result. A
green tick on the pull request is evidence about `ci.yml` and nothing else.
