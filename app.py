#################################################
# Import/ call dependencies and Setup
#################################################
import numpy as np
import datetime as dt
import pandas as pd

from dateutil.parser import parse

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool

# Import Flask
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool, echo=True)

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    # Design Homepage with the list of available routes and instructions
    """List all available api routes."""
    return (
        f"<font style='font-family:verdana'>"
        f"<h1 style='background-color:powderblue;'>Welcome to Climate App </h1>"
        f"<p> The following routes are available in this app:<p>"
        f"<ol>"
        f"<li><a href='/api/v1.0/precipitation' target='_blank'> /api/v1.0/precipitation </a> : This route will open a <u><i>new tab</i></u> in the browser with a list of json data for all precipitation information in the database, group by date.</li><br/>"
        f"<li><a href='/api/v1.0/daily_prcp' target='_blank'> /api/v1.0/daily_prcp </a> : This route will open a <u><i>new tab</i></u> in the browser with json data for the daily precipitation.</li><br/>"
        f"<li><a href='/api/v1.0/stations' target='_blank'> /api/v1.0/stations </a> : This route will open a <u><i>new tab</i></u> in the browser with json data for all stations.</li><br/>"
        f"<li><a href='/api/v1.0/tobs' target='_blank'> /api/v1.0/tobs </a> : This route open a <u><i>new tab</i></u> in the browser with json data for the most active station <b>'USC00519281'</b> for the 365 days from the lastest date (2017-08-23) in the data set. </li><br/>"
        f"<br/>***The date range in the data set is: <b>2010-01-01 to 2017-08-23.***</b><br/><br/>"
        f"<li>Minimum, Maximum and Average of TOBs data can be generated for a specific start date.<br/>"
        f"Json data can be accessed by entering to the browser the path:<b> <font color='green'>http://127.0.0.1:5000/api/v1.0/</font>"
        f"<font color='red'>start_date</font></b>, the start_date must be in the format of YYYY-MM-DD.<br/>"
        f"For example:  <font color='green' style='font-family:verdana'><b>http://127.0.0.1:5000/api/v1.0/2010-01-31</b></font></li><br/>"
        f"<li>Minimum, Maximum and Average of TOBs data can be generated for a range of dates, i.e. between the start date and end date.<br/>"
        f"Json data can be accessed by entering to the browser the path:<b> <font color='green'>http://127.0.0.1:5000/api/v1.0/</font>"
        f"<font color='red'>start_date/end_date</font></b>, the start_date and end_date must be in the format of YYYY-MM-DD.<br/>"
        f"For example:  <font color='green' style='font-family:verdana'><b>http://127.0.0.1:5000/api/v1.0/2012-07-12/2012-12-30</b></font></li><br/>"
        f"</ol></font>"
    )


#################################################
# Check user_input date format
#################################################
def validate(input_date):
    try:
        if input_date != dt.datetime.strptime(input_date, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False

#################################################
# Route to precipitation page
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query to return all precipitations
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    # Create a dictionary from the row data, whereas date is the key and prcp as the value, group by date
    all_prcp = {}
 
    for (key, value) in results:
        all_prcp.setdefault(key,[]).append(value)

    # Close the connection when the query is done    
    session.close()

    # Return a list of all precipitations group by date.
    return jsonify(all_prcp)


#################################################
# Route to precipitation page - daily
#################################################
@app.route("/api/v1.0/daily_prcp")
def daily_prcp():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query to return all precipitations
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    # Close the connection when the query is done    
    session.close()

    # Convert list of tuples into normal list
    all_prcp2 = list(np.ravel(results))

    # Return a daily list of all precipitations 
    return jsonify(all_prcp2)


#################################################
# Route to stations page
#################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query all stations and their details
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Close the connection when the query is done    
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for id, station, name, latitude, longitude, elevation in results:
        stations_dict = {}
        stations_dict["id"] = id
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation

        all_stations.append(stations_dict)

    # Return a list of all stations with their details
    return jsonify(all_stations)


#################################################
# Route to tobs page
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Query the lastest/ recent date
    recent_date_q = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = pd.to_datetime(pd.Series(recent_date_q[0]), format="%Y/%m/%d").dt.date
    
    # Get the same date of a year ago (ie. 12 months or 365 days ago)
    one_year = recent_date - dt.timedelta(days=365)
    # Convert the object to datetime format
    a_year_range = one_year[0]
    a_year_range

    # Query tobs for the last 12 months/365 days 
    tobs_q = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= a_year_range).\
                filter(Measurement.station == 'USC00519281').\
                order_by(Measurement.date).all()

    # Close the connection when the query is done    
    session.close()

    # Convert list of tuples into dictionary
    tobs = dict(tobs_q)

    # Return a list of tobs in 365 days from the latest date in the data set
    return jsonify(tobs)


#################################################
# Route to tobs page with a specified start date
#################################################
@app.route("/api/v1.0/<sdate>")
def tobs_one_date(sdate):

    # Validate the user input's date
    if validate(sdate) == True:

        # Create a session (link) from Python to the DB
        session = Session(engine)

        # Get all dates in the dataset and convert to list
        dataset_date_q = session.query(Measurement.date).all()
        all_dates = list(np.ravel(dataset_date_q))

        # Check whether the user_input date is in the dataset
        if sdate in all_dates:
            # Query tobs for a specified date
            start_date = session.query(Measurement.date, Measurement.station,func.min(Measurement.tobs),func.avg(Measurement.tobs), 
                        func.max(Measurement.tobs)).filter(Measurement.date >= sdate).group_by(Measurement.date).order_by(Measurement.date).order_by(Measurement.date).all()

            # Close the connection when the query is done    
            session.close()

            start_date_list = []
            for date, station, min, max, ave in start_date:
                average_dict = {}
                average_dict["date"] = date
                average_dict["station"] = station
                average_dict["min"] = min
                average_dict["max"] = max
                average_dict["average"] = ave

                start_date_list.append(average_dict)

            # Return a list of tobs for a specified start date
            return jsonify(start_date_list)

            # Exception handling:
            # If the user's input_date is not in the dataset date, alert user with error message and send back to previous page
        else:
            return (f"<script type='text/javascript'>alert('There is no {sdate} in the database. Click OK to go back to the previous page.');history.back();</script> ")
    
    # Exception handling:
    # If the user's input_date format is not yyyy-mm-dd
    else:
        return (f"<script type='text/javascript'>alert('Invalid date had been entered. Please try again.\\nThe format should be yyyy-mm-dd');history.back();</script> ")


#################################################
# Route to tobs page with the specified start date & end date
#################################################
@app.route("/api/v1.0/<sdate>/<edate>")
def tobs_range_date(sdate, edate):

    # Validate the user input's date
    if (validate(sdate) == True) and (validate(edate) == True):

        # Create a session (link) from Python to the DB
        session = Session(engine)

        # Get all dates in the dataset and convert to list
        dataset_date_q = session.query(Measurement.date).all()
        all_dates = list(np.ravel(dataset_date_q))

        # Check whether the user input dates range is in the dataset
        if (sdate in all_dates) and (edate in all_dates):
            # Query tobs min, max, average for a specified date range
            start_date = session.query(Measurement.date, Measurement.station,func.min(Measurement.tobs),func.avg(Measurement.tobs), 
                        func.max(Measurement.tobs)).filter(Measurement.date <= edate).filter(Measurement.date >= sdate).group_by(Measurement.date).order_by(Measurement.date).all()

            # Close the connection when the query is done    
            session.close()

            tobs_date_list = []
            for date, station, min, max, ave in start_date:
                average_dict = {}
                average_dict["date"] = date
                average_dict["station"] = station
                average_dict["min"] = min
                average_dict["max"] = max
                average_dict["average"] = ave

                tobs_date_list.append(average_dict)

            # Return a list of tobs for a specified date range
            return jsonify(tobs_date_list)

        # Exception handling:
        # If the user input date range is not in the dataset date, alert user with error message and send back to previous page
        else:
            return (f"<script type='text/javascript'>alert('The provided date range: {sdate} to {edate}, is not in the database. Click OK to go back to the previous page.');history.back();</script> ")
    
    # Exception handling:
    # If the user's input_date format is not yyyy-mm-dd
    else:
        return (f"<script type='text/javascript'>alert('Invalid date had been entered. Please try again.\\nThe format should be yyyy-mm-dd/yyyy-mm-dd');history.back();</script> ")


#################################################
# Define main
#################################################
if __name__ == '__main__':
    app.run(debug=True)
