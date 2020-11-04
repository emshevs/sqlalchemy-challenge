import numpy as np
import datetime as dt 
from datetime import timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station 

session = Session(engine)

last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

date_chosen = dt.date(2017,4,20) - dt.timedelta(days = 365)

session.close()

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate APP. The following routes are available: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start_date in the format of yyyy-mm-dd <br/>"
        f"/api/v1.0/start_date/end_date also in the format of yyyy-mm-dd<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precipitation = []
    for result in results:
        temp = {}
        temp[result[0]] = result[1]
        precipitation.append(temp)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)
    
    results = session.query(distinct(Station.station, Station.name)).all()

    session.close()
    
    stationlist = []
    for result in results:
        stat = {}
        stat["station"] = result[0]
        stat["name"] = result[1]
        stationlist.append(stat)

    return jsonify(stationlist)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    results = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= date_chosen).all()

    session.close()

    tobs = []
    for result in results: 
        d = {}
        d["date"] = result[1]
        d["temperature"] = result[0]
        tobs.append(d)

    return jsonify(tobs)


@app.route("/api/v1.0/start_date")
def start(start):

    session = Session(engine)

    formated_date = dt.datetime.strptime(start,"%Y-%m-%d").date()

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= formated_date).all()

    session.close()

    all_temperatures = []
    for result in results:
        d = {}
        d["min"] = result[0]
        d["avg"] = result[1]
        d["max"] = result[2]
        all_temperatures.append(d)

    return jsonify(all_temperatures)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    formated_start_date = dt.datetime.strptime(start,"%Y-%m-%d").date()
    formated_end_date = dt.datetime.strptime(end,"%Y-%m-%d").date()

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= formated_start_date).\
                filter(Measurement.date <= formated_end_date).all()


    session.close()

    all_temperatures2 = []
    for result in results:
        d = {}
        d["min"] = result[0]
        d["avg"] = result[1]
        d["max"] = result[2]
        all_temperatures2.append(d)

    return jsonify(all_temperatures2)

if __name__ == "__main__":
    app.run(debug=True)