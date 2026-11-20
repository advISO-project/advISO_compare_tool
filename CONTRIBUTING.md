# Contributing to the advISO validation toolkit

The tools in this repository are independently installable with independent
versions, dependencies, and release schedules. This guide defines the shared development and
release process, package guides supply commands, supported environments,
behavioural sources, and any additional verification requirements.
These development guidelines apply to human contributors and agents alike.

## Where guidance belongs

| Location | Purpose |
| --- | --- |
| Repository README | Tool catalogue and repository overview. |
| This guide | Shared development policy, code quality, testing, safety, and release procedure for all contributors. |
| `AGENTS.md` files | Agent-specific working instructions and pointers to the shared policy. |
| Package README | Tool overview, behavioural sources, and developer entry points. |
| Package contribution guide | Supported runtimes, exact commands, fixtures, CI and release details, and exceptions to shared conventions. |
| Package `docs/` | User documentation and implementation guidance. |
| Package `tests/` | Executable verification and controlled synthetic fixtures. |

Tool-specific implementation and dependencies should be kept within the relevant package.
Shared code or tooling should follow a concrete need agreed for the affected
packages. Shared procedures do not require a shared Python environment, wheel,
software version, dependency selection, or release date.

## Sources of truth

Before working on a package, read its README and contribution guide to identify
its behavioural contract, authoritative schemas, development procedures, and
verification requirements.

Tests and controlled fixtures verify the documented contract; they do not
override it or supply undocumented requirements. If the sources disagree, report
the exact conflict and its consequences and seek a decision. Do not silently
choose an interpretation, weaken a requirement, or invent behaviour.

## Development environments

Use an isolated Python environment with a version supported by the selected
tool. Each tool declares its dependency-management policy and installation
command. Developers may use their preferred environment manager, provided the
resulting environment supports those commands. Python's built-in `venv` and
`pip` provide the documented baseline; no alternative environment manager is
required.

Activate an existing isolated environment, or create one at the repository root:

```console
python -m venv .venv
. .venv/bin/activate
```

On Windows Command Prompt, activate it with `.venv\Scripts\activate`; in
PowerShell, use `.venv\Scripts\Activate.ps1`. Run installation, testing, and
build commands using that environment's Python interpreter. Follow the package
guide to install its development dependencies; installing one tool does not
establish the development environment for another.

## Working on a change

1. Read the selected package's contribution guidance and relevant behavioural
   documentation in full, including cross-referenced rules and schema
   definitions. Identify the specified behaviours affected by the change.
2. Run relevant existing tests to establish a baseline.
3. For an approved behavioural change or defect fix, adapt existing tests where
   possible and add focused coverage for uncovered behaviour. Confirm that a
   new regression fails for the expected reason before implementing the fix.
4. Keep implementation changes scoped to the selected package. Run focused
   checks during development, then proportionate wider tests, static checks,
   schema checks, and packaging checks.
5. Keep schemas, examples, user documentation, and implementation aligned. Update
   implementation guidance when responsibilities or data flow change.
6. Report what changed, commands and results, and remaining verification limits.
   Distinguish local checks from verification across supported environments.

Use test-driven development for behavioural changes and update the smallest
coherent set of tests that verifies the agreed behaviour. A failing test is useful
only when it represents current intended behaviour. Do not create tests for
discarded ideas, historical decisions, or renamed and removed properties.

For documentation-only work, check links and examples. Run documentation and
installed-distribution checks when changing published instructions or installed
files. A change to a shared procedure needs review against each affected tool's
configuration; it does not automatically require rerunning every behavioural test.

## Change control

- Agree changes to behavioural contracts, normative schemas, and established
  requirement semantics explicitly as part of the change's scope.
- Preserve schema version identifiers and canonical `$id` values unless a
  deliberate version change has been approved.
- When behaviour changes, update all affected normative text, schemas, tests,
  fixtures, and user documentation together.
- Do not add speculative features, extension points, compatibility layers,
  dependencies, or abstractions.
- Keep patches narrowly scoped. Do not mix behavioural work with unrelated
  restructuring or formatting.
- Preserve unrelated work already present in the worktree.

When a requirement is ambiguous, contradictory, or not implementable as written,
seek a decision rather than encoding an undocumented assumption.

## Code quality

- Follow PEP 8 and write idiomatic Python compatible with the package's supported
  Python versions.
- Follow PEP 257 for public-module, class, function, and method docstrings;
  document intent and constraints rather than restating the code.
- Where configured automated formatting, linting, or type-checking rules differ
  from general style guidance, the project configuration is authoritative.
- Avoid unrelated formatting changes that obscure the substantive patch.
- Keep the command-line layer thin and domain logic independently testable.
- Separate I/O, domain logic, validation, and presentation responsibilities.
- Prefer small explicit interfaces and ordinary modules over framework-like
  abstraction.
- Use type annotations for production interfaces and non-trivial internal
  functions.
- Prefer explicit domain types and immutable value objects where they prevent
  invalid states.
- Keep functions focused and transformation stages testable in isolation.
- Avoid mutable global state and import-time side effects.
- Use domain-specific exceptions or result types at architectural boundaries.
- Do not use broad exception handling to conceal defects.
- Keep dependencies minimal and justified, with runtime and development
  dependencies separated.
- Write deterministic code; do not depend accidentally on unordered collections,
  filesystem order, locale, or hash iteration.

Do not introduce or replace a formatter, linter, type checker, build backend,
test framework, dependency manager, or supported-Python policy as an incidental
edit. Project-wide tooling choices require deliberate configuration and approval.

## Formatting and linting

Python tools use Ruff for formatting and linting, configured in each package's
`pyproject.toml` and installed through its development dependencies. The shared
formatting target is 88 characters; syntax modernisation must respect each
package's minimum supported Python version. Check production Python and tests,
excluding generated version files, virtual environments, and build outputs.

| Rules | Purpose |
| --- | --- |
| `E4`, `E7`, `E9`, `F` | Basic errors, unused imports, and undefined names. |
| `I` | Import ordering. |
| `B` | Common bug-prone constructs. |
| `UP` | Compatible Python syntax modernisation. |

Each package documents exact commands and any narrowly scoped rule exceptions.
Review automatic fixes; do not apply unsafe fixes in bulk. After safe fixes and
formatting, rerun both checks and relevant tests for substantive corrections.
Editor integration and pre-commit hooks are optional.

Pin Ruff in each package's development dependencies so local and CI checks use
matching versions. Upgrade deliberately: review release notes, assess findings
and formatting changes without writing files first, and review cleanup separately
from behavioural changes. Rerun checks and relevant tests before merging. Do not
duplicate version pins in CI, hooks, or editor settings. Type checking is not a
repository-wide requirement.

## Testing and fixtures

Use descriptive behavioural test names and assertions. Do not embed requirement
or acceptance-scenario identifiers in code, tests, fixtures, snapshots, package
metadata, or runtime artefacts. Any formal
traceability belongs in review records as a one-way reference to software
artefacts. Every corrected material defect needs appropriate regression coverage;
adapt existing tests where they express the rule clearly.

Give parameterized cases descriptive IDs when inputs contain complex objects,
mutations, or several expected values. Simple scalar values can use default IDs.
Keep variants of one rule together; use separate tests when behaviours require
substantially different setup or assertions. Small helpers can share mechanical
setup while keeping inputs and expectations visible.

Test public behaviour and stable internal contracts rather than private
implementation details. Exercise both directions where behaviour requires
symmetry, boundary values, malformed inputs, and failure paths. Validate
representative configuration and result documents against their packaged schemas.
Include installed-entry-point and built-distribution tests as required by the
package's verification policy. Do not update expected outputs blindly; review
semantic changes field by field.

Use controlled, synthetic, non-sensitive fixtures under version control. Keep
purpose, configuration, inputs, and expected outcomes clear from the test or
fixture. Generated fixtures must be deterministic and document their generator
and regeneration command. For retained release evidence, identify fixture source
revisions or generation methods and record additional review if performed;
fixture digests may supplement the source revision. Do not imply independent
review when none occurred.

Keep fixtures small enough for meaningful review unless scale is the subject of
the test.

Package guides describe required coverage, helpers, special checks, and build or
installation scenarios. Property-based and mutation testing are optional
techniques, not mandatory release gates. Not every documentation or process rule
needs a direct automated test.

## Sensitive data and repository safety

- Never place real patient data, clinical identifiers, credentials, secrets, or
  identifying local paths in source, tests, fixtures, snapshots, logs, examples,
  or documentation.
- Confirm authorization and verify the exact target before destructive
  repository or filesystem operations.
- Never overwrite unrelated changes to make a check pass.
- Refer to the selected package's user guide for its operational security and
data-governance behaviour.

## Documentation

Keep user instructions accurate for the implemented software and distinguish
machine-enforced constraints from explanatory guidance. Complete examples should
validate against their applicable schemas and worked commands should produce the
documented outcomes. A material disagreement between behavioural documentation,
schemas, examples, and implementation must be resolved before release.

Keep READMEs accurate and do not describe planned behaviour as already available.
Link to normative material instead of copying substantial requirements into
explanatory documentation.

Developer setup and release procedures belong in contribution guidance; user
concepts and operational instructions belong in user documentation. Each package
identifies its authoritative behavioural sources and which documentation and
examples are shipped for offline use.

## Reporting completed work

In a change or pull-request description, report:

- the specified behaviours affected;
- tests added or updated and why they are sufficient;
- commands run and their results;
- schema, static, packaging, and documentation checks performed;
- checks not run and the reason; and
- remaining assumptions, limitations, or follow-up work.

Do not claim completion while relevant tests, schemas, documentation, or packaging
metadata are knowingly inconsistent with the implementation.

## Continuous integration and merge settings

Each tool documents its workflow, verification matrix, aggregate status check,
and retained artefacts. Python formatting/lint checks run once per workflow,
alongside the tool's runtime tests. Dependency resolution and retention policies
remain explicit in the package guide. Passing local tests alone does not establish
matrix or installed-product verification.

The `main` branch is protected by a GitHub ruleset requiring pull requests, the
configured status checks, and an up-to-date branch before merging. Another
person's approval is not required by the chosen merge policy. Each package lists
its required status check. When adding a tool, include its approved aggregate
check in the GitHub ruleset; committing a workflow does not configure protection.

Rulesets are maintained on GitHub, separately from workflow files. Workflow
changes deserve scrutiny because a PR runs the workflow from its temporary
merged state. An aggregate gate must fail when any required dependency fails,
is cancelled, or is skipped. Keep action pins and runner labels current through
deliberate updates.

CI jobs normally have read-only repository permissions. Only the tag-triggered
draft-preparation job receives permission to write release assets; it runs after
the required CI gate succeeds. It does not run on pull requests, branch pushes,
or manual verification runs.

## Versioning and compatibility

Use independent software versions and release tags for each tool. The tag format
is `<distribution-name>-v<version>`, for example `adviso-compare-v1.0.0`. Each
tool's Git-derived version calculation and CI tag trigger must select only its
own tag namespace. Do not rename or move existing published tags.

Software and schema families have independent version identifiers. Each release
states its supported schema versions and combinations where applicable. Before
changing a schema, publish compatibility rules; incompatible changes need a
migration path or documented transition arrangements. Changes to distribution,
executable, or import-package names also need compatibility consideration.
Package guides retain tool-specific compatibility commitments.

## Preparing a release

Publication is manual. Pushing a package's release tag starts its full CI and,
after the required checks succeed, prepares a **draft GitHub Release** with the
tested distributions and verification evidence. Review and complete the release
notes before choosing **Publish release**. CI never publishes the draft.

Follow the selected package's **Release details** table. The four steps below
use `adviso-compare` and version `1.0.0` as examples; substitute the selected
tool's tag, version, and workflow. Each tool owns its tag namespace and workflow:
a tag for one package must not trigger another package's checks or draft release.
When adding a tool, configure and verify that automation before using this
procedure for its first release.

These steps assume no existing checkout or Python environment. You need Git on
your computer, a GitHub account with repository write access, and ordinary Git
authentication for pushes. See [GitHub's Git setup instructions](https://docs.github.com/en/get-started/git-basics/set-up-git).
No local Python installation, virtual environment, build tools, or GitHub CLI
is needed to prepare a release; GitHub runs the verification and preparation.

1. **Choose the release contents and version — GitHub web interface.**

   Confirm that the intended features and fixes are merged into `main`, including
   any documentation and schema compatibility changes. A release can collect
   several already-merged changes. A separate release-preparation branch or PR
   is only needed if further repository changes are required.

   Choose an unused semantic version and its package-specific tag, for example
   `adviso-compare-v1.0.0`. Check **Tags** and **Releases** for existing names.
   Do not move or reuse a tag for different source. You can start writing release
   notes in a local editor now, or write them in the generated draft in step 3.
   Notes describe the changes, known limitations, supported runtimes, and schema
   compatibility; they are the release's description on GitHub, not a required
   repository file.

2. **Tag the merged source and push the tag — terminal on your computer.**

   If you do not have a checkout, run these commands in a directory where you
   want the repository to be created:

   ```console
   git clone https://github.com/advISO-project/validation_toolkit.git
   cd validation_toolkit
   ```

   Otherwise, open a terminal in your existing checkout's root. Confirm that
   `origin` points to this repository:

   ```console
   git remote -v
   ```

   Configure your Git name and email if needed for annotated tags; see the Git
   setup instructions above. Then run:

   ```console
   git fetch origin main --tags
   git tag -a adviso-compare-v1.0.0 -m "adviso-compare 1.0.0" origin/main
   git push origin adviso-compare-v1.0.0
   ```

   This tags the fetched `main` commit without switching branches or changing
   your working files. Check that this is the intended release point before
   pushing. The workflow containing draft preparation must already be merged
   there. Push only the intended package's tag. The workflow checks that its
   source is merged into `main` and that the built version matches the tag.

3. **Wait for verification and review the draft — GitHub web interface.**

   Open **Actions**, select the package's workflow, and open the run for the
   pushed tag. Wait for the complete workflow, including **Prepare draft
   release**, to succeed. The package's full runtime matrix, formatting/lint
   checks, schema/example checks, builds, and clean installation tests must pass.

   Open **Releases** and edit the draft for this tag. CI attaches:

   - the tested `.whl` and `.tar.gz`, copied without rebuilding;
   - `release-verification.md`, identifying the tag, commit, CI run/attempt,
     environments, schema versions, checks, and distribution hashes;
   - `verification-evidence.zip`, containing all matrix and quality-check
     reports, environment/dependency records, and job outcomes; and
   - `SHA256SUMS.txt`, with complete SHA-256 hashes for the other four assets.

   These are **release assets**, distinct from GitHub's automatically generated
   source-code ZIP and tarball. The workflow selects the distribution source
   listed in the package guide. The attached evidence retains verification
   records beyond CI artefact expiry. Dependency records identify what was
   tested; they do not fix future dependency resolution.

   Complete the **Changes** and **Known limitations** sections in the draft
   notes and review its generated runtime/schema statements. Check that the
   tag, version, verification summary, and attached files describe the intended
   release. Downloads and local checksum calculations are optional additional
   inspection; they are not required preparation steps. The generated record
   documents automated verification and does not assert independent human review.

   If verification or draft preparation fails, inspect the failed job. A failed
   preparation can leave a partial draft: do not publish it. Use **Re-run failed
   jobs** after resolving a transient failure. Reruns refresh generated assets
   on the same draft and preserve notes you have edited. They refuse to modify
   an already published release. If a source change is needed, merge it and use
   a new version/tag rather than moving the existing tag.

4. **Publish the reviewed release — GitHub web interface.**

   Once the workflow has succeeded and the notes and assets are ready, select
   **Publish release**. Stable releases should have **This is a pre-release**
   unchecked; the workflow marks prerelease versions accordingly. Choose
   **Set as latest release** deliberately: that label is repository-wide even
   though tools have independent versions.

   Open the published release and confirm its notes and five attached assets
   are present. No package-index publication is configured by this process.

Additional independent review, signing/build attestation, property-based testing,
and mutation testing are optional. Record them if performed; they are not
release gates and another person's approval is not a merge requirement.
