from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np


# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# 2. Create an app
app = Flask(__name__)

# 3 define what to do when a user hists the index route
@app.route('/')
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"Precipitation API = /api/v1.0/precipitation<br/>"
        f"Stations API = /api/v1.0/stations<br/>"
        f"Tobs API = /api/v1.0/tobs<br/>"
        f"Start Date = /api/v1.0/date/start<br/>"
        f"End Date = /api/v1.0/date/start/end<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station).all()
    session.close()

    stations = [station[0] for station in results]  # Unpack the tuple
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first().station

    # Query the last year of temperature data for this station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).\
        all()
    session.close()

    tobs_list = [tobs[1] for tobs in results]  # Unpack the tuple
    return jsonify(tobs_list)

@app.route('/api/v1.0/date/<start>')
@app.route("/api/v1.0/date/<start>/<end>")
def start(start, end=None):
     # Construct a basic select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    else:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
    session.close()

    tobs_list = [tobs[1] for tobs in results]  # Unpack the tuple
    return jsonify(tobs_list)

# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)