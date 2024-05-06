from flask_restful import Resource, request
from package.model import conn


class Prescribes(Resource):
    """Contains API to interact with prescribes"""

    def get(self):
        """Retrieve all prescriptions with doctor and patient details"""

        try:
            prescribes = conn.execute("""
                SELECT pr.doc_id, d.doc_first_name, d.doc_last_name,
                       pr.pat_id, p.pat_first_name, p.pat_last_name,
                       pr.p_date, pr.app_id
                FROM prescribes pr
                INNER JOIN doctor d ON pr.doc_id = d.doc_id
                INNER JOIN patient p ON pr.pat_id = p.pat_id
            """).fetchall()

            return {'status': 'success', 'prescribes': prescribes}, 200
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def post(self):
        """Add a new prescription"""

        try:
            prescribes = request.get_json(force=True)
            doc_id = prescribes['doc_id']
            pat_id = prescribes['pat_id']
            p_date = prescribes['p_date']
            app_id = prescribes['app_id']

            conn.execute("""
                INSERT INTO prescribes (doc_id, pat_id, p_date, app_id)
                VALUES (?, ?, ?, ?)
            """, (doc_id, pat_id, p_date, app_id))

            conn.commit()
            return {'status': 'success', 'message': 'Prescription Record created successfully'}, 201
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500


class Prescribe(Resource):
    """Contains API for a single prescription"""

    def get(self, doc_id):
        """Retrieve prescription details for a specific doctor"""

        try:
            prescriptions = conn.execute("""
                SELECT pr.*, p.*
                FROM prescribes pr
                INNER JOIN patient p ON pr.pat_id = p.pat_id
                WHERE pr.doc_id = ?
            """, (doc_id,)).fetchall()

            doctor = conn.execute("""
                SELECT doc_first_name, doc_last_name
                FROM doctor
                WHERE doc_id = ?
            """, (doc_id,)).fetchone()

            doctor_name = f"{doctor['doc_first_name']} {doctor['doc_last_name']}"

            patient_details = [{
                'patient_id': prescription['pat_id'],
                'patient_first_name': prescription['pat_first_name'],
                'patient_last_name': prescription['pat_last_name'],
                'patient_insurance_no': prescription['pat_insurance_no'],
                'patient_phone_number': prescription['pat_ph_no'],
                'patient_address': prescription['pat_address']
            } for prescription in prescriptions]

            return {'status': 'success', 'doctor_name': doctor_name, 'patient_details': patient_details}, 200
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def delete(self, doc_id):
        """Delete all prescriptions associated with a specific doctor"""

        try:
            conn.execute("DELETE FROM prescribes WHERE doc_id=?", (doc_id,))
            conn.commit()
            return {'status': 'success', 'message': 'Prescriptions deleted successfully'}, 200
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500

    def put(self, doc_id):
        """Update prescription details for a specific doctor"""

        try:
            prescribes = request.get_json(force=True)
            pat_id = prescribes['pat_id']
            med_code = prescribes['med_code']
            p_date = prescribes['p_date']
            app_id = prescribes['app_id']
            dose = prescribes['dose']

            conn.execute("""
                UPDATE prescribes
                SET pat_id=?, med_code=?, p_date=?, app_id=?, dose=?
                WHERE doc_id=?
            """, (pat_id, med_code, p_date, app_id, dose, doc_id))

            conn.commit()
            return {'status': 'success', 'message': 'Prescription updated successfully'}, 200
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500
