# Contributing to `adviso-compare`

Read the repository [contribution guide](../../CONTRIBUTING.md), which applies to
human contributors and agents alike. The
[implementation guide](docs/implementation-guide.md) explains the implementation and
points to the code and tests for each responsibility. The commands below run
from the repository root and apply to this package. Other tools have their own
development setup.

## Environment and editable installation

Linux is fully supported with CPython 3.11, 3.12, 3.13, 3.14, and 3.15. Windows
and macOS are expected to work, with full CI coverage on CPython 3.15 only.
Use the latest available patch release. Python 3.11 is the installation minimum;
additional Python/platform combinations need verification before joining the
verified matrix.

Follow the shared [environment guidance](../../CONTRIBUTING.md#development-environments)
and activate an isolated environment with a supported Python version.

Install the package and its development dependencies into that environment:

```console
python -m pip install -e "packages/adviso-compare[dev]"
```

The editable installation makes source changes available to the installed
`adviso-compare` command. Versions come from Git through `setuptools-scm`;
`src/adviso_compare/_version.py` is generated and is not maintained by hand.
Build and development environments require `setuptools-scm` 10.3.4 or later
for the package's tag-prefix configuration.

## Tests and checks

Run the complete package suite with:

```console
python -m pytest packages/adviso-compare/tests -q
```

For a focused run, select a relevant test module, for example:

```console
python -m pytest packages/adviso-compare/tests/test_inputs.py -q
```

The suite includes configuration and results schema validation, CLI behaviour,
documentation examples, and distribution builds and installation. The
[test conventions](#test-conventions) describe shared fixtures and schema helpers.

Additional local checks are:

```console
python -m pip check
python -m compileall -q packages/adviso-compare/src packages/adviso-compare/tests
git diff --check
```

The [CI workflow](../../.github/workflows/adviso-compare-ci.yml) requires Ruff
formatting and lint checks alongside the test, schema, example, build, and
installed-product checks. No type checker is configured.

### Formatting and linting

Follow the shared [Ruff policy](../../CONTRIBUTING.md#formatting-and-linting).
Run the checks from the repository root:

```console
python -m ruff format --check packages/adviso-compare
python -m ruff check packages/adviso-compare
```

For local cleanup, review the diff after running:

```console
python -m ruff check --fix packages/adviso-compare
python -m ruff format packages/adviso-compare
```

This package targets Python 3.11. `UP042` is excluded to retain the existing
enums' string conversion behaviour; converting to `StrEnum` is a separate
behavioural decision. The exact rule selection and Ruff pin live in
[`pyproject.toml`](pyproject.toml). No type checker is configured.

### Test conventions

Follow the shared [testing and fixture conventions](../../CONTRIBUTING.md#testing-and-fixtures).

Maintain coverage of parsing, translation, comparators, result semantics,
schemas, CLI errors and exit codes, deterministic output, and clean wheel and
source-archive installations. Exercise malformed inputs, both directions of
missing/extra content, composite and duplicate keys, and tolerance boundaries.

Reusable synthetic documents are built in `tests/support/documents.py`. Builders
return new objects on every call so tests can modify a document without leaking
state into another test. Fixed values are intentional: generated fixtures must
be deterministic and reviewable. A future generated on-disk fixture must record
its generator and regeneration command alongside the fixture.

Schema loading and validator construction live in `tests/support/schemas.py`.
Structural validators load each document's packaged schema independently and
enable JSON Schema format assertion.

## Build distributions

With the development dependencies installed, build a wheel and source archive:

```console
python -m build --no-isolation --outdir packages/adviso-compare/dist packages/adviso-compare
```

The output directory is generated content. The distribution test builds both
archives once, then installs each into a separate fresh virtual environment.
It resolves declared dependencies without borrowing development site-packages;
source-archive installation also uses isolated build dependencies. These tests
may need network access to a package index.

Both installations run outside the checkout, check dependency consistency and
installed resources, and exercise the same automatic, custom, repeated-run, and
error scenarios. Evidence is also validated using each installed package. The
archives and resolved dependency records remain in the pytest base temporary
directory for the run.

## Documentation and examples

The [user guide](docs/user-guide.md) and `docs/examples/` are installed with the
distribution. Check their runnable examples and installed copies with:

```console
python -m pytest packages/adviso-compare/tests/test_documentation.py packages/adviso-compare/tests/test_distribution.py -q
```

An editable installation does not keep installed documentation copies in sync
with edits to their source files. Use the maintained source guide during
development; the distribution test checks the guide installed from a fresh
wheel against that source.

The [user guide](docs/user-guide.md) defines observable behaviour and semantic
rules. The packaged [schemas](src/adviso_compare/schemas/) define permitted JSON
structures and structural constraints. Tests verify this contract; the
implementation guide explains its implementation. Resolve disagreements explicitly
rather than allowing one document or a passing test to silently override another.

The guide must remain usable offline and cover the complete CLI, supported
inputs, automatic and custom configuration rules, output fields, validation,
errors, limitations, and governance boundaries. Complete configuration and
results examples must validate against their respective schemas, and worked
commands must produce their documented outcomes. A material disagreement among
the guide, schemas, examples, and implementation blocks release.

## Continuous integration

The workflow runs on pull requests targeting `main` (including updates to those
pull requests), pushes to `main`, pushes of tags matching `adviso-compare-v*`,
and manual requests.
Pushes to development branches without an open pull request do not trigger it.
For `adviso-compare-v*` tag pushes only, a final job prepares a draft release
after the aggregate CI gate succeeds. Publication remains manual. Tags belonging
to other tools do not trigger this workflow.

A separate `adviso-compare / Ruff` job runs formatting and lint checks once on
`ubuntu-24.04` with CPython 3.11. It installs the development dependencies from
the package, including the pinned Ruff version, and checks without modifying
files. It also checks `.github/scripts/` using this package's Ruff configuration
and runs the release-preparation tests once. It runs alongside the seven runtime
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
python -m pytest packages/adviso-compare/tests -q --junitxml=ci-output/tests.xml --basetemp=ci-output/tmp
```

`ci-output/` is ignored generated content. Pytest clears the selected base
temporary directory before a run; use this command only with that disposable
path. The normal test command above lets pytest manage its own temporary path.

### Required status check

The aggregate check is **`adviso-compare CI passed`**. It succeeds only when all
seven runtime jobs and the Ruff/release-automation job succeed. The tag-only
draft-preparation job follows this gate; it does not change the required check. It is required by the `main`
ruleset; see the shared [merge settings](../../CONTRIBUTING.md#continuous-integration-and-merge-settings).

## Making a change

Start with the [user guide](docs/user-guide.md) and the relevant packaged
[schema definitions](src/adviso_compare/schemas/). Resolve any disagreement
between those sources before changing behaviour. The implementation guide's
[change map](docs/implementation-guide.md#where-to-make-a-change) helps locate the
implementation and existing tests.

Follow the shared [change workflow](../../CONTRIBUTING.md#working-on-a-change)
and documentation checks. Update the implementation guide when responsibilities
or data flow change.

## Compatibility and versioning

Follow the shared [versioning and compatibility policy](../../CONTRIBUTING.md#versioning-and-compatibility).
The software, comparison-configuration schema, and results schema have independent
versions. The user guide and release notes identify supported schema combinations;
unsupported versions or combinations are rejected. A configuration-format change
does not by itself require a results-schema revision: assess changes to results
structure or meaning separately. Preserve schema identifiers unless a deliberate
version change is approved.

## Release details

Follow the shared [release procedure](../../CONTRIBUTING.md#preparing-a-release),
using these values. The software version is independent of both JSON format
versions. CI prepares the draft and its assets; publication is manual.

| Detail | Value |
| --- | --- |
| Package directory | `packages/adviso-compare` |
| Distribution / executable / import package | `adviso-compare` / `adviso-compare` / `adviso_compare` |
| Release tag | `adviso-compare-v<version>`, for example `adviso-compare-v1.0.0` |
| CI tag filter | `adviso-compare-v*` |
| Workflow | `.github/workflows/adviso-compare-ci.yml`, displayed as **adviso-compare CI** |
| Required aggregate check | **`adviso-compare CI passed`** |
| Runtime verification | Full suite on all seven combinations in the matrix above, including clean wheel and source-archive installations |
| Quality verification | **adviso-compare / Ruff**, including release-preparation tests |
| Draft-preparation job | **adviso-compare / Prepare draft release**, after successful tag CI |
| Automated distribution source | `adviso-compare-ubuntu-24.04-python-3.11`; CI copies its tested archives without rebuilding |
| Distribution filenames | `adviso_compare-<version>-py3-none-any.whl` and `adviso_compare-<version>.tar.gz` |
| Additional release assets | `release-verification.md`, `verification-evidence.zip`, `SHA256SUMS.txt` |
| Supported schema combination | Configuration `1.0`, results `1.0` |
| Documentation/schema verification | Offline guide/examples and packaged schemas, included in the full suite |

The development-only script [adviso_compare_release.py](../../.github/scripts/adviso_compare_release.py)
validates the tag, merged source, successful jobs, source identifiers, JUnit
results, distribution versions, and required evidence before assembling the
assets. Its [tests](../../.github/scripts/test_adviso_compare_release.py) use small
synthetic artefacts and mocked GitHub commands; they do not create releases.
To run them locally with development dependencies installed:

```console
python -m pytest .github/scripts/test_adviso_compare_release.py -q
python -m ruff format --check packages/adviso-compare
python -m ruff check packages/adviso-compare
python -m ruff format --check --config packages/adviso-compare/pyproject.toml .github/scripts
python -m ruff check --config packages/adviso-compare/pyproject.toml .github/scripts
```

Only the draft-preparation job has repository write permission. It uses the
GitHub-hosted runner's GitHub CLI and workflow token; maintainers do not need a
local CLI or additional secret. It never publishes a release. A preparation
retry preserves edited draft notes, replaces generated assets, and refuses to
modify a published release.

Version derivation selects only `adviso-compare-v` tags; unrelated tools' tags
do not set this package's version. `_version.py` is generated. For example,
a clean checkout tagged `adviso-compare-v1.0.0` builds as `adviso-compare 1.0.0`.
