# Agent skills

A coding agent pointed at MeshBench can read the verb list and the client
references on this site, and from those it can work out what it is allowed to
call. What it cannot work out is which calls fail quietly: which wait has a
false premise, which reply is a refusal wearing the shape of a success, which
step of an import decides whether the mesh relays anything at all. That is the
knowledge MeshBench ships as agent skills.

Three skills are maintained beside the code, in `.claude/skills/` in the
MeshBench repository, and mirrored into two standalone repositories so they can
be installed by an agent working somewhere else.

## What a skill is

A skill is a directory holding a `SKILL.md`: YAML front matter carrying a
`name` and a `description`, then Markdown instructions. The agent loads only
the description at startup, which is enough to decide whether the skill is
relevant, and reads the body only when a task matches it. Many skills therefore
cost almost nothing until one of them is needed.

The format is the [Agent Skills](https://agentskills.io) open standard, which
several agents and editors read. A skill is plain Markdown in a folder, under
version control, with no runtime and nothing to install.

## The three skills

| Skill | Loads when | Repository |
|---|---|---|
| `meshcoresim` | driving the simulator to answer an RF or mesh question: link viability, coverage, why a packet missed, a firmware A/B | [`meshbench-scripting-skills`](https://github.com/MeshBench/meshbench-scripting-skills) |
| `meshbench-scripting` | writing or debugging a script that opens a session, brings a mesh up and waits for it | [`meshbench-scripting-skills`](https://github.com/MeshBench/meshbench-scripting-skills) |
| `wb2-design-language` | building or changing a Gio panel, control, menu or map drawing | [`meshbench-dev-skills`](https://github.com/MeshBench/meshbench-dev-skills) |

The split is by audience. The first two are for using MeshBench from outside,
and are useful to anyone driving a workbench. The third is for changing
MeshBench itself, and is only useful inside a checkout.

**`meshcoresim`** carries the order in which a scenario has to be built, the
region inference step that decides whether anything relays, the two spellings a
region has and which one goes on the wire, and the honesty rules a result is
held to: both directions, no verdict on an uncertain position, one run is not
evidence, quote the provenance. It also carries what the simulator does not
model, because the omissions all bias the same way and a number quoted without
that is a claim the model cannot support.

**`meshbench-scripting`** carries the failure modes of a driven session: which
waits have premises that do not hold, why `sim.start` is not the way a script
starts a run, which of the two consoles a node kind actually reads, and how a
refusal reaches a caller. It is written from faults found by running the
shipped examples end to end rather than from the API surface.

**`wb2-design-language`** carries the interface decisions: that colour and size
come from one theme package, that panels fire verbs rather than mutating state,
that a long operation announces itself, and that nothing counts as done until
it has been seen running.

The register differs from this site's. A skill states a rule with the reason
attached, in the voice of something learned rather than something specified,
because an agent that knows why a rule exists applies it to the case the rule
did not anticipate.

## Installing

Every agent below reads the same `SKILL.md`. What differs is only the directory
it looks in.

```console
git clone https://github.com/MeshBench/meshbench-scripting-skills
git clone https://github.com/MeshBench/meshbench-dev-skills
```

Then copy the skill directories from `skills/` into whichever of these the
agent reads. A project directory makes the skill available to anyone who
clones the project; a user directory makes it available in every project.

| Agent | Project directory | User directory |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| VS Code and GitHub Copilot | `.github/skills/`, `.claude/skills/` or `.agents/skills/` | `~/.copilot/skills/`, `~/.claude/skills/` or `~/.agents/skills/` |
| Cursor | `.cursor/skills/` or `.agents/skills/` | `~/.cursor/skills/` or `~/.agents/skills/` |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` |
| Codex | `.agents/skills/`, from the working directory up to the repository root | `~/.agents/skills/` |

**Only the Claude Code row is verified here**, because that is the agent the
MeshBench repository itself is set up for and the one the skills are exercised
under. Every other row is taken from that tool's own documentation, linked
under [further reading](#further-reading), and is stated rather than tested.
Check the tool's documentation before concluding a path is wrong.

`.agents/skills/` is read by Cursor, Gemini CLI, Codex and VS Code, so one
directory covers several agents at once. A skill directory may be a symbolic
link to a checkout elsewhere on disk, which is the way to install once and
update with `git pull` rather than by copying again.

```console
mkdir -p ~/.agents/skills
ln -s "$PWD/meshbench-scripting-skills/skills/meshbench-scripting" ~/.agents/skills/
```

Claude Code, Cursor, Gemini CLI and Codex all resolve a symbolic link and read
`SKILL.md` from its target.

### Agents that upload rather than read a directory

Claude in the browser and desktop applications, and the Skills API, take a
skill as an upload rather than from a directory on disk. Those paths accept
only the front-matter fields in the Agent Skills specification: `name`,
`description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Any
other field fails the upload rather than being ignored. MeshBench's skills
declare `name` and `description` and nothing else, so they upload unchanged.

### Agents with no skill support

An agent that has no skills mechanism can still be given the content: a
`SKILL.md` is Markdown, so its body pasted into that agent's rules or
instructions file works, at the cost of the progressive loading. The whole
skill then occupies context in every session rather than only in the sessions
that need it, which is the trade the skills format exists to avoid.

## Using them

A skill loads on its own when a task matches its description, so nothing has to
be typed to get the benefit. Asking an agent to write a script that brings a
mesh up should pull in `meshbench-scripting`; asking why a packet did not
arrive should pull in `meshcoresim`. Claude Code also invokes one directly by
name, as `/meshbench-scripting`.

A skill is not a substitute for the references on this site. It says what an
agent would otherwise get wrong; the [control socket
reference](reference-control.html), the [Python](reference-python.html),
[Go](reference-go.html) and [Node](reference-js.html) client references and the
[cookbook](cookbook.html) say what the calls are. Both are wanted: an agent
with the verb list and no skill writes code that runs and quietly measures
nothing.

## Keeping them true

The copies in the MeshBench repository under `.claude/skills/` are canonical.
The two standalone repositories are mirrors, updated by copying, and a skill
that changes in one place is expected to change in both in the same piece of
work. Nothing enforces that, so a mirror can be behind: when the two disagree,
the copy beside the code is the one that is right.

A skill that states something no longer true is worse than a skill that says
nothing, because it is acted on with confidence. That is why the skills name
the file or the command that settles each claim, and why counts that a script
generates are cited by their generator rather than written out as a number.

## Further reading

- [Agent Skills](https://agentskills.io), the format and its specification
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Agent skills in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [Cursor skills](https://cursor.com/docs/context/skills)
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)
- [Codex skills](https://developers.openai.com/codex/skills/)
