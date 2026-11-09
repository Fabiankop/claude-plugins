---
name: setup
description: Configure the factory for the current project, once - base branch, the checks command, protected paths, test globs, surfaces, models and what a human must always see. Writes .factory/config.json and .factory/checks.sh. Usage - /factory:setup
disable-model-invocation: true
---

# Factory: setup

You configure the factory for the project in the current directory. The
result is three things in the repo, and nothing else:

```
.factory/config.json     what this project's factory looks like
.factory/checks.sh       what "the checks pass" means here
.factory/jobs/           runtime state, gitignored
```

Everything else (agents, scripts, dashboard) comes from the plugin. Keep the
config small: the plugin has defaults for every key, so write only what
differs. Read `${CLAUDE_PLUGIN_ROOT}/bin/factory_common.py` for the defaults
and `${CLAUDE_PLUGIN_ROOT}/examples/config.nuon-apps.json` for a full example.

## Before you start

- `gh auth status` must succeed and the repo must have an `origin` on GitHub.
- Matt Pocock's skills must be installed (the plugin depends on them). If the
  project hasn't run `/setup-matt-pocock-skills`, tell the user to run it
  first: it configures the tracker and docs layout the engineering skills use,
  and the factory follows the same tracker (GitHub Issues) and labels.
- If `.factory/config.json` already exists, read it and offer to change it
  rather than overwrite it.

## Find out, then ask only what you can't find

Look before asking. Then ask the rest in one round, numbered, each with your
recommended answer (the way `grilling` does), so "yes" accepts it.

1. **Base branch**: the branch PRs target. Look at `AGENTS.md`, the default
   branch, branch protection. Recommend what the repo uses (`staging` if it
   promotes to `main`, else `main`).
2. **Checks**: the command or commands CI runs. Look at `.github/workflows/`,
   `Makefile`, `package.json` scripts, `pyproject.toml`. Recommend the smallest
   set that CI treats as blocking. This becomes `checks.sh`. If CI scopes
   suites to the changed paths, keep that scoping: the factory runs the checks
   on every round.
3. **Protected paths**: files a bot must never modify or delete. Default is
   `.factory/*` only. Recommend adding the project's constitution (mission,
   principles) if it has one. Don't protect tests by path: the gate already
   fails deleted tests and new `skip`/`xfail` markers.
4. **Test globs**: where tests live, so the gate recognises them. Look at the
   tree; the defaults cover `tests/`, `test_*.py`, `*.test.*`, `*.spec.*`.
   **Don't assume the project's layout is tidy**: list what is actually there.
5. **Surfaces and reviewers**: does the project have a UI (ux + ui reviewers)?
   Anything security-sensitive (security reviewer)? Default both on.
6. **Human must always see**: `human_paths` (globs: deploy config, shared
   data contracts, a design system) and `human_notes` (rules in prose: "a
   change in the brand manual needs the designer's sign-off"). Recommend the
   shortest list the project's `AGENTS.md` already implies. Remind the user
   that generated baselines that only shrink are **not** a reason to escalate,
   and leave them out.
7. **Models**: accept the defaults unless the user wants otherwise
   (`routing` by risk, `surface_reviewers`).
8. **Language** of issue comments, specs and PR bodies (`language`, default
   `es`), `concurrency` (default 2), `max_rounds` (default 5), dashboard port.
9. **Prices** for the cost column (`prices_usd_per_mtok` per model id), if the
   user wants cost tracking. Leave empty otherwise.

## Write

- `.factory/config.json` with only the non-default keys, formatted, and a
  `"$comment"` line pointing at the plugin's defaults.
- `.factory/checks.sh`: `#!/usr/bin/env bash`, `set -euo pipefail`, then the
  checks, scoped to the diff against the base branch where CI does the same.
  It runs from the job's worktree. Make it executable.
- `.factory/jobs/` added to `.gitignore`.
- Nothing in `.claude/agents/` or `.claude/skills/`: the plugin provides them.

Then run `factory-job summary` (prints an empty table) to prove the config
loads, and tell the user: "`/factory:run` drains the `factory` label;
`/factory:new <idea>` creates an issue the right way." One line each; no
recap of the config.

## Migrating a project that had the factory in-repo

If the project has a `factory/` folder with `bin/`, `config.json`,
`checks.sh` and `dashboard.html`, and agents under `.claude/agents/`:

1. Move `factory/config.json` → `.factory/config.json`, renaming
   `code` reviewers in `routing` to `standards` and `spec`, and moving the
   approver's repo-specific escalation rules into `human_paths` / `human_notes`.
2. Move `factory/checks.sh` → `.factory/checks.sh` and change its
   `factory/config.json` reference to `.factory/config.json`.
3. Delete `factory/` and `.claude/agents/`, and any copy of Pocock's skills
   under `.agents/skills/` (`grill-me`, `grilling`): the plugins provide them.
4. Replace `factory/jobs/` with `.factory/jobs/` in `.gitignore`.
5. Update the project's `AGENTS.md` section about the factory: the commands
   are now `/factory:run`, `/factory:new`, `/factory:setup`.

Open that as one PR named by the project's conventions.
