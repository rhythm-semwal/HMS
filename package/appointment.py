from flask_restful import Resource, request
from package.model import conn


class Appointments(Resource):
    """Contains API to interact with appointments"""

    def get(self):
        """Retrieve all appointments"""
        try:

            appointments = conn.execute("""
                SELECT a.*, p.*, d.*
                FROM appointment a
                LEFT JOIN patient p ON a.pat_id = p.pat_id
                LEFT JOIN doctor d ON a.doc_id = d.doc_id
                ORDER BY a.appointment_date DESC
            """).fetchall()

            return {'status': 'success', 'appointments': appointments}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def post(self):
        """Add a new appointment by associating patient and doctor with appointment date"""

        try:
            appointment = request.get_json(force=True)

            pat_id = appointment['pat_id']
            doc_id = appointment['doc_id']
            appointment_date = appointment['appointment_date']

            # Check if patient exists
            patient = conn.execute("SELECT * FROM patient WHERE pat_id=?", (pat_id,)).fetchone()
            if not patient:
                return {'status': 'error', 'message': 'Patient not found'}, 404

            # Check if doctor exists
            doctor = conn.execute("SELECT * FROM doctor WHERE doc_id=?", (doc_id,)).fetchone()
            if not doctor:
                return {'status': 'error', 'message': 'Doctor not found'}, 404

            # Insert new appointment
            query = """
                INSERT INTO appointment (pat_id, doc_id, appointment_date)
                VALUES (:pat_id, :doc_id, :appointment_date)
            """
            conn.execute(query, {
                'pat_id': pat_id,
                'doc_id': doc_id,
                'appointment_date': appointment_date
            })
            conn.commit()

            return {'status': 'success', 'message': f"Appointment successfully booked for {appointment_date}"}, 201
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500


class Appointment(Resource):
    """Contains API to interact with a single appointment"""

    def get(self, id):
        """Retrieve details of a specific appointment by ID"""

        appointment = conn.execute("SELECT * FROM appointment WHERE app_id=?", (id,)).fetchone()

        if not appointment:
            return {'status': 'error', 'message': 'Appointment not found'}, 404

        doctor = conn.execute("""
            SELECT d.*
            FROM doctor d
            JOIN appointment a ON d.doc_id = a.doc_id
            WHERE a.app_id = ?
        """, (id,)).fetchone()

        patient = conn.execute("""
            SELECT p.*
            FROM patient p
            JOIN appointment a ON p.pat_id = a.pat_id
            WHERE a.app_id = ?
        """, (id,)).fetchone()

        return {
            'status': 'success',
            'appointment': appointment,
            'doctor': doctor,
            'patient': patient
        }

    def delete(self, id):
        """Delete the appointment by its ID"""

        conn.execute("DELETE FROM appointment WHERE app_id=?", (id,))
        conn.commit()

        return {'status': 'success', 'message': 'Appointment successfully deleted'}

    def put(self, id):
        """Update the appointment details by its ID"""

        try:
            appointment = request.get_json(force=True)

            pat_id = appointment['pat_id']
            doc_id = appointment['doc_id']
            appointment_date = appointment['appointment_date']

            conn.execute("""
                UPDATE appointment
                SET pat_id=?, doc_id=?, appointment_date=?
                WHERE app_id=?
            """, (pat_id, doc_id, appointment_date, id))
            conn.commit()

            return {'status': 'success', 'message': 'Appointment successfully updated'}
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500
