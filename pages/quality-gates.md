# What the build enforces

MeshBench's limits are mechanical rather than advisory, because taste does not
survive scale. This is what actually fails a build, what only reports, and why
each one exists.

<figure>
<svg viewBox="0 0 780 240" role="img" aria-label="Which checks run at which trigger">
  <text x="20" y="30" font-size="12" font-weight="600" fill="var(--ink)">every pull request</text>
  <rect x="20" y="40" width="740" height="44" rx="8" fill="var(--good)" fill-opacity=".08" stroke="var(--good)" stroke-opacity=".4"/>
  <text x="390" y="67" font-size="11.5" fill="var(--ink)" text-anchor="middle">gofmt &#183; go vet &#183; golangci-lint + ratchet &#183; tests, four shards &#183; conflict markers &#183; file limits &#183; layout map &#183; licence inventory</text>
  <text x="20" y="116" font-size="12" font-weight="600" fill="var(--ink)">a v* tag, or a deliberate dispatch</text>
  <rect x="20" y="126" width="740" height="44" rx="8" fill="var(--warn)" fill-opacity=".08" stroke="var(--warn)" stroke-opacity=".4"/>
  <text x="390" y="153" font-size="11.5" fill="var(--ink)" text-anchor="middle">the race detector &#183; the release pipeline (package.yml) - nothing in a pull request exercises either</text>
  <text x="20" y="202" font-size="12" font-weight="600" fill="var(--ink)">on demand, for reading rather than gating</text>
  <rect x="20" y="212" width="740" height="24" rx="8" fill="var(--panel)" stroke="var(--rule)"/>
  <text x="390" y="228" font-size="11.5" fill="var(--dim)" text-anchor="middle">SonarQube: complexity, whole-tree duplication, per-package coverage</text>
</svg>
<figcaption>A green pull request is evidence about the first lane only. The
second lane stays invisible until a tag or a dispatch fires it.</figcaption>
</figure>

## On every pull request

| gate | what it refuses |
|---|---|
| `gofmt -l` | any file not formatted |
| `go vet` | the compiler's own suspicions |
| `golangci-lint` + ratchet | any *increase* in findings - see below |
| `go test ./...` | a failing test, across four parallel shards |
| conflict markers | `<<<<<<<`, `=======` or `>>>>>>>` committed in source |
| file length | over 500 lines without an exemption naming its reason |
| tracked build artifacts | a compiled binary or coverage profile in the index |
| the layout map | a package with no entry, or an entry with no package |
| the licence inventory | a dependency change that has not regenerated it |

The last three exist because each failure they refuse arrives silently and
looks fine in review.

## The lint ratchet

Twenty linters run, not a token few and not all 104. The
enabled set is those whose findings are worth acting on here, each with its
reason recorded in `.golangci.yml`.

Enabling the bug-class linters on an existing tree produces hundreds of
findings at once. Turning those into a red build would mean hundreds of
unreviewed changes in one commit, so the count is held at a baseline instead:

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

Not on every push - it multiplies an already slow suite by enough that the wait
becomes the thing people notice about the pipeline, and a check nobody waits for
is a check that gets worked around.

It runs when a `v*` tag is pushed, which is the moment it matters and the moment
nobody is waiting on the answer, and on request from the Actions tab. It is the
only gate that can find a startup race - exactly the class of fault review does
not catch.

## SonarQube

Run on demand rather than in CI, because a second gate to satisfy before a merge
is a second thing to work around. This one is for reading.

It covers what a per-file linter cannot measure: cognitive complexity per
function, duplication found across the whole tree rather than thresholded, and
coverage readable per package instead of as one number. Whole-tree duplication
is the class of finding a per-file linter cannot produce.

## What only reports

Some limits are stated but not enforced, and it is worth knowing which.
The house rules for the interface are one of them: they are carried as an
[agent skill](agent-skills.html) rather than as a check, because most of them
are about what a control means rather than about what compiles.

Function length is a **soft** 50 lines and 256 functions exceed it; enforcing
that would be inventing a rule rather than mechanising one. Nesting depth has
partial cover from the linter set. One type per panel file has four known
violations and wants those fixed before it can be a gate.

## The release pipeline is checked separately, and less

`package.yml` runs only on a tag push or a manual dispatch. **Nothing in a pull
request exercises it**, which is worth stating plainly: a breakage in it sits
invisible behind green pull-request checks until somebody dispatches it
deliberately.

If a change touches the release pipeline, dispatch it and read the result. A
green tick on the pull request is evidence about `ci.yml` and nothing else.
