# -*- coding: UTF-8 -*-
import os

from flask import Flask, g, render_template, request, jsonify, url_for, send_file, redirect, flash

import settings
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import uuid
from models import db_session, Dishes, DishType, Restoran, ReservedTable, User
import datetime

app = Flask(__name__, template_folder="templates")

app.config['SECRET_KEY'] = str(uuid.uuid4())
manager = LoginManager(app)

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(login=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('Mpage', page_name='index'))  # Измените на вашу главную страницу
        else:
            # В случае неверного логина или пароля, вы можете вернуть ошибку или перенаправить обратно на страницу входа
            return render_template('Mpage', error='Invalid username or password')
    return render_template("login.html")

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('Mpage', page_name='index'))  # Измените на вашу главную страницу

@app.route("/registration/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        # Дополнительная логика проверки, например, проверка уникальности имени пользователя и т.д.
        new_user = User(login=username, password=password, mail=email)
        db_session.add(new_user)
        db_session.commit()
        login_user(new_user)
        return redirect(url_for('Mpage'))  # Исправлено
    return render_template("registration.htm")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('PageSecond.html'), 404


@app.route('/menu')
def menu():
    return render_template("PageSecond.html", page_name = "Menu" )

@app.route('/Preview')
def Preview():
    return render_template("Preview.html", page_name = "Preview" )

@app.route("/PageOrder/", methods=['POST'])
@login_required
def Reserv_form():
    fio = request.form.get('fio')
    bookdate = request.form.get('bookdate')
    numtable = request.form.get('numtable')
    orderedfood = request.form.get('orderedfood')
    phonnumb = request.form.get('phonnumb')
    numppl = request.form.get('numppl')

    try:
        bookdate = bookdate.strip()
        bookdate = datetime.datetime.strptime(bookdate, '%Y-%m-%d %H:%M')
    except ValueError as e:
        flash("Invalid date format", "error")
        return redirect(url_for('main', page_name="PageOrder"))

    NewOrder = ReservedTable(
        fio=fio,
        bookdate=bookdate,
        numtable=numtable,
        orderedfood=orderedfood,
        phonnumb=phonnumb,
        numppl=numppl,
    )
    db_session.add(NewOrder)
    db_session.flush()
    order_id = NewOrder.id
    current_user.order_id = order_id
    db_session.commit()

    flash("Your reservation was successful!", "success")
    return redirect(url_for('main', page_name="PageOrder"))



@app.route("/PageSecond/")
def Mpage():
    dish = db_session.query(DishType).all()
    restorant = db_session.query(Restoran).all()

    DishType_id = request.args.get('dish_id', None , type = int)
    if DishType_id is not None:
        menudata = db_session.query(Dishes).filter(Dishes.dish_id == DishType_id).all()
    else:
        menudata = db_session.query(Dishes).all()
    return render_template("PageSecond.html",page_name = "Меню", button = dish, restbd = restorant, dishmenu = menudata)

@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route("/<page_name>/")
def main(page_name):
    return render_template(page_name+'.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5057, debug=True)

