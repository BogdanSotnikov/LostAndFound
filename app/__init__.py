import sqlite3
import random
from flask import Flask, render_template
from flask import session, request, redirect

# Flask
app = Flask(__name__)
app.secret_key = 'supersecret'

# SQLite
DB_FILE = "data.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()

c.execute("CREATE TABLE IF NOT EXISTS user_base(username TEXT, password TEXT, pfp TEXT, path TEXT, contributions TEXT, times_cont INTEGER);")
c.execute("CREATE TABLE IF NOT EXISTS story_base(path TEXT, title TEXT, content TEXT, last_entry TEXT, editors TEXT, author INTEGER);")

db.commit()
db.close()

# VARIABLES
pfps = []

# HTML PAGES
# LANDING PAGE
@app.route('/')
def homepage():
    if not 'u_rowid' in session: return redirect("/login")
    if request.method == 'POST':
        session['u_rowid'] = request.form['u_rowid']
    return render_template("landing.html")

# USER INTERACTIONS
@app.route('/login')
def login():
    if 'u_rowid' in session: return redirect("/")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if 'u_rowid' in session: return redirect("/")
    if request.method == "POST":
        if not request.form['password'] == request.form['confirm']: return render_template("register.html", error="Passwords do not match, please try again! <br><br>")
        if not create_user(request.form['username'], request.form['password']): return render_template("register.html", error="Username already taken, please try again! <br><br>")
        else: return redirect("/login")
    return render_template("register.html")

@app.route('/profile/<u_rowid>') # makes u_rowid a variable that is passed to the function
def profile(u_rowid):
    if not ('u_rowid' in session and 'u_rowid' == u_rowid): return redirect("/login")
    u_data = fetch('user_base', u_rowid, 'username,times_cont,contributions', "")[0]
    return render_template("profile.html", username=u_data[0], times_cont=u_data[1])

#STORY INTERACTIONS
@app.route('/story/<s_rowid>') # makes s_rowid a variable that is passed to the function
def story(s_rowid):
    if not 'u_rowid' in session: return redirect("/login")
    return render_template("story.html")

@app.route('/edit/<s_rowid>') # makes s_rowid a variable that is passed to the function
def edit(s_rowid):
    if not 'u_rowid' in session: return redirect("/login")
    return render_template("edit.html")

@app.route('/author/<u_rowid>') # makes u_rowid a variable that is passed to the function
def author(u_rowid):
    if not 'u_rowid' in session: return redirect("/login")
    return render_template("author.html")

# HELPER FUNCTIONS
def authenticate(query):

def fetch(table, rowid, data, criteria):
    query = "SELECT "
    for d in split(data, ","):
        query += d + ","
    query += f" FROM {table} WHERE ROWID={rowid}"
    for c in split(criteria,"&"): # IF MULTIPLE CRITERIA, THEY WILL BE SPLIT WITH A '&' CHARACTER
        query += " AND " + c
    c.execute(query + ";")
    return c.fetchall()

def check_existence(table, s_rowid):
    if 'u_rowid' in session:
        if table == story_base:
            c.execute(f"SELECT editors FROM story_base WHERE ROWID={s_rowid};")
            return str(session['u_rowid']) in split(c.fetchall()[0],',')
        else:
            c.execute(f"SELECT contributions FROM user_base WHERE ROWID={session['u_rowid']};")
            return str(s_rowid) in split(c.fetchall()[0], ',')

def create_user(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT username FROM user_base")
    if not username in c.fetchall():
        # creates user in table
        #pfp = random.choice(pfps)
        pfp = "temp"
        contributions = ""
        times_cont = 0
        c.execute(f"INSERT INTO user_base VALUES(\'{username}\', \'{password}\', \'{pfp}\', 'temp', \'{contributions}\', {times_cont})")

        # set path
        c.execute(f"SELECT rowid FROM user_base WHERE username=\'{username}\'")
        c.execute(f"UPDATE user_base SET path = '/profile/{c.fetchall()[0][0]}' WHERE username=\'{username}\'")
        db.commit()
        db.close()
        return True
    db.commit()
    db.close()
    return False

# Flask
if __name__=='__main__':
    app.debug = True
    app.run()
