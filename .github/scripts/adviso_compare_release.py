# Copyright (C) 2026 Cardiff University, the Wellcome Sanger Institute and
# the University of the Western Cape
# SPDX-License-Identifier: GPL-3.0-or-later

"""Assemble tested adviso-compare files and attach them to a draft release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from email.parser import BytesParser
from pathlib import Path
from typing import Any

import yaml
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/adviso-compare-ci.yml"
TAG_PREFIX = "v"
DISTRIBUTION_ARTIFACT = "adviso-compare-ubuntu-24.04-python-3.11"
QUALITY_RECORDS = (
    "commit.txt",
    "python.txt",
    "platform.txt",
    "test-dependencies.txt",
    "ruff-version.txt",
    "format.txt",
    "lint.txt",
    "release-tests.xml",
)
TEST_RECORDS = (
    "commit.txt",
    "python.txt",
    "platform.txt",
    "test-dependencies.txt",
    "tests.xml",
    "wheel-dependencies.txt",
    "sdist-dependencies.txt",
)


@dataclass(frozen=True)
class ReleaseContext:
    """Identify the immutable source and the CI run supplying the candidate."""

    tag: str
    commit: str
    repository: str
    run_id: str
    attempt: str

    @property
    def version(self) -> Version:
        """Require a v-prefixed release tag without development or local versions."""
        if not self.tag.startswith(TAG_PREFIX):
            raise ValueError("Release tag must start with v")
        version = Version(self.tag.removeprefix(TAG_PREFIX))
        if version.dev is not None or version.local is not None:
            raise ValueError("Release tag must not have a development or local version")
        return version

    @property
    def run_url(self) -> str:
        """Link to the run while recording its attempt separately."""
        return f"https://github.com/{self.repository}/actions/runs/{self.run_id}"


def gh(*arguments: str) -> str:
    """Run the authenticated CLI supplied by the GitHub-hosted runner."""
    return subprocess.check_output(["gh", *arguments], text=True)


def gh_json(*arguments: str) -> Any:
    """Decode a GitHub CLI JSON response, including paginated API responses."""
    return json.loads(gh(*arguments))


def verify_source(context: ReleaseContext) -> None:
    """Require the checked-out tag to identify source already merged to main."""
    _ = context.version
    for reference in ("HEAD", f"refs/tags/{context.tag}^{{commit}}"):
        actual = subprocess.check_output(
            ["git", "rev-parse", reference], cwd=ROOT, text=True
        ).strip()
        if actual != context.commit:
            raise ValueError("Release checkout or tag does not match the CI commit")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", context.commit, "origin/main"],
        cwd=ROOT,
        check=True,
    )


def _one(directory: Path, pattern: str) -> Path:
    matches = list(directory.rglob(pattern))
    if len(matches) != 1 or not matches[0].is_file() or matches[0].is_symlink():
        raise ValueError(f"Expected one regular {pattern} in {directory.name}")
    return matches[0]


def _check_report(path: Path) -> None:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    if not suites or sum(int(s.get("tests", "0")) for s in suites) == 0:
        raise ValueError("Test report contains no test results")
    if any(int(s.get("failures", "0")) or int(s.get("errors", "0")) for s in suites):
        raise ValueError("Test report contains failures or errors")


def _check_metadata(data: bytes, version: Version) -> None:
    metadata = BytesParser().parsebytes(data)
    if metadata["Name"] != "adviso-compare" or Version(metadata["Version"]) != version:
        raise ValueError("Distribution name or version does not match the release tag")


def build_candidate(
    inputs: Path,
    output: Path,
    workflow: dict[str, Any],
    context: ReleaseContext,
    ci_results: dict[str, str],
) -> list[Path]:
    """Validate all CI evidence before assembling the five publication assets."""
    version = context.version
    matrix = workflow["jobs"]["test"]["strategy"]["matrix"]["include"]
    names = [f"adviso-compare-{e['os']}-python-{e['python']}" for e in matrix]
    if any(ci_results.get(job) != "success" for job in ("test", "quality", "ci")):
        raise ValueError("Required CI dependencies have not all succeeded")

    records: dict[str, bytes] = {}
    selected = []
    schemas = {}
    for name in [*names, "adviso-compare-quality"]:
        directory = inputs / name
        required = QUALITY_RECORDS if name == "adviso-compare-quality" else TEST_RECORDS
        for filename in required:
            data = _one(directory, filename).read_bytes()
            if filename == "commit.txt" and data.decode().strip() != context.commit:
                raise ValueError(f"Artefact commit differs from the release: {name}")
            records[f"{name}/{filename}"] = data
        _check_report(
            _one(
                directory,
                "release-tests.xml"
                if name == "adviso-compare-quality"
                else "tests.xml",
            )
        )
        if name == "adviso-compare-quality":
            continue
        wheel = _one(directory, "*.whl")
        source = _one(directory, "*.tar.gz")
        if (
            wheel.name != f"adviso_compare-{version}-py3-none-any.whl"
            or source.name != f"adviso_compare-{version}.tar.gz"
        ):
            raise ValueError("Distribution filenames do not match the release version")
        with zipfile.ZipFile(wheel) as archive:
            metadata = [
                n for n in archive.namelist() if n.endswith(".dist-info/METADATA")
            ]
            if len(metadata) != 1:
                raise ValueError("Wheel metadata is missing or ambiguous")
            _check_metadata(archive.read(metadata[0]), version)
            if name == DISTRIBUTION_ARTIFACT:
                for family in ("configuration", "results"):
                    paths = [
                        n
                        for n in archive.namelist()
                        if n.startswith(f"adviso_compare/schemas/comparison-{family}-")
                        and n.endswith(".schema.json")
                    ]
                    schemas[family] = [
                        json.loads(archive.read(n))["properties"]["schema_version"][
                            "const"
                        ]
                        for n in paths
                    ]
                    if not schemas[family]:
                        raise ValueError("Release wheel is missing a required schema")
        with tarfile.open(source, "r:gz") as archive:
            members = [
                m
                for m in archive.getmembers()
                if m.name.count("/") == 1
                and m.name.endswith("/PKG-INFO")
                and m.isfile()
            ]
            if len(members) != 1:
                raise ValueError("Source archive metadata is missing or ambiguous")
            with archive.extractfile(members[0]) as metadata:
                _check_metadata(metadata.read(), version)
        if name == DISTRIBUTION_ARTIFACT:
            selected = [wheel, source]
    if not selected:
        raise ValueError("Designated distribution artefact is not in the matrix")

    output.mkdir(parents=True)
    files = [Path(shutil.copyfile(path, output / path.name)) for path in selected]
    evidence = output / "verification-evidence.zip"
    records["ci-results.json"] = (json.dumps(ci_results, indent=2) + "\n").encode()
    with zipfile.ZipFile(evidence, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(records.items()):
            member = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(member, data)
    files.append(evidence)
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files
    }
    runtime_lines = "\n".join(f"- {e['os']}: CPython {e['python']}" for e in matrix)
    record = output / "release-verification.md"
    record.write_text(
        f"# adviso-compare {version}: automated release verification\n\n"
        f"- Tag: `{context.tag}`\n- Commit: `{context.commit}`\n"
        f"- CI run: {context.run_url}\n- Run attempt: {context.attempt}\n"
        f"- Distribution source: `{DISTRIBUTION_ARTIFACT}`\n\n"
        f"## Verified environments\n\n{runtime_lines}\n\n"
        "All listed runtime jobs, Ruff/release-automation checks, and the aggregate "
        "CI gate succeeded for this commit. Runtime suites cover schemas, examples, "
        "determinism, and clean wheel/source installations. The published archives "
        "are copied from those tested bytes, without rebuilding.\n\n"
        f"Packaged schema versions: {json.dumps(schemas, sort_keys=True)}.\n\n"
        "Exact environments, dependencies, JUnit results, Ruff output and workflow "
        "dependency results are in `verification-evidence.zip`. Dependency records "
        "describe "
        "what was tested, not future dependency resolution.\n\n"
        "## SHA-256\n\n"
        + "\n".join(
            f"- `{name}`: `{digest}`" for name, digest in sorted(hashes.items())
        )
        + "\n\nIndependent human review is not asserted. Release-specific limitations "
        "and the publication decision belong in the manually reviewed release notes.\n",
        encoding="utf-8",
    )
    files.append(record)
    checksums = output / "SHA256SUMS.txt"
    checksums.write_text(
        "".join(
            f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n"
            for p in sorted(files)
        ),
        encoding="utf-8",
    )
    files.append(checksums)
    (output / "draft-notes.md").write_text(
        f"# adviso-compare {version}\n\n"
        "## Changes\n\nDescribe the features and fixes in this release before publishing.\n\n"
        f"## Supported environments\n\n{runtime_lines}\n\n"
        "Linux is fully supported. Windows and macOS compatibility is tested on "
        "the Python versions listed above.\n\n"
        f"## Schema compatibility\n\n{json.dumps(schemas, sort_keys=True)}\n\n"
        "## Known limitations\n\nReview the user guide and describe release-specific "
        "limitations or upgrade instructions before publishing.\n\n"
        "## Automated verification\n\nThe attached distributions passed the required "
        "checks. See `release-verification.md` and `verification-evidence.zip`. "
        "Publication and completion of these release notes require a human decision.\n",
        encoding="utf-8",
    )
    return files


def attach_to_draft(files: list[Path], output: Path, context: ReleaseContext) -> None:
    """Create only drafts; reruns preserve edited notes and refuse published tags."""
    pages = gh_json(
        "api", "--paginate", "--slurp", f"repos/{context.repository}/releases"
    )
    existing = [
        item for page in pages for item in page if item["tag_name"] == context.tag
    ]
    if existing and not existing[0]["draft"]:
        raise ValueError("Release is already published; refusing to modify it")
    if not existing:
        flags = ["--prerelease"] if context.version.is_prerelease else []
        gh(
            "release",
            "create",
            context.tag,
            "--repo",
            context.repository,
            "--draft",
            "--verify-tag",
            "--target",
            context.commit,
            "--title",
            f"adviso-compare {context.version}",
            "--notes-file",
            str(output / "draft-notes.md"),
            *flags,
        )
    gh(
        "release",
        "upload",
        context.tag,
        *map(str, files),
        "--repo",
        context.repository,
        "--clobber",
    )


def main() -> None:
    """Prepare a draft from the successful tag workflow's own artefacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("GITHUB_EVENT_NAME") != "push":
        raise ValueError("Draft release preparation requires a tag-push event")
    context = ReleaseContext(
        *(
            os.environ[key]
            for key in (
                "GITHUB_REF_NAME",
                "GITHUB_SHA",
                "GITHUB_REPOSITORY",
                "GITHUB_RUN_ID",
                "GITHUB_RUN_ATTEMPT",
            )
        )
    )
    verify_source(context)
    workflow = yaml.safe_load(WORKFLOW.read_text())
    gh(
        "run",
        "download",
        context.run_id,
        "--repo",
        context.repository,
        "--pattern",
        "adviso-compare-*-python-*",
        "--dir",
        str(args.inputs),
    )
    gh(
        "run",
        "download",
        context.run_id,
        "--repo",
        context.repository,
        "--name",
        "adviso-compare-quality",
        "--dir",
        str(args.inputs / "adviso-compare-quality"),
    )
    ci_results = {
        job: details["result"]
        for job, details in json.loads(os.environ["CI_RESULTS"]).items()
    }
    files = build_candidate(
        args.inputs,
        args.output,
        workflow,
        context,
        ci_results,
    )
    attach_to_draft(files, args.output, context)


if __name__ == "__main__":
    main()
