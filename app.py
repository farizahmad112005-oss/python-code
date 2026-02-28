from flask_cors import CORS
import mysql.connector
from flask import Flask, jsonify, request




#  Database Connection
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="admin",
            database="trackify",
            auth_plugin="mysql_native_password"
        )
        if conn.is_connected():
            print("✅ Connection Successful")
            return conn
    except mysql.connector.Error as err:
        print(f"❌ MySQL connection error: {err}")
        return None
    
    
    
    
    
def total_employes():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employe")
        total = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return total[0]  # 👈 return plain integer
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return 0
    
    
    
    
def total_pendingTasks():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("select count(*) from tasks where status = 'pending'")
        total = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return total[0]
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return 0
    
    
    
    
    
def total_inProgressTasks():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("select count(*) from tasks where status = 'in progress'")
        total = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return total[0]
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return 0
    
    

def total_CompletedTasks():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("select count(*) from tasks where status = 'completed'")
        total = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return total[0]
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return 0    
    
    
        



    
    
def total_OverdueTasks():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("select count(*) from tasks where status = 'Cancelled'")
        total = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return total[0]
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return 0
    
    
    

def recent_tasks():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
            t.task_id,
            t.title,
            t.description,
            t.status,
            t.priority,
            t.deadline,
            t.created_at,
            t.updated_at,
            -- Combine multiple employees into single fields
            GROUP_CONCAT(DISTINCT e.employe_id) as employee_ids,
            GROUP_CONCAT(DISTINCT CONCAT(e.first_name, ' ', e.last_name)) as employee_names,
            GROUP_CONCAT(DISTINCT e.email) as employee_emails,
            GROUP_CONCAT(DISTINCT e.job_title) as job_titles,
            GROUP_CONCAT(DISTINCT d.department_name) as departments,
            COUNT(DISTINCT e.employe_id) as assigned_employee_count
            FROM tasks t
            LEFT JOIN task_assignments ta ON t.task_id = ta.task_id
            LEFT JOIN employe e ON ta.employee_id = e.employe_id
            LEFT JOIN departments d ON e.department_id = d.department_id
            GROUP BY 
            t.task_id,
            t.title,
            t.description,
            t.status,
            t.priority,
            t.deadline,
            t.created_at,
            t.updated_at
            ORDER BY t.created_at DESC;
            """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return []
    
    


def Deadline_tasks():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * 
            FROM tasks
            WHERE deadline BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 DAY) 
              AND status != 'Completed'
            ORDER BY deadline ASC;
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return []
    



def create_employee(employee_data):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Extract data with defaults for optional fields
        first_name = employee_data.get('first_name')
        last_name = employee_data.get('last_name')
        email = employee_data.get('email')
        cnic = employee_data.get('cnic')
        dob = employee_data.get('dob')
        phone_number = employee_data.get('phone_number')
        job_title = employee_data.get('job_title')
        hire_date = employee_data.get('hire_date')
        status = employee_data.get('status', 'active')
        department_id = employee_data.get('department_id')
        role_id = employee_data.get('role_id')
        
        # Validate required fields
        if not all([first_name, last_name, email, cnic, role_id]):
            return False, "Missing required fields: first_name, last_name, email, cnic, role_id"
        
        # Insert query
        insert_query = """
            INSERT INTO employe 
            (first_name, last_name, email, cnic, DOB, phone_number, job_title, 
             hire_date, status, department_id, role_id, created_by, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute insert
        cursor.execute(insert_query, (
            first_name, last_name, email, cnic, dob, phone_number, job_title,
            hire_date, status, department_id, role_id, 1, 1  # Using 1 for created_by/updated_by for now
        ))
        
        conn.commit()
        employee_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return True, f"Employee created successfully with ID: {employee_id}"
        
    except mysql.connector.Error as err:
        print(f"❌ Database Error in create_employee: {err}")
        if conn:
            conn.rollback()
        return False, f"Database error: {err}"
    except Exception as e:
        print(f"❌ Unexpected error in create_employee: {e}")
        if conn:
            conn.rollback()
        return False, f"Unexpected error: {e}"


    
    
    
def AllEmployes():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                e.employe_id,
                e.first_name,
                e.last_name,
                e.email,
                e.phone_number,
                e.job_title,
                e.status,
                e.hire_date,
                e.DOB,
                e.cnic,
                e.created_at,
                e.updated_at,
                r.role_name,  -- This replaces role_id with role_name
                d.department_name,
                d.description AS department_description
            FROM employe e
            JOIN departments d ON e.department_id = d.department_id
            LEFT JOIN roles r ON e.role_id = r.role_id;
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return []
    
    
    
    
    
    
    
    
def AllRoles():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM Roles
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return []




def AllDepartments():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM departments
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return []
    
    
    
    
    


# Fetch data from performance table
def performance_data():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                p.performance_id,
                p.employee_id,
                e.first_name,
                e.last_name,
                p.score,
                p.comments,
                p.review_date
            FROM performance p
            JOIN employe e ON p.employee_id = e.employe_id
            ORDER BY p.score DESC;
        """)
        rows = cursor.fetchall()
        print("📊 Query Result:", rows)  # Debugging
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return []
    
    
    
    
    
def get_employee_tasks(employee_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                t.task_id as id,
                t.title,
                t.description,
                t.status,
                t.priority,
                t.deadline as dueDate,
                t.created_at as createdAt,
                t.updated_at as updatedAt,
                -- Add completion date logic
                CASE 
                    WHEN t.status = 'Completed' THEN t.updated_at
                    ELSE NULL
                END as completionDate
            FROM tasks t
            JOIN task_assignments ta ON t.task_id = ta.task_id
            WHERE ta.employee_id = %s
            ORDER BY t.created_at DESC
        """, (employee_id,))
        tasks = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for task in tasks:
            if task['dueDate']:
                task['dueDate'] = task['dueDate'].isoformat()
            if task['createdAt']:
                task['createdAt'] = task['createdAt'].isoformat()
            if task['updatedAt']:
                task['updatedAt'] = task['updatedAt'].isoformat()
            if task['completionDate']:
                task['completionDate'] = task['completionDate'].isoformat()
        
        cursor.close()
        conn.close()
        return tasks
    except mysql.connector.Error as err:
        print(f"❌ Database Error in get_employee_tasks: {err}")
        return []
    
    
    
def assign_tasks(employee_id, task_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()  
        cursor.execute("""INSERT INTO task_assignments (employee_id, task_id)
                       VALUES (%s, %s)""", (employee_id, task_id)) 
        conn.commit()  
        cursor.close()
        conn.close()
        return True 
    except mysql.connector.Error as err:
        print(f"❌ Database Error in assign_tasks: {err}")
        return False  
    


def unassign_tasks(employee_id, task_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()  
        cursor.execute("""Delete from task_assignments where employee_id = %s and task_id = %s """, (employee_id, task_id)) 
        conn.commit()  
        cursor.close()
        conn.close()
        return True 
    except mysql.connector.Error as err:
        print(f"❌ Database Error in assign_tasks: {err}")
        return False  
        
    




app = Flask(__name__)
CORS(app)


@app.route("/api/performance")
def hello():
    p_data = performance_data() 
    return jsonify(p_data)


@app.route("/api/employes")
def employes():
    p_data = AllEmployes() 
    return jsonify(p_data)



@app.route("/api/employees/<int:employee_id>/tasks")
def employee_tasks(employee_id):
    tasks = get_employee_tasks(employee_id)
    return jsonify(tasks)



@app.route("/api/roles")
def roles():
    p_data = AllRoles() 
    return jsonify(p_data)

@app.route("/api/departments")
def departments():
    p_data = AllDepartments()
    return jsonify(p_data)


@app.route("/api/recentTasks")
def recentTasks():
    p_data = recent_tasks()
    return jsonify(p_data)


@app.route("/api/UpcomingDeadlines")
def UpcomingDeadlines():
    p_data = Deadline_tasks()
    return jsonify(p_data)



@app.route("/api/employecount")
def employecount():
    employe_count = total_employes() 
    return jsonify(employe_count)



@app.route("/api/pendingTaskCount")
def pendingTaskCount():
    task_count = total_pendingTasks()
    return jsonify(task_count)





@app.route("/api/inProgressTaskCount")
def inProgressTaskCount():
    task_count = total_inProgressTasks()
    return jsonify(task_count)


@app.route("/api/OverdueTaskCount")
def OverdueTaskCount():
    task_count = total_OverdueTasks()
    return jsonify(task_count)


@app.route("/api/CompletedTaskCount")
def CompletedTaskCount():
    task_count = total_CompletedTasks()
    return jsonify(task_count)

@app.route("/api/test")
def test():
    test_msg="Test Successfull"
    return(test_msg)


@app.route("/api/employees/<int:employee_id>/tasks/<int:task_id>", methods=['POST'])
def assign_task_to_employee(employee_id, task_id):
    # Code to assign the task to the employee
    result = assign_tasks(employee_id, task_id)  # Your assignment function
    return jsonify({"message": "Task assigned successfully", "employee_id": employee_id, "task_id": task_id})



@app.route("/api/employees/<int:employee_id>/tasks/<int:task_id>", methods=['DELETE'])
def unassign_task_from_employee(employee_id, task_id):
    result = unassign_tasks(employee_id, task_id)
    if result:
        return jsonify({
            "message": "Task unassigned successfully", 
            "employee_id": employee_id, 
            "task_id": task_id
        }), 200
    else:
        return jsonify({
            "error": "Failed to unassign task"
        }), 400
        
        
        
@app.route("/api/employees", methods=['POST'])
def create_employee_route():
    try:
        # Get JSON data from request
        employee_data = request.get_json()
        
        if not employee_data:
            return jsonify({"error": "No data provided"}), 400
        
        # Call the create_employee function
        success, message = create_employee(employee_data)
        
        if success:
            return jsonify({
                "message": message,
                "status": "success"
            }), 201
        else:
            return jsonify({
                "error": message,
                "status": "error"
            }), 400
            
    except Exception as e:
        print(f"❌ Error in create_employee_route: {e}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "status": "error"
        }), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
