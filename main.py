from bson import ObjectId
from flask import Flask, request, render_template, redirect, session,Blueprint, url_for
from datetime import date
import pymongo
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
import os

today = date.today()
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["mydatabase"]
blog_table = db["mydatabase"]
fav_table = db["favourite"]
comment_table = db["comments"]
users_table = db["User"]

app = Flask(__name__)

app.secret_key = 'super secret key'

UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#authentication Done
#picture storing and viewing Done
#user authorisation Done
#favourite posts Done
#my posts (filtering) Done
#search post Done
#edit Done
#delete Done
#comment
#custom catagory
#Profile
#report post
#archieve post
#Group creation
#Group discussion
#Support
#favourite count
#deleting from favourite for second tap


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', "POST"])
def register():
    if request.method == "POST":
        std = dict(request.form)
        username = request.form['username']
        password = request.form['pass']
        pass1 = request.form['pass1']
        print(username)
        print(password)
        print(pass1)
        if request.form["pass"] == request.form["pass1"]:
            users_table.insert_one({"id":username,"pass":password, "pass1":pass1})
            return redirect("/")
        else:
            message = "passwords did not match"
    return render_template("signup.html", **locals())

@app.route('/login', methods=['GET', "POST"])
def login():
    if request.method == "POST":
        form_data = dict(request.form)
        form_username = form_data["username"]
        form_password = form_data["password"]

        print(form_username)
        print(form_password)
        db_user = users_table.find_one({"id": form_username})
        print(db_user)
        if db_user is None:
            return "Username not found"
        if form_password != db_user["pass"]:
            return "password did not match"
        session["logged_in"] = True
        session["username"] = form_username
    if "logged_in" in session:
        return redirect('/')
    return render_template("Login.html", **locals())

@app.route('/logout', methods=['GET', "POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route('/create', methods=['GET', "POST"])
def create ():
    if request.method =="POST":
        form_data = request.form
        title = form_data["title"]
        text = form_data["desc"]
        author = session["username"]
        date = today.strftime("%d %B %Y")

        file = request.files['inputFile']
        filename = secure_filename(file.filename)
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            blog_title = blog_table.insert_one({"title": title, "author": author, "date": date, "description": text, "image": file.filename})
            msg = 'File successfully uploaded '
            return redirect('/')
        else:
            msg = "Invalid Uplaod only txt, pdf, png, jpg, jpeg, gif"
            return redirect('/')
    return render_template("index.html", **locals())  

@app.route('/edit/<string:id>', methods=['GET', "POST"])
def edit (id):
    data = blog_table.find_one({"_id": ObjectId(id)})
    print(id)
    print(data)
    if data:
        title = data["title"]
        desc = data["description"]
        if request.method=="POST":
            if request.form["title"] != "":
                blog_table.delete_one({"_id": ObjectId(id)})
                form_data = request.form
                title = form_data["title"]
                text = form_data["desc"]
                blog_title = blog_table.insert_one({"title": title, "description": text})
            msg = "Upload Successfull!"
            return redirect('/')

        print(title)
        print (desc)
    return render_template("edit.html", **locals())

@app.route('/delete/<string:id>', methods=['GET', "POST"])
def delete (id):
    data = blog_table.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
            blog_table.delete_one({"_id": ObjectId(id)})
            return redirect('/')
    return render_template("delete.html", **locals())


@app.route('/', methods=['GET', "POST"])
def home():
    if "logged_in" in session:
        user = session["username"]
    list1 = {}
    posts = list(blog_table.find())
    commen = list(comment_table.find())
    print(posts)
    for t in posts:
        list1[t["title"]]= t["description"]
        # print (t["title"])
    # print(list1)
    return render_template('dash.html', **locals())

@app.route('/fav/<string:id>', methods=['GET', "POST"])
def fav(id):
    if "logged_in" in session:
        user = session["username"]
    data = blog_table.find_one({"_id": ObjectId(id)})
    data["person"]= user
    print("visited")
    if request.method=="POST":
        fav_table.insert_one(data)
        return redirect("/")

@app.route('/favPage', methods=['GET', "POST"])
def favouritePage():
    if "logged_in" in session:
        user = session["username"]
    list1 = {}
    posts = list(fav_table.find({"person": user}))
    print (posts)
    return render_template("favourite.html", **locals())

@app.route('/myPosts', methods=['GET', "POST"])
def myPosts():
    if "logged_in" in session:
        user = session["username"]
    list1 = {}
    posts = list(blog_table.find({"author": user}))
    print (posts)
    return render_template("dash.html", **locals())

@app.route('/searchPosts', methods=['GET', "POST"])
def search():
    title = request.form["searc"]
    posts = list(blog_table.find({"title": title}))
    return render_template('searched.html',**locals())

@app.route('/comments/<string:id>', methods=['GET', "POST"])
def comment(id):
    if "logged_in" in session:
        user = session["username"]
    data = blog_table.find_one({"_id": ObjectId(id)})
    com=dict()
    com["id"] = id
    print(com["id"])
    if request.method=="POST":
        comment= request.form['comm']
        com["commenter"] = user
        com["comment"] = comment
        comment_table.insert_one(com)
        return redirect("/")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5002)
    #serve(app, host='127.0.0.1', port=5002)
    #serve(app, host='0.0.0.0', port=80)