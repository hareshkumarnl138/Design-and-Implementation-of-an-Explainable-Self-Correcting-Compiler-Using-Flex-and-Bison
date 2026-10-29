# Backend API

From the repository root:

```bash
python -m pip install -r requirements.txt
python backend/app.py
```

The development API binds to `127.0.0.1:5000`.

- `GET /api/health`
- `POST /api/diagnose`
- `POST /api/repair`

POST requests expect JSON with a string field named `source`. The repair endpoint returns the suggested source, each applied edit, and diagnostics after repair. Repairs are heuristic and must be reviewed.
