"""Route real Git changes through this repository's CI lane configuration."""

# These are the inputs whose behaviour these tests pin; the lane planner reads them
# to select the routing lane when they change.
# gv:test-dependency: .github/test-lanes.json
# gv:test-dependency: .github/workflows/test.yml
# gv:test-dependency: .github/workflows/benchmark.yml
# gv:test-dependency: .github/workflows/release.yml
# gv:test-dependency: requirements-mypy.txt

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml
from pytest_selective.ci import LaneConfig, plan

ROOT = Path(__file__).resolve().parents[2]
CONFIG = LaneConfig.model_validate_json(
    (ROOT / ".github/test-lanes.json").read_text(encoding="utf-8")
)
NONE = dict.fromkeys(CONFIG.lanes, False)
EVERY = dict.fromkeys(CONFIG.lanes, True)
PLAN_LANES = "gigaverse-app/pytest-selective/actions/plan-lanes@"
PLAN_LANES_SHA = "286d0aeb75991d35f2ffafc7dda0517b7250b5c3"
LANE_IF = (
    "${{{{ always() && !cancelled() && (needs.select-tests.result != 'success' || "
    "fromJSON(needs.select-tests.outputs.lanes).{lane}) }}}}"
)

Mutation = Callable[[Path], None]


def git(repo: Path, *args: str) -> str:
    """Run Git in ``repo`` with a fixed identity and return its output."""
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=Lane routing",
            "-c",
            "user.email=routing@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def lanes(*names: str) -> dict[str, bool]:
    """The expected plan: exactly ``names`` run."""
    assert set(names) <= set(CONFIG.lanes), names
    return {name: name in names for name in CONFIG.lanes}


def append(path: str) -> Mutation:
    """Append a line to ``path``, creating it when absent."""

    def mutate(repo: Path) -> None:
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("\n# routing probe\n")

    return mutate


def delete(path: str) -> Mutation:
    """Remove ``path`` from the head commit."""

    def mutate(repo: Path) -> None:
        git(repo, "rm", "-q", path)

    return mutate


def edit_job(workflow: str, job: str) -> Mutation:
    """Change one job of ``workflow`` semantically, leaving every other job intact."""

    def mutate(repo: Path) -> None:
        target = repo / ".github/workflows" / workflow
        text = target.read_text(encoding="utf-8")
        header = f"\n  {job}:\n"
        assert text.count(header) == 1, (workflow, job)
        target.write_text(
            text.replace(header, f"{header}    timeout-minutes: 77\n"),
            encoding="utf-8",
            newline="\n",
        )

    return mutate


def edit_workflow_settings(workflow: str) -> Mutation:
    """Change a setting outside ``jobs:`` that every job of ``workflow`` inherits."""

    def mutate(repo: Path) -> None:
        target = repo / ".github/workflows" / workflow
        text = target.read_text(encoding="utf-8")
        assert text.count("\njobs:\n") == 1, workflow
        target.write_text(
            text.replace("\njobs:\n", "\nconcurrency: routing-probe\n\njobs:\n"),
            encoding="utf-8",
            newline="\n",
        )

    return mutate


@pytest.fixture(scope="module")
def template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A Git repository whose single commit holds this checkout's files."""
    repo = tmp_path_factory.mktemp("template")
    git(repo, "init", "-q", "-b", "main")
    listed = git(ROOT, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    for name in filter(None, listed.split("\0")):
        source = ROOT / name
        if source.is_file():
            target = repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    return repo


def change(template: Path, tmp_path: Path, *mutations: Mutation) -> tuple[Path, str]:
    """Clone the template, commit ``mutations`` and return the clone and its base."""
    repo = tmp_path / "repo"
    git(tmp_path, "clone", "-q", str(template), str(repo))
    base = git(repo, "rev-parse", "HEAD").strip()
    for mutate in mutations:
        mutate(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "change")
    return repo, base


DOCUMENTATION = [
    "docs/time.md",
    "docs/requirements.txt",
    "docs/css/code_select.css",
    "mkdocs.yml",
    ".readthedocs.yml",
    "RELEASING.md",
    ".github/CONTRIBUTING.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
]


@pytest.mark.parametrize(
    "mutation, expected",
    [
        # Prose, the docs site and its own requirements run no lane.
        *[(append(path), NONE) for path in DOCUMENTATION],
        # Development metadata validated by the always-run Lint and Mypy jobs.
        # Mypy checks these tests with the pinned planner, so its pins run them.
        (append("requirements-mypy.txt"), lanes("routing")),
        (append(".pre-commit-config.yaml"), NONE),
        (append(".github/labels.yml"), NONE),
        (append(".github/renovate.json"), NONE),
        (edit_job("lint.yml", "lint"), NONE),
        (edit_job("docs.yml", "build"), NONE),
        # README.md and LICENCE are embedded in the built distributions.
        (append("README.md"), lanes("package")),
        (append("LICENCE"), lanes("package")),
        (append(".gitignore"), lanes("package")),
        # Library code, catalogues and the scripts the jobs and tests execute.
        (append("src/humanize/number.py"), lanes("tests", "benchmark", "package")),
        (append("src/humanize/py.typed"), lanes("tests", "benchmark", "package")),
        (
            append("src/humanize/locale/de_DE/LC_MESSAGES/humanize.po"),
            lanes("tests", "benchmark", "package"),
        ),
        (
            append("scripts/generate-translation-binaries.sh"),
            lanes("tests", "benchmark", "package"),
        ),
        # test_i18n.py runs this script in a subprocess.
        (append("scripts/update-translations.sh"), lanes("tests")),
        # Tests: edited, added and deleted.
        (append("tests/test_time.py"), lanes("tests")),
        (append("tests/test_new.py"), lanes("tests")),
        (delete("tests/test_lists.py"), lanes("tests")),
        (append("tests/test_benchmarks.py"), lanes("tests", "benchmark")),
        (append("ci/tests/test_lane_routing.py"), lanes("routing")),
        # Environment, collection policy and the lane configuration run every lane.
        (append("pyproject.toml"), EVERY),
        (append("tox.ini"), EVERY),
        (append(".github/test-lanes.json"), EVERY),
        # Execution workflows select the lanes of the jobs that changed.
        (edit_job("test.yml", "test"), lanes("tests", "routing")),
        (edit_job("test.yml", "select-tests"), lanes("routing")),
        (edit_job("test.yml", "routing"), lanes("routing")),
        (edit_job("test.yml", "success"), lanes("routing")),
        (edit_workflow_settings("test.yml"), lanes("tests", "routing")),
        (edit_job("benchmark.yml", "benchmarks"), lanes("benchmark", "routing")),
        (edit_job("benchmark.yml", "select-tests"), lanes("routing")),
        (edit_job("release.yml", "build-package"), lanes("package", "routing")),
        (edit_job("release.yml", "release-pypi"), lanes("routing")),
    ],
)
def test_change_selects_exactly_its_lanes(
    template: Path, tmp_path: Path, mutation: Mutation, expected: dict[str, bool]
) -> None:
    """Each change runs exactly the lanes whose inputs it touches."""
    repo, base = change(template, tmp_path, mutation)
    result = plan(repo, CONFIG, base, "HEAD")
    assert result.lanes == expected, result.lane_reasons


def test_documentation_only_commit_runs_no_lane(template: Path, tmp_path: Path) -> None:
    """One commit touching every documentation input still runs nothing."""
    repo, base = change(template, tmp_path, *map(append, DOCUMENTATION))
    assert plan(repo, CONFIG, base, "HEAD").lanes == NONE


def test_full_checkpoint_and_missing_history_run_every_lane(
    template: Path, tmp_path: Path
) -> None:
    """Explicit full runs and an unknown base never skip a lane."""
    repo, base = change(template, tmp_path, append("docs/time.md"))
    assert plan(repo, CONFIG, base, "HEAD", full=True).lanes == EVERY
    missing = "0" * 40
    assert plan(repo, CONFIG, missing, "HEAD").lanes == EVERY


def workflow(name: str) -> dict[str, Any]:
    """The parsed workflow ``name``."""
    document = yaml.safe_load(
        (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
    )
    assert isinstance(document, dict)
    return document


def squash(text: str) -> str:
    """``text`` with whitespace runs collapsed, for comparing folded expressions."""
    return " ".join(text.split())


def assert_pinned_planner(job: dict[str, Any]) -> None:
    """The job uses the published planner major and repository configuration."""
    step = next(
        step for step in job["steps"] if step.get("uses", "").startswith(PLAN_LANES)
    )
    assert step["with"]["config"] == ".github/test-lanes.json"
    assert step["uses"] == PLAN_LANES + PLAN_LANES_SHA


def test_every_lane_gates_a_job() -> None:
    """Each lane is consumed by the job that executes it, behind the planner."""
    test_jobs = workflow("test.yml")["jobs"]
    for lane in ("tests", "routing"):
        job = test_jobs[lane if lane == "routing" else "test"]
        assert job["needs"] == "select-tests"
        assert squash(job["if"]) == squash(LANE_IF.format(lane=lane))
    benchmark = workflow("benchmark.yml")["jobs"]["benchmarks"]
    assert benchmark["needs"] == "select-tests"
    assert squash(benchmark["if"]) == squash(
        "${{ always() && !cancelled() && (needs.select-tests.result != 'success' || "
        "fromJSON(needs.select-tests.outputs.lanes).benchmark) }}"
    )
    build = workflow("release.yml")["jobs"]["build-package"]
    assert "needs" not in build, "publishing jobs must keep their single dependency"
    steps = build["steps"]
    plan_step = next(step for step in steps if step.get("id") == "plan")
    assert plan_step["if"] == "github.event_name == 'pull_request'"
    assert plan_step["continue-on-error"] is True
    admitted = steps[steps.index(plan_step) + 2 :]
    assert admitted
    for step in admitted:
        assert step["if"] == "steps.admit.outputs.build == 'true'", step
    for jobs in (test_jobs, workflow("benchmark.yml")["jobs"]):
        planner = jobs["select-tests"]
        checkout = planner["steps"][0]
        assert checkout["with"]["fetch-depth"] == 0
        assert_pinned_planner(planner)
    assert_pinned_planner(build)
    # The full checkpoint that dependency selection relies on.
    # PyYAML reads the bare ``on`` key as the boolean True.
    triggers = yaml.safe_load(
        (ROOT / ".github/workflows/test.yml").read_text(encoding="utf-8")
    )[True]
    assert triggers["schedule"]


def test_routing_job_installs_the_planner_release() -> None:
    """Routing, Mypy and the planner use the measured pytest-selective release."""
    for name in ("test.yml", "benchmark.yml", "release.yml"):
        text = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
        assert PLAN_LANES + PLAN_LANES_SHA in text
    run = workflow("test.yml")["jobs"]["routing"]["steps"][-1]["run"]
    assert '"pytest-selective==1.4.0"' in run
    mypy = (ROOT / "requirements-mypy.txt").read_text(encoding="utf-8")
    assert "pytest-selective==1.4.0" in mypy


def heredoc(run: str) -> str:
    """The Python program embedded in a ``python3 - <<'PY'`` step."""
    body = run.split("<<'PY'\n", 1)[1].rsplit("PY", 1)[0]
    return textwrap.dedent(body)


@pytest.mark.parametrize(
    "plan_result, lanes_json, test_result, routing_result, passes",
    [
        ("success", '{"tests": false, "routing": false}', "skipped", "skipped", True),
        ("success", '{"tests": true, "routing": false}', "success", "skipped", True),
        ("success", '{"tests": true, "routing": true}', "success", "success", True),
        # A skip is accepted only when the plan explicitly said the lane is unaffected.
        ("success", '{"tests": true, "routing": false}', "skipped", "skipped", False),
        ("success", '{"tests": false, "routing": true}', "skipped", "skipped", False),
        ("success", '{"tests": true, "routing": false}', "failure", "skipped", False),
        ("success", '{"tests": true, "routing": true}', "cancelled", "success", False),
        # A failed planner runs every job, and still blocks the gate.
        ("failure", "", "success", "success", False),
        ("success", "{}", "success", "success", False),
        ("success", '{"tests": "true", "routing": true}', "success", "success", False),
    ],
)
def test_success_gate_accepts_only_planned_skips(
    plan_result: str,
    lanes_json: str,
    test_result: str,
    routing_result: str,
    passes: bool,
) -> None:
    """The required ``Test successful`` check stays meaningful on the empty route."""
    gate = workflow("test.yml")["jobs"]["success"]
    assert gate["if"] == "always()"
    assert gate["needs"] == ["select-tests", "test", "routing"]
    step = gate["steps"][-1]
    assert set(step["env"]) == {"PLAN_RESULT", "LANES", "TEST_RESULT", "ROUTING_RESULT"}
    env = os.environ | {
        "PLAN_RESULT": plan_result,
        "LANES": lanes_json,
        "TEST_RESULT": test_result,
        "ROUTING_RESULT": routing_result,
    }
    completed = subprocess.run(
        [sys.executable, "-c", heredoc(step["run"])], env=env, check=False
    )
    assert (completed.returncode == 0) is passes


def test_fork_benchmarks_execute_without_publishing() -> None:
    """Forks run benchmarks locally; only upstream publishes to CodSpeed."""
    steps = workflow("benchmark.yml")["jobs"]["benchmarks"]["steps"]
    published = next(
        step for step in steps if step.get("uses", "").startswith("CodSpeedHQ/action@")
    )
    assert published["if"] == "github.event.repository.fork == false"
    local = next(
        step for step in steps if step.get("name") == "Run benchmark tests on forks"
    )
    assert local["if"] == "github.event.repository.fork == true"
    assert local["run"].strip() == "pytest tests/test_benchmarks.py --benchmark-disable"
