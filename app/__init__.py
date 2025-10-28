import sqlite3
from flask import Flask, render_template
from flask import session, request, redirect

# Flask
app = Flask(__name__)

# SQLite
DB_FILE = "data.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()

# HTML PAGES
# LANDING PAGE
@app.route('/')
def homepage():
    if not 'u_rowid' in session: return redirect('/login')

# USER INTERACTIONS
@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    pass

@app.route('/profile/<u_rowid>') # makes u_rowid a variable that is passed to the function
def profile(u_rowid):
    authenticate()

#STORY INTERACTIONS
@app.route('/story/<s_rowid>') # makes s_rowid a variable that is passed to the function
def story(s_rowid):
    authenticate()

@app.route('/edit/<s_rowid>') # makes s_rowid a variable that is passed to the function
def edit(s_rowid):
    authenticate()

@app.route('/author/<u_rowid>') # makes u_rowid a variable that is passed to the function
def author(u_rowid):
    authenticate()

# HELPER FUNCTIONS
def authenticate():
    if not 'u_rowid' in session: return redirect('/login')

def fetch(TABLE, ROWID, DATA, CRITERIA):
    query = "SELECT " + DATA + " FROM " + TABLE + " WHERE ROWID=" + ROWID
    for criteria in split(CRITERIA,"&"):
        query += " AND " + criteria
    c.execute(query)
    return c.fetchall()

def check_existence(TABLE, S_ROWID):
    if 'u_rowid' in session:
        if TABLE == story_base:
            c.execute("SELECT editors FROM story_base WHERE ROWID=S_ROWID")
            return str(session['u_rowid']) in split(c.fetchall(),',')
        else:
            c.execute("SELECT contributions FROM user_base WHERE ROWID=" + str(session['u_rowid']))
            return str(S_ROWID) in split(c.fetchall(), ',')
            
# SQLite
db.commit()
db.close()

# Flask
if __name__=='__main__':
    app.debug = True
    app.run(port = 8000)
