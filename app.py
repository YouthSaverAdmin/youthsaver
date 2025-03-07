import datetime
from functools import wraps
import hashlib
import os
import random
import re
from bson import ObjectId
from flask import session
from flask import Flask, flash, jsonify, redirect, request, render_template,  url_for, session, make_response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import secrets
import pymongo
from pymongo.errors import DuplicateKeyError
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message
from flask_socketio import send
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired
import firebase_admin
from firebase_admin import credentials, storage
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()



def generate_reset_token():
    # Generate a random token using the secrets module
    token = secrets.token_urlsafe(32)

    # Hash the token using SHA-256 for additional security
    hashed_token = hashlib.sha256(token.encode()).hexdigest()

    return hashed_token

app = Flask(__name__)
socketio = SocketIO(app)
# Set the secret key to enable sessions


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB connection settings
client = MongoClient('mongodb+srv://deathcross70:Ijingo18@cluster0.au9vyaa.mongodb.net/web-app')
db = client['web-app']
incident_collection = db['Incidents']
person_collection = db['Persons']
involvement_collection = db['Involvements']
users_collection = db['Users']
profiles_collection = db['Profiles']
responses_collection = db['Responses']
roles_collection = db['Roles']
reset_tokens_collection = db['ResetTokens']  # Collection to store reset tokens
student_notifications_collection = db['Student_Notifications']
admin_notifications_collection = db['Admin_Notifications']
user_profiles_collection = db['User_Profiles']
responses_to_reports_collection = db['ResponsesToReports']  # MongoDB collection


# Configure Flask app for sending emails using Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use port 587 for TLS/STARTTLS
app.config['MAIL_USE_TLS'] = True  # Enable TLS/STARTTLS security
app.config['MAIL_DEFAULT_SENDER'] = 'youthsaver101@gmail.com'
app.config['MAIL_USERNAME'] = 'youthsaver101@gmail.com'  # Your Gmail email address
app.config['MAIL_PASSWORD'] = 'otqe bbar lgng vacs'  # Your Gmail account password

mail = Mail(app)





import firebase_admin
from firebase_admin import credentials, storage
from datetime import timedelta






cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'web-pictures-13450.appspot.com'
})

bucket = storage.bucket()

def list_files_and_generate_urls():
    blobs = bucket.list_blobs(prefix='pictures/')
    urls = []
    for blob in blobs:
        if blob.name.endswith('/'):
            continue  
        url = blob.generate_signed_url(timedelta(days=3600)) 
        urls.append(url)
    return urls

urls = list_files_and_generate_urls()




def generate_6_char_code():
    return secrets.token_hex(3)  # Generates a 6-character hex code

def store_reset_token(email, code):
    expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    reset_tokens_collection.insert_one({'email': email, 'code': code, 'expiry_time': expiry_time})

def validate_reset_token(email, code):
    token = reset_tokens_collection.find_one({'email': email, 'code': code})
    if token:
        if datetime.datetime.now() <= token['expiry_time']:
            return True
    return False


def get_next_involvement_id():
    max_id = involvement_collection.find_one(sort=[("_id", -1)])
    if max_id:
        return max_id['_id'] + 1
    else:
        return 1

def get_next_incident_id():
    max_id = incident_collection.find_one(sort=[("_id", -1)])
    if max_id:
        return max_id['_id'] + 1
    else:
        return 1

def get_next_person_id():
    max_id = person_collection.find_one(sort=[("_id", -1)])
    if max_id:
        return max_id['_id'] + 1
    else:
        return 1
    
def get_next_profile_id():
    max_id = profiles_collection.find_one(sort=[("_id", -1)])
    if max_id:
        return max_id['_id'] + 1
    else:
        return 1
    
def get_next_response_id():
    max_id = responses_collection.find_one(sort=[("_id", -1)])
    if max_id:
        return max_id['_id'] + 1
    else:
        return 1


# Define roles
ROLES = {
    'admin': 1,
    'staff': 2,
    'student': 3
}

# Implement this function to retrieve user's role from database or session
def get_user_role(username):
    # Example implementation (replace with your actual logic)
    user = users_collection.find_one({'username': username})
    if user:
        return user.get('role_id')
    else:
        return None

# Decorator function to check if user is logged in and has correct role
def login_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('index'))

            username = session['username']
            user_role = get_user_role(username)
            
            if user_role is None or ROLES.get(role) != user_role:
                # Redirect to appropriate welcome page based on current role
                if user_role == ROLES['admin']:
                    return redirect(url_for('welcome_admin', username=username))
                elif user_role == ROLES['staff']:
                    return redirect(url_for('welcome_staff', username=username))
                elif user_role == ROLES['student']:
                    return redirect(url_for('welcome_student', username=username))
                else:
                    # Handle unexpected role or None case
                    return redirect(url_for('index'))
            
            return view_func(*args, **kwargs)
        return wrapper
    return decorator
@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        user = users_collection.find_one({'username': username})
        if user:
            role_id = user.get('role_id')
            if role_id == 1:
                return redirect(url_for('welcome_admin', username=username))
            elif role_id == 2:
                return redirect(url_for('welcome_staff', username=username))
            elif role_id == 3:
                return redirect(url_for('welcome_student', username=username))

    # If user is not logged in or role is not recognized, render the index template
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('logout')
def handle_logout():
    print('User logged out')





# Route for the login page
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/wellness_student')
def wellness_student_page(): 
    return render_template('pages/wellness_student.html')


@app.route('/wellness')
def wellness_page():
    return render_template('pages/wellness.html')

@app.route('/wellness2')
def wellness_page2():
    return render_template('pages/wellness2.html')

@app.route('/wellness3')
def wellness_page3():
    return render_template('pages/wellness3.html')


@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/profiles.html')
def profiles():
    return render_template('profiles.html')

@app.route('/password_reset/<int:student_number>', methods=['GET'])
def password_reset(student_number):
    # Render the password_reset template, passing the student_number to the template
    return render_template('pages/password_reset.html', student_number=student_number)


@app.route('/update')
def update_page():
    # Fetch profiles data from MongoDB
    profiles_data = list(profiles_collection.find())
    return render_template('update.html', profiles=profiles_data)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if request.method == 'POST':
        # Get data from the form
        profile_id = request.form['profile_id']
        first_name = request.form['first_name']
        middle_initial = request.form['middle_initial']
        surname = request.form['surname']
        birth_date = request.form['birth_date']
        gender = request.form['gender']
        address = request.form['address']
        gmail = request.form['gmail']
        student_number = int(request.form['student_number'])
        

        # Check if the email already exists in another profile
        existing_email_profile = profiles_collection.find_one({'gmail': gmail, '_id': {'$ne': int(profile_id)}})
        if existing_email_profile:
            error_message = 'Email already exists in another profile. Please choose a different email.'
            return render_template('update.html', error_message=error_message)

        # Check if the student number already exists in another profile
        existing_student_number_profile = profiles_collection.find_one({'student_number': student_number, '_id': {'$ne': int(profile_id)}})
        if existing_student_number_profile:
            error_message = 'Student number already exists in another profile. Please choose a different student number.'
            return render_template('update.html', error_message=error_message)

        # Update profile in the database
        profiles_collection.update_one(
            {'_id': int(profile_id)},
            {'$set': {'first_name': first_name,
                      'middle_initial': middle_initial,
                      'surname': surname,
                      'birth_date': birth_date,
                      'gender': gender,
                      'address': address,
                      'gmail': gmail,
                      'student_number': student_number}}
        )
    return redirect(url_for('update_page'))



@app.route('/registerStudent', methods=['POST'])
def register_student():
    username = request.form['username']
    password = request.form['password']
    student_number = int(request.form['student_number'])
    role_id = 3  # Automatically set the role_id to 3 for students

    # Check if the username already exists
    existing_user = users_collection.find_one({'username': username, 'student_number': student_number})
    if existing_user:
        error_message = 'Username already exists or student number. Please choose a different username.'
        return render_template('register.html', message2_0=error_message)

    try:
        highest_id_document = users_collection.find_one(sort=[('_id', -1)])
        highest_id = highest_id_document['_id'] if highest_id_document else 0

        new_id = highest_id + 1

        # Insert student data into MongoDB
        student_data = {'_id': new_id, 'username': username, 'password': password, 'role_id': role_id, 'student_number': student_number}
        users_collection.insert_one(student_data)

        return redirect(url_for('login'))  # Redirect to login page after registration

    except DuplicateKeyError:
        error_message = 'An error occurred. Please try again.'
        return render_template('register.html', message2_0=error_message)


@app.route('/registerStaff', methods=['POST'])
def register_staff():
    username = request.json.get('username')
    password = request.json.get('password')
    section_and_department = request.json.get('section_and_department')
    role_id = 2  # Automatically set the role_id to 2 for staff

    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'status': 'error', 'message': 'Username already exists. Please choose a different username.'})

    try:
        highest_id_document = users_collection.find_one(sort=[('_id', -1)])
        highest_id = highest_id_document['_id'] if highest_id_document else 0
        new_id = highest_id + 1

        staff_data = {'_id': new_id, 'username': username, 'password': password,'section_and_department': section_and_department, 'role_id': role_id}
        users_collection.insert_one(staff_data)

        return jsonify({'status': 'success', 'message': 'Staff registered successfully!'})

    except DuplicateKeyError:
        return jsonify({'status': 'error', 'message': 'An error occurred. Please try again.'})
    
    

@app.route('/submitAdminForms', methods=['POST'])
def submit_admin_forms():
    try:
        data = request.json
        formData = data.get('formData')

        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not logged in'}), 401

        # Check if the email already exists in the database
        existing_profile = profiles_collection.find_one({'gmail': formData.get('gmail')})
        if existing_profile:
            return jsonify({'error': 'Email already exists'}), 400

        # Extract data from the form
        student_number_str = formData.get('studentNumber')
        if student_number_str:
            try:
                student_number = int(student_number_str)
            except ValueError:
                return jsonify({'error': 'Invalid student number'}), 400
        else:
            return jsonify({'error': 'Student number is required'}), 400

        # Check if the student number already exists in the database
        existing_profile = profiles_collection.find_one({'student_number': student_number})
        if existing_profile:
            return jsonify({'error': 'Student number already exists'}), 400

        # Check if a profile with the same first name, middle initial, and last name already exists
        existing_profile = profiles_collection.find_one({
            'first_name': formData.get('firstName'),
            'surname': formData.get('surname')
        })
        if existing_profile:
            return jsonify({'error': 'Profile with the same name already exists'}), 400

        next_profile_id = get_next_profile_id()

        # Extract and format date
        birth_date_str = formData.get('birthDate')
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Expected YYYY-MM-DD.'}), 400

        # Prepare form data
        form_data = {
            '_id': next_profile_id,
            'first_name': formData.get('firstName'),
            'middle_initial': formData.get('middleInitial'),
            'surname': formData.get('surname'),
            'birth_date': birth_date.isoformat(),  # Store date as ISO 8601 string
            'gender': formData.get('gender'),
            'address': formData.get('address'),
            'student_number': student_number,
            'username': username
        }

        if 'gmail' in formData:
            form_data['gmail'] = formData.get('gmail')

        # Insert data into the AdminForms collection
        profiles_collection.insert_one(form_data)

        # Send an email notification
        if 'gmail' in form_data:
            recipient_email = form_data['gmail']
            try:
                msg = Message("Account Creation Notification", recipients=[recipient_email])
                msg.body = "You may now make an account for login. Please use your student number for registration."
                mail.send(msg)
            except Exception as e:
                app.logger.error(f"Error sending email: {e}")
                return jsonify({'message': 'Profile submitted, but failed to send email notification.'}), 200

        return jsonify({'message': 'Admin form submitted successfully! Email notification sent.'}), 200

    except Exception as e:
        app.logger.error(f'Error submitting admin form: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500




@app.route('/getUserReports', methods=['GET'])
def get_user_reports():
    username = session.get('username')
    if not username:
        return 'Unauthorized', 401
    
    try:
        user = users_collection.find_one({'username': username})
        role_id = user.get('role_id') if user else None
        
        reports = []
        
        # Fetch involvements for the user
        if role_id in [1, 2]:  # Admin role can see all involvements
            involvements = involvement_collection.find({})
        else:
            involvements = involvement_collection.find({'username': username})
        
        for involvement in involvements:
            incident_id = involvement['incident_id']
            
            # Find incident details from the incidents collection
            incident = incident_collection.find_one({'_id': incident_id})
            if not incident:
                continue
            
            person_id = involvement['person_id']
            person = person_collection.find_one({'_id': person_id})
            
            # Check if there are responses for this incident_id
            response_exists = responses_to_reports_collection.find_one({'incident_id': incident_id}) is not None
            
            read_status = incident.get('read', False)  # Ensure read status from incident
            
            # Prepare base report data
            report = {
                'incident_id': incident_id,
                'incident_date': incident['date'].strftime('%Y-%m-%d'),
                'case_details': incident['case_details'],
                'location': incident['location'],
                'type': incident['type'],
                'relation_to_incident': involvement['relation_to_incident'],
                'person_name': person['name'],
                'person_date': person['date'].strftime('%Y-%m-%d %I:%M %p'),
                'username': involvement['username'],
                'hasResponse': response_exists,  # Flag indicating if responses exist
                'read': read_status  # Ensure read status is set from incident
            }
            
            reports.append(report)
        
        return jsonify(reports), 200
    
    except Exception as e:
        app.logger.error('Error fetching user reports: %s', str(e))
        return 'Internal Server Error', 500


@app.route('/markReportAsRead/<incident_id>', methods=['PUT'])
def mark_report_as_read(incident_id):
    try:
        # Convert incident_id to ObjectId
        incident_oid = int(incident_id)
        
        # Update the document in incident_collection
        result = incident_collection.update_one(
            {'_id': incident_oid},
            {'$set': {'read': True}}
        )
        
        # Check if the update was successful
        if result.matched_count == 0:
            return jsonify({'error': 'Incident not found.'}), 404
        
        return jsonify({'message': 'Incident marked as read successfully!'}), 200
    
    except pymongo.errors.PyMongoError as e:
        app.logger.error(f'Error marking incident as read: {str(e)}')
        return jsonify({'error': 'Database error'}), 500
    
    except Exception as e:
        app.logger.error(f'Unexpected error marking incident as read: {str(e)}')
        return jsonify({'error': 'Unexpected error'}), 500


@app.route('/check_profiles', methods=['POST'])
def check_profiles():
    try:

        data = request.json
        formData = data.get('formData')
        
        # Extract data from the form
        student_number = formData.get('studentNumber')
        first_name = formData.get('firstName')
        surname = formData.get('surname')



        # Check if all required fields are provided
        if not student_number:
            return 'Student number is missing', 400
        if not (first_name and surname):
            return 'Name is missing', 400

         # Create case-insensitive regular expression patterns
        first_name_pattern = re.compile(first_name, re.IGNORECASE)
        surname_pattern = re.compile(surname, re.IGNORECASE)

        # Check if the student number already exists in the profiles collection
        existing_profile = profiles_collection.find_one({
            'student_number': student_number,
            'first_name': {'$regex': first_name_pattern},
            'surname': {'$regex': surname_pattern}
        })

        if existing_profile:
            # If a matching profile is found, check if there is an existing user with the same student number
            existing_user = users_collection.find_one({'student_number': int(student_number)})
            if existing_user:
                # If a matching user is found, return an appropriate message
                return 'An account already exists with the same student number.', 400
            # If no matching user is found, redirect to the registration page
            return redirect('/register.html')

        # If no existing profile is found, return a message prompting the user to register
        return 'No existing account found. Please register.', 400
    
    except Exception as e:
        print('Error checking profiles:', e)
        return 'Internal Server Error', 500



def create_student_notification(incident_id, username):
    notification = {
        'incident_id': incident_id,
        'username': username,
        'message': f'New form submitted by {username}',
        'timestamp': datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        'read': False
    }
    student_notifications_collection.insert_one(notification)
    
@app.route('/submitForms', methods=['POST'])
def submit_forms():
    try:
        data = request.json
        formData = data.get('formData')

        # Get the username of the current user from the session
        username = session.get('username')

        # Convert date string to datetime object
        incident_date = datetime.strptime(formData.get('incidentDate'), '%Y-%m-%d')

        next_incident_id = get_next_incident_id()

        # Extract data for Incidents
        incident_data = {
            '_id': next_incident_id,
            'date': incident_date,
            'case_details': formData.get('caseDetails'),
            'location': formData.get('location'),
            'type': formData.get('type'),
            'read': False  # Adding read status initially set to False
        }

        # If type is 'other', use the value from 'otherType' field
        if formData.get('type') == 'other':
            incident_data['type'] = formData.get('otherType')

        # Insert incident data into Incidents collection
        incident_collection.insert_one(incident_data)

        next_person_id = get_next_person_id()

        report_date = datetime.now()
        # Extract data for Persons
        person_data = {
            '_id': next_person_id,
            'name': username,
            'date': report_date
        }

        # Insert person data into Persons collection
        person_collection.insert_one(person_data)

        next_involvement_id = get_next_involvement_id()

        user = users_collection.find_one({'username': username})
        if user:
            role_id = user['role_id']
        else:
            role_id = None

        # Extract data for Involvements
        involvement_data = {
            '_id': next_involvement_id,
            'incident_id': next_incident_id,
            'relation_to_incident': formData.get('relationToIncident'),
            'person_id': next_involvement_id,
            'role_id': next_involvement_id,
            'username': username
        }

        # Insert involvement data into Involvements collection
        involvement_collection.insert_one(involvement_data)
        
        # Create a notification for the admin with read status
        create_student_notification(next_incident_id, username)

        return jsonify({'message': 'Response form submitted successfully!'}), 200

    except Exception as e:
        print('Error submitting form:', e)
        return 'Internal Server Error', 500

    


def authenticate_user(username, password):
    user = users_collection.find_one({'username': username, 'password': password})
    if user:
        return user  # Return the user object if authentication is successful
    return None



# Assuming you have a function to determine the appropriate route based on the user's role
def get_welcome_route(user_role_id):
    if user_role_id == 1:
        return 'welcome_admin'
    elif user_role_id == 2:
        return 'welcome_staff'
    elif user_role_id == 3:
        return 'welcome_student'
    else:
        return 'index'  # Default route if role is unrecognized or not provided

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None  # Initialize message variable
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        user = authenticate_user(username, password)
        
        if user:
            session['username'] = username  # Store the username in the session
            
            # Determine the appropriate route based on the user's role
            welcome_route = get_welcome_route(user.get('role_id'))
            
            # Set a cookie to remember the username
            response = make_response(redirect(url_for(welcome_route, username=username)))
            response.set_cookie('username', username)
            return response
        
        else:
            message = 'Invalid username or password.'  # Set error message for invalid credentials
    else:
        message = 'Invalid request method.'  # Set error message for invalid request method
            
    return render_template('login.html', message=message)


# Assuming your existing get_student_notifications function
def get_student_notifications(filter_read=None):
    try:
        # Fetch notifications from both collections
        student_notifications = list(student_notifications_collection.find({}, {'_id': False}))
        responses_to_reports = list(responses_to_reports_collection.find({}, {'_id': False}))

        # Combine both lists of notifications
        notifications = student_notifications + responses_to_reports

        # Filter notifications based on read status if specified
        if filter_read is not None:
            filtered_notifications = [notif for notif in notifications if notif.get('read') == filter_read]
            return filtered_notifications

        return notifications

    except Exception as e:
        print('Error fetching notifications:', e)
        return []  # Return an empty list if there's an error

@app.route('/notifications', methods=['GET'])
def fetch_notifications():
    notifications = get_student_notifications()
    has_unread = any(notif.get('read') == False for notif in notifications)
    return jsonify(notifications=notifications, has_unread=has_unread)

@app.route('/mark_notifications_read', methods=['POST'])
def mark_notifications_read():
    try:
        student_notifications_collection.update_many({'read': False}, {'$set': {'read': True}})
        responses_to_reports_collection.update_many({'read': False}, {'$set': {'read': True}})
        return jsonify(status='success')
    except Exception as e:
        print('Error marking notifications as read:', e)
        return jsonify(status='error', message=str(e))




@app.route('/admin_notifications', methods=['GET'])
def admin_notifications():
    try:
        username = request.args.get('username')  # Get username from request query parameters
        
        # Fetch incident IDs involving the user
        user_involvements = involvement_collection.find({'username': username})
        incident_ids = [involvement['incident_id'] for involvement in user_involvements]
        
        # Fetch admin notifications related to user's incident IDs
        admin_notifications = list(admin_notifications_collection.find(
            {'incident_id': {'$in': incident_ids}},
            {'_id': False}
        ))
        
        # Check if any notification is unread
        has_unread = any(notif.get('read') == False for notif in admin_notifications)
        
        return jsonify(admin_notifications=admin_notifications, has_unread=has_unread), 200
    
    except Exception as e:
        print(f'Error fetching admin notifications: {e}')
        return jsonify(error='Internal Server Error'), 500


@app.route('/mark_admin_notifications_read', methods=['POST'])
def mark_admin_notifications_read():
    try:
        # Update all admin notifications where 'read' is False to set 'read' to True
        admin_notifications_collection.update_many({'read': False}, {'$set': {'read': True}})
 
        return jsonify(status='success')

    except Exception as e:
        print('Error marking notifications as read:', e)
        return jsonify(status='error', message=str(e))
    

# Assuming your existing get_student_notifications function
def get_staff_notifications(filter_read=None):
    try:
        # Fetch notifications only from responses_to_reports_collection
        notifications = list(responses_to_reports_collection.find({}, {'_id': False}))

        # Filter notifications based on read status if specified
        if filter_read is not None:
            filtered_notifications = [notif for notif in notifications if notif.get('read') == filter_read]
            return filtered_notifications

        return notifications

    except Exception as e:
        print('Error fetching staff notifications:', e)
        return []  # Return an empty list if there's an error

@app.route('/staff_notifications', methods=['GET'])
def fetch_staff_notifications():
    notifications = get_staff_notifications()
    has_unread = any(notif.get('read') == False for notif in notifications)
    return jsonify(notifications=notifications, has_unread=has_unread)

@app.route('/mark_staff_notifications_read', methods=['POST'])
def mark_staff_notifications_read():
    try:
        # Update only responses_to_reports_collection
        responses_to_reports_collection.update_many({'read': False}, {'$set': {'read': True}})
        return jsonify(status='success')
    except Exception as e:
        print('Error marking notifications as read:', e)
        return jsonify(status='error', message=str(e))

@app.route('/welcome_student/<username>')
@login_required('student')
def welcome_student(username):
    try:
      
        admin_notifications
        
        return render_template('pages/welcome_student.html', username=username, notifications=admin_notifications)

    except Exception as e:
        print('Error fetching admin notifications for student:', e)
        return render_template('pages/welcome_student.html', username=username, notifications=[])


@app.route('/welcome_admin/<username>')
@login_required('admin')
def welcome_admin(username):
    
    notifications = get_student_notifications()  
    
    return render_template('pages/welcome_admin.html', username=username, notifications=notifications)

@app.route('/welcome_staff/<username>')
@login_required('staff')
def welcome_staff(username):
    notifications = get_staff_notifications()
    return render_template('pages/welcome_staff.html', username=username, notifications=notifications)


@app.route('/back_to_admin')
def back_to_admin():
    username = session.get('username')
    if username:
        return redirect(url_for('welcome_admin', username=username))
    return redirect(url_for('login'))


@app.route('/back_to_student')
def back_to_student():
    username = session.get('username')
    if username:
        return redirect(url_for('welcome_student', username=username))
    return redirect(url_for('login'))


@app.route('/getIncidentId', methods=['GET'])
def get_incident_id():
    try:
        report_id = int(request.args.get('reportId'))
        involvement = involvement_collection.find_one({'_id': report_id})
        if involvement:
            incident_id = involvement.get('incident_id')
            if incident_id:
                return jsonify({'incident_id': incident_id}), 200
            else:
                return jsonify({'error': 'Incident ID not found in involvement document'}), 404
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        print('Error fetching incident ID:', e)
        return jsonify({'error': 'Internal Server Error'}), 500


def create_admin_notification(incident_id, responder):
    # Find admin users associated with the incident
    admin_users = users_collection.find({'role_id': {'$in': [1, 2]}})

    # Create notifications for each admin user associated with the incident
    for admin_user in admin_users:
        notification = {
            'incident_id': incident_id,
            'username': admin_user['username'],
            'message': f'New response submitted by {responder} for incident ID {incident_id}',
            'timestamp': datetime.now(),
            'read': False
        }
        admin_notifications_collection.insert_one(notification)

@app.route('/submitResponseForm', methods=['POST'])
def submit_response_form():
    try:
        data = request.json
        formData = data.get('formData')  # Extract formData from the request JSON

        if not formData:
            return jsonify({'error': 'No form data received.'}), 400

        # Extract individual response details from formData
        incident_id = formData.get('incident_id')
        response = formData.get('response')

        if not incident_id or not response:
            return jsonify({'error': 'Missing form data fields.'}), 400

        # Get the username of the current user from the session
        responder = session.get('username')

        if not responder:
            return jsonify({'error': 'User not logged in.'}), 403

        next_response_id = get_next_response_id()

        # Get current datetime
        current_time = datetime.now()

        # Construct response data with current datetime
        response_data = {
            '_id': next_response_id,
            'incident_id': int(incident_id),
            'responder': responder,  # Add responder field
            'response': response,
            'date': current_time,  # Use current datetime as datetime object
            'read': False  # Initialize read status as False
        }

        # Insert response data into Responses collection
        responses_collection.insert_one(response_data)

        # Create notifications for admin users associated with the incident
        create_admin_notification(int(incident_id), responder)

        return jsonify({'message': 'Response form submitted successfully!'}), 200

    except Exception as e:
        app.logger.error(f'Error submitting response form: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/getResponses/<incident_id>', methods=['GET'])
def get_responses(incident_id):
    try:
        responses = list(responses_collection.find({'incident_id': int(incident_id)}))
        if responses:
            read = False  # Assume unread if there are responses
            for response in responses:
                response['_id'] = str(response['_id'])
                response['date'] = response['date'].strftime('%Y-%m-%d %I:%M %p')  # Format date to string
                if response.get('read', False):
                    read = True  # Mark as read if any response is marked as read
            return jsonify({'responses': responses, 'read': read}), 200
        else:
            return jsonify({'message': 'No responses from staff or admin yet.', 'read': False}), 200
    except Exception as e:
        print('Error fetching responses:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
    

@app.route('/markResponseAsRead/<incident_id>', methods=['POST'])
def mark_response_as_read(incident_id):
    try:
        result = responses_collection.update_one(
            {'incident_id': int(incident_id)},
            {'$set': {'read': True}}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Response not found.'}), 404

        return jsonify({'message': 'Response marked as read successfully!'}), 200

    except Exception as e:
        app.logger.error(f'Error marking response as read: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/acceptResponseNotification', methods=['POST'])
def accept_response_notification():
    try:
        data = request.get_json()
        incident_id = data.get('incident_id')
        
        # Example: Retrieve username from session or other authentication context
        if 'username' in session:
            username = session['username']
        else:
            return jsonify({'error': 'User not authenticated.'}), 401

        if not incident_id:
            return jsonify({'error': 'Incident ID is required.'}), 400
        
        # Logic to create a notification
        create_notification(username, 'accepted the response', incident_id)

        return jsonify({'message': 'Notification sent successfully!'}), 200

    except Exception as e:
        app.logger.error(f'Error creating notification: {e}')
        return jsonify({'error': 'Internal Server Error'}), 500
def create_notification(username, action, incident_id):
    # Decide where to store the notification (e.g., Student_Notifications or Admin_Notifications)
    # Assuming it's stored in Student_Notifications for students
    notification = {
        'username': username,
        'message': f'{username} has {action} for incident {incident_id}',  # Example message format
        'incident_id': int(incident_id),  # Include the incident ID in the notification
        'timestamp': datetime.now(),  # Store current datetime as a datetime object
        'read': False
    }
    responses_to_reports_collection.insert_one(notification)
    # You can add more logic here if needed for admin notifications

# Function to format datetime for display
def format_datetime_for_display(dt):
    return dt.strftime('%Y-%m-%d %I:%M:%S %p')



@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
@socketio.on('logout')
def handle_logout():
    print('User logged out')
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        # Emit logout event to all connected clients
        socketio.emit('logout')
        
        # Clear the session data
        session.clear()
        
        # Redirect the user to the index page
        return redirect(url_for('index'))
    
    # If the method is GET or any other method, return Method Not Allowed
    return 'Method Not Allowed', 405


def generate_reset_code():
    # Generate a random 6-digit code
    return ''.join(random.choices('0123456789', k=6))




@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Process the form submission
        email = request.form.get('email')
        student_number = int(request.form.get('student_number'))

        # Check if student number exists in the users collection
        user = users_collection.find_one({"student_number": student_number})
        if not user:
            return make_response("Student number does not exist", 400)
        
        # Get username
        username = user.get('username')  # Assuming 'username' is the key for the username in the users_collection
        
        # Generate a reset code
        reset_code = generate_reset_code()

        # Store the reset code, email, and username in the reset_tokens collection
        reset_tokens_collection.insert_one({
            "email": email,
            "student_number": student_number,
            "reset_code": reset_code,
            "username": username,
            "expiration_time": datetime.utcnow() + timedelta(minutes=5)  # Expiry time 5 minutes from now
        })

        # Send the reset code via email
        send_reset_code(email, username, reset_code)

        # Redirect the user to the reset_password route
        return redirect(url_for('password_reset', student_number=student_number))


    # Render the forgot_password template for GET requests
    return render_template('pages/forgot_password.html')


def send_reset_code(email, username, reset_code):
    try:
        # Create message object
        msg = Message('Password Reset Code', recipients=[email])
        
        # Set email body
        msg.body = f'Hello {username},\n\nYour password reset code is: {reset_code}. It will expire in 5 minutes.'

        # Send email
        mail.send(msg)
        
        return 'Reset code sent successfully!'
    except Exception as e:
        return f'Failed to send email: {str(e)}'

@app.route('/verify_reset_code', methods=['POST'])
def verify_reset_code():
    data = request.json
    email = data.get('email')
    reset_code = data.get('reset_code')

    if not email or not reset_code:
        return jsonify({'error': 'Email and reset code are required'}), 400

    # Fetch the reset token from the database
    reset_token = reset_tokens_collection.find_one({'email': email, 'reset_code': reset_code})

    if reset_token:
        # Check if the reset code has expired
        if datetime.utcnow() <= reset_token['expiration_time']:
            return jsonify({'message': 'Reset code is valid'}), 200
        else:
            return jsonify({'error': 'Reset code has expired'}), 400
    else:
        return jsonify({'error': 'Invalid reset code'}), 400

@app.route('/reset_password', methods=['POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        reset_code = request.form.get('reset_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if email and reset_code and new_password and confirm_password:
            # Retrieve the reset token from the database
            reset_token = reset_tokens_collection.find_one({'email': email, 'reset_code': reset_code})
            
            if reset_token:
                # Check if the reset code is still valid (within the expiry time)
                if datetime.utcnow() <= reset_token['expiration_time']:
                    # Check if the new password matches the confirm password
                    if new_password == confirm_password:
                        # Retrieve the student_number associated with the reset token
                        student_number = reset_token.get('student_number')
                        
                        # Find the user in the users collection using the student_number
                        user = users_collection.find_one({'student_number': student_number})
                        
                        if user:
                            # Perform the password reset action by updating the user's password in the database
                            users_collection.update_one({'student_number': student_number}, {'$set': {'password': new_password}})
                            
                            # After resetting the password, delete the reset token from the collection
                            reset_tokens_collection.delete_one({'email': email, 'reset_code': reset_code})
                            
                            # Return a success message
                            return redirect('/login')
                        else:
                            # If the user is not found, return an error message
                            return "User not found. Please make sure the provided email and reset code are correct.", 400
                    else:
                        # If new password and confirm password do not match, return an error message
                        return "New password and confirm password do not match.", 400
                else:
                    # If the reset code has expired, return an error message
                    return "Reset code has expired. Please request a new reset code.", 400
            else:
                # If the reset token is not found, return an error message
                return "Invalid reset code. Please make sure you have the correct code.", 400
        else:
            # If any field is missing, return an error message
            return "All fields are required.", 400
    else:
        # If method is not POST, return Method Not Allowed
        return "Method Not Allowed", 405

if __name__ == "__main__":
    app.run(debug=True)
