from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import pandas as pd
from functools import wraps
import openpyxl

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    import os
    # Use environment variables for AWS deployment
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'Mihir@197'),
        database=os.getenv('DB_NAME', 'quiz_app')
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Static Files ---
@app.route('/')
def home():
    return send_from_directory('templates', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if filename.endswith('.html'):
        return send_from_directory('templates', filename)
    return send_from_directory('static', filename)

# --- Authentication APIs ---
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    hashed_password = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        conn.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except mysql.connector.Error as err:
        if err.errno == 1062:
            return jsonify({'error': 'Email already registered'}), 409
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['email'] = user['email']
        return jsonify({'message': 'Login successful', 'user': {'id': user['id'], 'email': user['email']}}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/user', methods=['GET'])
@login_required
def api_get_user():
    return jsonify({'user': {'id': session['user_id'], 'email': session['email']}}), 200

# --- Question Management APIs ---
@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    try:
        df = pd.read_excel(file, engine='openpyxl')
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM answers")
        cursor.execute("DELETE FROM questions")
        
        for index, row in df.iterrows():
            cursor.execute(
                "INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_ans) VALUES (%s,%s,%s,%s,%s,%s)",
                (row['Question'], row['Option_A'], row['Option_B'], row['Option_C'], row['Option_D'], row['Correct_Ans'])
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Questions uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/questions', methods=['GET'])
@login_required
def api_get_questions():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    questions_response = []
    for q in questions:
        questions_response.append({
            'id': q['id'],
            'question': q['question'],
            'option_a': q['option_a'],
            'option_b': q['option_b'],
            'option_c': q['option_c'],
            'option_d': q['option_d']
        })
    
    return jsonify({'questions': questions_response}), 200

@app.route('/api/questions/count', methods=['GET'])
@login_required
def api_question_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    return jsonify({'count': count}), 200

# --- Quiz APIs ---
@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def api_submit_quiz():
    data = request.get_json()
    answers = data.get('answers', {})
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    score = 0
    
    for q_id_str, selected_option in answers.items():
        q_id = int(q_id_str)
        cursor.execute("SELECT correct_ans FROM questions WHERE id=%s", (q_id,))
        correct = cursor.fetchone()[0]
        is_correct = (correct == selected_option)
        
        if is_correct:
            score += 1
            
        cursor.execute(
            "INSERT INTO answers (user_id, question_id, selected_option, is_correct) VALUES (%s, %s, %s, %s)",
            (user_id, q_id, selected_option, is_correct)
        )
    
    # Get actual total questions from database before closing cursor
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({
        'score': score, 
        'total': total_questions,
        'percentage': round((score/total_questions)*100, 2) if total_questions > 0 else 0
    }), 200

# --- Dashboard API ---
@app.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    question_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT answered_at) FROM answers WHERE user_id = %s", (session['user_id'],))
    quiz_attempts = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'user': {'id': session['user_id'], 'email': session['email']},
        'stats': {
            'question_count': question_count,
            'quiz_attempts': quiz_attempts
        }
    }), 200

# --- Excel Template Download ---
@app.route('/questions_template.xlsx')
def download_template():
    return send_from_directory('.', 'questions_template.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)