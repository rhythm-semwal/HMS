from flask import Flask, request

from flask_restful import Resource, Api
from package.patient import Patients, Patient
from package.doctor import Doctors, Doctor
from package.appointment import Appointments, Appointment
from package.department import Departments, Department
from package.prescribes import Prescribes, Prescribe

import json

with open('config.json') as data_file:
    config = json.load(data_file)

app = Flask(__name__, static_url_path='')
api = Api(app)

api.add_resource(Patients, '/patient')
api.add_resource(Patient, '/patient/<int:id>')
api.add_resource(Doctors, '/doctor')
api.add_resource(Doctor, '/doctor/<int:id>')
api.add_resource(Appointments, '/appointment')
api.add_resource(Appointment, '/appointment/<int:id>')
api.add_resource(Departments, '/department')
api.add_resource(Department, '/department/<int:department_id>')
api.add_resource(Prescribes, '/prescribe')
api.add_resource(Prescribe, '/prescribe/<int:doc_id>')


# Routes

@app.route('/')
def index():
    return {'message': 'Welcome to Hospital Management System'}


@app.route('/patient/search')
def search_patients():
    """Search patients by attributes"""
    filter_criteria = {}
    for key in request.args:
        filter_criteria[key] = request.args[key]
    return Patients().get_with_filters(filter_criteria)


@app.route('/doctor/search')
def search_doctors():
    """Search doctors by attributes"""
    filter_criteria = {}
    for key in request.args:
        filter_criteria[key] = request.args[key]
    return Doctors().get_with_filters(filter_criteria)


@app.route('/department/search')
def search_departments():
    """Search departments by attributes"""
    filter_criteria = {}
    for key in request.args:
        filter_criteria[key] = request.args[key]
    return Departments().get_with_filters(filter_criteria)


if __name__ == '__main__':
    app.run(debug=True, host=config['host'], port=config['port'])
