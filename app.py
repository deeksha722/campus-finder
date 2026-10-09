from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'campus.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            building VARCHAR(50) NOT NULL,
            floor INTEGER NOT NULL,
            capacity INTEGER NOT NULL,
            equipment VARCHAR(255),
            availability VARCHAR(100)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            date VARCHAR(20) NOT NULL,
            time VARCHAR(10) NOT NULL,
            location VARCHAR(100) NOT NULL,
            description TEXT,
            capacity INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            title VARCHAR(50) NOT NULL,
            department VARCHAR(100) NOT NULL,
            office_room VARCHAR(50),
            office_building VARCHAR(50),
            email VARCHAR(100),
            office_hours VARCHAR(100),
            specialization VARCHAR(100)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            location VARCHAR(100) NOT NULL,
            hours VARCHAR(100),
            phone VARCHAR(20),
            description TEXT
        )
    ''')
    
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM classrooms')
    if cursor.fetchone()[0] == 0:
        classrooms_data = [
            ('Room 101', 'Building A', 1, 50, 'Projector, Whiteboard, AC', 'Mon-Fri 8AM-5PM'),
            ('Room 205', 'Building B', 2, 100, 'Smart Board, Projector, Sound System', 'Mon-Fri 8AM-6PM'),
            ('Lab 301', 'Building C', 3, 30, 'Computers, Workstations', 'Mon-Fri 9AM-7PM'),
        ]
        cursor.executemany('''
            INSERT INTO classrooms (name, building, floor, capacity, equipment, availability)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', classrooms_data)
        
        events_data = [
            ('Tech Talk 2026', '2026-03-25', '2:00 PM', 'Auditorium', 'Industry Expert Talk on AI', 200),
            ('Hackathon 2026', '2026-04-05', '9:00 AM', 'Computer Lab', '3-day Hackathon Event', 150),
            ('Career Fair', '2026-04-15', '10:00 AM', 'Sports Complex', '50+ Companies Recruiting', 500),
        ]
        cursor.executemany('''
            INSERT INTO events (name, date, time, location, description, capacity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', events_data)
        
        faculty_data = [
            ('Dr. John Smith', 'Professor', 'Computer Science', '410', 'Building A', 'john.smith@campus.edu', 'Tue & Thu 3-5 PM', 'AI & Machine Learning'),
            ('Prof. Sarah Johnson', 'Associate Professor', 'Mathematics', '320', 'Building B', 'sarah.johnson@campus.edu', 'Mon & Wed 2-4 PM', 'Calculus & Statistics'),
            ('Dr. Michael Brown', 'Professor', 'Physics', '510', 'Building C', 'michael.brown@campus.edu', 'Wed & Fri 4-6 PM', 'Quantum Physics'),
        ]
        cursor.executemany('''
            INSERT INTO faculty (name, title, department, office_room, office_building, email, office_hours, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', faculty_data)
        
        resources_data = [
            ('Main Library', 'Library', 'Floor 1, Building A', '8 AM - 10 PM', '(555) 123-4567', 'Book Lending, Study Rooms'),
            ('Health Center', 'Medical', 'Building D', '9 AM - 5 PM', '(555) 987-6543', 'General Check-ups'),
            ('Computer Lab', 'Tech', 'Floor 2, Building C', '24/7', '(555) 456-7890', 'High-Speed Internet'),
            ('Cafeteria', 'Food', 'Ground Floor, Building E', '7 AM - 8 PM', '(555) 234-5678', 'Vegetarian & Non-Vegetarian'),
        ]
        cursor.executemany('''
            INSERT INTO resources (name, type, location, hours, phone, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', resources_data)
        
        conn.commit()
    
    conn.close()

init_db()

@app.route('/api/classrooms', methods=['GET'])
def get_classrooms():
    try:
        conn = get_db_connection()
        classrooms = conn.execute('SELECT * FROM classrooms').fetchall()
        conn.close()
        return jsonify([dict(c) for c in classrooms])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        conn = get_db_connection()
        events = conn.execute('SELECT * FROM events').fetchall()
        conn.close()
        return jsonify([dict(e) for e in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faculty', methods=['GET'])
def get_faculty():
    try:
        conn = get_db_connection()
        faculty = conn.execute('SELECT * FROM faculty').fetchall()
        conn.close()
        return jsonify([dict(f) for f in faculty])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resources', methods=['GET'])
def get_resources():
    try:
        conn = get_db_connection()
        resources = conn.execute('SELECT * FROM resources').fetchall()
        conn.close()
        return jsonify([dict(r) for r in resources])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        conn = get_db_connection()
        results = {
            'classrooms': [dict(c) for c in conn.execute('SELECT * FROM classrooms WHERE name LIKE ?', (f'%{query}%',)).fetchall()],
            'events': [dict(e) for e in conn.execute('SELECT * FROM events WHERE name LIKE ?', (f'%{query}%',)).fetchall()],
            'faculty': [dict(f) for f in conn.execute('SELECT * FROM faculty WHERE name LIKE ?', (f'%{query}%',)).fetchall()],
            'resources': [dict(r) for r in conn.execute('SELECT * FROM resources WHERE name LIKE ?', (f'%{query}%',)).fetchall()]
        }
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == '__main__':
    print("=" * 50)
    print("🏫 Campus Finder API Server")
    print("=" * 50)
    print("Server running on: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)