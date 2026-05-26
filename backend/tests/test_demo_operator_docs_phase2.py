from __future__ import annotations

import importlib.util
from pathlib import Path

from app import seed_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs" / "demo-readiness.md"
README_PATH = REPO_ROOT / "README.md"
RESEED_SCRIPT_PATH = REPO_ROOT / "backend" / "scripts" / "reseed_demo.py"


def _load_reseed_demo_module():
    spec = importlib.util.spec_from_file_location("reseed_demo_script", RESEED_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_demo_operator_doc_references_real_seeded_accounts_and_outcomes():
    contents = DOC_PATH.read_text(encoding="utf-8")

    assert seed_demo.DEMO_ORG_NAME in contents
    assert seed_demo.DEMO_COURSE_TITLE in contents
    assert "backend\\venv\\Scripts\\python.exe backend\\scripts\\reseed_demo.py" in contents
    assert "alembic upgrade head" in contents

    for key in ("org_admin", "teacher", "student1", "student2", *seed_demo.DEMO_ARCHETYPE_LEARNER_KEYS):
        profile = seed_demo.DEMO_USERS[key]
        assert profile["username"] in contents

    for expected_state in ("enrichment", "reteach", "review", "monitor", "normal"):
        assert expected_state in contents


def test_readme_links_to_demo_operator_runbook():
    contents = README_PATH.read_text(encoding="utf-8")

    assert "backend\\venv\\Scripts\\python.exe backend\\scripts\\reseed_demo.py" in contents
    assert "docs/demo-readiness.md" in contents


def test_reseed_script_runs_seed_entrypoint_and_prints_summary(monkeypatch, capsys):
    module = _load_reseed_demo_module()
    called = {"run": 0}

    def fake_run():
        called["run"] += 1

    monkeypatch.setattr(module.seed_demo, "run", fake_run)

    exit_code = module.main()

    output = capsys.readouterr().out
    assert exit_code == 0
    assert called["run"] == 1
    assert "Running EchoEd demo reseed..." in output
    assert "EchoEd demo reseed completed successfully." in output
    assert seed_demo.DEMO_ORG_NAME in output
    assert seed_demo.DEMO_COURSE_TITLE in output
    assert seed_demo.DEMO_USERS["teacher"]["username"] in output
    assert seed_demo.DEMO_USERS["mastered_student"]["username"] in output
    assert "expected runtime recommendation=enrichment" in output
