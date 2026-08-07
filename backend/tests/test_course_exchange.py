from app.course_exchange import echoed_json_adapter
from app.course_templates import template_catalog, template_course


def test_template_catalog_has_valid_authoring_graphs():
    catalog = template_catalog()
    assert catalog
    for template in catalog:
        graph = template_course(template["id"])
        document = {"format": "echoed-json-v1", "course": graph}
        assert not [issue for issue in echoed_json_adapter.validate_import(document) if issue.severity == "blocking"]
        assert echoed_json_adapter.to_authoring_draft(document).units


def test_exchange_adapter_reports_unsupported_constructs_before_persistence():
    document = {
        "format": "echoed-json-v1",
        "course": {"title": "Portable course", "description": "", "units": [], "scorm_package": "unsupported.zip"},
    }
    issues = echoed_json_adapter.validate_import(document)
    assert any(issue.code == "unsupported_construct" and issue.path == "course.scorm_package" for issue in issues)


def test_exchange_adapter_rejects_unknown_format():
    issues = echoed_json_adapter.validate_import({"format": "imscc", "course": {"title": "Course", "units": []}})
    assert any(issue.code == "unsupported_format" and issue.severity == "blocking" for issue in issues)
