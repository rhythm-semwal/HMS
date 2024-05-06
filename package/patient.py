import json

from flask_restful import Resource, request
from package.model import conn


class Patients(Resource):
    """Contains all the APIs for interacting with specific patients"""

    def __init__(self):
        with open('config.json') as config_file:
            config = json.load(config_file)
        self.default_limit = config['pagination']['default_limit']
        self.max_limit = config['pagination']['max_limit']

    def get(self):
        """Retrieve paginated list of patients"""

        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', self.default_limit))
            limit = min(limit, self.max_limit)
            offset = (page - 1) * limit

            query = "SELECT * FROM patient ORDER BY pat_date DESC LIMIT ? OFFSET ?"
            patients = conn.execute(query, (limit, offset)).fetchall()

            return {'status': 'success', 'patients': patients}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def post(self):
        """API to add a new patient to the database"""

        try:
            # Parse JSON data from request
            patient_input = request.get_json(force=True)

            # Extract required fields from JSON data
            pat_first_name = patient_input.get('pat_first_name')
            pat_last_name = patient_input.get('pat_last_name')
            pat_insurance_no = patient_input.get('pat_insurance_no')
            pat_ph_no = patient_input.get('pat_ph_no')
            pat_address = patient_input.get('pat_address')

            # Validate required fields
            if not all([pat_first_name, pat_last_name, pat_insurance_no, pat_ph_no, pat_address]):
                return {'status': 'error', 'message': 'Missing required fields'}, 400

            # Insert new patient record into the database
            query = """
                INSERT INTO patient (pat_first_name, pat_last_name, pat_insurance_no, pat_ph_no, pat_address)
                VALUES (:first_name, :last_name, :insurance_no, :ph_no, :address)
            """
            result = conn.execute(query, {
                'first_name': pat_first_name,
                'last_name': pat_last_name,
                'insurance_no': pat_insurance_no,
                'ph_no': pat_ph_no,
                'address': pat_address
            })

            # Get the ID of the newly inserted patient record
            pat_id = result.lastrowid

            # Commit the transaction
            conn.commit()

            return {'status': 'success', 'message': 'Patient Record created successfully', 'pat_id': pat_id}, 201
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def get_with_filters(self, filter_criteria):
        """Retrieve patients based on filter criteria with pagination"""

        try:
            page = int(filter_criteria.pop('page', 1))
            limit = int(filter_criteria.pop('limit', self.default_limit))
            limit = min(limit, self.max_limit)
            offset = (page - 1) * limit

            query = "SELECT * FROM patient WHERE "
            query += " AND ".join(f"{key} = ?" for key in filter_criteria.keys())
            query += " ORDER BY pat_date DESC LIMIT ? OFFSET ?"

            query_values = list(filter_criteria.values()) + [limit, offset]
            patients = conn.execute(query, tuple(query_values)).fetchall()

            return {'status': 'success', 'patients': patients}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500


class Patient(Resource):
    """Contains all APIs for a single patient entity"""

    def get(self, id):
        """Retrieve details of a patient by ID"""

        try:
            patient = conn.execute("SELECT * FROM patient WHERE pat_id=?", (id,)).fetchall()
            if not patient:
                return {'status': 'error', 'message': 'Patient Record Not Found'}, 404
            return {'status': 'success', 'patient': patient}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def delete(self, id):
        """Delete a patient by ID"""

        try:
            patient = conn.execute("SELECT * FROM patient WHERE pat_id=?", (id,)).fetchall()
            if not patient:
                return {'status': 'error', 'message': 'Patient Record Not Found'}, 404
            conn.execute("DELETE FROM patient WHERE pat_id=?", (id,))
            conn.commit()
            return {'status': 'success', 'message': 'Patient Record deleted successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def put(self, id):
        """Update a patient by ID"""

        try:
            patient_input = request.get_json(force=True)
            pat_first_name = patient_input['pat_first_name']
            pat_last_name = patient_input['pat_last_name']
            pat_insurance_no = patient_input['pat_insurance_no']
            pat_ph_no = patient_input['pat_ph_no']
            pat_address = patient_input['pat_address']

            conn.execute(
                "UPDATE patient SET pat_first_name=?,pat_last_name=?,pat_insurance_no=?,pat_ph_no=?,pat_address=? "
                "WHERE pat_id=?",
                (pat_first_name, pat_last_name, pat_insurance_no, pat_ph_no, pat_address, id))
            conn.commit()

            return {'status': 'success', 'message': 'Patient Record updated successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500
