from app.services import job_search


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"results": []}


def captured_params(monkeypatch, **filters):
    seen = {}

    def fake_get(url, params, timeout):
        seen["url"] = url
        seen["params"] = params
        return FakeResponse()

    monkeypatch.setattr(job_search.requests, "get", fake_get)
    job_search.search_adzuna("Software Developer", "Berlin", "de", **filters)
    return seen


def test_no_filters_sends_only_the_basic_search(monkeypatch):
    seen = captured_params(monkeypatch)

    assert seen["url"].endswith("/jobs/de/search/1")
    assert set(seen["params"]) == {"app_id", "app_key", "what", "where", "results_per_page", "content-type"}


def test_every_filter_is_passed_to_adzuna(monkeypatch):
    seen = captured_params(
        monkeypatch,
        job_types=["full_time", "permanent"],
        salary_min=40000,
        salary_max=90000,
        max_days_old=7,
        distance=25,
    )["params"]

    assert seen["full_time"] == 1
    assert seen["permanent"] == 1
    assert seen["salary_min"] == 40000
    assert seen["salary_max"] == 90000
    assert seen["max_days_old"] == 7
    assert seen["distance"] == 25


def test_unset_filters_are_left_out_rather_than_sent_as_zero(monkeypatch):
    params = captured_params(monkeypatch, salary_min=50000)["params"]

    assert params["salary_min"] == 50000
    for absent in ("salary_max", "max_days_old", "distance", "full_time", "part_time"):
        assert absent not in params


def test_a_salary_of_zero_is_still_sent(monkeypatch):
    # 0 is a real value the user typed, not "unset" - only None means unset.
    assert captured_params(monkeypatch, salary_min=0)["params"]["salary_min"] == 0


def test_adzuna_results_are_mapped_to_jobs():
    results = {"results": [{
        "title": "Dev",
        "company": {"display_name": "Acme"},
        "location": {"display_name": "Berlin"},
        "description": "Build things",
        "redirect_url": "https://example.com/1",
    }]}

    assert job_search.extract_jobs_from_adzuna(results) == [{
        "title": "Dev", "company": "Acme", "location": "Berlin",
        "description": "Build things", "link": "https://example.com/1",
    }]


def test_missing_adzuna_fields_get_safe_defaults():
    jobs = job_search.extract_jobs_from_adzuna({"results": [{}]})

    assert jobs[0]["title"] == "Unknown Job"
    assert jobs[0]["company"] == "Unknown Company"
