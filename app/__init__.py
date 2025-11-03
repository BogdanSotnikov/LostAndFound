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
pfps = [f"/static/pfp{i}.jpg" for i in range(1,13)]

# HTML PAGES
# LANDING PAGE
@app.route('/')
def homepage():
    if not 'u_rowid' in session:
        return redirect("/login")
    #if request.method == 'POST':
        #session['u_rowid'] = request.form['u_rowid']
    return render_template("landing.html")

# USER INTERACTIONS
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        usernames = [row[0] for row in fetch("user_base", "TRUE", "username")]
        if not request.form['username'] in usernames or len(request.form['username']) < 1:
            return render_template("login.html", error="Wrong username or password!<br><br>")
        elif request.form['password'] != fetch("user_base",
                                f"username = \"{request.form['username']}\"",
                                "password")[0][0]:
                return render_template("login.html", error="Wrong username or password!<br><br>")
        else:
            session["u_rowid"] = fetch("user_base",
                                f"username = \"{request.form['username']}\"",
                                "rowid")[0]
    if 'u_rowid' in session:
        return redirect("/")
    return render_template("login.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.pop("u_rowid", None)
    return redirect("/login")

@app.route('/register', methods=["GET", "POST"])
def register():
    if 'u_rowid' in session:
        return redirect("/")
    if request.method == "POST":
        if not request.form['password'] == request.form['confirm']:
            return render_template("register.html",
                                   error="Passwords do not match, please try again! <br><br>")
        if not create_user(request.form['username'], request.form['password']):
            return render_template("register.html",
                                   error="Username already taken, please try again! <br><br>")
        else:
            return redirect("/login")
    return render_template("register.html")

@app.route('/profile', methods=["GET", "POST"])
def profileDefault():
    return redirect(f"/profile/{session['u_rowid'][0]}");

@app.route('/profile/<u_rowid>', methods=["GET", "POST"]) # makes u_rowid a variable that is passed to the function
def profile(u_rowid):
    # session.clear()
    if not 'u_rowid' in session and session['u_rowid'] == u_rowid:
        return redirect("/login")
    u_data = fetch('user_base',
                   f"ROWID={u_rowid}",
                   'username, pfp, times_cont, contributions')[0]

    # pfp editing
    if request.method=='POST':
        if 'pfp' in request.form:
            update_pfp(request.form['pfp'], u_rowid)
            return redirect(f"/profile/{u_rowid}")
        else:
            edit = f"<form method='POST' action={u_rowid} id='PFPform'>"
            for pfp in pfps:
                edit += f"""<button type='submit' name='pfp' class='ibutton' value={pfp}>
                <img src={pfp} alt='profile choice' class='image'>
                </button>"""
            edit += "</form>"
    else:
        edit = f"""<form method='POST' action={u_rowid}>
        <input type='hidden' name='hidden'>
        <input type='Image' src='/static/edit.png' name='Change PFP'>
        </form>"""

    # sets badge/title
    if u_data[2] < 5:
        badge = "Newbie"
    elif u_data[2] < 10:
        badge = "Active Contributor"
    else:
        badge = "Top Contributor"

    # renders page
    if len(u_data[3]) > 0:
        conts = []
        for story in u_data[3].split(','):
            conts.append(fetch('story_base', f"rowid = {story}", 'title, path')[0])
        return render_template("profile.html",
            username=u_data[0],
            pfp=u_data[1],
            pfps=pfps,
            edit=edit,
            badge=badge,
            times_cont=u_data[2],
            contributions=conts)
    else:
        return render_template("profile.html",
            username=u_data[0],
            pfp=u_data[1],
            pfps=pfps,
            edit=edit,
            badge=badge,
            times_cont=u_data[2],
            if_conts="No contributions yet.")

#STORY INTERACTIONS
@app.route('/story/<s_rowid>') # makes s_rowid a variable that is passed to the function
def story(s_rowid):
    if not 'u_rowid' in session:
        return redirect("/login")
    return render_template("story.html")

@app.route('/edit/<s_rowid>') # makes s_rowid a variable that is passed to the function
def edit(s_rowid):
    if not 'u_rowid' in session:
        return redirect("/login")
    return render_template("edit.html")

@app.route('/author/<u_rowid>') # makes u_rowid a variable that is passed to the function
def author(u_rowid):
    if not 'u_rowid' in session:
        return redirect("/login")
    return render_template("author.html")

# HELPER FUNCTIONS
def fetch(table, criteria, data):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    query = f"SELECT {data} FROM {table} WHERE {criteria};"
    c.execute(query)
    data = c.fetchall()
    db.commit()
    db.close()
    return data

def check_existence(table, s_rowid):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    if 'u_rowid' in session:
        if table == story_base:
            c.execute(f"SELECT editors FROM story_base WHERE ROWID={s_rowid};")
            db.commit()
            db.close()
            return str(session['u_rowid']) in c.fetchall()[0].split(',')
        else:
            c.execute(f"SELECT contributions FROM user_base WHERE ROWID={session['u_rowid']};")
            db.commit()
            db.close()
            return str(s_rowid) in c.fetchall()[0].split(',')

def create_user(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT username FROM user_base")
    if not username in c.fetchall():
        # creates user in table
        pfp = random.choice(pfps)
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

def update_pfp(pfp, u_rowid):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute(f"UPDATE user_base SET pfp = \'{pfp}\' WHERE ROWID=\'{u_rowid}\'")
    db.commit()
    db.close()

# Flask
if __name__=='__main__':
    app.debug = True
    app.run()
