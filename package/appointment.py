from flask_restful import Resource, request
from package.model import conn


class Appointments(Resource):
    """Contains API to interact with appointments"""

    def get(self):
        """Retrieve all appointments"""

        appointment = conn.execute(
            "SELECT p.*,d.*,a.* from appointment a LEFT JOIN patient p ON a.pat_id = p.pat_id LEFT JOIN doctor d ON "
            "a.doc_id = d.doc_id ORDER BY appointment_date DESC").fetchall()
        return {'status': 'success', 'appointment': appointment}

    def post(self):
        """Add a new appointment by associating patient and doctor with appointment date"""

        appointment = request.get_json(force=True)
        pat_id = appointment['pat_id']
        patient = conn.execute("SELECT * FROM patient WHERE pat_id=?", (pat_id,)).fetchall()
        if not patient:
            return {'status': 'success', 'message': 'Patient Not Found. Please Try Again'}

        doc_id = appointment['doc_id']
        doctor = conn.execute("SELECT * FROM doctor WHERE doc_id=?", (doc_id,)).fetchall()
        if not doctor:
            return {'status': 'success', 'message': 'Doctor Not Found. Please Try Again'}

        appointment_date = appointment['appointment_date']
        appointment['app_id'] = conn.execute('''INSERT INTO appointment(pat_id,doc_id,appointment_date)
            VALUES(?,?,?)''', (pat_id, doc_id, appointment_date)).lastrowid
        conn.commit()
        return {'status': 'success', 'message': f"Appointment Successfully booked for {appointment_date}"}


class Appointment(Resource):
    """This contains all api doing activity with single appointment"""

    def get(self, id):
        """Retrieve details of a specific appointment by ID"""

        # Fetch appointment details
        appointment = conn.execute("SELECT * FROM appointment WHERE app_id=?", (id,)).fetchone()

        if not appointment:
            return {'status': 'error', 'message': 'Appointment not found'}, 404

        # Fetch doctor details for the appointment
        doctor = conn.execute('''
            SELECT doctor.*
            FROM doctor
            JOIN appointment ON doctor.doc_id = appointment.doc_id
            WHERE appointment.app_id = ?
        ''', (id,)).fetchone()

        # Fetch patient details for the appointment
        patient = conn.execute('''
            SELECT patient.*
            FROM patient
            JOIN appointment ON patient.pat_id = appointment.pat_id
            WHERE appointment.app_id = ?
        ''', (id,)).fetchone()

        response = {
            'status': 'success',
            'appointment': appointment,
            'doctor': doctor,
            'patient': patient
        }

        return response

    def delete(self, id):
        """Delete teh appointment by its id"""

        conn.execute("DELETE FROM appointment WHERE app_id=?", (id,))
        conn.commit()
        return {'msg': 'successfully deleted'}

    def put(self, id):
        """Update the appointment details by the appointment id"""

        appointment = request.get_json(force=True)
        pat_id = appointment['pat_id']
        doc_id = appointment['doc_id']
        appointment_date = appointment['appointment_date']
        conn.execute("UPDATE appointment SET pat_id=?,doc_id=?,appointment_date=? WHERE app_id=?",
                     (pat_id, doc_id, appointment_date, id))
        conn.commit()
        return {'status': 'success', 'message': 'Appointment Updated successfully'}
