# Contributing to `adviso-compare`

This guide covers development, verification, and release preparation for
`adviso-compare`. Its policies apply equally to human contributors and agents.
Run commands from the repository root unless stated otherwise.

| Document | Purpose |
| --- | --- |
| [README](README.md) | Tool overview, support status, and entry points. |
| This guide | Development policies, setup, checks, CI, and release preparation. |
| [AGENTS.md](AGENTS.md) | Agent-specific working instructions. |
| [User guide](docs/user-guide.md) | User-facing behaviour and semantic rules. |
| [Implementation guide](docs/implementation-guide.md) | Architecture, data flow, and maintenance guidance. |

## Sources of truth

Start with the [user guide](docs/user-guide.md) and the relevant packaged
[schema definitions](src/adviso_compare/schemas/). The guide defines observable
behaviour and semantic rules; the schemas define document structure and
structural constraints. The [implementation guide](docs/implementation-guide.md)
explains how these are implemented and provides a change map.

Tests and controlled fixtures verify the documented contract; they do not
override it or supply undocumented requirements. If the sources disagree, report
the exact conflict and its consequences and seek a decision. Do not silently
choose an interpretation, weaken a requirement, or invent behaviour.

## Development environments

Linux is fully supported with CPython 3.11–3.15. Windows and macOS are expected
to work, with full CI coverage on CPython 3.15 only. Python 3.11 is the installation
minimum; use the latest available patch release. Additional combinations need
verification before joining the verified matrix.

Use an isolated Python environment. Developers may use their preferred environment
manager, provided it supports the documented commands. Python's built-in `venv`
and `pip` provide the baseline; no alternative environment manager is required.

Activate an existing isolated environment, or create one at the repository root:

```console
python -m venv .venv
. .venv/bin/activate
```

On Windows Command Prompt, activate it with `.venv\Scripts\activate`; in
PowerShell, use `.venv\Scripts\Activate.ps1`. Run installation, testing, and
build commands using that environment's Python interpreter. Install the package
and its development dependencies:

```console
python -m pip install -e ".[dev]"
```

This editable installation makes source changes available to the installed
`adviso-compare` command. Git-derived versions use `setuptools-scm`;
`src/adviso_compare/_version.py` is generated, not maintained by hand. Build and
development environments require `setuptools-scm` 10.3.4 or later for the
configured tag prefix. Setuptools 77 or later is required for the SPDX licence
expression and licence-file metadata in `pyproject.toml`.

## Working on a change

1. Read the relevant behavioural documentation in full, including
   cross-referenced rules and schema definitions. Identify the specified behaviours affected by the change.
2. Run relevant existing tests to establish a baseline.
3. For an approved behavioural change or defect fix, adapt existing tests where
   possible and add focused coverage for uncovered behaviour. Confirm that a
   new regression fails for the expected reason before implementing the fix.
4. Keep changes focused on the agreed scope. Run focused checks during
   development, then proportionate wider tests, static checks,
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
files. Review procedure changes against the configuration they describe; they
do not automatically require rerunning every behavioural test.

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

- Follow PEP 8 and write idiomatic Python compatible with the supported
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

Ruff is configured in [pyproject.toml](pyproject.toml) and pinned in the
development dependencies. It checks application code, tests, and `.github/scripts/`,
excluding generated version files, virtual environments, and build outputs.
The formatting target is 88 characters and the syntax target is Python 3.11.

```console
python -m ruff format --check .
python -m ruff check .
```

| Rules | Purpose |
| --- | --- |
| `E4`, `E7`, `E9`, `F` | Basic errors, unused imports, and undefined names. |
| `I` | Import ordering. |
| `B` | Common bug-prone constructs. |
| `UP` | Compatible Python syntax modernisation. |

`UP042` is excluded to retain existing enums' string conversion behaviour;
converting to `StrEnum` would be a separate behavioural change. No type checker
is configured. Editor integration and pre-commit hooks are optional.

For local cleanup:

```console
python -m ruff check --fix .
python -m ruff format .
```

Review automatic fixes; do not apply unsafe fixes in bulk. After fixing and
formatting, inspect the diff and rerun checks and relevant tests. Upgrade Ruff
deliberately: assess findings and formatting changes without writing files first,
and review cleanup separately from behavioural changes. Keep its version pin in
`pyproject.toml`, without duplicating it in CI, hooks, or editor settings.

## Testing and fixtures

Use descriptive behavioural test names and assertions. Do not embed requirement
or acceptance-scenario identifiers in code, tests, fixtures, snapshots, package
metadata, or runtime artefacts. Any formal traceability belongs in review
records as a one-way reference to software artefacts. Every corrected material defect needs appropriate regression coverage;
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
Include installed-entry-point and built-distribution checks as described below.
Do not update expected outputs blindly; review semantic changes field by field.

Use controlled, synthetic, non-sensitive fixtures under version control. Keep
purpose, configuration, inputs, and expected outcomes clear from the test or
fixture. Generated fixtures must be deterministic and document their generator
and regeneration command. For retained release evidence, identify fixture source
revisions or generation methods and record additional review if performed;
fixture digests may supplement the source revision. Do not imply independent
review when none occurred.

Keep fixtures small enough for meaningful review unless scale is the subject of
the test.

Property-based and mutation testing are optional techniques, not mandatory
release gates. Not every documentation or process rule
needs a direct automated test.

Run the full runtime suite or a focused module:

```console
python -m pytest tests -q
python -m pytest tests/test_inputs.py -q
```

The suite covers parsing, translation, comparators, configuration/results schema
validation, CLI behaviour and exit codes, deterministic output, documentation
examples, and clean wheel/source installations. It exercises malformed inputs,
both directions of missing/extra content, composite and duplicate keys, and
tolerance boundaries.

Release-preparation tests run separately, once in CI's quality job:

```console
python -m pytest .github/scripts/test_adviso_compare_release.py -q
```

Run both paths together to check all runtime and automation tests locally:

```console
python -m pytest tests .github/scripts/test_adviso_compare_release.py -q
```

Reusable synthetic documents live in `tests/support/documents.py`; builders return
new objects on every call to avoid state leaking between tests. Fixed values are
intentional. `tests/support/schemas.py` loads each document's packaged schema
independently and enables JSON Schema format assertion. Evidence assertions live
in `tests/support/evidence.py`.

Additional checks are:

```console
python -m pip check
python -m compileall -q src tests .github/scripts
git diff --check
```

## Build distributions

With the development dependencies installed, build a wheel and source archive:

```console
python -m build
```

The archives are written to the generated `dist/` directory. `MANIFEST.in`
explicitly includes documentation and test sources, including test support
modules, in source archives. The project licence expression and `LICENSE` file
are declared in `pyproject.toml`; both distributions include the licence text.
The distribution test verifies these notices and builds both
archives once, then installs each into a separate fresh virtual environment.
It resolves declared dependencies without borrowing development site-packages;
source-archive installation also uses isolated build dependencies. These tests
may need network access to a package index.

Both installations run outside the checkout, check dependency consistency and
installed resources, and exercise the same automatic, custom, repeated-run, and
error scenarios. Evidence is also validated using each installed package. The
archives and resolved dependency records remain in the pytest base temporary
directory for the run.

## Sensitive data and repository safety

- Never place real patient data, clinical identifiers, credentials, secrets, or
  identifying local paths in source, tests, fixtures, snapshots, logs, examples,
  or documentation.
- Confirm authorization and verify the exact target before destructive
  repository or filesystem operations.
- Never overwrite unrelated changes to make a check pass.
- Refer to the [user guide](docs/user-guide.md) for operational security and
  data-governance behaviour.

## Documentation

Keep user instructions accurate for the implemented software and distinguish
machine-enforced constraints from explanatory guidance. Complete examples should
validate against their applicable schemas and worked commands should produce the
documented outcomes. A material disagreement between behavioural documentation,
schemas, examples, and implementation must be resolved before release.

Keep the README accurate and do not describe planned behaviour as already available.
Link to normative material instead of copying substantial requirements into
explanatory documentation.

Developer setup and release procedures belong in contribution guidance; user
concepts and operational instructions belong in user documentation. The sources
of truth are identified above.

The user guide and `docs/examples/` are installed with the distribution for
offline use. Check runnable examples and installed copies with:

```console
python -m pytest tests/test_documentation.py tests/test_distribution.py -q
```

An editable installation does not keep installed documentation copies in sync
with source edits. Use the maintained source guide during development; the
distribution test checks that a fresh wheel installs the same guide.

The user guide covers the complete CLI, supported inputs, automatic/custom
configuration rules, output fields, validation, errors, limitations, and governance
boundaries. Link to it and the schemas rather than duplicating substantial
behavioural requirements in developer documentation. Update the implementation
guide when responsibilities or data flow change.

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

## Continuous integration

The workflow runs on pull requests targeting `main` (including updates to those
pull requests), pushes to `main`, pushes of tags matching `v*`,
and manual requests.
Pushes to development branches without an open pull request do not trigger it.
For `v*` tag pushes only, a final job prepares a draft release
after the aggregate CI gate succeeds. Publication remains manual.

A separate `adviso-compare / Ruff` job runs formatting and lint checks once on
`ubuntu-24.04` with CPython 3.11. It installs the development dependencies from
the project, including the pinned Ruff version, and checks without modifying
files. It includes `.github/scripts/` and runs the release-preparation tests once. It runs alongside the seven runtime
test configurations below; Ruff is not rerun in each matrix job.

Each run executes the full suite, including schema/example checks, builds,
and clean wheel/source-archive installation scenarios, on all seven combinations
in the verification matrix using these standard GitHub-hosted runners:

| Runner | Architecture | CPython versions |
| --- | --- | --- |
| `ubuntu-24.04` | x86-64 | 3.11, 3.12, 3.13, 3.14, 3.15 |
| `macos-15` | ARM64 | 3.15 |
| `windows-2025` | x86-64 | 3.15 |

The same full suite and matrix apply to pull requests, `main`, version-tag pushes,
and manual runs. Linux is the fully supported deployment platform. Windows and
macOS compatibility is checked on Python 3.15; other Python versions on those
platforms are outside the verified matrix. No reduced test selection is used
for any matrix job. Review this coverage when preparing a release or updating
the support policy.

These identify the environments exercised by CI, rather than every supported
OS release or architecture. Runner images and Python patch releases can change;
each job records the platform, architecture, Python version, checked-out commit,
and resolved test dependencies. The distribution tests also record dependencies
for each clean installation. Every job installs the package normally, rather
than relying on an editable source installation, before running the full suite.

Dependency version ranges are declared in `pyproject.toml`; there is no
committed lockfile fixing the exact direct and indirect dependency versions.
Fresh installations resolve compatible versions from those ranges, so
developers and CI runs may receive different dependency versions over time.
This exercises compatibility with evolving dependencies. The recorded versions
identify what each CI run tested; they do not guarantee that a later
installation selects the same versions.

The workflow retains JUnit test results, built wheel/source archives, and
version/dependency records for 30 days, including available reports on failure.
It does not upload the temporary comparison datasets or evidence packages.
A separate `adviso-compare-quality` artefact retains Ruff output, release-automation
test results, and its environment records for the same period. Successful tag
runs attach the verification records to the draft release for longer retention.
Superseded pull-request runs are cancelled. Other matrix jobs continue after a
failure to show the full set of outcomes.

To reproduce the test command locally, use a supported Python environment with
the development dependencies installed:

```console
python -c "from pathlib import Path; Path('ci-output').mkdir(exist_ok=True)"
python -m pytest tests -q --junitxml=ci-output/tests.xml --basetemp=ci-output/tmp
```

`ci-output/` is ignored generated content. Pytest clears the selected base
temporary directory before a run; use this command only with that disposable
path. The normal test command above lets pytest manage its own temporary path.

### Merge settings

The aggregate check **`adviso-compare CI passed`** succeeds only when all seven
runtime jobs and the Ruff/release-automation job succeed. It fails if a required
job fails, is cancelled, or is skipped. The tag-only draft-preparation job follows
this gate. GitHub supplies the runtime matrix, quality job, and gate results
directly to release preparation through the workflow's `needs` context. These
aggregate results are retained as `ci-results.json` in the evidence ZIP; the
script does not query job display names or reconstruct earlier run attempts.
On a retry, successful dependencies and their artefacts can be reused.

The `main` branch is protected by a GitHub ruleset requiring a pull request, this
status check, and an up-to-date branch before merging. Another person's approval
is not required. Rulesets are maintained on GitHub separately from workflow files;
committing a workflow does not configure protection.

Workflow changes deserve scrutiny because a PR runs the workflow from its
temporary merged state. Keep action pins and runner labels current through
deliberate updates. Jobs normally have read-only repository permission. Only the
tag-triggered draft-preparation job receives release write permission, after the
CI gate succeeds; it does not run on pull requests, branch pushes, or manual runs.

## Versioning and compatibility

Release tags use `v<version>`, for example `v1.0.0`. Git-derived version
calculation and the CI tag trigger select that prefix. A clean checkout tagged
`v1.0.0` builds as version `1.0.0`.
Do not rename or move published tags.

The software, comparison-configuration schema, and results schema have independent
versions. The user guide and release notes identify supported schema combinations;
unsupported versions or combinations are rejected. A configuration-format change
does not by itself require a results-schema revision: assess results structure
and meaning separately. Preserve schema identifiers unless a deliberate version
change is approved.

Before changing a schema, publish compatibility rules; incompatible changes need
a migration path or documented transition arrangements. Changes to distribution,
executable, or import-package names also need compatibility consideration.

## Preparing a release

Publication is manual. Pushing a release tag starts its full CI and,
after the required checks succeed, prepares a **draft GitHub Release** with the
tested distributions and verification evidence. Review and complete the release
notes before choosing **Publish release**. CI never publishes the draft.

The four steps below use version `1.0.0` and tag `v1.0.0` as examples; substitute the intended version consistently.

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

   Choose an unused semantic version and its tag, for example
   `v1.0.0`. Check **Tags** and **Releases** for existing names.
   Do not move or reuse a tag for different source. You can start writing release
   notes in a local editor now, or write them in the generated draft in step 3.
   Notes describe the changes, known limitations, supported runtimes, and schema
   compatibility; they are the release's description on GitHub, not a required
   repository file.

2. **Tag the merged source and push the tag — terminal on your computer.**

   If you do not have a checkout, run these commands in a directory where you
   want the repository to be created:

   ```console
   git clone https://github.com/advISO-project/advISO_compare_tool.git
   cd advISO_compare_tool
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
   git tag -a v1.0.0 -m "adviso-compare 1.0.0" origin/main
   git push origin v1.0.0
   ```

   This tags the fetched `main` commit without switching branches or changing
   your working files. Check that this is the intended release point before
   pushing. The workflow containing draft preparation must already be merged
   there. The workflow checks that its source is merged into `main` and that the
   built version matches the tag.

3. **Wait for verification and review the draft — GitHub web interface.**

   Open **Actions**, select **adviso-compare CI**, and open the run for the
   pushed tag. Wait for the complete workflow, including **Prepare draft
   release**, to succeed. The full runtime matrix, formatting/lint
   checks, schema/example checks, builds, and clean installation tests must pass.

   Open **Releases** and edit the draft for this tag. CI attaches:

   - the tested `.whl` and `.tar.gz`, copied without rebuilding;
   - `release-verification.md`, identifying the tag, commit, CI run/attempt,
     environments, schema versions, checks, and distribution hashes;
   - `verification-evidence.zip`, containing all matrix and quality-check
     reports, environment/dependency records, and workflow dependency results; and
   - `SHA256SUMS.txt`, with complete SHA-256 hashes for the other four assets.

   These are **release assets**, distinct from GitHub's automatically generated
   source-code ZIP and tarball. The distributions come from the tested
   `adviso-compare-ubuntu-24.04-python-3.11` artefact. The attached evidence retains
   verification records beyond CI artefact expiry. Dependency records identify
   what was tested; they do not fix future dependency resolution.

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
   **Set as latest release** for the current stable release as appropriate.

   Open the published release and confirm its notes and five attached assets
   are present. No package-index publication is configured by this process.

Additional independent review, signing/build attestation, property-based testing,
and mutation testing are optional. Record them if performed; they are not
release gates and another person's approval is not a merge requirement.

### Release preparation implementation

The development-only [script](.github/scripts/adviso_compare_release.py) validates
the tag, merged source, workflow dependency results, commit identifiers, JUnit
reports, distribution versions, and required evidence before assembling the five
assets.
Its [tests](.github/scripts/test_adviso_compare_release.py) use synthetic artefacts
and mocked GitHub commands; they do not create releases. It uses the GitHub-hosted
runner's GitHub CLI and workflow token; no additional secret is required.

The distribution and executable are `adviso-compare`; the import package is
`adviso_compare`. Distribution filenames are
`adviso_compare-<version>-py3-none-any.whl` and
`adviso_compare-<version>.tar.gz`. The supported schema combination is configuration
`1.0` with results `1.0`. CI's full suite checks schemas, offline examples, and
clean installations before preparing the draft.
