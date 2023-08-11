# Import the dependencies.

import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask , jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
           

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year = dt.date(2017,8,23) - dt.timedelta(days= 365)

    prcp_scores = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= last_year, measurement.prcp != None).\
    order_by(measurement.date).all()

    return jsonify(dict(prcp_scores))


@app.route("/api/v1.0/stations")

def stations():
    result_station = session.query(station.station).all()
    list_station = list(np.ravel(result_station))
    return jsonify (list_station)



@app.route("/api/v1.0/tobs")

def tobs():
    
    result_tobs = session.query(measurement.tobs).\
            filter(measurement.station == 'USC00519281' ).\
            filter(measurement.date >= '2017,8,23').all()
    list_tobs = list(np.ravel(result_tobs))
    return jsonify (list_tobs)
    


def start_temp(start_date):
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

@app.route ("/api/v1.0/<start>")

def start_date(start):
    calc_start_temp = start_temp(start)
    t_temp= list(np.ravel(calc_start_temp))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dict = {'TMIN': t_min, 'TMAX': t_max, 'TAVG': t_avg}

    return jsonify(t_dict)
            
def calc_temps(start_date, end_date):
    return session.query(func.min(measurement.tobs), \
                         func.avg(measurement.tobs), \
                         func.max(measurement.tobs)).\
                         filter(measurement.date >= start_date).\
                         filter(measurement.date <= end_date).all()


@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start, end):
    
    calc_temp = calc_temps(start, end)
    ta_temp= list(np.ravel(calc_temp))

    tmin = ta_temp[0]
    tmax = ta_temp[2]
    tavg = ta_temp[1]
    temp_dict = { 'TMIN': tmin, 'TMAX': tmax, 'TAVG': tavg}

    return jsonify(temp_dict)


if __name__ == "__main__":
   app.run(debug=False)

