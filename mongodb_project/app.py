from flask import Flask,render_template,url_for,request,redirect
from pymongo import MongoClient
from bson.objectid import ObjectId

app=Flask(__name__)

client = MongoClient('localhost',27017)


@app.route("/",methods=['GET','POST'])
def index():
    
    #Check if the httprequest == post method
    if request.method=='POST':
        content=request.form['content']
        degree=request.form['degree']
        todos.insert_one({'content':content, 'degree':degree})
        return redirect(url_for('index'))
    
    all_todos = todos.find()    #Handles thepost requests
    
    return render_template('index.html', todos=all_todos) #Saves all todos from the db 

#@app.route("/",methods=['POST']) OR
@app.post("/<id>/delete/")
def delete(id):
    todos.delete_one({"_id":ObjectId(id)})
    return redirect(url_for('index'))

#this is a mongodb database
db= client.flask_database
#Create tables in the db

todos=db.todos
#Crweate records in the table






if __name__== "__main__":
    app.run(debug=True)