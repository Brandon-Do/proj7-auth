import os
from flask import Flask, redirect, url_for, request, render_template
import flask
from pymongo import MongoClient
import acp_times
import arrow

app = Flask(__name__)

client = MongoClient("db", 27017)
db = client.tododb

@app.route('/')
def todo():
    return render_template('calc.html')

@app.route('/clear',methods=['POST'])
def clear():
    db.tododb.delete_many({})
    return redirect(url_for('todo'))

@app.route('/save', methods=['POST'])
def new():

    data = {
        "opens" : request.form.getlist("open"),
        "close" : request.form.getlist("close"),
        "km" : request.form.getlist("km"),
    }

    for key in data.keys():
        data[key] = list(map(str, data[key]))
    app.logger.debug(data)

    for i in range(len(data["km"])):
        result = {"open":data["opens"][i], "close":data["close"][i], "km":data["km"][i]}
        if result["km"] != "":
            db.tododb.insert_one(result)


    return redirect(url_for('todo'))

@app.route('/show', methods=['POST'])
def show():
    data = db.tododb.find()
    results = []
    for d in data:
        result = {"km":d["km"], "open":d["open"], "close":d["close"]}
        results.append(result)


    if results == []:
        app.logger.debug("No data entered to display")
        return render_template('calc.html')
    return render_template('todo.html', items=results)


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times", methods=['GET', 'POST'])
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """

    app.logger.debug("Got a JSON request")

    km = request.args.get('km', 999, type=float)
    distance = request.args.get('distance', 200, type=int)
    begin_time = request.args.get('begin_time', type=str)
    begin_date = request.args.get('begin_date', type=str)

    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))

    print("request.args: {}".format(request.args))
    print("dates:", begin_time, begin_date)

    print(begin_date + " " + begin_time)
    start_arrow = arrow.get(begin_date + " " + begin_time, "YYYY-MM-DD HH:mm")
    print('start', start_arrow.isoformat())

    open_time = acp_times.open_time(km, distance, start_arrow)
    close_time = acp_times.close_time(km, distance, start_arrow)
    result = {"open": open_time, "close": close_time}

    return flask.jsonify(result=result)


#############

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
