from flask import Flask, g, render_template, request, flash, redirect, url_for, session, abort
import os
import sqlite3
from data import Data

app = Flask(__name__)
app.config.from_object(__name__)


DATABASE = "/tmp/films.db"
app.secret_key = "A0Zr98j/3yX R~XHH!jmN]LWX/,?RT"
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'films.db')))


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/')
def hello_world():
    return render_template('layout.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' not in session.keys():
        if request.method == 'POST':
            db = get_db()
            data = Data(db)
            ans = data.check_login(request.form['username'], request.form['password'])
            if ans:
                session['logged_in'] = True
                session['current_user'] = ans
                return redirect(url_for('films'))
            else:
                flash("NO SUCH USER. TRY AGAIN OR REGISTER NEW USER")
        return render_template('login.html')
    flash("YOU`RE LOGGED IN. LOG OUT IF YOU WANNA CHANGE PROFILE")
    return redirect(url_for('films'))


@app.route('/logout')
def logout():
    if 'logged_in' in session.keys():
        session.pop('logged_in', None)
        session.pop('current_user', None)
        flash('YOU`VE LOGGED OUT. LOG IN AGAIN')
        return redirect(url_for('login'))
    else:
        flash("YOU CAN'T LOG OUT, LOG IN FIRST")
        return redirect(url_for('login'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if 'logged_in' not in session.keys():
        if request.method == 'POST':
            db = get_db()
            data = Data(db)
            if request.form['password'] == request.form['password2']:
                res = data.add_user(request.form['username'], request.form['password'])
            else:
                flash("PASSWORDS ARE DIFFERENT, TRY AGAIN")
                return redirect(url_for("registration"))
            if res:
                flash('REGISTRATION COMPLETED')
                return redirect(url_for('login'))
            else:
                flash("THIS LOGIN IS ALREADY TAKEN, TRY ANOTHER")
        return render_template('registration.html')
    flash("YOU`RE LOGGED IN ALREADY. LOGOUT IF YOU WANNA REGISTER ANOTHER PROFILE")
    return redirect(url_for('films'))


@app.route('/films')
def films():
    if 'logged_in' in session.keys():
        db = get_db()
        data = Data(db)
        return render_template("films.html", films=data.get_rows())
    else:
        flash("LOGIN FIRST")
        return redirect(url_for('login'))


@app.route('/films/<film_id>')
def film(film_id):
    if 'logged_in' in session.keys():
        db = get_db()
        data = Data(db)
        inf = data.get_film(film_id)
        inf2 = data.get_film_add_info(film_id)
        flag_plan = data.check_if_planned(session['current_user'], film_id)
        flag_watch = data.check_if_watched(session['current_user'], film_id)
        rate = 0
        if not flag_watch:
            rate = data.get_rating(session['current_user'], film_id)
        pict = film_id + '.jpg'
        if inf:
            return render_template("film.html", info=inf, add_inf=inf2, pict=pict, flag_p=flag_plan, flag_w=flag_watch, your_rating=rate)
        return abort(404)
    else:
        flash("LOGIN FIRST")
        return redirect(url_for('login'))


@app.route('/add_planned/<title_id>', methods=['POST'])
def add_planned(title_id):
    flash("ADDED TO PLANNED")
    db = get_db()
    data = Data(db)
    planned = data.get_planned(session['current_user'])
    planned += title_id + '\n'
    data.set_planned(session['current_user'], planned)
    return redirect(url_for('film', film_id=title_id))


@app.route('/delete_planned/<title_id>', methods=['POST'])
def delete_planned(title_id):
    flash("DELETED FROM PLANNED")
    db = get_db()
    data = Data(db)
    planned = data.get_planned(session['current_user'])
    planned = data.delete_planned(planned, title_id)
    data.set_planned(session['current_user'], planned)
    return redirect(url_for('film', film_id=title_id))


@app.route('/add_watched/<title_id>', methods=['POST'])
def add_watched(title_id):
    if request.form['rate'].isdigit() and 10 >= int(request.form['rate']) >= 1:
        flash("ADDED TO WATCHED")
        db = get_db()
        data = Data(db)
        watched = data.get_watched(session['current_user'])
        watched += title_id + ' ' + request.form['rate'] + '\n'
        planned = data.get_planned(session['current_user'])
        planned = data.delete_planned(planned, title_id)
        data.set_planned(session['current_user'], planned)
        data.set_watched(session['current_user'], watched)
    else:
        flash("RATING MUST BE INTEGER FROM 1 TO 10")
    return redirect(url_for('film', film_id=title_id))


@app.route('/my_profile')
def profile():
    if 'logged_in' in session.keys():
        db = get_db()
        data = Data(db)
        watched = data.get_watched(session['current_user'])
        watched_list = watched.split('\n')
        watched_rating = data.get_rating_watched(watched_list)
        watched_list = data.get_title_watched(watched_list)
        for i in range(len(watched_rating)):
            if watched_rating[i]:
                watched_list[i] = (watched_list[i], "Your mark is " + watched_rating[i])
        planned = data.get_planned(session['current_user'])
        planned_list = planned.split('\n')
        planned_list = data.get_title(planned_list)
        return render_template('profile.html', watched_list=watched_list, planned_list=planned_list)
    flash("LOGIN FIRST")
    return redirect(url_for('login'))


@app.errorhandler(405)
@app.errorhandler(404)
def error(error):
    flash('error')
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
