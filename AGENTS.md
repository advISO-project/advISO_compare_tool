# Agent guidance for the AdvISO validation toolkit

Follow the repository [contribution guide](CONTRIBUTING.md) and the applicable
package contribution guide. Their development policies apply equally to human
contributors and agents. This file adds agent-specific working instructions;
it does not define product behaviour or a separate development policy.

## Before starting

- Read the selected package's README and contribution guide. Use the shared
  [sources-of-truth guidance](CONTRIBUTING.md#sources-of-truth) to locate its
  behavioural contract, schemas, and verification requirements.
- Inspect the worktree before editing so you can distinguish existing user
  changes from your own work.

## Scope and permissions

- Stay within the user's authorized task. Change behavioural contracts, schemas,
  or established requirement semantics only when that change is explicitly
  authorized.
- Report ambiguous requirements or conflicting sources to the user and request
  a decision before implementing dependent changes.
- Obtain explicit user authorization and verify the exact target before
  destructive repository or filesystem operations.

## Completion

Report results according to [Reporting completed work](CONTRIBUTING.md#reporting-completed-work),
including verification performed and any remaining limitations.
