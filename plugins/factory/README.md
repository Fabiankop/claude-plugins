# Factory

Unattended software factory for Claude Code. Builds every GitHub issue
labeled `factory` end to end and opens one PR per issue:

```
intake → spec → build → gate → review → approve → merged PR (or needs-human)
```

The methodology at each station comes from **Matt Pocock's skills**
(`mattpocock-skills`): `grilling` at intake, `to-spec` and `diagnosing-bugs` in
the spec, `tdd` in the builder, the two axes of `code-review` as separate
reviewers. What this plugin adds is what Pocock doesn't have because in his
flow the human sits right there: the state machine, the deterministic gate,
the surface reviewers (UX, UI, security), the approver that decides whether
the PR merges on its own, and the dashboard.

## Install

```bash
claude plugin marketplace add Fabiankop/claude-plugins   # once per machine
claude plugin install factory@fabiankop                   # in each project
```

`factory` depends on `mattpocock-skills` from the official marketplace; the
dependency installs itself (the marketplace allows it via
`allowCrossMarketplaceDependenciesOn`), or install it first with
`claude plugin install mattpocock-skills@claude-plugins-official`.

To try a local copy without publishing:

```bash
claude --plugin-dir ./plugins/factory
```

## Set up a project

Once per repo, inside the repo:

```
/setup-matt-pocock-skills     tracker (GitHub Issues), labels, where the docs go
/factory:setup                base branch, checks command, protected paths, surfaces
```

The result in the project is this and nothing more:

```
.factory/config.json    only the keys that differ from the defaults
.factory/checks.sh      what CI runs in this repo
.factory/jobs/          runtime state (gitignored)
```

Agents, scripts and dashboard come from the plugin. A complete config example:
[`examples/config.nuon-apps.json`](examples/config.nuon-apps.json).

## Use

```
/factory:new <idea>        the only station with a human: grilling, labeled issue, into the queue
/factory:run               drains the queue; also resumes what a previous session left behind
/factory:issue <n>         one issue now
/factory:rework <n>        a needs-human job goes back to the builder with your PR comments
```

The dashboard starts with every `/factory:run` (`factory-dashboard`, port
8787): the board by station, each agent's `## Summary` in plain language,
the technical files behind them, and what it's waiting on from you.

## How each station decides

| Station | Pocock skill | Model | Writes |
|---|---|---|---|
| intake | `grilling` | fable | `intake.md`: ACCEPT, NEEDS-INFO or REJECT; risk and surfaces |
| spec-writer | `to-spec` (template), `codebase-design`, `diagnosing-bugs` | opus | `spec.md`: the to-spec template plus `## Seams` and `## Acceptance criteria` |
| builder | `tdd` | by risk | commits, draft PR, `build.md` |
| gate | — (deterministic) | — | `round-N/checks.md` |
| reviewer-standards | `code-review`, Standards axis | by risk | `review-standards.md` |
| reviewer-spec | `code-review`, Spec axis | by risk | `review-spec.md` |
| reviewer-ux / ui / security | — | by surface | `review-<r>.md` |
| approver | — | opus | `decision.md`: APPROVE, ESCALATE or EXTEND |

Routing by risk and surface lives in `config.json`
(`routing`, `surface_reviewers`).

## Rules the factory enforces on its own

- **Deterministic gate.** `checks.sh` runs from the main checkout against the
  job's worktree: a branch cannot change the checks it is judged by.
- **Tests by behaviour, not by path.** The gate fails if the branch deletes a
  test file or adds `skip`/`xfail`. Tests can be edited; they can't disappear
  or be switched off. It doesn't assume tests live in `tests/`.
- **`Refs` vs `Closes`.** A job that intake rescoped cannot close its issue.
- **The base moved.** If the gate fails to sync before the merge, the builder
  gets one more round; nobody interrupts you.
- **Rounds exhausted.** The approver decides EXTEND (findings are converging)
  or ESCALATE; escalation is not the default.
- **Escalation by project rules, not plugin rules.** `human_paths` and
  `human_notes` in `config.json` are the only list of "a person always sees
  this".
- **The label is the trust boundary.** Only issues labeled `factory` run; the
  issue text reaches the agents quoted as data.
- **Docs describe intent; the tree describes reality.** Agents verify where
  the code actually lives before judging or building, and don't reorganize
  along the way: moving code is another issue
  (`/improve-codebase-architecture` produces them).

## How Pocock's skills plug in

An agent **preloads** a skill with `skills:` in its frontmatter: the full text
enters its context at startup. That works with the skills Pocock marks as
model-invocable: `grilling`, `tdd`, `code-review`, `codebase-design`,
`diagnosing-bugs`, `domain-modeling`.

The ones he marks `disable-model-invocation: true` (`to-spec`, `to-tickets`,
`wayfinder`, `triage`, `grill-with-docs`, `handoff`, `retro`…) are meant to be
typed by a person, and Claude Code doesn't allow preloading or invoking them
from an agent. The factory uses them like this:

- `to-spec`: the spec-writer reads its `SKILL.md` from the plugin cache and
  uses its template. Pocock's method, the factory's destination.
- `grill-with-docs`: `/factory:new` calls its two parts, `grilling` and
  `domain-modeling`.
- `wayfinder`, `to-tickets`, `triage`, `handoff`, `retro`: you run them
  yourself, before or after the factory; each one's README says when.

## Verified

Tested with Claude Code and `mattpocock-skills` 1.3.1 installed:

- The plugin loads with its 5 skills, 9 agents and the hook (`claude plugin validate` passes;
  `claude plugin details factory` lists them).
- `skills:` in an agent preloads Pocock's skill by its short name
  (`grilling` arrived complete in `intake`'s context).
- The `SubagentStop` hook fires when `factory:builder` finishes with the
  matcher `factory:builder` (plain `builder` doesn't fire).
- `factory-job`, `factory-gate` and `factory-dashboard` run against a project
  with `.factory/config.json`; the gate detects a deleted test and a new
  `@pytest.mark.skip`.

What remains untested is a full job against a real repo: that's the first
`/factory:issue` in the pilot project.

## Structure

```
plugins/factory/
├── .claude-plugin/plugin.json     depends on mattpocock-skills
├── skills/{run,new,issue,rework,setup}/SKILL.md
├── agents/                        intake, spec-writer, builder, reviewer-*, approver
├── bin/                           factory-job, factory-gate, factory-route, factory-dashboard
├── hooks/hooks.json               builder's SubagentStop → factory-gate --hook
├── dashboard/index.html
└── examples/config.nuon-apps.json
```
