import json
from flask_restful import Resource, request
from package.model import conn


class Departments(Resource):
    """Contains API to interact with departments"""

    def __init__(self):
        with open('config.json') as config_file:
            config = json.load(config_file)
        self.default_limit = config['pagination']['default_limit']
        self.max_limit = config['pagination']['max_limit']

    def get(self):
        """Retrieve all departments with pagination"""

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', self.default_limit))

        # Validate and clamp limit to max_limit
        limit = min(limit, self.max_limit)

        # Calculate offset based on pagination parameters
        offset = (page - 1) * limit

        departments = conn.execute("""
            SELECT *
            FROM department
            ORDER BY department_id
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

        return {'status': 'success', 'departments': departments}

    def post(self):
        """Add a new department"""

        try:
            department = request.get_json(force=True)
            department_name = department['department_name']

            conn.execute("""
                INSERT INTO department (department_name)
                VALUES (?)
            """, (department_name,))
            conn.commit()

            return {'status': 'success', 'message': 'Department added successfully'}, 201
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500

    def get_with_filters(self, filter_criteria):
        """Retrieve departments based on filter criteria"""

        page = int(filter_criteria.pop('page', 1))
        limit = int(filter_criteria.pop('limit', self.default_limit))
        limit = min(limit, self.max_limit)

        offset = (page - 1) * limit

        query = "SELECT * FROM department WHERE "
        query += " AND ".join(f"{key} = ?" for key in filter_criteria.keys())
        query += " LIMIT ? OFFSET ?"

        query_values = list(filter_criteria.values()) + [limit, offset]

        departments = conn.execute(query, tuple(query_values)).fetchall()

        return {'status': 'success', 'departments': departments}


class Department(Resource):
    """Contains API for a single department"""

    def get(self, department_id):
        """Retrieve details of a specific department"""

        doctors = conn.execute("""
            SELECT doctor.*
            FROM doctor
            JOIN department_doctor ON doctor.doc_id = department_doctor.doc_id
            WHERE department_doctor.department_id = ?
        """, (department_id,)).fetchall()

        department = conn.execute("""
            SELECT *
            FROM department
            WHERE department_id=?
        """, (department_id,)).fetchone()

        return {'status': 'success', 'department': department, 'doctors': doctors}

    def delete(self, department_id):
        """Delete a department by its ID"""

        try:
            conn.execute("DELETE FROM department WHERE department_id=?", (department_id,))
            conn.commit()
            return {'status': 'success', 'message': 'Department deleted successfully'}
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500

    def put(self, department_id):
        """Update a department by its ID"""

        try:
            department = request.get_json(force=True)
            department_name = department['department_name']

            conn.execute("""
                UPDATE department
                SET department_name=?
                WHERE department_id=?
            """, (department_name, department_id))
            conn.commit()

            return {'status': 'success', 'message': 'Department updated successfully'}
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500

    def post(self, department_id):
        """Assign doctors to a department"""

        try:
            data = request.get_json(force=True)
            doctor_ids = data.get('doctor_ids', [])

            if not doctor_ids:
                return {'status': 'error', 'message': 'No doctors specified for assignment'}, 400

            for doctor_id in doctor_ids:
                conn.execute("INSERT INTO department_doctor(department_id, doc_id) VALUES(?, ?)",
                             (department_id, doctor_id))

            conn.commit()
            return {'status': 'success', 'message': 'Doctors assigned to department successfully'}
        except Exception as e:
            conn.rollback()
            return {'status': 'error', 'message': str(e)}, 500
