from flask import Flask , redirect, Response, render_template, url_for, session , request, flash 
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()  # 
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# mysql config 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = "dairy_app"

mysql = MySQL(app)


#sign-up page 


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # check empty input
        if not username or not password:
            flash("Please enter valid input", "error")
            return redirect(url_for('signup'))

        conn = mysql.connection
        cursor = conn.cursor()

        # check if user already exists
        cursor.execute("SELECT * FROM user_pass WHERE username = %s", (username,))
        check_user = cursor.fetchone()

        if check_user:
            flash("Username already exists", "error")
            return redirect(url_for('signup'))

        else:
            hashed_password = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO user_pass (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()

            #  auto login after signup
            session["user"] = username

            return redirect(url_for('apppage'))

    return render_template('signup.html')


#login form page
@app.route('/login', methods = ["GET","POST"])
def login ():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # check every input box are filled or not 
        if not username or not password:
            flash("Please enter valid input", "loginerror")
            return redirect(url_for('login'))

        conn = mysql.connection
        cursor = conn.cursor()

        # check if user already exists
        cursor.execute("SELECT password FROM user_pass WHERE username=%s",(username,))
        check_user = cursor.fetchone()

        # if username not in database show signup error
        if not check_user:
            flash("please signup","signuperror")
            return redirect(url_for('login'))

        else:
            db_password = check_user [0]     # store password

            # check password 
            if check_password_hash(db_password, password):
                session["user"] = username
                return redirect(url_for('apppage'))
            
            else:
                flash("Wrong password", "passworderror")
                return redirect(url_for('login'))
        
    return render_template('login.html')


#home page 
@app.route('/apppage', methods=["GET", "POST"])
def apppage():
    if 'user' not in session:
        return redirect(url_for('login'))
    

    return render_template('homepage.html')


#logout to frist page
@app.route('/logout')
def logout():
    session.pop("user",None)

    return redirect(url_for('login'))

@app.route('/subscription', methods = ["GET","POST"])
def subscription ():
    return render_template('subscription.html')

# command to run
if __name__ == "__main__":
    app.run(debug=True)



     