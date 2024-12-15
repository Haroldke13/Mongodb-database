from flask import Flask, render_template, url_for, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_frozen import Freezer

app = Flask(__name__)
freezer = Freezer(app)

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client.flask_database
todos = db.todos

@app.route("/", methods=['GET', 'POST'])
def index():
    # Check if the HTTP request is POST
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})
        return redirect(url_for('index'))
    
    all_todos = todos.find()  # Fetch all todos from the database
    return render_template('index.html', todos=all_todos)

@app.route("/<id>/delete/", methods=['POST', 'GET'])
def delete(id):
    """
    Allow the `GET` method for the `/delete/` route during static site generation.
    """
    if request.method == 'POST':
        todos.delete_one({"_id": ObjectId(id)})
        return redirect(url_for('index'))
    # Handle the GET request during the static export
    return f"Simulating deletion of todo with id {id} for static export."

# **Handle dynamic routes for Frozen-Flask**
@freezer.register_generator
def delete():
    """
    Generates static versions of the `/delete/` routes
    for all `todos` in the MongoDB collection.
    """
    for todo in todos.find():
        yield {'id': str(todo['_id'])}  # Yield the `id` of each todo

if __name__ == "__main__":
    # First freeze the app to generate static files
    freezer.freeze()
    app.run(debug=True)
