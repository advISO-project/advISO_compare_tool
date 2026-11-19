# Contributing to the AdvISO validation toolkit

This repository contains independently installable tools with independent
versions, dependencies, and release schedules. Start with the selected package's
README and contribution guide. This guide defines the shared development and
release process; package guides supply commands, supported environments,
behavioural sources, and any additional verification requirements.

The first tool is [`adviso-compare`](packages/adviso-compare/README.md); its
[contribution guide](packages/adviso-compare/CONTRIBUTING.md) supplies its development
setup and release details. Additional tools should provide the same information
when their implementation is approved.

## Where guidance belongs

| Location | Purpose |
| --- | --- |
| Repository README | Tool catalogue and repository overview. |
| This guide | Shared environment guidance, contribution conventions, and release procedure. |
| `AGENTS.md` files | Agent instructions and detailed code-quality/change-control guidance. |
| Package README | Tool overview, behavioural sources, and developer entry points. |
| Package contribution guide | Supported runtimes, exact commands, fixtures, CI and release details, and exceptions to shared conventions. |
| Package `docs/` | User documentation and implementation guidance. |
| Package `tests/` | Executable verification and controlled synthetic fixtures. |

Keep tool-specific implementation and dependencies within the relevant package.
Shared code or tooling should follow a concrete need agreed for the affected
packages. Shared procedures do not require a shared Python environment, wheel,
software version, dependency selection, or release date.

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

1. Read the applicable `AGENTS.md` instructions and the selected package's
   behavioural contract, schemas, and contribution guidance.
2. Run relevant existing tests to establish a baseline.
3. For an approved behavioural change or defect fix, adapt existing tests where
   possible and add focused coverage for uncovered behaviour. Confirm that a
   new regression fails for the expected reason before implementing the fix.
4. Keep implementation changes scoped to the selected package. Run focused
   checks during development, then its wider tests and relevant packaging checks.
5. Keep schemas, examples, user documentation, and implementation aligned. Update
   implementation guidance when responsibilities or data flow change.
6. Report what changed, commands and results, and remaining verification limits.
   Distinguish local checks from verification across supported environments.

For documentation-only work, check links and examples. Run documentation and
installed-distribution checks when changing published instructions or installed
files. A change to a shared procedure needs review against each affected tool's
configuration; it does not automatically require rerunning every behavioural test.
Detailed code-quality and change-control guidance is in [AGENTS.md](AGENTS.md).

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
or acceptance-scenario identifiers in tests, fixtures, or snapshots. Any formal
traceability belongs in review records as a one-way reference to software
artefacts. Every corrected material defect needs appropriate regression coverage;
adapt existing tests where they express the rule clearly.

Give parameterized cases descriptive IDs when inputs contain complex objects,
mutations, or several expected values. Simple scalar values can use default IDs.
Keep variants of one rule together; use separate tests when behaviours require
substantially different setup or assertions. Small helpers can share mechanical
setup while keeping inputs and expectations visible.

Use controlled, synthetic, non-sensitive fixtures under version control. Keep
purpose, configuration, inputs, and expected outcomes clear from the test or
fixture. Generated fixtures must be deterministic and document their generator
and regeneration command. For retained release evidence, identify fixture source
revisions or generation methods and record additional review if performed;
fixture digests may supplement the source revision. Do not imply independent
review when none occurred.

Package guides describe required coverage, helpers, special checks, and build or
installation scenarios. Property-based and mutation testing are optional
techniques, not mandatory release gates. Not every documentation or process rule
needs a direct automated test.

## Documentation

Keep user instructions accurate for the implemented software and distinguish
machine-enforced constraints from explanatory guidance. Complete examples should
validate against their applicable schemas and worked commands should produce the
documented outcomes. A material disagreement between behavioural documentation,
schemas, examples, and implementation must be resolved before release.

Developer setup and release procedures belong in contribution guidance; user
concepts and operational instructions belong in user documentation. Each package
identifies its authoritative behavioural sources and which documentation and
examples are shipped for offline use.

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


Release publication is manual; the CI workflow builds and verifies distributions
but does not publish them. Each release needs:

- a fixed semantic version and immutable source identification;
- passing full-suite CI on all combinations in the selected tool's verification matrix;
- passing Ruff formatting and lint checks;
- passing documentation/example, schema, build, and installed-product checks;
- release notes stating changes, known limitations, supported runtimes, and
  supported schema versions and combinations; and
- retained verification evidence identifying the source commit, published
  artefacts and SHA-256 checksums, checks and outcomes, environments, and resolved
  dependencies.

Additional independent review, signing or build attestation, property-based
testing, and mutation testing are optional. Record them if performed. They are
not release gates, and another person's approval is not a merge requirement.

Follow the selected package's **Release details** table when using the following
six steps. The commands illustrate an `adviso-compare` release; for another tool,
use its package directory, release tag, executable, workflow, required checks,
and distribution filenames. Read those details before copying commands.
Commands in steps 1–2 run in a terminal at the repository root, with the
development environment activated. Steps labelled
**GitHub web interface** take place in the repository on GitHub. Use a separate
directory outside the checkout for downloaded release files and records, so
preparing those records does not change the tagged source tree.

Before starting, use a text editor to create `release-verification.md` in that
external directory. This is the **verification record** for this release: it
connects the published files to their source commit and verification evidence.
Fill it in as you proceed, recording the version/tag, commit SHA, CI run and
outcomes, distribution filenames and checksums, and any limitations or additional
review. It will be attached to the GitHub Release with the supporting CI records.

The examples use version `1.0.0` and tag `adviso-compare-v1.0.0`; substitute the
intended version consistently. They assume `origin` points to this repository.
Creating tags and publishing require repository write access.

1. **Confirm release readiness — terminal and GitHub web interface.**

   Confirm that all features and fixes intended for the release have been merged
   into `main`. A release may collect several already-merged changes. There is
   no requirement for a separate release-preparation branch or pull request.

   Review the user guide, examples, runtime support, licensing, package metadata,
   and schema compatibility statements. Draft release notes describing the
   capabilities or changes, their impact on comparison semantics and evidence
   formats, supported Python/OS combinations, supported schema combinations,
   and known limitations. Keep the draft outside the checkout unless a source
   documentation change is intended.

   In the terminal, install the development dependencies and run:

   ```console
   python -m pip install -e "packages/adviso-compare[dev]"
   python -m ruff format --check packages/adviso-compare
   python -m ruff check packages/adviso-compare
   python -m pytest packages/adviso-compare/tests -q
   python -m pip check
   git diff --check
   ```

   The suite includes schema/example checks, builds, and clean installations of
   both distributions. These local results cover your environment only.

   If the readiness review or checks identify changes to repository files, such
   as documentation or package metadata, make those changes through the normal
   development branch and pull-request process. Wait for the required aggregate
   CI check listed in the package guide and merge them into `main` before tagging.
   Otherwise, proceed directly to step 2 without another branch or pull request.

2. **Select and tag the merged source — terminal.**

   Start with a clean checkout: `git status --short` should show no changes.
   Fetch tags and update the local `main` branch without creating a merge commit:

   ```console
   git fetch origin --tags
   git switch main
   git pull --ff-only origin main
   git status --short
   git rev-parse HEAD
   git tag --list adviso-compare-v1.0.0
   ```

   Confirm the checkout is still clean and `HEAD` is the intended merged release
   commit. Save its full SHA for the verification record. The tag-list command
   should print nothing for a new version; stop if that tag already exists.
   Then create an annotated tag at that commit and check the derived version:

   ```console
   git tag -a adviso-compare-v1.0.0 -m "adviso-compare 1.0.0"
   git rev-parse "adviso-compare-v1.0.0^{commit}"
   python -m pip install -e "packages/adviso-compare[dev]"
   adviso-compare --version
   ```

   The tag's commit must match the saved SHA and the installed executable must
   report version `1.0.0`, without a development or local suffix. Reinstalling
   the editable package refreshes its installed version metadata after tagging.
   Follow the selected package's version-check command: a bare
   `setuptools_scm.get_version(root='.')` call does not load its tag-filter
   configuration. Do not edit generated version files. Once these checks pass,
   push only the selected tag:

   ```console
   git push origin adviso-compare-v1.0.0
   ```

   Do not move an existing published tag or replace published distribution
   files. Corrections receive a new version.

3. **Build and verify the tagged release — GitHub web interface.**

   Pushing `adviso-compare-v1.0.0` in step 2 automatically starts CI for that tag.
   The tagged commit must contain the tool-specific tag-push trigger, so merge this
   configuration before creating the release tag. No separate dispatch command
   or local release build is needed.

   On GitHub, open **Actions**, select the workflow listed in the package guide,
   and select the new tag-push run. Confirm it identifies the intended tag and
   commit. Wait for all declared runtime test jobs, the Ruff job, and the required
   aggregate CI check listed in the package guide to succeed. Each
   runtime job builds and tests the wheel and source archive; no separate local
   release build is needed. Record the run URL and run attempt. If source changes
   are needed, return to release preparation and use a new version/tag for the
   corrected candidate. For an infrastructure failure on unchanged tagged source,
   use **Re-run jobs → Re-run failed jobs** on the run page; record the successful
   attempt. Building and testing are automatic; publication remains manual in
   step 6.

4. **Download the verified distributions — GitHub web interface and terminal.**

   In the successful run's summary, find **Artifacts**. Download all test
   artefacts before the retention deadline listed in the package guide. Keep the
   downloaded ZIPs with their distinct job names. Use the preferred distribution
   artefact listed there as the source of the release files; extract that ZIP
   into its own directory outside the checkout. Retain the other ZIPs as evidence
   of the remaining matrix jobs.

   Locate the distributions and verification records using the package guide.
   In the `adviso-compare` example, the `distributions` directory contains
   the wheel, the source archive, `wheel-dependencies.txt`, and
   `sdist-dependencies.txt`. The artefact also contains `tests.xml`, `commit.txt`,
   `python.txt`, `platform.txt`, and `test-dependencies.txt`; extraction may
   preserve intermediate directories. Check that `commit.txt` matches the saved
   release SHA and the archive filenames identify the intended version.

   In a terminal, change to the directory containing the two distribution files
   and calculate their SHA-256 checksums using the development environment's
   Python, or another Python with pip installed:

   ```console
   python -m pip hash --algorithm sha256 adviso_compare-1.0.0-py3-none-any.whl adviso_compare-1.0.0.tar.gz
   ```

   Copy the filenames and complete hashes into `release-verification.md`. These
   exact files were exercised by the clean-installation tests. Do not substitute
   local rebuilds. If a rebuild is necessary, verify the replacement archives
   and record their new checksums before publication.

5. **Assemble the release evidence and draft — local editor and GitHub web interface.**

   Review and complete the existing `release-verification.md`. Check that it
   records the version/tag, full commit SHA, CI run URL and attempt,
   supplying artefact/job, matrix outcomes and Ruff outcome, distribution
   filenames and SHA-256 hashes, and known limitations or additional review.
   State that the suite included schema, documentation/example, determinism,
   and clean wheel/source-installation checks. The downloaded records identify
   the exact environments and resolved dependencies; retain them with this file.

   On GitHub, open **Releases → Draft a new release**. Select the **existing**
   `adviso-compare-v1.0.0` tag, give it a title such as `adviso-compare 1.0.0`, and
   paste the release notes from step 1. Attach the verified `.whl` and `.tar.gz` files,
   `release-verification.md`, and all CI artefact ZIPs. Retain the workflow
   logs as well, including the Ruff results, using the run's log-download option.
   Include those logs as a release attachment. Choose **Save draft** while
   checking that all notes and attachments are complete.

   This keeps release evidence beyond ordinary CI retention without growing a
   rolling document in the source repository. GitHub's automatically generated
   **Source code** downloads are repository snapshots; they are not substitutes
   for the tested Python source distribution. See
   [downloading workflow artefacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
   and [creating a release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository?tool=webui).

6. **Publish and confirm the files — GitHub web interface and terminal.**

   Review the draft's tag, version, notes, evidence, and distribution attachments.
   For a stable release, leave **This is a pre-release** unchecked and select
   **Set as latest release** as appropriate. The latest-release label is
   repository-wide, so choose it deliberately when tools have independent release
   versions. Once ready, choose
   **Publish release**.

   Download the published wheel and Python source archive into a separate
   directory. In a terminal there, rerun the `python -m pip hash` command from
   step 4. Confirm both filenames and hashes match `release-verification.md`.
   Keep those verified files and records together.

   A GitHub Release distributes the attached files; it does not publish them to
   PyPI. Users can install the wheel using the user guide's file-based commands.
   If package-index publication is also wanted, arrange that separately and
   upload the same verified distribution files rather than rebuilding them.

The build and installation commands above also support local preparation, but
a passing local suite does not replace the required matrix evidence. The
release dependency records document what was installed and tested for those
artefacts. They do not constrain future installations to the same dependency
versions or guarantee that users will resolve identical environments.
