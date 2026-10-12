from tests.conftest import application_body


def save(client, **overrides):
    response = client.post("/save-application", json=application_body(**overrides))
    assert response.status_code == 200
    return response.json()["id"]


def test_saved_application_appears_in_the_list(client):
    save(client)

    listed = client.get("/applications").json()

    assert len(listed) == 1
    assert listed[0]["company"] == "Acme"


def test_application_saved_with_documents_reports_them_without_sending_them(client):
    save(
        client,
        tailored_resume={"basics": {"name": "Jo"}},
        cover_letter="Dear team",
        job_description="We need Python",
    )

    listed = client.get("/applications").json()[0]

    assert listed["has_tailored_resume"] is True
    assert listed["has_cover_letter"] is True
    # The list stays small: the documents themselves are fetched on demand.
    assert "tailored_resume" not in listed
    assert "cover_letter" not in listed


def test_application_saved_without_documents_reports_none(client):
    save(client)

    listed = client.get("/applications").json()[0]

    assert listed["has_tailored_resume"] is False
    assert listed["has_cover_letter"] is False


def test_documents_round_trip(client):
    app_id = save(
        client,
        tailored_resume={"basics": {"name": "Jo"}},
        cover_letter="Dear team",
        job_description="We need Python",
    )

    assert client.get(f"/applications/{app_id}/documents").json() == {
        "tailored_resume": {"basics": {"name": "Jo"}},
        "cover_letter": "Dear team",
        "job_description": "We need Python",
    }


def test_editing_the_resume_does_not_wipe_the_cover_letter(client):
    app_id = save(client, tailored_resume={"v": 1}, cover_letter="Dear team", job_description="JD")

    client.put(f"/applications/{app_id}/documents", json={"tailored_resume": {"v": 2}})
    documents = client.get(f"/applications/{app_id}/documents").json()

    assert documents["tailored_resume"] == {"v": 2}
    assert documents["cover_letter"] == "Dear team"
    assert documents["job_description"] == "JD"


def test_documents_can_be_added_to_an_application_saved_without_them(client):
    app_id = save(client)

    client.put(f"/applications/{app_id}/documents", json={"cover_letter": "Late letter"})

    assert client.get(f"/applications/{app_id}/documents").json()["cover_letter"] == "Late letter"


def test_another_user_cannot_see_or_change_my_application(client, acting):
    app_id = save(client, tailored_resume={"secret": True}, cover_letter="private")

    acting.user_id = "user-b"

    assert client.get("/applications").json() == []
    assert client.get(f"/applications/{app_id}/documents").status_code == 404
    assert client.put(f"/applications/{app_id}/documents", json={"cover_letter": "hacked"}).status_code == 404

    acting.user_id = "user-a"
    assert client.get(f"/applications/{app_id}/documents").json()["cover_letter"] == "private"


def test_another_user_cannot_delete_or_change_the_status_of_my_application(client, acting):
    app_id = save(client)

    acting.user_id = "user-b"
    client.delete(f"/applications/{app_id}")
    client.put(f"/applications/{app_id}/status", params={"status": "Rejected"})

    acting.user_id = "user-a"
    remaining = client.get("/applications").json()
    assert len(remaining) == 1
    assert remaining[0]["status"] == "Saved"


def test_documents_of_a_missing_application_return_404(client):
    assert client.get("/applications/999/documents").status_code == 404
    assert client.put("/applications/999/documents", json={"cover_letter": "x"}).status_code == 404


def test_status_update_and_delete_work_for_the_owner(client):
    app_id = save(client)

    client.put(f"/applications/{app_id}/status", params={"status": "Interview"})
    assert client.get("/applications").json()[0]["status"] == "Interview"

    client.delete(f"/applications/{app_id}")
    assert client.get("/applications").json() == []
