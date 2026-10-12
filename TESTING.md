# Running the tests

The backend tests run without a real database, OpenAI key, or Supabase
account: they use an in-memory database and dummy settings, so they're safe
to run any time and never touch live data.

```bash
cd backend
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt   # once
.venv/Scripts/python.exe -m pytest
```

What's covered:

- **Applications** - saving, listing, status changes, deleting, and the
  saved resume / cover letter (including that one user can never see or
  change another user's application).
- **Master resume** - one per user, saving twice updates instead of
  duplicating.
- **Login token checking** - valid, expired, wrong audience, forged, and
  missing tokens.
- **Job search** - that each filter (job type, salary, recency, radius) is
  sent to Adzuna, and left out when unset.

Run the tests before every deploy. If you change how a rule works, change
its test in the same commit.
