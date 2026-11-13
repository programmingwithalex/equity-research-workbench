"""Exercise CI formatting against local Git remotes with GitHub calls stubbed."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "format-pr.sh"


def _git(repo: Path, *arguments: str) -> str:
    """Run a local Git command and return its stripped standard output.

    Args:
        repo: Temporary repository directory.
        arguments: Git arguments; these tests never use a network remote.

    Returns:
        Standard output, raising on an unexpected Git failure.
    """
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def format_repo(tmp_path: Path) -> tuple[Path, Path, dict[str, str], str]:
    """Create local-only repositories and an observable GitHub CLI replacement.

    Args:
        tmp_path: Pytest-managed temporary directory.

    Returns:
        Working repository, bare origin, script environment, and original head.
        The GH stub records arguments and can simulate dispatch failure.
    """
    repo, remote, binaries = (
        tmp_path / "work",
        tmp_path / "origin.git",
        tmp_path / "bin",
    )
    repo.mkdir()
    binaries.mkdir()
    subprocess.run(
        ["git", "init", "--bare", str(remote)], check=True, capture_output=True
    )
    _git(repo, "init", "--initial-branch=feature")
    _git(repo, "config", "user.name", "programmingwithalex")
    _git(repo, "config", "user.email", "programmingwithalex3@gmail.com")
    _git(repo, "config", "core.autocrlf", "false")
    _git(repo, "remote", "add", "origin", remote.as_posix())
    (repo / "sample.py").write_text("values = [1, 2, 3]\n", encoding="utf-8")
    _git(repo, "add", "sample.py")
    _git(repo, "commit", "-m", "Seed formatting fixture")
    _git(repo, "push", "origin", "HEAD:feature")

    gh = binaries / "gh"
    gh.write_text(
        '#!/usr/bin/env bash\nprintf "%s\\n" "$*" > "$DISPATCH_LOG"\n'
        'exit "${DISPATCH_EXIT_CODE:-0}"\n',
        encoding="utf-8",
    )
    gh.chmod(0o755)
    env = dict(os.environ)
    env.update(
        PATH=str(binaries) + os.pathsep + env["PATH"],
        FORMAT_PYTHON=Path(sys.executable).as_posix(),
        PR_BRANCH="feature",
        GH_REPO="example/equity-research-fixture",
        GH_STUB_PATH=gh.as_posix(),
        GITHUB_OUTPUT=(tmp_path / "output.txt").as_posix(),
        DISPATCH_LOG=(tmp_path / "dispatch.txt").as_posix(),
    )
    return repo, remote, env, _git(repo, "rev-parse", "HEAD")


def _run(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run the actual CI helper using the current test's Python and GH stub.

    Args:
        repo: Temporary working repository.
        env: Isolated helper configuration and stub command path.

    Returns:
        Captured output and exit code, including expected failure cases.
    """
    if sys.platform == "win32":
        git = shutil.which("git")
        assert git is not None
        bash = str(Path(git).resolve().parents[1] / "bin" / "bash.exe")
    else:
        located = shutil.which("bash")
        assert located is not None
        bash = located
    probe = subprocess.run(
        [bash, "-c", 'test "$(command -v gh)" -ef "$GH_STUB_PATH"'],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    assert probe.returncode == 0, "Refuse to run tests against the real GitHub CLI."
    return subprocess.run(
        [bash, SCRIPT.as_posix()], cwd=repo, env=env, capture_output=True, text=True
    )


def _commit_unformatted(repo: Path) -> str:
    """Commit malformed spacing to represent a PR that requires formatting.

    Args:
        repo: Temporary working repository with a tracked Python file.

    Returns:
        Commit ID before the formatter creates its correction.
    """
    (repo / "sample.py").write_text("values= [1,2,3]\n", encoding="utf-8")
    _git(repo, "add", "sample.py")
    _git(repo, "commit", "-m", "Introduce unformatted source")
    return _git(repo, "rev-parse", "HEAD")


def test_formatted_checkout_creates_no_commit_or_dispatch(
    format_repo: tuple[Path, Path, dict[str, str], str],
) -> None:
    """Avoid pointless formatting commits and recursive workflow runs."""
    repo, remote, env, original = format_repo
    result = _run(repo, env)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(remote, "rev-parse", "feature") == original
    assert Path(env["GITHUB_OUTPUT"]).read_text().strip() == "changed=false"
    assert not Path(env["DISPATCH_LOG"]).exists()


def test_formatter_commits_pushes_and_dispatches_new_checks(
    format_repo: tuple[Path, Path, dict[str, str], str],
) -> None:
    """Publish corrected formatting with the required identity and recheck request."""
    repo, remote, env, _ = format_repo
    original = _commit_unformatted(repo)
    result = _run(repo, env)

    assert result.returncode == 0, result.stdout + result.stderr
    head = _git(repo, "rev-parse", "HEAD")
    assert head != original
    assert _git(remote, "rev-parse", "feature") == head
    assert _git(remote, "show", "feature:sample.py") == "values = [1, 2, 3]"
    assert _git(repo, "log", "-1", "--format=%an|%ae|%cn|%ce") == (
        "programmingwithalex|programmingwithalex3@gmail.com|"
        "programmingwithalex|programmingwithalex3@gmail.com"
    )
    assert Path(env["GITHUB_OUTPUT"]).read_text().strip() == "changed=true"
    assert Path(env["DISPATCH_LOG"]).read_text().strip() == (
        "workflow run ci.yml --repo example/equity-research-fixture --ref feature"
    )


def test_concurrent_push_is_not_overwritten(
    format_repo: tuple[Path, Path, dict[str, str], str], tmp_path: Path
) -> None:
    """Fail a stale normal push instead of overwriting a contributor's newer work."""
    repo, remote, env, _ = format_repo
    _commit_unformatted(repo)
    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", "--branch", "feature", str(remote), str(other)],
        check=True,
        capture_output=True,
    )
    _git(other, "config", "user.name", "programmingwithalex")
    _git(other, "config", "user.email", "programmingwithalex3@gmail.com")
    (other / "new.txt").write_text("Concurrent contributor change.\n", encoding="utf-8")
    _git(other, "add", "new.txt")
    _git(other, "commit", "-m", "Advance remote fixture")
    _git(other, "push", "origin", "HEAD:feature")
    advanced = _git(remote, "rev-parse", "feature")

    result = _run(repo, env)

    assert result.returncode != 0
    assert _git(remote, "rev-parse", "feature") == advanced
    assert not Path(env["DISPATCH_LOG"]).exists()


def test_dispatch_failure_is_reported_after_a_successful_push(
    format_repo: tuple[Path, Path, dict[str, str], str],
) -> None:
    """Keep CI failed when fresh checks could not be requested for the new head."""
    repo, remote, env, original = format_repo
    env["DISPATCH_EXIT_CODE"] = "1"
    _commit_unformatted(repo)

    result = _run(repo, env)

    assert result.returncode != 0
    assert _git(remote, "rev-parse", "feature") != original
    assert _git(remote, "show", "feature:sample.py") == "values = [1, 2, 3]"
    assert not Path(env["GITHUB_OUTPUT"]).exists()
