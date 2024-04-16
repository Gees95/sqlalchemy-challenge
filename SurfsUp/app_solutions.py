from flask import Flask
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base
import datetime as dt


# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


# 2. Create an app
app = Flask(__name__)

# 3 define what to do when a user hists the index route
@app.route('/')
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session()
    one_year_ago = datetime.now() - timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    session = Session()
    results = session.query(Station.station).all()
    session.close()

    stations = [station[0] for station in results]  # Unpack the tuple
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session()
    one_year_ago = datetime.now() - timedelta(days=365)

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

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session()
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        all()
    session.close()

    data = list(np.ravel(results))
    return jsonify(data)

# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)