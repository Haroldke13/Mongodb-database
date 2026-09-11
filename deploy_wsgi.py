"""Deployment entrypoint for Mongodb-database.

Additive only — app.py is untouched. It:

  * repoints the MongoDB connection at MONGO_URI,
  * sets a session secret from the environment,
  * registers a /healthz probe.

app.py builds its client at import time with a hardcoded
`MongoClient('localhost', 27017)`, but every route looks the `todos` collection
up as a module global at call time. Rebinding that module attribute after import
is therefore enough, and does not depend on any framework internals.

Run with:  gunicorn deploy_wsgi:app
"""

import os

from pymongo import MongoClient

import app as todo_module  # noqa: E402
from app import app  # noqa: E402

# --- MongoDB ----------------------------------------------------------------
_uri = os.environ.get("MONGO_URI")
if _uri:
    _client = MongoClient(_uri)
    _db = _client.get_default_database()
    if _db is None:
        # No database name in the URI; keep app.py's choice of `flask_database`.
        _db = _client["flask_database"]
    todo_module.client = _client
    todo_module.db = _db
    todo_module.todos = _db["todos"]

# --- session secret ---------------------------------------------------------
# app.py never sets one. Flask only needs it if flash()/session are used later,
# but setting it costs nothing and avoids a future surprise.
_secret = os.environ.get("SECRET_KEY")
if _secret:
    app.secret_key = _secret

# --- health probe -----------------------------------------------------------
if "healthz" not in app.view_functions:

    @app.route("/healthz")
    def healthz():
        """Liveness probe. No MongoDB round trip: the index route already fails
        loudly if the database is unreachable."""
        return {"status": "ok"}, 200


if __name__ == "__main__":  # pragma: no cover - local smoke test only
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5762)))
