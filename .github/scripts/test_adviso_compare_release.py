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
        tag="adviso-compare-v1.0.0",
        commit="a" * 40,
        repository="example/toolkit",
        run_id="123",
        attempt="1",
    )
    inputs = tmp_path / "inputs"
    jobs = []
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
        jobs.append(
            {
                "name": f"adviso-compare / {entry['os']} / Python {entry['python']}",
                "status": "completed",
                "conclusion": "success",
                "head_sha": context.commit,
                "run_id": 123,
                "run_attempt": 1,
            }
        )
    quality = inputs / "adviso-compare-quality"
    quality.mkdir()
    for name in release.QUALITY_RECORDS:
        (quality / name).write_text(
            context.commit if name == "commit.txt" else "passed\n"
        )
    (quality / "release-tests.xml").write_text(
        '<testsuite tests="1" failures="0" errors="0" />'
    )
    for job in ("quality", "ci"):
        jobs.append(
            {
                "name": workflow["jobs"][job]["name"],
                "status": "completed",
                "conclusion": "success",
                "head_sha": context.commit,
                "run_id": 123,
                "run_attempt": 1,
            }
        )
    return inputs, tmp_path / "output", workflow, context, jobs


def test_candidate_keeps_tested_bytes_and_collects_complete_evidence(candidate):
    inputs, output, workflow, context, jobs = candidate
    files = release.build_candidate(inputs, output, workflow, context, jobs)
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
    with zipfile.ZipFile(output / "verification-evidence.zip") as evidence:
        assert (
            len([name for name in evidence.namelist() if name.endswith("/tests.xml")])
            == 7
        )
        assert "adviso-compare-quality/ruff-version.txt" in evidence.namelist()
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
        "failed-job",
        "wrong-tag",
    ],
)
def test_inconsistent_candidate_evidence_is_rejected(candidate, problem):
    inputs, output, workflow, context, jobs = candidate
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
    elif problem == "failed-job":
        jobs[0]["conclusion"] = "failure"
    else:
        context = release.ReleaseContext(
            "another-tool-v1.0.0", context.commit, context.repository, "123", "1"
        )
    with pytest.raises(ValueError):
        release.build_candidate(inputs, output, workflow, context, jobs)
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


@pytest.mark.parametrize("latest_conclusion", ["success", "failure"])
def test_retry_uses_latest_job_outcome_and_retains_other_successes(
    candidate, latest_conclusion
):
    inputs, output, workflow, context, jobs = candidate
    context = release.ReleaseContext(
        context.tag, context.commit, context.repository, "123", "2"
    )
    jobs.append({**jobs[0], "run_attempt": 2, "conclusion": latest_conclusion})
    jobs[0]["conclusion"] = "failure" if latest_conclusion == "success" else "success"
    if latest_conclusion == "success":
        release.build_candidate(inputs, output, workflow, context, jobs)
        with zipfile.ZipFile(output / "verification-evidence.zip") as archive:
            outcomes = json.loads(archive.read("jobs.json"))
        assert outcomes[0]["run_attempt"] == 2
        assert outcomes[1]["run_attempt"] == 1
    else:
        with pytest.raises(ValueError, match="not succeeded"):
            release.build_candidate(inputs, output, workflow, context, jobs)
        assert not output.exists()


def test_tag_run_downloads_its_own_evidence_and_prepares_only_a_draft(
    candidate, monkeypatch
):
    inputs, output, _, context, jobs = candidate
    calls = []
    for key, value in {
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REF_NAME": context.tag,
        "GITHUB_SHA": context.commit,
        "GITHUB_REPOSITORY": context.repository,
        "GITHUB_RUN_ID": context.run_id,
        "GITHUB_RUN_ATTEMPT": "2",
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
        if "/attempts/1/jobs" in endpoint:
            return [{"jobs": jobs}]
        if "/attempts/2/jobs" in endpoint:
            return [{"jobs": []}]
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
