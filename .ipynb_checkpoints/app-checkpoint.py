#################################################
# Import the dependencies.
#################################################

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text, inspect
from flask import Flask, jsonify

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


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Create the Homepage with all available routes

@app.route('/')
def home():
    return(
        f"Data on precipitation and temperatures in Hawaii.<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"Please note 'start_date' and 'end_date' in the above paths must be between 2016-08-23 and 2017-08-23 inclusive<br/>"
    )

#################################################

# Precipitation route

@app.route("/api/v1.0/precipitation")

# Define parameters for precipitation data

def precipitation():

#Open session
    session = Session(engine)

    
    last_date = dt.date(2017,8, 23)
    start_date =  last_date - dt.timedelta(days = 365)
    last_year_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).all()


# Create a dictionary with date as the key and prcp as the value

    precipitation_data = {}
    for date, prcp in last_year_data:
        precipitation_data[date] = prcp

    # Close the session
    session.close()
    
    return jsonify(precipitation_data)

#################################################

# Stations API route- Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():

#Open session
    session = Session(engine)
    
    all_stations = session.query(station.station).all()
    list_stations = list(np.ravel(all_stations))

# Close the session
    session.close()
    
    return jsonify(list_stations)

#################################################

# Temperature Observations route- query dates and observations of most active station of previous year

@app.route("/api/v1.0/tobs")
def tobs():

    #Open session
    session = Session(engine)
    
    last_date = dt.date(2017,8, 23)
    first_date =  last_date - dt.timedelta(days = 365)
    most_active_station = session.query(measurement.station).group_by(measurement.station).order_by(func.count().desc()).first()[0]
    previous_year_obs = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).filter(measurement.date >= first_date).all()
    temperature_data = [{date: tobs} for date, tobs in previous_year_obs]

    # Close the session
    session.close()
    
    # Convert to JSON list
    return jsonify(temperature_data)

#################################################

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):

# Convert the input date to a datetime object
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    
#Open session
    session = Session(engine)

    stats_start = session.query(func.min(measurement.tobs).label('min'),\
                                func.avg(measurement.tobs).label('avg'),\
                                func.max(measurement.tobs).label('max')).\
    filter(measurement.date >= start_date).group_by(measurement.date).all()
    
   
    start_dict = []
    
    for row in stats_start:
        dictionary = {
            'min': row.min,
            'avg': row.avg,
            'max': row.max
            }
        start_dict.append(dictionary)
    

    # Close the session
    session.close()

    # Show a list
    return jsonify(start_dict)


#################################################

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive. 

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date, end_date):

# Convert the input dates to datetime objects
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()

#Open session
    session = Session(engine)
    
    stats_startend = session.query(func.min(measurement.tobs).label('min'),\
                                func.avg(measurement.tobs).label('avg'),\
                                func.max(measurement.tobs).label('max')).\
    filter(measurement.date >= start_date).filter(measurement.date <= end_date).group_by(measurement.date).all()
    
    startend_dict = []
    
    for row in stats_startend:
        dictionary = {
            'min': row.min,
            'avg': row.avg,
            'max': row.max
            }
        startend_dict.append(dictionary)
    
    # Close the session
    session.close()
    
    # Show a list
    return jsonify(startend_dict)






if __name__ == '__main__':
    app.run(debug=True)