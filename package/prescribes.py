from flask_restful import Resource, request
from package.model import conn


class Prescribes(Resource):
    """Contains API to interact with prescribes"""

    def get(self):
        """Retrieve all prescribes"""

        # prescribes = conn.execute("SELECT * from prescribes").fetchall()
        prescribes = conn.execute("SELECT prescribes.doc_id, doctor.doc_first_name, doctor.doc_last_name, "
                                  "prescribes.pat_id, patient.pat_first_name, patient.pat_last_name, "
                                  "prescribes.p_date, prescribes.app_id FROM prescribes "
                                  "INNER JOIN doctor ON prescribes.doc_id = doctor.doc_id INNER JOIN patient ON "
                                  "prescribes.pat_id = patient.pat_id").fetchall()
        return prescribes

    def post(self):
        """Add a new prescription"""

        prescribes = request.get_json(force=True)
        doc_id = prescribes['doc_id']
        pat_id = prescribes['pat_id']
        p_date = prescribes['p_date']
        app_id = prescribes['app_id']
        conn.execute('''INSERT INTO prescribes(doc_id, pat_id, p_date, app_id) VALUES(?,?,?,?)''',
                     (doc_id, pat_id, p_date, app_id))
        conn.commit()
        return {'status': 'success', 'message': 'Prescription Record created successfully'}, 201


class Prescribe(Resource):
    """Contains API for a single prescribe"""

    def get(self, doc_id):
        """Retrieve prescriptions details along with doctor and patient details"""

        # Fetch prescriptions along with doctor and patient details based on doc_id
        prescriptions = conn.execute('''
            SELECT 
                p.*, 
                d.doc_first_name AS doctor_first_name, 
                d.doc_last_name AS doctor_last_name,
                pt.*
            FROM prescribes p
            JOIN doctor d ON p.doc_id = d.doc_id
            JOIN patient pt ON p.pat_id = pt.pat_id
            WHERE p.doc_id = ?
        ''', (doc_id,)).fetchall()

        doctor = conn.execute("SELECT doc_first_name, doc_last_name FROM doctor WHERE doc_id=?", (doc_id,)).fetchone()

        doctor_name = f"{doctor['doc_first_name']} {doctor['doc_last_name']}"

        patient_details = []
        for prescription in prescriptions:
            patient_detail = {
                    'patient_id': prescription['pat_id'],
                    'patient_first_name': prescription['pat_first_name'],
                    'patient_last_name': prescription['pat_last_name'],
                    'patient_insurance_no': prescription['pat_insurance_no'],
                    'patient_phone_number': prescription['pat_ph_no'],
                    'patient_address': prescription['pat_address']
                }
            patient_details.append(patient_detail)

        return {'status': 'success', 'doctor_name': doctor_name, 'patient_details': patient_details}

    def delete(self, doc_id):
        """Delete the prescribes by its doc_id"""

        conn.execute("DELETE FROM prescribes WHERE doc_id=?", (doc_id,))
        conn.commit()
        return {'msg': 'sucessfully deleted'}

    def put(self, doc_id):
        """Update the prescribes details by the doc_id"""

        prescribes = request.get_json(force=True)
        pat_id = prescribes['pat_id']
        med_code = prescribes['med_code']
        p_date = prescribes['p_date']
        app_id = prescribes['app_id']
        dose = prescribes['dose']
        conn.execute("UPDATE prescribes SET doc_id=?,pat_id=?,med_code=?,p_date=?,app_id=?,dose=?, WHERE doc_id=?",
                     (doc_id, pat_id, med_code, p_date, app_id, dose, doc_id))
        conn.commit()
        return prescribes
