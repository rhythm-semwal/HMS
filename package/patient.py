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

        # Get pagination parameters from query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', self.default_limit))

        # Validate and clamp limit to max_limit
        limit = min(limit, self.max_limit)

        # Calculate offset based on pagination parameters
        offset = (page - 1) * limit

        patients = conn.execute("SELECT * FROM patient ORDER BY pat_date DESC LIMIT ? OFFSET ?",
                                (limit, offset)).fetchall()

        return {'status': 'success', 'patients': patients}

    def post(self):
        """api to add the patient in the database"""

        patient_input = request.get_json(force=True)
        pat_first_name = patient_input['pat_first_name']
        pat_last_name = patient_input['pat_last_name']
        pat_insurance_no = patient_input['pat_insurance_no']
        pat_ph_no = patient_input['pat_ph_no']
        pat_address = patient_input['pat_address']
        patient_input['pat_id'] = conn.execute('''INSERT INTO patient(
        pat_first_name,pat_last_name,pat_insurance_no,pat_ph_no,pat_address)
            VALUES(?,?,?,?,?)''', (pat_first_name, pat_last_name, pat_insurance_no, pat_ph_no, pat_address)).lastrowid
        conn.commit()
        return {'status': 'success', 'message': 'Patient Record created successfully'}, 201

    def get_with_filters(self, filter_criteria):
        """Retrieve patients based on filter criteria with pagination"""

        # Extract pagination parameters from filter_criteria
        page = int(filter_criteria.pop('page', 1))
        limit = int(filter_criteria.pop('limit', self.default_limit))

        # Validate and clamp limit to max_limit
        limit = min(limit, self.max_limit)

        # Calculate offset based on pagination parameters
        offset = (page - 1) * limit

        # Construct SQL query with filter criteria and pagination
        query = "SELECT * FROM patient WHERE "
        query += " AND ".join(f"{key} = ?" for key in filter_criteria.keys())
        query += " LIMIT ? OFFSET ?"

        # Prepare query values including filter criteria, limit, and offset
        query_values = list(filter_criteria.values()) + [limit, offset]

        # Execute the query and fetch patients
        patients = conn.execute(query, tuple(query_values)).fetchall()

        return {'status': 'success', 'patients': patients}


class Patient(Resource):
    """It contains all apis doing activity with the single patient entity"""

    def get(self, id):
        """api to retrieve details of the patient by it id"""

        patient = conn.execute("SELECT * FROM patient WHERE pat_id=?", (id,)).fetchall()
        return {'status': 'success', 'patient': patient}

    def delete(self, id):
        """api to delete the patient by its id"""

        patient = conn.execute("SELECT * FROM patient WHERE pat_id=?", (id,)).fetchall()
        if not patient:
            return {'status': 'success', 'message': 'Patient Record Not Found'}

        conn.execute("DELETE FROM patient WHERE pat_id=?", (id,))
        conn.commit()

        return {'status': 'success', 'message': 'Patient Record deleted successfully'}

    def put(self, id):
        """api to update the patient by it id"""

        patient_input = request.get_json(force=True)
        pat_first_name = patient_input['pat_first_name']
        pat_last_name = patient_input['pat_last_name']
        pat_insurance_no = patient_input['pat_insurance_no']
        pat_ph_no = patient_input['pat_ph_no']
        pat_address = patient_input['pat_address']
        conn.execute(
            "UPDATE patient SET pat_first_name=?,pat_last_name=?,pat_insurance_no=?,pat_ph_no=?,pat_address=? WHERE "
            "pat_id=?",
            (pat_first_name, pat_last_name, pat_insurance_no, pat_ph_no, pat_address, id))
        conn.commit()
        return {'status': 'success', 'message': 'Patient Record updated successfully'}

