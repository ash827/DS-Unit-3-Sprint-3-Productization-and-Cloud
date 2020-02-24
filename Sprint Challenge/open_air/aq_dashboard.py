""" Main application and routing logic for aq_dashboard """
import openaq
import pandas as pd
import datetime
from flask import Flask, request, render_template
from .models import *
from .function import *


#instantiate an API object
open_api = openaq.OpenAQ() 

def create_app():
    """create + config Flask app obj"""
    app = Flask(__name__)

    #configure the app object 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openaq.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        message = ''
        rec_10 = Record.query.filter(Record.value >= 10).all()
        return render_template('homepage.html', message=message, rec_10=rec_10)
    
    def create_DB_records(DB):
        """Pull Los Angeles data from OpenAq & create db records"""
    for index, row in DB.iterrows():
        rec = Record(datetime=row['date.utc'], value=row['value'])
        DB.session.add(rec)
        DB.session.commit()

    @app.route('/refresh')
    def refresh():
        """Pull fresh data from Open AQ and replace existing data."""
        DB.drop_all()
        DB.create_all()
        db_measure = open_api.measurements(city='Los Angeles', parameter='pm25', df=True)
        db_measure['date.utc'] = db_measure['date.utc'].astype(str)
        create_DB_records(db_measure)
        DB.session.commit()
        message = 'Data refreshed on: ' + str(datetime.datetime.now())
        rec_10 = Record.query.filter(Record.value >= 10).all()
        return render_template('homepage.html', message=message, rec_10=rec_10)

    @app.route('/resetDB')
    def resetDB():
        DB.drop_all()
        DB.create_all()
        message = 'DB emptied!'
        return render_template('homepage.html', message=message)

    return app
