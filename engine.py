# -*- coding: UTF-8 -*-
import os
from flask import Flask, g, render_template, request, jsonify, url_for, redirect

import settings
from  database import Arendator, Place, Contract, Contract_Place, db_session
app = Flask(__name__)

app.config['SECRET_KEY'] = settings.SECRET_KEY


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.htm'), 404

@app.route("/top/")
def top():
    return "Очень горячие новости", 200

@app.route("/catalog/films/<type_>/all")
def catalogs_all(type_):
    return f"Вы попали на страницу {type_} - все фильмы", 200


@app.route("/catalog/films/<type_>/<value>")
def catalogs(type_, value):
    return render_template('catalog.htm', type_=type_, value=value), 200

@app.route("/news/<news_time_original>/")
def news_at(news_time_original):
    g.news_title = "Вышел новый фильм"
    return render_template('news.htm', news_time=news_time_original), 200


@app.route("/places/new", methods=["GET", ])
def add_place_view():
    return render_template('new_place.htm')


@app.route("/places/new", methods=["POST", ])
def add_place():
    obj = Place(title=request.form.get('title', "Не задано"),
                square=int(request.form.get('square', 0)),
                is_office=bool('is_office' in request.form)
               )
    db_session.add(obj)
    db_session.commit()
    return redirect(url_for('places'))

@app.route("/places/")
def places():
    items = Place.query.all()
    return render_template('table.htm', fields={'#':"id",
                                                'Наименование':"title",
                                                'Площадь (м2)':"square",
                                                'Тип помещения':"office_title",
                                                'Число договоров':"contract_count",
                                                "Договора":'contract_dates',
                                                },
                                        title="Список арендуемых помещений",
                                        items=items)



@app.route("/arendators/")
def arendators():
    items = Arendator.query\
                           .order_by(Arendator.title.desc())\
                           .all()
    return render_template('table.htm', fields={'#':"id",
                                                'Наименование':"title",
                                                'Описание':"description"
                                                },
                                        title="Арендаторы",
                                        items=items)



@app.route("/hello/")
def test():
    return "Hello", 200

@app.route("/<page_name>/")
def main(page_name):
    g.page_name = page_name
    # Тут надо бы вставить проверку на нормальность page_name
    return render_template([page_name+'.htm', 'home.htm'])


if __name__ == "__main__":
##    #Еще один способ добавления статической дирректории
    from werkzeug.middleware.shared_data import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })
    app.run(host='0.0.0.0', port=5056, debug=True)
