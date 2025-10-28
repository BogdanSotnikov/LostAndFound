import sqlite3
from flask import Flask, render_template
from flask import session, request, redirect

# Flask
app = Flask(__name__)

# SQLite
DB_FILE = "data.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()

c.execute("CREATE TABLE IF NOT EXIST user_base(username TEXT, password TEXT, pfp TEXT, path TEXT, contributions TEXT, times_cont INTEGER);")
c.execute("CREATE TABLE IF NOT EXIST story_base(path TEXT, title TEXT, content TEXT, last_entry TEXT, editors TEXT, author INTEGER);")

# HTML PAGES
# LANDING PAGE
@app.route('/')
def homepage():
    return authenticate("landing.html")

# USER INTERACTIONS
@app.route('/login')
def login():
    return authenticate("login.html")

@app.route('/register')
def register():
    return authenticate("register.html")

@app.route('/profile/<u_rowid>') # makes u_rowid a variable that is passed to the function
def profile(u_rowid):
    return authenticate("profile.html")

#STORY INTERACTIONS
@app.route('/story/<s_rowid>') # makes s_rowid a variable that is passed to the function
def story(s_rowid):
    return authenticate("story.html")

@app.route('/edit/<s_rowid>') # makes s_rowid a variable that is passed to the function
def edit(s_rowid):
    return authenticate("edit.html")

@app.route('/author/<u_rowid>') # makes u_rowid a variable that is passed to the function
def author(u_rowid):
    return authenticate("author.html")

# HELPER FUNCTIONS
def authenticate(query):
    if 'login' in query or 'register' in query:
        if 'u_rowid' in session: return redirect('/')
    elif not 'u_rowid' in session: return redirect("/login")
    return render_template(query)

def fetch(table, rowid, data, criteria):
    query = f"SELECT {data} FROM {table} WHERE ROWID={rowid}"
    for c in split(criteria,"&"): # IF MULTIPLE CRITERIA, THEY WILL BE SPLIT WITH A '&' CHARACTER
        query += " AND " + c
    c.execute(query + ";")
    return c.fetchall()

def check_existence(table, s_rowid):
    if 'u_rowid' in session:
        if table == story_base:
            c.execute(f"SELECT editors FROM story_base WHERE ROWID={s_rowid};")
            return str(session['u_rowid']) in split(c.fetchall(),',')
        else:
            c.execute(f"SELECT contributions FROM user_base WHERE ROWID={session['u_rowid']};")
            return str(s_rowid) in split(c.fetchall(), ',')

def create_user(username, password):
    pfp = "temp"
    path = "temp"
    contributions = ""
    times_cont = 0
    c.execute(f"INSERT INTO user_base VALUES(\"{username}\", \"{password}\", \"{pfp}\", \"{path}\", \"{contributions}\", {times_cont},)")

# SQLite
db.commit()
db.close()

# Flask
if __name__=='__main__':
    app.debug = True
    app.run()
