def test_no_master_resume_yet_returns_404(client):
    assert client.get("/master-resume").status_code == 404


def test_saving_twice_updates_instead_of_duplicating(client):
    client.put("/master-resume", json={"resume_json": {"v": 1}})
    client.put("/master-resume", json={"resume_json": {"v": 2}, "source_type": "pdf_upload"})

    saved = client.get("/master-resume").json()

    assert saved["resume_json"] == {"v": 2}
    assert saved["source_type"] == "pdf_upload"


def test_each_user_has_their_own_master_resume(client, acting):
    client.put("/master-resume", json={"resume_json": {"owner": "a"}})

    acting.user_id = "user-b"
    assert client.get("/master-resume").status_code == 404
    client.put("/master-resume", json={"resume_json": {"owner": "b"}})

    acting.user_id = "user-a"
    assert client.get("/master-resume").json()["resume_json"] == {"owner": "a"}
