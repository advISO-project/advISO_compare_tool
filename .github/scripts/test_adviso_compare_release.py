# Copyright (C) 2026 Cardiff University, the Wellcome Sanger Institute and
# the University of the Western Cape
# SPDX-License-Identifier: GPL-3.0-or-later

"""Checks for candidate assembly and draft-only GitHub release preparation."""

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import zipfile

import adviso_compare_release as release
import pytest
import yaml


@pytest.fixture
def candidate(tmp_path):
    """Build small synthetic CI artefacts with the real workflow's matrix."""
    workflow = yaml.safe_load(release.WORKFLOW.read_text())
    context = release.ReleaseContext(
        tag="v1.0.0",
        commit="a" * 40,
        repository="example/toolkit",
        run_id="123",
        attempt="1",
    )
    inputs = tmp_path / "inputs"
    ci_results = {"test": "success", "quality": "success", "ci": "success"}
    for entry in workflow["jobs"]["test"]["strategy"]["matrix"]["include"]:
        directory = inputs / f"adviso-compare-{entry['os']}-python-{entry['python']}"
        records = directory / "tmp" / "distributions"
        records.mkdir(parents=True)
        for name in (
            "commit.txt",
            "python.txt",
            "platform.txt",
            "test-dependencies.txt",
        ):
            (directory / name).write_text(
                context.commit if name == "commit.txt" else "synthetic\n"
            )
        (directory / "tests.xml").write_text(
            '<testsuite tests="1" failures="0" errors="0" skipped="0" />'
        )
        for name in ("wheel-dependencies.txt", "sdist-dependencies.txt"):
            (records / name).write_text("synthetic==1.0\n")
        metadata = b"Name: adviso-compare\nVersion: 1.0.0\n"
        with zipfile.ZipFile(
            records / "adviso_compare-1.0.0-py3-none-any.whl", "w"
        ) as wheel:
            wheel.writestr("adviso_compare-1.0.0.dist-info/METADATA", metadata)
            for family in ("configuration", "results"):
                wheel.writestr(
                    f"adviso_compare/schemas/comparison-{family}-v1.0.schema.json",
                    json.dumps({"properties": {"schema_version": {"const": "1.0"}}}),
                )
        with tarfile.open(records / "adviso_compare-1.0.0.tar.gz", "w:gz") as source:
            member = tarfile.TarInfo("adviso_compare-1.0.0/PKG-INFO")
            member.size = len(metadata)
            source.addfile(member, io.BytesIO(metadata))
    quality = inputs / "adviso-compare-quality"
    quality.mkdir()
    for name in release.QUALITY_RECORDS:
        (quality / name).write_text(
            context.commit if name == "commit.txt" else "passed\n"
        )
    (quality / "release-tests.xml").write_text(
        '<testsuite tests="1" failures="0" errors="0" />'
    )
    return inputs, tmp_path / "output", workflow, context, ci_results


def test_candidate_keeps_tested_bytes_and_collects_complete_evidence(candidate):
    inputs, output, workflow, context, ci_results = candidate
    files = release.build_candidate(inputs, output, workflow, context, ci_results)
    assert len(files) == 5
    selected = inputs / release.DISTRIBUTION_ARTIFACT / "tmp" / "distributions"
    for name in (
        "adviso_compare-1.0.0-py3-none-any.whl",
        "adviso_compare-1.0.0.tar.gz",
    ):
        assert (output / name).read_bytes() == (selected / name).read_bytes()
    for line in (output / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert digest == hashlib.sha256((output / name).read_bytes()).hexdigest()
    matrix = workflow["jobs"]["test"]["strategy"]["matrix"]["include"]
    with zipfile.ZipFile(output / "verification-evidence.zip") as evidence:
        assert len(
            [name for name in evidence.namelist() if name.endswith("/tests.xml")]
        ) == len(matrix)
        assert "adviso-compare-quality/ruff-version.txt" in evidence.namelist()
        assert json.loads(evidence.read("ci-results.json")) == ci_results
    record = (output / "release-verification.md").read_text()
    assert context.commit in record and "/actions/runs/123" in record
    assert "Independent human review is not asserted" in record


@pytest.mark.parametrize(
    "problem",
    [
        "missing-record",
        "wrong-commit",
        "failed-report",
        "wrong-version",
        "wrong-tag",
    ],
)
def test_inconsistent_candidate_evidence_is_rejected(candidate, problem):
    inputs, output, workflow, context, ci_results = candidate
    selected = inputs / release.DISTRIBUTION_ARTIFACT
    if problem == "missing-record":
        (selected / "python.txt").unlink()
    elif problem == "wrong-commit":
        (selected / "commit.txt").write_text("b" * 40)
    elif problem == "failed-report":
        (selected / "tests.xml").write_text(
            '<testsuite tests="1" failures="1" errors="0" />'
        )
    elif problem == "wrong-version":
        wheel = selected / "tmp/distributions/adviso_compare-1.0.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr(
                "adviso_compare-2.0.0.dist-info/METADATA",
                "Name: adviso-compare\nVersion: 2.0.0\n",
            )
    else:
        context = release.ReleaseContext(
            "release-1.0.0", context.commit, context.repository, "123", "1"
        )
    with pytest.raises(ValueError):
        release.build_candidate(inputs, output, workflow, context, ci_results)
    assert not output.exists()


@pytest.mark.parametrize("already_published", [False, True])
def test_existing_releases_are_never_published_or_rewritten(
    candidate, monkeypatch, already_published
):
    _, output, _, context, _ = candidate
    output.mkdir()
    files = [output / "release-verification.md"]
    calls = []
    existing = {
        "tag_name": context.tag,
        "draft": not already_published,
        "body": "Human release notes",
    }
    monkeypatch.setattr(release, "gh_json", lambda *args: [[existing]])
    monkeypatch.setattr(release, "gh", lambda *args: calls.append(args))
    if already_published:
        with pytest.raises(ValueError, match="published"):
            release.attach_to_draft(files, output, context)
        assert calls == []
    else:
        release.attach_to_draft(files, output, context)
        assert len(calls) == 1 and calls[0][:2] == ("release", "upload")
        assert existing["body"] == "Human release notes"


def test_new_release_is_created_as_draft_with_existing_tag(candidate, monkeypatch):
    _, output, _, context, _ = candidate
    output.mkdir()
    calls = []
    monkeypatch.setattr(release, "gh_json", lambda *args: [[]])
    monkeypatch.setattr(release, "gh", lambda *args: calls.append(args))
    release.attach_to_draft([output / "release-verification.md"], output, context)
    assert calls[0][:3] == ("release", "create", context.tag)
    assert "--draft" in calls[0] and "--verify-tag" in calls[0]
    assert "--notes-file" in calls[0]
    assert calls[1][:2] == ("release", "upload")


@pytest.mark.parametrize("problem", ["different-checkout", "unmerged-source"])
def test_unmerged_or_different_source_cannot_prepare_a_release(
    candidate, monkeypatch, problem
):
    _, _, _, context, _ = candidate
    monkeypatch.setattr(
        release.subprocess,
        "check_output",
        lambda *args, **kwargs: (
            "b" * 40 if problem == "different-checkout" else context.commit
        ),
    )

    def reject_unmerged(command, **kwargs):
        assert command[:3] == ["git", "merge-base", "--is-ancestor"]
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(release.subprocess, "run", reject_unmerged)
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        release.verify_source(context)


@pytest.mark.parametrize(
    ("job", "result"),
    [("test", "failure"), ("quality", "cancelled"), ("ci", "skipped"), ("test", None)],
)
def test_candidate_requires_successful_workflow_dependencies(candidate, job, result):
    inputs, output, workflow, context, ci_results = candidate
    if result is None:
        ci_results.pop(job)
    else:
        ci_results[job] = result
    with pytest.raises(ValueError, match="CI dependencies"):
        release.build_candidate(inputs, output, workflow, context, ci_results)
    assert not output.exists()


def test_tag_run_downloads_its_own_evidence_and_prepares_only_a_draft(
    candidate, monkeypatch
):
    inputs, output, _, context, ci_results = candidate
    calls = []
    for key, value in {
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REF_NAME": context.tag,
        "GITHUB_SHA": context.commit,
        "GITHUB_REPOSITORY": context.repository,
        "GITHUB_RUN_ID": context.run_id,
        "GITHUB_RUN_ATTEMPT": "2",
        "CI_RESULTS": json.dumps(
            {
                job: {"result": result, "outputs": {}}
                for job, result in ci_results.items()
            }
        ),
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(
        sys, "argv", ["release", "--inputs", str(inputs), "--output", str(output)]
    )
    monkeypatch.setattr(release, "verify_source", lambda selected: None)
    monkeypatch.setattr(release, "gh", lambda *args: calls.append(args))

    def api(*arguments):
        calls.append(arguments)
        endpoint = arguments[-1]
        assert endpoint == f"repos/{context.repository}/releases"
        return [[]]

    monkeypatch.setattr(release, "gh_json", api)
    release.main()
    downloads = [call for call in calls if call[:2] == ("run", "download")]
    assert len(downloads) == 2
    assert all(call[2] == context.run_id for call in downloads)
    assert "adviso-compare-*-python-*" in downloads[0]
    assert "adviso-compare-quality" in downloads[1]
    create = next(call for call in calls if call[:2] == ("release", "create"))
    assert "--draft" in create
    upload = next(call for call in calls if call[:2] == ("release", "upload"))
    assert len([part for part in upload if part.startswith(str(output))]) == 5
