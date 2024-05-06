import json

from flask_restful import Resource, request
from package.model import conn


class Doctors(Resource):
    """Contains API to interact with doctors"""

    def __init__(self):
        with open('config.json') as config_file:
            config = json.load(config_file)
        self.default_limit = config['pagination']['default_limit']
        self.max_limit = config['pagination']['max_limit']

    def get(self):
        """Retrieve all doctors"""

        # Get pagination parameters from query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', self.default_limit))

        # Validate and clamp limit to max_limit
        limit = min(limit, self.max_limit)

        # Calculate offset based on pagination parameters
        offset = (page - 1) * limit

        doctors = conn.execute("SELECT * FROM doctor ORDER BY doc_date DESC LIMIT ? OFFSET ?",
                               (limit, offset)).fetchall()

        return {'status': 'success', 'doctors': doctors}

    def post(self):
        """Add a new doctor"""

        doctor_input = request.get_json(force=True)
        doc_first_name = doctor_input['doc_first_name']
        doc_last_name = doctor_input['doc_last_name']
        doc_ph_no = doctor_input['doc_ph_no']
        doc_address = doctor_input['doc_address']
        doctor_input['doc_id'] = conn.execute('''INSERT INTO doctor(doc_first_name,doc_last_name,doc_ph_no,doc_address)
            VALUES(?,?,?,?)''', (doc_first_name, doc_last_name, doc_ph_no, doc_address)).lastrowid
        conn.commit()
        return {'status': 'success', 'message': 'Doctor Record created successfully'}, 201

    def get_with_filters(self, filter_criteria):
        """Retrieve doctor based on filter criteria"""

        page = int(filter_criteria.pop('page', 1))
        limit = int(filter_criteria.pop('limit', self.default_limit))

        limit = min(limit, self.max_limit)

        offset = (page - 1) * limit

        query = "SELECT * FROM doctor WHERE "
        query += " AND ".join(f"{key} = ?" for key in filter_criteria.keys())
        query += " LIMIT ? OFFSET ?"

        query_values = list(filter_criteria.values()) + [limit, offset]

        doctors = conn.execute(query, tuple(query_values)).fetchall()

        return {'status': 'success', 'doctors': doctors}


class Doctor(Resource):
    """Contains API for a single doctor"""

    def get(self, id):
        """Retrieve a doctor by ID"""

        doctor = conn.execute("SELECT * FROM doctor WHERE doc_id=?", (id,)).fetchall()
        departments = conn.execute('''
                    SELECT department.*
                    FROM department
                    JOIN department_doctor ON department.department_id = department_doctor.department_id
                    WHERE department_doctor.doc_id = ?
                ''', (id,)).fetchall()

        return {'status': 'success', 'doctor': doctor, 'departments': departments}

    def delete(self, id):
        """Delete the doctor by its id"""

        doctor = conn.execute("SELECT * FROM doctor WHERE doc_id=?", (id,)).fetchall()

        if not doctor:
            return {'status': 'success', 'message': 'Doctor Record Not Found'}

        conn.execute("DELETE FROM doctor WHERE doc_id=?", (id,))
        conn.commit()
        return {'status': 'success', 'message': 'Doctor Record deleted successfully'}

    def put(self, id):
        """Update the doctor by its id"""

        doctor_input = request.get_json(force=True)
        doc_first_name = doctor_input.get('doc_first_name')
        doc_last_name = doctor_input.get('doc_last_name')
        doc_ph_no = doctor_input.get('doc_ph_no')
        doc_address = doctor_input.get('doc_address')
        conn.execute(
            "UPDATE doctor SET doc_first_name=?,doc_last_name=?,doc_ph_no=?,doc_address=? WHERE doc_id=?",
            (doc_first_name, doc_last_name, doc_ph_no, doc_address, id))
        conn.commit()
        return {'status': 'success', 'message': 'Doctor Record updated successfully'}
