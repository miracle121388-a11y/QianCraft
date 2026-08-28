# QianCraft workspace instructions

These instructions apply to the entire QianCraft workspace, except where a more specific nested `AGENTS.md` applies.

## Mandatory workflow maintenance

Before changing project code, data, configuration, dependencies, tests, outputs, or product documentation, read the root [`WORKFLOW.md`](WORKFLOW.md).

Every material update must maintain `WORKFLOW.md` in the same turn:

1. Update its `最后维护` date and version when appropriate.
2. Synchronize any affected current-state counts, workflow steps, directory responsibilities, commands, validation status, or known constraints.
3. Add a new entry at the top of `更新日志` describing the change, reason, actual validation, remaining boundaries, and affected files.
4. Never delete or silently rewrite historical log entries. Add a correction entry when an older record is inaccurate.
5. Do not claim an update is complete until the workflow document is current.

In the final handoff, link to `WORKFLOW.md` and identify the new log entry.

## Project boundaries

- Keep QianCraft-owned orchestration in `app/`, `scripts/`, `tests/`, `data/`, and `docs/`.
- Preserve upstream licenses and notices. Avoid editing extracted upstream projects unless the task explicitly requires it.
- Never expose API keys or crawler cookies in source, documentation, command lines, logs, or outputs.
- Keep cultural facts evidence-backed and distinguish them from strategy inferences.
- The user has authorized the Design Agent phase through `DesignPackage`, factory quote/sample brief, and concept poster. Stop before production release, factory order, commercial artwork approval, or claims of manufacturing/compliance readiness unless the user explicitly authorizes that later phase.
