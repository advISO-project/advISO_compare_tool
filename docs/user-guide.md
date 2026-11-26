# `adviso-compare` user guide

## Contents

- [1. Introduction](#1-introduction)
  - [1.1 Records, fields, and comparison rules](#11-records-fields-and-comparison-rules)
  - [1.2 Findings and run status](#12-findings-and-run-status)
- [2. Installation](#2-installation)
  - [2.1 Install with pip](#21-install-with-pip)
  - [2.2 Install with pipx](#22-install-with-pipx)
  - [2.3 Check the installation](#23-check-the-installation)
- [3. Quick start](#3-quick-start)
  - [3.1 Run your first comparison](#31-run-your-first-comparison)
  - [3.2 Read and interpret the results](#32-read-and-interpret-the-results)
- [4. Command and input reference](#4-command-and-input-reference)
  - [4.1 Command options and exit codes](#41-command-options-and-exit-codes)
  - [4.2 Input datasets](#42-input-datasets)
  - [4.3 Automatic mode](#43-automatic-mode)
- [5. Custom comparison configurations](#5-custom-comparison-configurations)
  - [5.1 A small custom comparison](#51-a-small-custom-comparison)
  - [5.2 Runnable custom example with transformations](#52-runnable-custom-example-with-transformations)
  - [5.3 Configuration checks and conventions](#53-configuration-checks-and-conventions)
  - [5.4 Top-level properties](#54-top-level-properties)
  - [5.5 Field definitions](#55-field-definitions)
  - [5.6 Logical types](#56-logical-types)
  - [5.7 Null policy and typed value descriptions](#57-null-policy-and-typed-value-descriptions)
  - [5.8 Source normalisation](#58-source-normalisation)
  - [5.9 Value mapping](#59-value-mapping)
  - [5.10 Collections written as text](#510-collections-written-as-text)
  - [5.11 Typed normalisation](#511-typed-normalisation)
  - [5.12 Comparators](#512-comparators)
  - [5.13 Processing order](#513-processing-order)
- [6. The evidence package](#6-the-evidence-package)
- [7. JSON output reference](#7-json-output-reference)
  - [7.1 `comparison-configuration.json`](#71-comparison-configurationjson)
  - [7.2 `comparison-results.json`](#72-comparison-resultsjson)
- [8. Errors and corrective action](#8-errors-and-corrective-action)
- [9. Security, governance, and limitations](#9-security-governance-and-limitations)
- [10. Reproducing the examples](#10-reproducing-the-examples)

## 1. Introduction

`adviso-compare` compares a reference dataset with a query dataset, such as the
output of a bioinformatics pipeline. A comparison configuration describes how
to pair records, associate fields, and translate values into a shared form.
The tool reports differences that remain after translation and problems that
prevented parts of the comparison.

The output is comparison evidence. Your laboratory decides how that evidence
contributes to its validation and quality processes; the tool does not make an
acceptance decision or establish ISO 15189 compliance.

This guide defines observable behaviour and comparison semantics for `adviso-compare`. The packaged JSON schemas define permitted JSON structures and structural constraints. Examples illustrate the rules rather than prescribe laboratory comparison policies.

### 1.1 Records, fields, and comparison rules

A dataset contains **records**, such as rows in a CSV file. Each record has
**fields**, such as a sample identifier or a measurement. The **reference**
is the dataset you compare against; the **query** is the dataset being checked.

A **record key** identifies corresponding records on the two sides. For
example, a sample identifier can pair a reference row with the query row for
the same sample. A key uses one field, or several fields together as a
**composite key**. Keys are unique within each dataset; record order does not
establish correspondence.

A configuration can associate differently named source fields with one
**canonical field**: a shared name used within the comparison. For example,
reference field `resist_stat` and query field `res_stat` could both represent the canonical field `resistance_status`. A **logical type**, such as decimal or date, describes how to interpret a value. A **comparator** is the rule used to decide whether two values match. The resulting shared representations are called
**canonical values**.

A **parser-native value** is the value and type read from the input before
configured transformations. CSV cells start as text; JSON can distinguish
text, numbers, booleans, and other value types. A scalar is a single value,
such as a string or number, rather than a collection of values.

A present field can contain **null**, an explicit no-value marker. An absent
field is missing entirely; an empty string is present text with no characters.

The **effective configuration** is the configuration used for a run. You can
supply a custom configuration, or let automatic mode generate one. Its
**scope** selects the fields to assess. Fields outside that scope are reported
as **exclusions** and are not compared.

### 1.2 Findings and run status

The report contains **findings**: individual differences or problems that
prevented assessment. Findings have two broad meanings:

- A **comparison difference** remains after the applicable translation and
  comparison rules have been applied.
- An **assessment issue** explains a problem applying those rules, such as a
  required field being absent or a value that cannot be interpreted as declared.

A run is **complete** when every applicable comparison was performed. It can
be complete and still report differences. A run is **incomplete** when some
intended value comparisons could not be performed. Both produce an **evidence
package**: a directory containing the results, configuration, and HTML report.
An execution error prevents a trustworthy result and produces no new package.

## 2. Installation

`adviso-compare` requires Python 3.10 or later. It is fully supported on Linux
with CPython 3.10, 3.11, 3.12, 3.13, 3.14, and 3.15. Windows and macOS are expected to work, with pre-release testing done on CPython 3.10 only. You should use the latest available patch release of your selected Python version.

You can download the `.whl` file for your chosen release from
[GitHub Releases](https://github.com/advISO-project/advISO_compare_tool/releases),
or use a wheel supplied by your laboratory. In the commands below, you should
replace `/path/to/adviso_compare-VERSION-py3-none-any.whl` with the actual path
and versioned filename on your system. Paths containing spaces need quotes.

You can install into an existing virtual environment with `pip`, create a new
one, or use `pipx` to manage a dedicated environment for the tool. Installing
the wheel with `pip` does not install or upgrade Python itself. If you have no
supported Python installation, you can obtain one from
[python.org](https://www.python.org/downloads/) or your system administrator.

The commands are intended for a terminal. Long commands elsewhere in this guide
use a trailing `\` to continue onto the next line in bash or zsh. In Windows
Command Prompt or PowerShell, the equivalent command is a single line, with
spaces in place of the continuation backslashes and line breaks.

### 2.1 Install with pip

If you already have a virtual environment, you can activate it and continue to
the version check below. For a new environment, you should first choose an
installed Python version supported by the tool. These examples select Python
3.12; you can substitute another supported installed version if needed.

On macOS or Linux, you can create and activate the environment with:

```console
python3.12 -m venv .venv
. .venv/bin/activate
```

On Windows, the Python launcher can create the environment:

```console
py -3.12 -m venv .venv
```

You can then activate it with `.venv\Scripts\activate` in Command Prompt, or
`.venv\Scripts\Activate.ps1` in PowerShell. If you do not use the Python
launcher, you can replace `py -3.12` with the path to your chosen Python
executable. PowerShell needs `&` before a quoted executable path.

With the environment active, `python --version` should report Python 3.10 or
later. You can then install the wheel and its dependencies:

```console
python --version
python -m pip install "/path/to/adviso_compare-VERSION-py3-none-any.whl"
```

### 2.2 Install with pipx

If you use [pipx](https://pipx.pypa.io/stable/), you can select the Python
interpreter for the tool's environment with `--python`. The installed version
needs to be supported by both `adviso-compare` and `pipx`; `pipx` may require
a newer Python than the tool's 3.10 minimum. This example selects Python 3.12:

```console
pipx install --python 3.12 "/path/to/adviso_compare-VERSION-py3-none-any.whl"
```

You can also give `--python` the full path to your chosen Python executable.
`pipx` creates and manages a separate virtual environment for `adviso-compare`
and makes the command available on your PATH. There is no need to activate
that environment to run the command.

### 2.3 Check the installation

Installation may use a package index to obtain dependencies. Once installed,
the comparison itself needs no network service. After either installation,
you can check that the command is available with:

```console
adviso-compare --version
adviso-compare --help
```

The full guide is installed with the software under
`share/doc/adviso-compare/user-guide.md` in the Python environment.
For a `pipx` installation, this is the environment managed by `pipx`; `pipx list` shows where it keeps application environments.

## 3. Quick start

The installed examples provide a first comparison without creating a
configuration yourself. You can start with the automatic example and explore
its report. Section 5 shows how to supply your own configuration.

### 3.1 Run your first comparison

**Automatic strict-exact mode** is suitable when both datasets already use the
same field names and representations. It generates the comparison configuration
for you when `--configuration` is omitted.

To try the examples, you can copy the `examples` directory installed next to
this guide to a writable location outside the Python environment. The copy
should include both its `automatic` and `custom` subdirectories. The commands
below create evidence beside your copies of the inputs.

From the copied `examples` directory, you can run:

```console
adviso-compare \
  --reference automatic/reference.csv \
  --query automatic/query.csv \
  --output automatic-evidence
```

The single-line equivalent for Windows Command Prompt or PowerShell is:

```console
adviso-compare --reference automatic/reference.csv --query automatic/query.csv --output automatic-evidence
```

The example has no `record_id`. `sample_id` is the only valid key candidate, so
it is discovered automatically. The run is complete and reports one changed
`lineage`. The query-only `pipeline_version` field appears in the exclusions.

The completion summary has this form, with a different run-directory name on
each invocation:

```text
Run status: complete
Comparison differences: 1
Assessment issues: 0
Evidence package: automatic-evidence/20261111T143205Z-123e4567-e89b-42d3-a456-426614174000
```

Repeating the command with `--output automatic-evidence` adds another run
directory while preserving the first. Section 6 shows the resulting layout.

Automatic mode is deliberately conservative. A custom configuration is useful
when source field names differ, values require translation, a composite key is
needed, or automatic key selection is ambiguous. [Section 4.3](#43-automatic-mode) gives the full selection rules.

### 3.2 Read and interpret the results

You can open `comparison-report.html` in the directory named by the completion
summary. Beside it are `comparison-results.json`, for software use and detailed
review, and `comparison-configuration.json`, the effective configuration.

A useful review order is run completeness, comparison differences, assessment
issues, then exclusions. The automatic example reports a complete run with one
comparison difference and no assessment issues. Its query-only
`pipeline_version` field was excluded, so it did not create a finding.

The report describes several aspects of the comparison:

#### 3.2.1 The reporting model

| Concept | What it describes | Examples |
| --- | --- | --- |
| Run status | Whether the comparison as a whole could be completed | `complete`, `incomplete`, `error` |
| Phase status | Whether one of the three comparison phases completed its applicable work | `complete`, `incomplete` |
| Finding | One reported difference or problem that requires attention | A missing record or an invalid field value |
| Finding classification | The broad meaning of a finding | `comparison_difference`, `assessment_issue` |
| Finding code | The specific type of finding | `value_mismatch`, `mapping_failure` |
| Value-opportunity outcome | What happened when one in-scope field was considered for one aligned record | `matched`, `mismatched`, `not_assessable` |
| Exclusion | A field that was deliberately or implicitly outside the comparison | A configured or undeclared field exclusion |
| Review priority | Optional presentation priority for a finding about a configured field | `low`, `normal`, `high` |

A finding is an individual entry in the report. Every finding has one
classification and one more-specific finding code. The classification explains
the general nature of the finding; the code explains exactly what happened.

#### 3.2.2 Comparison phases

Every comparison performs three phases in order:

1. **Contract:** checks that configured fields are present when required and
   can be translated under the declared rules for types, nulls, validity, and mapping.
2. **Records:** pairs records using their keys and identifies
   missing and extra records.
3. **Values:** compares each assessable, in-scope, non-key field in aligned
   records.

A problem in an earlier phase does not automatically stop all later work. The
tool continues wherever the required information remains valid and
unambiguous. The phase attached to a finding records where the finding arose;
it is separate from the finding's classification.

Contract checks cover every applicable record on each side, including records
without a counterpart. Values are compared only for aligned records. All
assessable differences are collected rather than stopping at the first finding.

#### 3.2.3 Findings, classifications, and codes

There are two finding classifications.

`comparison_difference` means that the relevant translation and comparison
prerequisites succeeded, and a difference remained. It includes a reference
record missing from the query, an extra query record, or two valid translated
values that do not match.

`assessment_issue` means that the declared translation or assessment could not
be applied cleanly to some input content. For example, a required field may be
absent or a source value may not have an entry in a configured mapping. Such an
issue can be important, but the tool cannot call it a post-translation
difference because the intended translation did not succeed.

The eight finding codes are:

| Code | Classification | Meaning |
| --- | --- | --- |
| `missing_record` | `comparison_difference` | A reference record has no aligned query record. |
| `extra_record` | `comparison_difference` | A query record has no aligned reference record. |
| `value_mismatch` | `comparison_difference` | Two valid translated values differ under the comparator. |
| `missing_required_field` | `assessment_issue` | A required source field is absent. |
| `type_mismatch` | `assessment_issue` | The source value type cannot be used for the declared logical type. |
| `invalid_field_value` | `assessment_issue` | The source value type is acceptable, but the value itself is invalid. |
| `null_policy_violation` | `assessment_issue` | A null is present where null is not allowed. |
| `mapping_failure` | `assessment_issue` | A closed mapping has no entry for the source value. |

Successful record and value matches are included in summary counts rather than
reported as individual findings.

#### 3.2.4 Value-opportunity outcomes

A value opportunity is one in-scope, non-key field considered for one pair of
aligned records. Every such opportunity is counted as exactly one of:

- `matched`: both sides were assessable and matched under the configured
  comparator;
- `mismatched`: both sides were assessable but did not match, producing a
  `value_mismatch` finding; or
- `not_assessable`: the intended comparison could not be performed because a
  prerequisite failed, producing the applicable `assessment_issue` finding.

`not_assessable` is a summary outcome, not a finding code. The associated
finding explains why the comparison could not be performed. At least one
not-assessable opportunity makes the values phase, and therefore the run,
`incomplete`.

#### 3.2.5 Run and phase status

The possible run statuses are:

- `complete`: every applicable comparison was performed;
- `incomplete`: the record model remains trustworthy, but at least one intended
  value comparison was not assessable; and
- `error`: no trustworthy comparison result could be produced, for example
  because an input was malformed or a record key was invalid.

In a published evidence package, the contract and records phases are always
`complete`. The values phase is `incomplete` when at least one value opportunity
is not assessable, and `complete` otherwise. The overall run status therefore
matches the values-phase status. An errored run has no evidence package and
therefore no reported phase statuses.

Contract findings do not themselves make the contract phase incomplete: the
check was performed and found a problem. Likewise, missing and extra records
do not make the records phase incomplete. A blocked value opportunity makes
the values phase incomplete. Issues confined to unaligned records can therefore
coexist with a complete run, because those records create no value opportunities.

#### 3.2.6 Exclusions and review priority

An exclusion records a field that was outside the comparison:

- `configured_field_excluded` means that the configuration describes the field
  but leaves it outside the selected scope;
- `undeclared_field_excluded` means that a source field was observed but is not
  represented by a field definition on that side.

Excluded fields are not assessed. They do not produce findings or value
opportunities, and they do not make a run incomplete. This is different from
`not_assessable`, which describes an intended comparison that could not be
performed.

`review_priority` may be `low`, `normal`, or `high`. It helps organise findings
about configured fields for human review. It does not change the comparison,
the finding classification, run status, or exit code, and it is not a statement
of clinical significance. Record findings (in contrast to field findings) do not carry a review priority; they are counted as `unassigned` in the priority summary.

## 4. Command and input reference

### 4.1 Command options and exit codes

Standard usage:

```text
adviso-compare \
  --reference REFERENCE \
  --query QUERY \
  --output OUTPUT \
  [--configuration CONFIGURATION]
```

| Option | Meaning |
| --- | --- |
| `--reference REFERENCE` | Reference dataset. Required. |
| `--query QUERY` | Query dataset produced by the pipeline. Required. |
| `--output OUTPUT` | Parent directory under which to create a new run directory. Required. |
| `--configuration CONFIGURATION` | Custom YAML comparison configuration. If omitted, automatic strict-exact mode is used. |
| `--version` | Print the installed version and exit. |
| `--help` | Print concise help and exit. |

`--output` selects a parent directory/folder. Each complete or incomplete run
creates its own sub-folder within the specified output folder and preserves existing content. Section 6 explains directory names, permissions, and publication errors.

The command prints a short completion summary to standard output. An execution
error is printed to standard error. Comparison attempts emit no progress stream.
The exit codes are:

| Code | Meaning |
| ---: | --- |
| `0` | The run is complete. This includes complete runs that found differences. |
| `1` | The run is incomplete because at least one intended value comparison was not assessable. An evidence package is still written. |
| `2` | Expected operational error, such as an invalid option, configuration, input, key, resource condition, or output destination. No evidence package is written. |
| `3` | Unexpected internal error. No evidence package is written. |

Exit code `0` means the configured comparison completed - it does not indicate
"validity" of the query dataset (or the pipeline that generated it).

### 4.2 Input datasets

The reference and query can independently be CSV, TSV, or JSON. The
case-insensitive filename extension selects the format: `.csv`, `.tsv`, or
`.json`. There is no format override. Both files must be UTF-8.

#### 4.2.1 CSV and TSV

CSV uses commas; TSV uses tabs. Both use a double quote as the quote character.
A double quote inside a quoted cell is written twice. Quoted cells may contain
the delimiter or a line break. LF and CRLF line endings are accepted.
There is no separate backslash escape mechanism.

A header is required. Header names must be non-empty and unique. Every data row
must contain the same number of cells as the header. All cells initially count
as strings, including empty cells and text that looks like a number or boolean.

#### 4.2.2 JSON

JSON must contain one array of record objects at its root, even when there is
only one record:

```json
[
  {"sample_id": "S1", "result": "detected"},
  {"sample_id": "S2", "result": "not_detected"}
]
```

A single root object is not accepted. Every array item must be an object.
Top-level record field names must be non-empty and unique. Duplicate member
names anywhere in the JSON give rise to an error.

JSON strings, integers, decimals, booleans, nulls, arrays, and objects retain
their natural JSON type. Decimal numbers are read exactly without first being
converted to binary floating point, and their original spelling is retained as
evidence. `NaN` and infinities are not valid JSON numbers.

Numbers without a fraction or exponent are integers; numbers with either are
decimals. Under `preserved_exact`, categories must agree: integer `1` and decimal `1.0` differ, while decimals `1.0`, `1.00`, and `1e0` match numerically. Arrays compare recursively in order; objects compare recursively by member name and value, regardless of member order.

#### 4.2.3 Empty datasets

`[]` is a valid zero-record JSON dataset. A header with no data rows is a valid
zero-record CSV or TSV dataset. A zero-byte file is not a valid dataset.

A custom configuration can compare empty datasets when it supplies the needed
field and key information. Automatic mode cannot select a key from two empty
JSON arrays because they expose no fields.

Headers still expose structure without records. A missing required column in a
header-only CSV/TSV produces one dataset-level `missing_required_field` finding
for that field and side. An empty JSON array exposes no field structure, so it
cannot produce that finding. Requirements on individual records have no
opportunities when there are no records.

With valid configuration and keys, two zero-record datasets have no record
differences or value opportunities, and their records and values phases are
complete. If only one dataset has records, each record is reported as missing
or extra as appropriate; there are still no value opportunities. Header-derived
contract findings do not change those phase statuses. In automatic mode, shared
`record_id` headers permit selection even when both tabular datasets are empty;
other automatic candidates require at least one shared value.

### 4.3 Automatic mode

`adviso-compare` discovers fields from CSV/TSV headers and from the union of
member names across all JSON records. It matches names exactly, including case
and whitespace, without aliases or Unicode normalisation. It selects the record
key as follows:

1. If both sides contain `record_id`, that field is used. It must contain a
   unique, non-null string in every record on both sides. An invalid shared
   `record_id` causes an error; the tool does not fall back to another field.
2. Otherwise, a candidate must be a shared field containing a unique,
   non-null string in every record on both sides, with at least one value shared
   between the datasets.
3. Exactly one candidate must remain. No candidate or more than one candidate
   is an `input.invalid_record_key` error.

Candidates use preserved strings without conversion or normalisation. The tool
does not rank candidates by name, column position, or degree of overlap, and
does not construct composite keys automatically.

The selected key is compared as a typed string. All other shared fields are
compared using strict parser-native equality: value types must match as well as
content. For example, JSON integer `1` does not equal JSON string `"1"`.
Fields found on only one side are reported as exclusions, not differences.

The tool creates an effective configuration internally and saves it as
`comparison-configuration.json` alongside the results and report. The key is required and non-nullable on both sides. Other shared fields are
optional, allow null (with nulls on each side considered equal), and use `preserved_exact` without additional processing. Canonical names and source names are identical. The `record_key` contains only the selected key; `in_scope` lists that key first, then the other shared fields in Unicode code-point order. The generated configuration is validated before assessment begins.

## 5. Custom comparison configurations

A custom configuration lets you choose the record key, associate different
reference and query field names, and declare how values are interpreted and compared. It is one UTF-8 YAML document. The `.yaml` or `.yml` suffix is recommended so that its format is easy to recognise.

### 5.1 A small custom comparison

This example pairs samples whose identifier fields have different names and
compares their measurements as decimals. In a working directory of your
choice, you can save the following as `reference.csv`:

```csv
record_id,measurement
S1,1.00
S2,2.00
```

The corresponding query can be saved as `query.csv` in the same directory:

```csv
sample_id,result
S1,1
S2,2.10
```

This complete configuration can be saved as `configuration.yaml`:

```yaml
schema_version: "1.0"
metadata:
  id: "org.example.simple-comparison"
  revision: "1"
fields:
  record_key: ["sample"]
  in_scope: ["sample", "measurement"]
  definitions:
    sample:
      source_fields: {reference: "record_id", query: "sample_id"}
      required: {reference: true, query: true}
      logical_type: "string"
      null_policy: {allowed: false, nulls_equal: false}
      comparator: {name: "typed_exact"}
    measurement:
      source_fields: {reference: "measurement", query: "result"}
      required: {reference: true, query: true}
      logical_type: "decimal"
      null_policy: {allowed: false, nulls_equal: false}
      comparator: {name: "numeric_exact"}
```

`schema_version` identifies the configuration format. `metadata` gives this
configuration a stable ID and revision; it does not change comparison rules.
`fields` describes record identity, scope, and the values to compare.

The canonical field `sample` associates the two identifier names and provides
the record key. `measurement` associates the values to compare. Both fields
are required on both sides, and neither permits null.
`typed_exact` compares the interpreted key strings; `numeric_exact` compares
exact decimal values. No tolerance or rounding is applied.

From that directory, you can run:

```console
adviso-compare \
  --reference reference.csv \
  --query query.csv \
  --configuration configuration.yaml \
  --output evidence
```

The run completes with one comparison difference and no assessment issues.
For `S1`, `1.00` and `1` represent the same decimal value. For `S2`, `2.00` and
`2.10` differ, producing one `value_mismatch` finding.

### 5.2 Runnable custom example with transformations

For a richer example, you can use the writable copy of the `examples` directory
from Section 3.1. If you are starting here, you can first copy the installed
`examples` directory to a working directory outside the Python environment.
From the copied `examples` directory, the command is:

```console
adviso-compare \
  --reference custom/reference.json \
  --query custom/query.csv \
  --configuration custom/configuration.yaml \
  --output custom-evidence
```

The configuration maps different source field names to shared canonical names.
It shows decimal quantisation and absolute tolerance, string trimming and case
folding, value mapping, and translation of slash-delimited text to a set. It
also declares `curator_note` but leaves it out of `fields.in_scope`, while the
query's undeclared `pipeline_version` is also excluded. The run is complete and
reports three comparison differences, with no assessment issues:

- `SAMPLE-001`: `reported_interpretation` maps to `not_detected`, while the
  reference's `expected_interpretation` maps to `detected`.
- `SAMPLE-002`: `reported_markers` contains an additional `MUT` member after
  translation, compared with `expected_markers`.
- `SAMPLE-002`: `reported_value` differs from `expected_value` by 0.2 after
  quantisation, exceeding the absolute tolerance of 0.01.

For `SAMPLE-001`, the numerical difference is within tolerance and the marker
sets match after translation. These successful comparisons produce no findings.

A stable ID and revision, review of changes, and testing with representative
data help your laboratory manage each configuration as a controlled document.
The evidence package retains the complete effective configuration as
`comparison-configuration.json`. Local quality arrangements remain the
authority for approval and retention.

### 5.3 Configuration checks and conventions

The configuration is one UTF-8 YAML mapping, using YAML 1.2 scalar resolution.
The file is checked before either dataset is read. YAML aliases, anchors,
merge keys, explicit tags, duplicate keys, and unsafe
object constructors are rejected, as are unknown properties. Quoting textual
values helps prevent YAML from interpreting them as numbers or booleans. In
particular, `schema_version` is a quoted string, and decimal parameters use
strings such as `"0.1"`. The examples use quotes to make intended string values
clear.

A JSON schema describes a document's permitted structure and values.
`comparison-configuration-v1.0.schema.json` defines the expected configuration
structure. After parsing the YAML, the tool checks it against this schema and
rejects configurations that do not conform.

The tool also checks relationships between settings: key and in-scope fields
have definitions; source field names are unique on each dataset side; mapping
sources are not repeated, conflicting, or unreachable; and operations and
comparators suit their field. It rejects custom configurations using the
reserved automatic-mode ID
`adviso-compare:automatic-strict-exact`.

### 5.4 Top-level properties

| Property | Required | Meaning |
| --- | --- | --- |
| `schema_version` | Yes | Configuration format version; the supported version is `"1.0"`. |
| `metadata` | Yes | Identity and description of the configuration. It does not alter the comparison. |
| `fields` | Yes | Key, scope, field correspondence, and comparison rules. |

`metadata` has these properties:

| Property | Required | Meaning |
| --- | --- | --- |
| `id` | Yes | Stable, non-empty identifier chosen by the configuration owner. |
| `revision` | Yes | Non-empty revision string managed by the configuration owner. |
| `title` | No | Human-readable title; may be empty. |
| `description` | No | Human-readable description; may be empty. |

`fields` has these properties:

| Property | Required | Meaning |
| --- | --- | --- |
| `record_key` | Yes | Non-empty ordered list of canonical field names forming one key. Order matters for a composite key. |
| `in_scope` | Yes | Non-empty list of canonical fields to assess. Key fields must be included. List order does not affect results. |
| `definitions` | Yes | Non-empty mapping from user-chosen canonical field names to field definitions. |

A definition not listed in `in_scope` is deliberately excluded and appears once
as `configured_field_excluded`. A source field not named by any definition on
its side (reference or query) appears as `undeclared_field_excluded`. Neither kind is compared or makes a run incomplete.

### 5.5 Field definitions

Every entry in `fields.definitions` is an object with a canonical field name as
key, and has the following properties:

| Property | Required | Meaning |
| --- | --- | --- |
| `source_fields` | Yes | `reference` and `query` give the source field name on each side. Both are required non-empty strings. |
| `required` | Yes | `reference` and `query` booleans say whether every applicable record on that side must contain the field. |
| `logical_type` | Usually | Scalar type or collection declaration. Omitted for `preserved_exact`; otherwise required. |
| `null_policy` | Yes | Defines whether null is allowed and how two nulls compare. |
| `source_normalisation` | No | Side-specific ordered text operations before mapping and type parsing. |
| `collection_representation` | Collections only, optional | Describes how either side writes a collection. |
| `value_mapping` | Scalar typed fields only, optional | Side-specific closed translation tables. |
| `typed_normalisation` | Scalar typed fields only, optional | Ordered operations applied to parsed values on both sides. |
| `comparator` | Yes | Comparison rule and, where needed, its parameters. |
| `review_priority` | No | `low`, `normal`, or `high`; defaults to `normal`. It labels findings and groups their priority counts without affecting which differences or assessment issues are detected, run status, or exit code. It does not indicate clinical significance. |

For each record-key field, the tool requires an entry in `definitions` and
`in_scope`, a scalar logical type, and `typed_exact` comparison. The field is
required and non-nullable on both sides. Key fields may use explicit source
normalisation or value mapping.

### 5.6 Logical types

For a scalar field, `logical_type` is `string`, `integer`, `decimal`, `boolean`,
`date`, or `datetime`. Parsing is strict. In particular, CSV and TSV cells
start as strings and are parsed only because a logical type was declared. Dates use `YYYY-MM-DD`. Datetimes use RFC 3339 with an explicit timezone.

The tool accepts these source values for each declared type:

| Logical type | Accepted parser-native input |
| --- | --- |
| `string` | String only. |
| `integer` | JSON integer, or text containing an optional sign and ASCII digits. Decimal points and exponents are not accepted. |
| `decimal` | JSON integer or decimal, or signed decimal text in plain or scientific notation. Text such as `.5` or `1.` is not accepted. |
| `boolean` | JSON boolean, or exactly the lowercase text `true` or `false`. |
| `date` | String containing a valid Gregorian `YYYY-MM-DD` date. |
| `datetime` | String containing a full RFC 3339 date and time with `Z` or a numeric offset. A local time without an offset is not accepted. |

Integer text accepts leading zeros, which have no numerical significance.
The `string` type preserves leading zeros in identifiers. Decimal text follows
`[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?`, using ASCII digits.
Parsing retains all supplied numerical precision, without binary floating-point
conversion or implicit rounding. Booleans are distinct from integers.

Datetime input accepts uppercase or lowercase `T` and `Z`, but no space in place
of `T`. Numeric offsets range from `+00:00` to `+23:59` and from `-00:01` to
`-23:59`; `-00:00` is rejected because it denotes an unknown offset. Leap seconds are rejected. Equivalent instants compare equally; supplied fractional precision is retained unless explicit truncation is configured. Canonical output uses UTC with uppercase `T` and `Z` and removes only redundant fractional zeros.

JSON objects cannot be converted to any of the logical types. They may be compared as complete, untyped JSON values using `preserved_exact`. More generally, the tool uses the declared logical type for parsing. Translations beyond those parsing rules can be described with `value_mapping`.

A collection uses an object:

```yaml
logical_type:
  collection_type: "set"
  element_type: "string"
  element_comparator:
    name: "typed_exact"
```

`collection_type` is `list`, `set`, or `multiset`. `element_type` is one of the
scalar types. Nested collections are not supported. Lists keep order, sets
ignore order and reject duplicates, and multisets ignore order but retain how
many times each value occurs. Sets and multisets require `typed_exact` elements.
Lists allow `typed_exact`, or `numeric_tolerance` for integer or decimal
elements.
List elements compare positionally, and list lengths must match. Duplicate set
elements are detected after element processing and typed parsing: integer
strings `"01"` and `"1"` are duplicates. Elements cannot be null. An invalid or
null element prevents construction of the canonical collection and makes the
aligned field opportunity not assessable.
A null element is reported as `invalid_field_value`.

### 5.7 Null policy and typed value descriptions

`null_policy.allowed` and `null_policy.nulls_equal` are required booleans. If
null is not allowed, `nulls_equal` must be false. JSON null is always recognised
as null. [Section 1.1](#11-records-fields-and-comparison-rules) describes how null differs from an absent field or empty text.

Empty strings, whitespace-only strings, null, absent fields, and configured
missing tokens remain distinct unless an explicit field policy transforms them.
Two permitted nulls match only when `nulls_equal` is true; a valid null/non-null
pair mismatches. A prohibited null produces a contract finding and blocks the
affected value comparison.

Two absent optional fields match. One absent optional field and one valid
present field mismatch, including when the present value is a permitted null.
Absence on a required side produces a contract finding and makes an aligned
value opportunity not assessable; two absent required fields do not match.

Within a field's `null_policy`, optional `missing_tokens` may contain a
non-empty `reference` list, a non-empty `query` list, or both. Each item
describes a parser-native value to treat as null. For example, this fragment
belongs inside a field definition:

```yaml
null_policy:
  allowed: true
  nulls_equal: true
  missing_tokens:
    reference:
      - category: "string"
        value: "NA"
    query:
      - category: "string"
        value: "."
```

Each missing token describes a non-null source value using a category and a value. The permitted categories are `string`, `integer`, `decimal`, and `boolean`. Strings, integers, and decimals use a textual `value`; booleans use `true` or `false`. An actual JSON `null` does not need to be listed because the tool recognises it automatically.

Value descriptions match by parser-native category and value after source
normalisation, rather than by numerical spelling. Decimal descriptions `"1.0"`
and `"1.00"` describe the same decimal value, distinct from integer `"1"`.
The same matching rule applies to mapping sources.

### 5.8 Source normalisation

`source_normalisation` may have `reference`, `query`, or both. Each present
side is a non-empty ordered list. Operations affect only parser-native strings
from that side. Non-strings pass through unchanged.

Within a string field's definition, for example:

```yaml
source_normalisation:
  query:
    - operation: "trim"
      parameters:
        side: "both"
    - operation: "case_fold"
```

This trims leading and trailing whitespace from query strings, then folds their
case: `" Detected "` becomes `"detected"`. Each list item names its `operation`;
only `trim` needs `parameters` in this example.

| Operation | Parameters | Effect |
| --- | --- | --- |
| `unicode_normalise` | `form`: `NFC`, `NFD`, `NFKC`, or `NFKD` | Applies the named Unicode normalisation form. |
| `trim` | `side`: `leading`, `trailing`, or `both` | Removes Unicode White_Space characters from the chosen end or ends. |
| `case_fold` | No `parameters` property | Applies locale-independent full Unicode case folding. |

Operations run in list order. Case folding does not silently perform Unicode
normalisation; both operations can be listed when both are needed.
Unicode operations use the Unicode-data version recorded in `runtime.unicode_version`.

### 5.9 Value mapping

`value_mapping` may have `reference`, `query`, or both. Each present side is a
non-empty list of `from` and `to` value descriptions:

```yaml
value_mapping:
  query:
    - from: {category: "string", value: "pos"}
      to: {category: "string", value: "detected"}
```

The mapping is closed: when a side has a mapping, every non-null value on that
side must match an entry. An unmapped value produces a `mapping_failure`; it is
not passed through. Many source values may map to the same destination. A
destination may be null, after which the null policy applies.

A mapping destination may also use `category: "null"` without a `value`. This converts the mapped source value to null, after which the field’s `null_policy` is applied. Mapping from null is not supported because an actual JSON null is recognised and handled before value mapping.

Mapping happens after source normalisation and missing-token recognition, and
before parsing to the logical type.

### 5.10 Collections written as text

`collection_representation` may have `reference`, `query`, or both. An omitted
side defaults to `json_array` with no element processing.

Each side requires `format`:

- `json_array` means a JSON array value, or a CSV/TSV string containing valid
  JSON-array text. It must not have a `delimiter`.
- `delimited_text` means a parser-native string split on the required,
  non-empty `delimiter` string.

Delimiters are literal strings, not regular expressions. Splitting proceeds
left to right through non-overlapping occurrences. Empty text represents an
empty collection; otherwise leading, trailing, or consecutive delimiters create
empty-string elements. Whitespace is retained unless explicitly normalised.
CSV/TSV quoting is resolved before splitting; collection text has no additional
quoting or escaping, so delimiter text cannot be included inside an element.

Optional `element_normalisation` is a non-empty ordered list of the text
operations in Section 5.8. Optional `element_mapping` is a non-empty closed
mapping whose `from` and `to` values must both be non-null. These act on each
element, not the collection as a whole. Collection fields cannot also use the
field-level `source_normalisation`, `value_mapping`, or `typed_normalisation`.
Element processing uses the scalar parsing rules. Whole-field missing-token and
null policies are not reapplied to individual elements. An unmapped element
produces a `mapping_failure` and blocks that collection's value comparison.

### 5.11 Typed normalisation

`typed_normalisation` is an optional, non-empty ordered list of operations
applied to parsed values from both the reference and query. Operations run
before the comparator is applied.

#### Decimal quantisation

`decimal_quantise` fixes the number of digits retained after the decimal point:

```yaml
typed_normalisation:
  - operation: "decimal_quantise"
    parameters:
      places: 2
      rounding: "half_even"
```

Here, `places: 2` means that values are quantised to two digits after the
decimal point. A value is not first converted to binary floating point; exact
decimal arithmetic is used.

The available rounding methods are:

| Method | Meaning |
| --- | --- |
| `half_even` | Round to the nearest value. If the discarded part is exactly halfway between two possible results, choose the result whose last retained digit is even. For example, at two decimal places, `1.235` becomes `1.24`, while `1.245` becomes `1.24`. |
| `half_up` | Round to the nearest value. If the discarded part is exactly halfway between two possible results, round away from zero. At two decimal places, `1.235` becomes `1.24` and `-1.235` becomes `-1.24`. |
| `down` | Discard digits beyond the requested number of decimal places, moving towards zero rather than rounding to the nearest value. At two decimal places, `1.239` becomes `1.23` and `-1.239` becomes `-1.23`. |

`places: 0` quantises to a whole-number value, although the field remains
logically a decimal. Quantisation is applied independently to both reference
and query values before they are compared.

#### Datetime truncation

`datetime_truncate` limits fractional-second precision after the datetime has
been converted to UTC:

```yaml
typed_normalisation:
  - operation: "datetime_truncate"
    parameters:
      precision: "millisecond"
```

The permitted values are:

- `second`: remove the entire fractional-second part;
- `millisecond`: retain at most three fractional digits; and
- `microsecond`: retain at most six fractional digits.

Discarded digits are removed without rounding. For example, millisecond
truncation changes `.1238` seconds to `.123`, not `.124`.

### 5.12 Comparators

Every comparator is an object with `name`. The following take no parameters:

| Name | Use |
| --- | --- |
| `preserved_exact` | Parser-native equality without a declared logical type. Array order matters; object member order does not. |
| `typed_exact` | Exact equality after typed parsing and configured processing. |
| `normalised_string` | Exact comparison of processed strings. |
| `numeric_exact` | Exact comparison of integer or decimal values. |
| `date_exact` | Exact canonical calendar date. |
| `datetime_exact` | Same instant after conversion to UTC. |
| `list_exact` | Ordered collection comparison. |
| `set_exact` | Order-independent unique collection comparison. |
| `multiset_exact` | Order-independent comparison retaining duplicate counts. |

String comparators require `logical_type: "string"`; numeric comparators require
`integer` or `decimal`; date and datetime comparators require their matching
temporal type; and each collection comparator requires the collection type with
the same name. `normalised_string` also requires at least one applicable
normalisation operation. `preserved_exact` is the only comparator with no
`logical_type`, and it cannot be combined with normalisation, mapping,
collection representation, typed normalisation, or configured missing tokens.

`numeric_tolerance` requires exactly one entry inside `parameters`. For
example, this field-level comparator allows an absolute difference of up to
`0.1`:

```yaml
comparator:
  name: "numeric_tolerance"
  parameters:
    absolute_tolerance: "0.1"
```

With `absolute_tolerance`, values match when their absolute difference is no
greater than the tolerance. With `relative_tolerance` in its place, values match
when:

```text
absolute difference <= relative tolerance × absolute reference value
```

The tolerance is a quoted, non-negative finite decimal. The boundary is
included. A relative tolerance around a zero reference allows only exact zero;
an absolute tolerance can allow a non-zero difference around zero.

The schema restricts the possible shape of comparators. The tool's further
checks ensure that a comparator suits the declared logical type and collection
kind.

### 5.13 Processing order

For a field with a scalar `logical_type`, processing follows this order:

1. distinguish absence from a present parser-native value;
2. apply side-specific source normalisation to strings;
3. recognise explicit null or configured missing tokens; for null, apply the
   null policy and skip mapping and type parsing;
4. for non-null values, apply the side-specific closed value mapping;
5. if mapping produces null, apply the null policy and skip type parsing;
6. otherwise parse the declared logical type;
7. apply typed normalisation where applicable; and
8. compare the canonical values under the configured null and comparison rules.

Fields using `preserved_exact` compare parser-native values directly, subject
to their presence and null rules, without normalisation, mapping, or type parsing.

For a collection, whole-field missing-token and null handling happens before
the representation is decoded. Element normalisation, mapping, and typed
parsing then happen for each element before collection comparison.

## 6. The evidence package

Each complete or incomplete run publishes one new directory under `OUTPUT`.
For example, two successive runs can produce:

```text
OUTPUT/
├── 20261111T143205Z-123e4567-e89b-42d3-a456-426614174000/
│   ├── comparison-results.json
│   ├── comparison-configuration.json
│   └── comparison-report.html
└── 20261111T145810Z-123e4567-e89b-42d3-a456-426614174001/
    ├── comparison-results.json
    ├── comparison-configuration.json
    └── comparison-report.html
```

Each run directory contains exactly these three regular evidence files.
Packages are validated and generated in private staging on the destination
filesystem before publication. The destination must support exclusive
directory rename;
if safe publication is unavailable, the run returns `output.write_failed`
and preserves existing content.

The output parent may already exist and contain any files or directories.
Existing contents and permissions are preserved. If the parent does not exist,
the tool creates it using normal filesystem permissions; its enclosing
directory must already exist.
The selected parent cannot be a symbolic link, regular file, or special
filesystem object. Symbolic links in ancestor directories are permitted.

Each complete or incomplete run publishes a new immediate child named
`YYYYMMDDTHHMMSSZ-<run-id>`. The timestamp and full UUID come directly from that
result's UTC `run.completed_at` and `run.id`. An occupied run-directory path is an error; the tool never replaces it or chooses a different name for that run.

On error, no new evidence package is published and existing parent contents
remain intact. A parent created during publication preparation may remain
empty. Input and configuration errors do not create it. Private temporary
staging is cleaned up after success and, where safe, after an error.

The completion summary's `Evidence package:` line identifies the published
sub-folder. With a relative `--output`, it shows the relative parent and sub-folder. With an absolute `--output`, it shows only the parent basename and sub-folder; for a filesystem-root parent it shows only the sub-folder name. Absolute paths are not printed. For automation, retain the selected parent path and use the reported sub-folder name to locate that run. The reported sub-folder identifies this run reliably; concurrent runs may finish in a different order from when they started.

Retention and disposal of accumulated evidence remain the laboratory's
responsibility; the tool does not remove earlier runs or maintain a `latest`
pointer.

`comparison-results.json` is the canonical result for software use and detailed
review. `comparison-configuration.json` retains the complete effective
configuration: the selected custom document or the generated automatic
document, including metadata and explicit declarations. Omitted optional
properties remain absent; internal defaults are not added. List order is
preserved. The saved file is JSON, rather than a copy of the source YAML bytes;
`--configuration` continues to accept only custom YAML.

Both JSON files use UTF-8 without a byte-order mark, two-space indentation, LF
line endings, and exactly one final newline. Non-ASCII text is emitted directly
unless JSON escaping is needed. Fixed properties follow their schema order;
dynamic names use Unicode code-point order. Identical effective configurations
produce identical saved bytes, without run identifiers or timestamps.

For identical input bytes and basenames, configuration selection, software
version, and runtime identity, results are identical except for `run.id` and
`run.completed_at`. Automatic configuration generation follows the same rule.

Changing record order or accepted LF/CRLF line endings preserves the comparison
outcome: run and phase statuses, summary counts, exclusions, and each finding's
classification, code, phase, side, record and field identity, priority, and value
evidence. Input byte provenance, source locations, location-dependent messages,
and report-local finding IDs may change. Software/runtime provenance is also
outside the comparison outcome.

To reproduce a run, use the recorded software version and Python runtime.
Python versions can ship different Unicode data, so configured Unicode
normalisation or case folding can produce different comparison outcomes for
some characters. The Unicode-data version is recorded in
`runtime.unicode_version`.

The three files form one evidence package and should be kept together. The
results link to the saved configuration by its exact-byte SHA-256 digest, as
explained in Section 7.2.2.
`comparison-report.html` is a self-contained, offline view made solely from the
validated results and saved configuration, with verified linkage. It adds fixed
explanatory text and external review space, but no comparison facts. Rendering
does not reread the original YAML. The report opens in an ordinary browser,
and works offline. Required styling is embedded; the report loads no external scripts, fonts, images, or other network resources. Its content remains available with scripting disabled.

## 7. JSON output reference

The evidence package contains the comparison configuration and the results as
separate JSON documents. Before publication, `adviso-compare` checks their
structures, the configuration digest, and agreement with the inputs and
comparison outcomes. Both schemas are included with the installed software.

### 7.1 `comparison-configuration.json`

For a custom comparison, this is the configuration supplied as YAML in
[Section 5](#5-custom-comparison-configurations), saved as JSON. The property
names, structure, and comparison rules are the same. For an automatic comparison,
it contains the
configuration generated according to [Section 4.3](#43-automatic-mode).

In automatic mode, `metadata.id` is
`adviso-compare:automatic-strict-exact` and `metadata.revision` is `"1.0"`.
This revision identifies the generated configuration, separately from its
schema version. Configuration identity and revision are read from this file,
rather than duplicated in the results. It contains no run ID or completion
timestamp; the results link to its exact saved bytes through
`comparison_configuration_digest`.

### 7.2 `comparison-results.json`

The complete example below continues the
[small custom comparison in Section 5.1](#51-a-small-custom-comparison).
Both records align; the measurements for `S1` match, while `2.00` and `2.10`
for `S2` produce one finding. The run completes without assessment issues.

The run ID, timestamp, software version, and runtime below are illustrative.
Input sizes and hashes correspond to the Section 5.1 files saved with LF line
endings and a final newline. The configuration digest corresponds to the JSON
saved by the tool. Formatting is compacted here for readability; no properties
or array entries have been omitted.

```json
{
  "schema_version": "1.0",
  "run": {
    "id": "123e4567-e89b-42d3-a456-426614174000",
    "status": "complete",
    "completed_at": "2026-11-24T12:00:00Z"
  },
  "phases": {"contract": "complete", "records": "complete", "values": "complete"},
  "software": {"name": "adviso-compare", "version": "0.1.0"},
  "runtime": {"python": "cpython-3.12.16", "platform": "linux-x86_64", "unicode_version": "15.0.0"},
  "inputs": {
    "reference": {
      "basename": "reference.csv",
      "format": "csv",
      "encoding": "utf-8",
      "size_bytes": 38,
      "digest": {
        "algorithm": "sha256",
        "value": "32951431ac179b397b844aa192f2a8f3ac15dc4c9d9dea220eeb93a30be90020"
      }
    },
    "query": {
      "basename": "query.csv",
      "format": "csv",
      "encoding": "utf-8",
      "size_bytes": 30,
      "digest": {
        "algorithm": "sha256",
        "value": "7a5f3f7ffed017defbab7f42453ff88c4c34446a476a09394f0557eae2367c0f"
      }
    }
  },
  "record_key_fields": {"reference": ["record_id"], "query": ["sample_id"], "canonical": ["sample"]},
  "comparison_configuration_digest": {
    "algorithm": "sha256",
    "value": "141da1749976240af55aec559a30f47787c5058f72bd61918354c09496960920"
  },
  "summary": {
    "records": {"reference": 2, "query": 2, "matched": 2, "missing": 0, "extra": 0},
    "values": {"matched": 1, "mismatched": 1, "not_assessable": 0},
    "findings": {
      "total": 1,
      "by_classification": {"comparison_difference": 1, "assessment_issue": 0},
      "by_code": {
        "missing_record": 0,
        "extra_record": 0,
        "missing_required_field": 0,
        "type_mismatch": 0,
        "invalid_field_value": 0,
        "null_policy_violation": 0,
        "mapping_failure": 0,
        "value_mismatch": 1
      },
      "by_review_priority": {"low": 0, "normal": 1, "high": 0, "unassigned": 0}
    }
  },
  "exclusions": [],
  "findings": [
    {
      "id": "F000001",
      "classification": "comparison_difference",
      "code": "value_mismatch",
      "phase": "values",
      "message": "Reference and query values for field 'measurement' differ.",
      "affected_side": "both",
      "record_identity": {"reference": ["S2"], "query": ["S2"], "canonical": ["S2"]},
      "source_locations": {
        "reference": {"record_number": 2, "line_number": 3, "field": "measurement"},
        "query": {"record_number": 2, "line_number": 3, "field": "result"}
      },
      "field": "measurement",
      "review_priority": "normal",
      "values": {
        "reference": {
          "state": "present",
          "source": {"category": "string", "value": "2.00"},
          "canonical": {"logical_type": "decimal", "value": "2"}
        },
        "query": {
          "state": "present",
          "source": {"category": "string", "value": "2.10"},
          "canonical": {"logical_type": "decimal", "value": "2.1"}
        }
      }
    }
  ]
}
```

The schema is
[`comparison-results-v1.0.schema.json`](https://github.com/advISO-project/advISO_compare_tool/blob/main/src/adviso_compare/schemas/comparison-results-v1.0.schema.json).
All root properties shown are required, including empty `exclusions` and
`findings` arrays when applicable. For automation, structured properties and finding codes
provide the comparison facts; English `message` text is intended for readers.

#### 7.2.1 Run and provenance

The opening properties identify the results format, run, software and runtime.

Each run receives its own random lowercase UUID version 4 and a UTC completion
timestamp in `YYYY-MM-DDTHH:MM:SSZ` form. Start time and elapsed duration are not recorded.

In the example, all three phases are complete. As explained in
[Section 3.2](#32-read-and-interpret-the-results), completion does not imply
agreement. Published results always have complete contract and records phases;
the values phase is incomplete if any value opportunity is not assessable.
`run.status` follows that values-phase status. Error runs produce no results
JSON.

`software.name` is always `adviso-compare`; `version` records the installed
version. An optional non-empty `build` can identify a build. Runtime names are
lowercase: Python uses `<implementation>-<major>.<minor>.<micro>` with a
prerelease suffix where applicable, and the platform uses
`<operating-system-family>-<architecture>`. Architecture names normalize
`amd64` to `x86_64` and `arm64` to `aarch64`. `unicode_version` identifies the
text-processing database as `<major>.<minor>.<patch>`.

`inputs.reference` and `inputs.query` then identify the files read. In this
example, `reference.csv` is 38 bytes and `query.csv` is 30 bytes. Each input
records its basename, format (`csv`, `tsv`, or `json`), encoding (`utf-8`),
byte size, and SHA-256 digest. Digests are lowercase 64-character strings and
cover the exact original bytes, so changing line endings changes the digest.

Provenance omits absolute paths, usernames, hostnames, distribution and kernel
versions, environment variables, working directories, raw command lines, and
dependency inventories. Input basenames can still be sensitive.

#### 7.2.2 Record keys and configuration digest

The example associates the two source identifier names with canonical `sample`.
These are non-empty arrays of unique field names. Their order defines the
component order for a composite key; a single-field key still uses an array.

The `comparison_configuration_digest` object links the results to the saved configuration.
`algorithm` is always `sha256`. The lowercase 64-character `value` hashes the
exact bytes of `comparison-configuration.json`, including its final newline,
rather than the original YAML. Even a whitespace edit changes the digest.
Downstream software can check the link by hashing the saved file directly;
parsing and reserializing it may change the bytes. This establishes content
linkage, not authenticity or laboratory approval.

The configuration's schema version, ID, and revision remain in that file's
`schema_version`, `metadata.id`, and `metadata.revision`. Its sibling filename
is fixed; the results do not select another path, URI, or filename.

#### 7.2.3 Summary counts

The summary records the outcome of the comparison as a whole. In the example,
both input records matched by key; none were missing or extra. The reference
count equals matched plus missing, and the query count equals matched plus
extra.

There are two in-scope non-key value opportunities, one measurement for each
sample. `S1` contributes one match and `S2` one mismatch. Key fields do not
contribute to these counts. Every opportunity is counted exactly once as
`matched`, `mismatched`, or `not_assessable`; all counts are non-negative.

`summary.findings` groups the individual findings. A single finding contributes once
to each grouping. `by_classification` always includes both classifications,
`by_code` all eight codes from [Section 3.2.3](#323-findings-classifications-and-codes),
and `by_review_priority` includes `low`, `normal`, `high`, and `unassigned`.
Zero entries remain present; each grouping sums to `total`.

#### 7.2.4 Findings

`findings` is an array: each entry describes one comparison difference or
assessment issue. The example has one entry. It identifies a `value_mismatch`
in the values phase, affecting both sides, with default review priority
`normal`. The classifications and codes have the meanings explained in
[Section 3.2.3](#323-findings-classifications-and-codes).

Every finding has `id`, `classification`, `code`, `phase`, `message`, and
`affected_side` (`reference`, `query`, or `both`, as allowed for its code).
The deterministic English message adds no facts beyond the structured
properties. IDs such as `F000001` are assigned after sorting; they identify
findings within this report, not across runs.

The record and source locations show where that difference occurred.
`record_identity` contains ordered reference, query, and canonical key-value
arrays. Here, all identify `S2`. `field` is the canonical field name, while the
locations identify the actual source fields: `measurement` and `result`.
CSV/TSV `record_number` and starting physical `line_number` are one-based;
the header explains why record 2 starts on line 3. Tabular locations may include
a `field`; JSON locations instead use an RFC 6901 `json_pointer`.

The `values` object explains what was compared. Each side has a presence `state`,
a `source` representation, and, for this typed field, a translated `canonical`
representation. CSV source values are strings. The canonical decimal strings
`"2"` and `"2.1"` represent the unequal numbers 2 and 2.1; numeric values are
encoded as strings to preserve precision. Comparator parameters and processing rules
remain in the saved configuration.

`present` means the source field exists, not that translation succeeded or the
value is non-null. `absent` means the field or its record is missing and carries
no `source` or `canonical`. A present side may also contain only its state if
its value is not needed to explain the finding.

Other findings retain only the context and evidence they need:

| Finding form | Record/field context and value evidence |
| --- | --- |
| `missing_record`, `extra_record` | Record identity and locations; the absent record's side is null. No `field`, `review_priority`, or `values`. |
| Record-specific `missing_required_field` | Identity, locations, field, and priority; `values` contains only both presence states. An absent field's location points to its containing record. |
| Zero-record dataset-level `missing_required_field` | Only field and priority beyond the common properties; no individual record, location, or `values`. |
| `type_mismatch`, `invalid_field_value`, `mapping_failure` | Identity, locations, field, and priority; both presence states and the affected side's source value, without a canonical value. |
| `null_policy_violation` | The same context and presence states, with the affected source value and, for a typed field, canonical null. |
| `value_mismatch` | Identity, locations, field, and priority; source values for present sides and canonical values for typed present sides. Untyped `preserved_exact` fields have no canonical value. |

Independent contract violations on the two sides produce separate findings;
a value mismatch produces one finding with side `both`. Category incompatibility,
invalid content within an accepted category, and valid unequal values produce
`type_mismatch`, `invalid_field_value`, and `value_mismatch`, respectively,
rather than overlapping findings for the same affected value. Untyped category
differences are value mismatches. There is no additional `not_assessable`
finding: the causal assessment issue explains the blocked opportunity.

#### 7.2.5 Exclusions

The small example has `"exclusions": []`: every source field is declared and
in scope. The [richer custom example](#52-runnable-custom-example-with-transformations)
shows both exclusion forms. Its array includes entries such as:

```json
{
  "exclusions": [
    {"code": "configured_field_excluded", "canonical_field": "curator_note"},
    {
      "code": "undeclared_field_excluded",
      "side": "query",
      "source_field": "pipeline_version",
      "record_count": 2
    }
  ]
}
```

A configured exclusion names its `canonical_field`. An undeclared exclusion
names its `side` and `source_field`; `record_count` is the non-negative number
of records containing it, including zero for a field exposed only by a header
in an empty dataset. Exclusions are not findings and do not affect run status.

Configured exclusions come first, sorted by canonical field name. Undeclared
exclusions follow, sorted by side (`reference`, then `query`) and source field
name. Field-name sorting uses Unicode code-point order.

#### 7.2.6 Encoding and ordering details

These conventions apply when reading values beyond the decimal example above:

| Representation | Encoding |
| --- | --- |
| Source scalar | `category` is `string`, `integer`, `decimal`, `boolean`, or `null`. Strings and booleans use JSON strings and booleans. Numbers use JSON strings retaining their original lexical text, including decimal places and exponent notation. Native null has no `value` property. |
| Source collection | `category` is `array` or `object`. Its `value` is an array of source-value objects, or an object mapping member names to source-value objects. Each nested value carries its own category. |
| Canonical scalar | `logical_type` declares the type. Strings contain processed text; booleans use JSON booleans. Integers, decimals, dates, and datetimes use JSON strings in the forms below. |
| Canonical collection | `logical_type` is `list`, `set`, or `multiset`, with `element_type`. `value` is an array of canonical elements without per-element type wrappers. Lists retain order; sets and multisets sort by Unicode code-point order of canonical element strings, retaining multiset duplicates. |
| Canonical null | The declared logical type with `"value": null`; a null collection still has `element_type`. A present null is distinct from an absent field. |

Canonical integers use base-10 text without a leading plus or redundant zeros.
Canonical decimals use `"0"` for every zero, including negative zero; non-zero
values use one non-zero digit before the decimal point, no trailing fractional
zeros, lowercase `e`, and no redundant exponent sign or zeros. Exponent zero
is omitted: `12.30`, `1000`, and `0.0010` become `"1.23e1"`, `"1e3"`, and
`"1e-3"`. Dates use `YYYY-MM-DD`; datetimes use UTC ending in `Z`, with redundant
fractional zeros removed.

Findings have a total order, independent of locale:

1. Classification: `comparison_difference`, then `assessment_issue`.
2. Phase: `contract`, `records`, then `values`.
3. Dataset-level findings before record-specific findings.
4. Canonical record identity, component by component in Unicode code-point order.
5. Canonical field name, omitted as a sorting component for record findings.
6. Code: `missing_record`, `extra_record`, `missing_required_field`,
   `type_mismatch`, `invalid_field_value`, `null_policy_violation`,
   `mapping_failure`, then `value_mismatch`.
7. Side: `reference`, `query`, then `both`.
8. Source locations: reference before query, with null before present. Tabular
   locations compare record number, starting line, then field name; JSON
   locations compare JSON Pointer in Unicode code-point order.
9. Canonical JSON serialization of remaining structured properties, excluding
   `id` and `message`.

Candidates identical under that key are combined into one finding. Sorted
findings receive IDs `F000001`, `F000002`, and so on.

## 8. Errors and corrective action

The first error line has the form:

```text
ERROR [category.code]: message
```

| Code or category | What to check |
| --- | --- |
| `invocation.invalid_arguments` | `adviso-compare --help` lists the options. The reference, query, and output options are required. |
| `configuration.unreadable` | The configuration file's location and read permissions. |
| `configuration.invalid_syntax` | UTF-8 encoding and permitted YAML syntax: aliases, anchors, tags, merges, and duplicate keys are rejected. |
| `configuration.schema_violation` | The reported YAML path identifies the missing, unknown, or invalid property. |
| `configuration.semantic_violation` | Named fields, key rules, logical types, operations, mappings, and comparator compatibility. |
| `configuration.unsupported_version` | The configuration's schema version must be supported by the installed tool. |
| `input.unreadable` | The input file's location and read permissions. |
| `input.unsupported_format` | The filename needs a recognised `.csv`, `.tsv`, or `.json` extension. |
| `input.invalid_encoding` | The input's UTF-8 encoding; any conversion should avoid silent character replacement. |
| `input.invalid_syntax` | CSV/TSV quoting and record endings, or JSON syntax. |
| `input.invalid_structure` | Headers, row widths, JSON root shape, record objects, and field names. |
| `input.invalid_record_key` | The chosen key needs to be present, non-null, valid, and unique. A custom configuration can resolve ambiguous automatic selection. |
| `resource.exhausted` | Input size and available resources. A smaller input or additional resources may allow the run to complete; no partial result is valid. |
| `output.invalid_destination` | The output parent's enclosing directory must exist, and any existing parent must be a regular directory. An occupied run-directory path is also rejected. |
| `output.write_failed` | Parent-directory permissions, available storage, and filesystem support for exclusive directory rename. |
| `internal.unexpected` | A retry may resolve a transient failure. If it persists, a useful issue report includes the software version and safe reproduction details using synthetic data. |

An assessment issue inside an otherwise readable and alignable dataset is a
finding, not an execution error. Those issues are available for review in the
evidence package.

Errors are written to standard error with a non-empty, single-line message;
additional non-sensitive context may follow. Record-key diagnostics identify
the affected dataset, key field names, and available source locations, while
withholding key values. Automatic discovery errors state that both inputs were
considered and identify candidate field names where available. Error diagnostics
do not include findings, comparison counts, phase statuses, or tracebacks.
Unexpected generated-evidence validation failures use `internal.unexpected`
and publish no package.

## 9. Security, governance, and limitations

The tool operates locally and does not transmit inputs, configurations, or
results. The evidence package can contain sensitive laboratory or patient
information, including record identifiers, values needed to explain findings,
and input basenames. You should store it with permissions, retention, backup,
and disposal controls suitable for the source data. The laboratory remains
responsible for appropriate pseudonymisation.

New output parents, run directories, and evidence files use normal filesystem
creation permissions, subject to the process's `umask` on POSIX systems and
applicable inherited access controls. Existing parent permissions are retained.
On POSIX systems, the temporary outer staging directory remains owner-only
while the package is being assembled.

For confidential output, you should select a parent directory with access
restricted to the appropriate users or laboratory group. The tool does not
enforce owner-only access to published evidence. On other systems, you should
use the corresponding filesystem access controls under laboratory policy.

Routine terminal output and error diagnostics do not reproduce record
identifiers or source values. The tool does not provide de-identification,
identifier hashing, access control, encryption, or sensitivity policies.

`adviso-compare` compares one complete reference dataset with one complete query
dataset. It does not download data, run a bioinformatics pipeline, subset a
validation dataset, apply acceptance thresholds, decide fitness for purpose,
or produce a complete ISO 15189 validation dossier. It supports the evidence
review that forms part of a wider, governed validation process.

There is no fixed input-size or record-count limit. Available memory,
storage, and operating-system resources still impose practical limits. Resource
exhaustion produces an error and no partial evidence package.

## 10. Reproducing the examples

The examples use synthetic, non-sensitive data. Section 5.1 provides complete
file contents you can save yourself. The other example files are installed in
the `examples` directory next to this guide. Their expected outcomes are:

| Example | Status | Comparison differences | Assessment issues |
| --- | --- | ---: | ---: |
| automatic (Section 3.1) | `complete` | 1 | 0 |
| small custom (Section 5.1) | `complete` | 1 | 0 |
| custom with transformations (Section 5.2) | `complete` | 3 | 0 |

You can reproduce the examples by running the commands in Sections 3.1, 5.1,
and 5.2, then opening the report in each run directory and checking the outcomes
against the table. The same output parents can be reused: each invocation adds
a new run directory. Run IDs and completion times change on every run.
Software and runtime provenance can change between environments. Input digests
change if the input files are edited. The outcomes in the table provide a check
that each example ran as described.
