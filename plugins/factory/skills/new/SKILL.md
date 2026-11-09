---
name: new
description: Turn an idea into a factory issue the right way - grill it with the user first, record the decisions, create the labeled GitHub issue, then run it. Usage - /factory:new <idea in one line>
disable-model-invocation: true
---

# Factory: new

The idea: `$ARGUMENTS`

This is the one attended step of the factory. The person is here now, so every
decision gets settled before the issue exists; the factory then builds it
without coming back with questions.

1. **Grill.** This is what Pocock's `/grill-with-docs` does, in its two
   parts: call the Skill tool with `grilling` and work the design tree with the
   user until the frontier is empty (scope, behaviour, what is out, how each
   criterion is verified, which seams get tested); then call the Skill tool
   with `domain-modeling` to write the terms and decisions that crystallised
   into the project's glossary and ADRs, where that skill puts them.
2. **Write the issue.** Follow the project's issue conventions (`AGENTS.md`,
   `.github/ISSUE_TEMPLATE/`, a `github-issues` skill if the project has one):
   title, type, body with every settled decision as a checked criterion. **No
   unchecked box assigned to a person may remain**; if one does, go back to 1.
   Add the `factory` label (`labels.queue` in `.factory/config.json`).
   Without a project skill:
   `gh api repos/{owner}/{repo}/issues -X POST -f title=… -f type=Feature -f 'labels[]=factory' -f body=…`
3. **Run it.** Call the Skill tool with `factory:run` and args `issue <n>`.

If the idea is too large for one pull request, say so after the grilling and
stop: the user runs `/wayfinder` (map the decisions), then `/to-spec` and
`/to-tickets` (Pocock's flow for multi-ticket work); each resulting ticket gets
the `factory` label and enters the queue through `/factory:run`.
