from __future__ import annotations

TEMPLATES = {
    "backward-design": {
        "id": "backward-design",
        "name": "Backward design course",
        "description": "Plan outcomes, evidence, then learning experiences.",
        "course": {
            "title": "",
            "description": "",
            "learning_objectives": "",
            "units": [{"title": "Unit 1", "content": "", "lessons": [{"title": "Lesson 1", "objective": "", "activities": []}]}],
        },
    },
    "workshop-series": {
        "id": "workshop-series",
        "name": "Workshop series",
        "description": "A repeatable sequence for facilitated learning.",
        "course": {
            "title": "",
            "description": "",
            "units": [{"title": "Workshop 1", "lessons": [{"title": "Explore, practice, reflect", "activities": [{"type": "discussion", "title": "Opening discussion", "content": ""}]}]}],
        },
    },
}


def template_catalog() -> list[dict]:
    return list(TEMPLATES.values())


def template_course(template_id: str) -> dict | None:
    template = TEMPLATES.get(template_id)
    return template["course"] if template else None
