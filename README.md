# Mongodb-database

A small Flask + PyMongo to-do list, with a Frozen-Flask step that exports the rendered pages to
static HTML for GitHub Pages.

This is a learning exercise following the common "How To Use MongoDB in a Flask Application"
tutorial pattern — a single collection, add and delete, nothing more. The repository name describes
the topic rather than the app.

## What it does

`app.py` is 50 lines:

- **`GET /`** — renders every document in the `todos` collection.
- **`POST /`** — inserts `{content, degree}`, where `degree` is a radio choice of
  `important` / `unimportant`.
- **`POST /<id>/delete/`** — deletes one document by `ObjectId`.
- **`GET /<id>/delete/`** — returns the literal string
  `"Simulating deletion of todo with id … for static export."` This exists only so Frozen-Flask can
  crawl the route; it is not a real page.
- A `@freezer.register_generator` yields every todo's id so Frozen-Flask can enumerate the delete URLs.

There is no editing, no completion state, no accounts and no validation.

## Tech stack

Python 3, Flask, PyMongo, Frozen-Flask, plain CSS. No JavaScript.

MongoDB connection is hardcoded in `app.py`:

```python
client = MongoClient('localhost', 27017)
db = client.flask_database        # collection: todos
```

## Setup

**There is no `requirements.txt` in this repo.** From the imports you need:

```bash
python3 -m venv venv && source venv/bin/activate
pip install Flask pymongo Frozen-Flask
```

You also need a MongoDB server on `localhost:27017`. The `flask_database` database and the `todos`
collection are created on first insert.

## Running it

```bash
python app.py
```

Be aware of what this does: `__main__` calls **`freezer.freeze()` before `app.run()`**, so every run
first regenerates the `build/` directory from whatever is currently in MongoDB, then starts the dev
server on <http://127.0.0.1:5000>. If MongoDB is not reachable, the freeze step fails and the server
never starts.

## The `build/` and root `index.html`

`build/` is committed Frozen-Flask output from a past run, including two stale delete pages named
after MongoDB ObjectIds that no longer exist in anyone else's database. The root-level `index.html`
is a copy of `templates/index.html` and **still contains unrendered Jinja**
(`{{ url_for('static', ...) }}`, `{% for todo in todos %}`), so it does not display correctly if
served directly.

The last commit is "Deploy to GitHub Pages", but a Frozen-Flask export of this app is a dead snapshot —
the form posts back to a Flask route that does not exist on static hosting.

## Other notes

- `google_auth.py` is **an empty file**. Nothing imports it. Google authentication was presumably
  planned and never started. It can be deleted.
- No `.gitignore`.

## Status

**Finished as a tutorial exercise, not maintained.** Last commit December 2024. The core add/list/delete
loop works against a local MongoDB; the static-export half is a dead end.

## Licence

None. **TODO: add a LICENSE file** — without one, the default is "all rights reserved".
