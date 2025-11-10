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
math_problems = [f"/static/math/math{i}.png" for i in range(1, 11)]
math_ans = [26, 40, 14, 16, 32, 1, 271, 15, 10, 12]
math = list(zip(math_problems, math_ans))

# HTML PAGES
# LANDING PAGE
@app.route('/', methods=["GET", "POST"])
def homepage():
    if not 'u_rowid' in session:
        return redirect("/login")
    if request.method == 'POST':
        if "search" in request.form:
            return redirect(f"/search/{request.form['searchText']}")
    tableString = ""
    for i in range(fetch('story_base', True, 'COUNT(*)')[0][0]):
        if (i%3==0):
            tableString +="<tr>"
        story_id = i+1
        title = fetch("story_base", f"rowid={story_id}", "title")[0][0]
        author_id = fetch("story_base", f"rowid={story_id}", "author")[0][0]
        author = fetch("user_base", f"rowid={author_id}", "username")[0][0]
        tableString+= f"""
        <td>
            <a href='/story/{story_id}'>{title}</a>
            <p>by <a href='/profile/{author_id}'>{author}</a></p>
        </td>"""
        if (i%3==2):
            tableString +="</tr>"
    if not tableString.strip().endswith("</tr>"):
        tableString+="</tr>"
    return render_template("landing.html", stories = tableString)

# USER INTERACTIONS
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        usernames = [row[0] for row in fetch("user_base", "TRUE", "username")]
        # FORGOT PASSWORD
        if "forgot" in request.form:
            return render_template("login.html",
                normal=False,
                prompt="Please &nbsp enter &nbsp your &nbsp username &nbsp below:",
                request="""<input type='Text' name='f_user' required> <br><br>
                <input type='Submit' name='sub1' class='sub1' value='Submit'>""")
        elif "f_user" in request.form:
            if request.form['f_user'] in usernames:
                if not 'question' in session:
                    session['question'] = random.randint(1, 9)
                session['username'] = request.form['f_user']
                return render_template("login.html",
                    normal=False,
                    prompt="Solve &nbsp the &nbsp math &nbsp problem &nbsp below:",
                    request=f"""<image src="{math[session['question']][0]}" class="question"> <br><br>
                    <input type='number' name='answer' required> <br><br>
                    <input type='Submit' name='sub1' class='sub1' value='Submit'>""")
            return render_template("login.html",
                normal=False,
                error="User &nbsp does &nbsp not &nbsp exist",
                prompt="Please &nbsp enter &nbsp your &nbsp username &nbsp below:",
                request="""<input type='Text' name='f_user' required> <br><br>
                <input type='Submit' name='sub1' class='sub1' value='Submit'>""")
        elif "answer" in request.form:
            if int(request.form['answer']) == math[session['question']][1]:
                return render_template("login.html",
                    normal=False,
                    prompt="Enter &nbsp your &nbsp new &nbsp password &nbsp below:",
                    request="""<input type='Text' name='new_pw' required> <br><br>
                    <p>Confirm<p><br>
                    <input type='Text' name='confirm' required> <br><br>
                    <input type='Submit' name='sub1' class='sub1' value='Submit'>""")
            else:
                return render_template("login.html",
                    normal=False,
                    error="You got it wrong :(",
                    prompt="Solve &nbsp the &nbsp math &nbsp problem &nbsp below:",
                    request=f"""<image src="{math[session['question']][0]}" class="question"> <br><br>
                    <input type='number' name='answer' required> <br><br>
                    <input type='Submit' name='sub1' class='sub1' value='Submit'>""")
        elif "new_pw" in request.form:
            if not request.form['new_pw'] == request.form['confirm']:
                return render_template("login.html",
                    normal=False,
                    error="Passwords do not match, please try again!",
                    prompt="Enter &nbsp your &nbsp new &nbsp password &nbsp below:",
                    request="""<input type='Text' name='new_pw'> <br><br>
                    <p>Confirm<p><br>
                    <input type='Text' name='confirm'> <br><br>
                    <input type='Submit' name='sub1' class='sub1' value='Submit'>""")
            update_password(request.form['new_pw'], session['username'])
            return render_template("login.html", normal=True)


        # SIGNING IN
        elif not request.form['username'] in usernames:
            return render_template("login.html",
                error="Wrong &nbsp username &nbsp or &nbsp password!<br><br>",
                normal=True)
        elif request.form['password'] != fetch("user_base", "username = ?", "password", (request.form['username'],))[0][0]:
                return render_template("login.html",
                    error="Wrong &nbsp username &nbsp or &nbsp password!<br><br>",
                    normal=True)
        else:
            session["u_rowid"] = fetch("user_base", "username = ?", "rowid", (request.form['username'],))[0]
    if 'u_rowid' in session:
        return redirect("/")
    session.clear()
    return render_template("login.html", normal=True)

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
    if not 'u_rowid' in session:
        return redirect("/login")
    return redirect(f"/profile/{session['u_rowid'][0]}")

@app.route('/profile/<u_rowid>', methods=["GET", "POST"]) # makes u_rowid a variable that is passed to the function
def profile(u_rowid):
    # session.clear()
    if not 'u_rowid' in session:
        return redirect("/login")
    u_data = fetch('user_base', "ROWID=?", 'username, pfp, times_cont, contributions', (u_rowid,))[0]
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
        for story in u_data[3].split(',')[1:]:
            conts.append(fetch('story_base', 'rowid = ?', 'title, path, author', (story,))[0])
        conts_au = []
        conts_ed = []
        for st in conts:
            if st[2] == int(u_rowid):
                conts_au.append(st)
            else:
                conts_ed.append(st)
        contss = [conts_au, conts_ed]
        return render_template("profile.html",
            username=u_data[0],
            pfp=u_data[1],
            pfps=pfps,
            edit=edit,
            own_profile=(session['u_rowid'][0] == int(u_rowid)),
            badge=badge,
            times_cont=u_data[2],
            contributions=contss)
    else:
        contss = []
        return render_template("profile.html",
            username=u_data[0],
            pfp=u_data[1],
            pfps=pfps,
            edit=edit,
            own_profile=(session['u_rowid'][0] == int(u_rowid)),
            badge=badge,
            times_cont=u_data[2],
            if_conts="No contributions yet. <br><br><br>",
            contributions=contss)

#STORY INTERACTIONS
@app.route('/story/<s_rowid>') # makes s_rowid a variable that is passed to the function
def story(s_rowid):
    if not 'u_rowid' in session:
        return redirect("/login")
    if int(s_rowid) > fetch('story_base', True, 'COUNT(*)')[0][0]:
        return redirect("/")

    story_data = fetch("story_base", "rowid == ?", "*", (s_rowid,))[0]
    u_rowid = session['u_rowid'][0]
    cont = fetch('user_base', 'ROWID=?','contributions', (u_rowid,))[0][0].split(',')[1:]
    editor_ids = []
    if len(story_data[4]) > 0:
        editor_ids = [fetch('user_base', "username==?", 'rowid', (editor,))[0][0] for editor in story_data[4].split(',')[1:]]
    editors = dict(zip(editor_ids, story_data[4].split(',')[1:]))
    no_edit = (s_rowid not in cont)
    if no_edit and len(editor_ids) > 0:
        entries = "..." + story_data[3]
    else:
        entries = story_data[2]
    return render_template(
        "story.html",
        title=story_data[1],
        content=entries,
        editors=editors,
        author_id=story_data[5],
        story_id=s_rowid,
        didnt_edit=no_edit,
        author_user=fetch('user_base', "ROWID=?", 'username', (story_data[5],))[0][0]
    )

@app.route('/edit/<s_rowid>', methods=["GET", "POST"]) # makes s_rowid a variable that is passed to the function
def edit(s_rowid):
    if not 'u_rowid' in session:
        return redirect("/login")
    if s_rowid in fetch('user_base', f"ROWID={session['u_rowid'][0]}", 'contributions')[0][0].split(','):
        return redirect(f"/story/{s_rowid}")
    if int(s_rowid) > fetch('story_base', True, 'COUNT(*)')[0][0]:
        return redirect("/")
    if request.method == "POST":
        if s_rowid == '0':
            title = request.form['story_title']
        else:
            title = ''
        update = update_story(
            s_rowid,
            session['u_rowid'][0],
            title,
            request.form['content']
        )

        if update:
            if s_rowid == '0':
                return redirect(f"/story/{fetch('story_base', True, 'COUNT(*)')[0][0]}")
            else:
                return redirect(f"/story/{s_rowid}")
        else:
            return render_template(
                "edit.html",
                display_title = (s_rowid == '0'), # always true since title is empty string for editing existing story
                recent = "",
                error="""
                <p style=\"color: red;\">
                    Title already exists, please choose a different title
                </p>
                """)
    recent = "" # displays most recent entry if editing existing story
    if s_rowid != '0':
        story_d = fetch('story_base', "rowid == ?", 'title, last_entry', (s_rowid,))
        recent = f"""
        <h1> {story_d[0][0]} </h1>
        <p> Last entry: <br> {story_d[0][1]} </p>
        """
    return render_template("edit.html", display_title = (s_rowid == '0'), recent_content = recent)

@app.route('/search/<rqst>')
def search(rqst):
    rslts = ""
    r = []
    for find in fetch("story_base", "title LIKE ?", "rowid", (f"%{rqst}%",)):
        ttl = fetch("story_base", f"rowid={find[0]}", "title")[0][0]
        athr_id = fetch("story_base", f"rowid={find[0]}", "author")[0][0]
        athr = fetch("user_base", f"rowid={athr_id}", "username")[0][0]
        rslts += f"""<a href='/story/{find[0]}'>{ttl}</a>
        <p>by
        <a href='/profile/{athr_id}'>{athr}</a>
        </p>
        </br>
        """
        r += [ttl]
    for find in fetch("story_base", "content LIKE ?", "rowid", (f"%{rqst}%",)):
        ttl = fetch("story_base", f"rowid={find[0]}", "title")[0][0]
        athr_id = fetch("story_base", f"rowid={find[0]}", "author")[0][0]
        athr = fetch("user_base", f"rowid={athr_id}", "username")[0][0]
        if ttl not in r:
            rslts += f"""<a href='/story/{find[0]}'>{ttl}</a>
            <p>by
            <a href='/profile/{athr_id}'>{athr}</a>
            </p>
            </br>
            """
    if len(rslts) < 1:
        rslts = "<p> No such stories found. </p>"
    return render_template("search.html", query = rqst, results = rslts)


# HELPER FUNCTIONS
def fetch(table, criteria, data, params = ()):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    query = f"SELECT {data} FROM {table} WHERE {criteria}"
    c.execute(query, params)
    data = c.fetchall()
    db.commit()
    db.close()
    return data

def create_user(username, password):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT username FROM user_base")
    list = [username[0] for username in c.fetchall()]
    if not username in list:
        # creates user in table
        pfp = random.choice(pfps)
        contributions = ""
        times_cont = 0
        c.execute("INSERT INTO user_base VALUES (?, ?, ?, ?, ?, ?)",(username, password, pfp, 'temp', contributions, times_cont))

        # set path
        c.execute("SELECT rowid FROM user_base WHERE username=?", (username,))
        c.execute(f"UPDATE user_base SET path = '/profile/{c.fetchall()[0][0]}' WHERE username=?", (username,))
        db.commit()
        db.close()
        return True
    db.commit()
    db.close()
    return False

def update_story(s_rowid, editor_id, title, content):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    original_cont = fetch('user_base', "rowid == ?", 'contributions', (editor_id,))[0][0] # adds story id to contirbutions ",#,#"
    new_num_cont = fetch('user_base', "rowid == ?", 'times_cont', (editor_id,))[0][0] + 1
    if s_rowid == '0': # creating new story
        c.execute("SELECT title FROM story_base")
        titles = [t[0] for t in c.fetchall()]
        if not title in titles:
            author_user = fetch("user_base", "rowid == ?", "username", (editor_id,))[0][0]
            path = f"/story/{fetch('story_base', True, 'COUNT(*)')[0][0] + 1}"
            c.execute("INSERT INTO story_base (path, title, content, last_entry, editors, author) VALUES (?, ?, ?, ?, ?, ?)", (path, title, content, content, '', editor_id))
            new_cont = str(fetch('story_base', True, 'COUNT(*)')[0][0] + 1)
            cc = original_cont + "," + new_cont
            c.execute("UPDATE user_base SET contributions = ? WHERE rowid == ?", (cc, editor_id))
            c.execute("UPDATE user_base SET times_cont = ? WHERE rowid == ?", (new_num_cont, editor_id))
            db.commit()
            db.close()
            return True
        return False # title already exists, prompt user to change title

    else: # updating existing story
        cc = original_cont + "," + s_rowid
        c.execute("UPDATE user_base SET contributions = ? WHERE rowid == ?", (cc, editor_id))
        c.execute("UPDATE user_base SET times_cont = ? WHERE rowid == ?", (new_num_cont, editor_id))
        original_content = fetch('story_base', 'rowid == ?', 'content', (s_rowid,))[0][0]
        cnt = original_content + "<br><br>" + content
        c.execute("UPDATE story_base SET content = ? WHERE rowid == ?", (cnt, s_rowid))
        c.execute("UPDATE story_base SET last_entry = ? WHERE rowid == ?", (content, s_rowid))
        original_editors = fetch('story_base', 'rowid == ?', 'editors', (s_rowid,))[0][0]
        new_editor = fetch('user_base', 'rowid == ?', 'username', (editor_id,))[0][0]
        eds = original_editors + "," + new_editor
        c.execute("UPDATE story_base SET editors = ? WHERE rowid == ?", (eds, s_rowid))
        db.commit()
        db.close()
        return True

def update_pfp(pfp, u_rowid):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("UPDATE user_base SET pfp = ? WHERE ROWID=?", (pfp, u_rowid))
    db.commit()
    db.close()

def update_password(pw, username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("UPDATE user_base SET password = ? WHERE username=?", (pw, username))
    db.commit()
    db.close()

# Flask
if __name__=='__main__':
    app.debug = True
    app.run()
