#Libraries
from datetime import datetime, time, timedelta
import flask
import random
import string
import socket
import hashlib
from flask_mail import Mail, Message

app = flask.Flask(__name__, template_folder='templates', static_folder='static')
# Dictionary to store failed login attempts with timestamps
LOGIN_ATTEMPTS = {} 

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'pisces.zaiby03@gmail.com'  
app.config['MAIL_PASSWORD'] = 'yhqq uoji swbj qfbq'

mail = Mail(app)
STORED_OTP = ''
EMAIL=''
# Constants for lockout mechanism
LOCKOUT_THRESHOLD = 3  
LOCKOUT_TIMEFRAME = timedelta(minutes=5)
LOCKOUT_DURATION = timedelta(minutes=10)  

#Utility Functions for locking feature
def increment_failed_login_attempts(email):
    if email in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[email]['attempts'] += 1
    else:
        LOGIN_ATTEMPTS[email] = {'attempts': 1, 'timestamp': datetime.now()}

def reset_failed_login_attempts(email):
    if email in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[email]

def is_user_locked_out(email):
    if email in LOGIN_ATTEMPTS:
        attempts_info = LOGIN_ATTEMPTS[email]
        timestamp = attempts_info['timestamp']
        attempts = attempts_info['attempts']
        # Check if the threshold is reached within the specified timeframe
        if attempts >= LOCKOUT_THRESHOLD and datetime.now() - timestamp < LOCKOUT_TIMEFRAME:
            return True
    return False

# Utility Functions for Access Control: Location
def check_location_access():
    def get_first_two_octets(ip_address):
        return '.'.join(ip_address.split('.')[:2])
    hostname = socket.gethostname()
    host_ip_address = socket.gethostbyname(hostname)
    required_ip = "192.168.100.12"
    return get_first_two_octets(host_ip_address) == get_first_two_octets(required_ip)

# Utility Functions for Access Control: Time
def check_working_hours():
    now = datetime.now().time()
    start_time = time(9, 0, 0)
    end_time = time(18, 0, 0)
    return start_time <= now <= end_time

# Utility Functions for Access Control: Role
def get_user_role(email):
    users_info = get_attributes_dict()
    for user_info in users_info:
        if user_info['email'] == email:
            return user_info['Role']
    return None  

# Utility Functions for Access Control: Resource
def grant_access(resource, email):
    if (check_location_access()) and (check_working_hours()):
        role = get_user_role(email)
        if role == 'Project_Manager':
            return True
        elif role == 'Developer' and resource == 'Task':
            return True
        elif role == 'Developer' and resource == 'Bug':
            return True
        elif role == 'Developer' and resource == 'Project':
            return False
        elif role == 'Developer' and resource == 'Code':
            return True
        elif role == 'SQA_Engineer' and resource == 'Project':
            return False
        elif role == 'SQA_Engineer' and resource == 'Bug':
            return True
        elif role == 'SQA_Engineer' and resource == 'Task':
            return False
        elif role == 'SQA_Engineer' and resource == 'Code':
            return True        
        else:
            return False
    else:
        return False

# Utility Functions for OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    msg = Message('Your OTP', sender='wemma7932@gmail.com', recipients=[email])
    msg.body = f'Your OTP is: {otp}'
    mail.send(msg)

def set_stored_otp(otp):
    global STORED_OTP
    STORED_OTP = otp

def get_stored_otp():
    return STORED_OTP

# Flask App Routes
@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return flask.render_template('index.html')
    elif flask.request.method == 'POST':
        email = flask.request.form['Email']
        global EMAIL
        EMAIL = email
        password = flask.request.form['Password']
        # Check if the user is locked out
        if is_user_locked_out(email):
            return flask.render_template('index.html', message='Account locked due to multiple unsuccessful login attempts. Please try again later.')
        # Authenticate the user using AccessControl
        auth_result = authenticate_user(email, password)
        if auth_result:
            reset_failed_login_attempts(email)  # Reset failed login attempts upon successful login
            otp = generate_otp()
            set_stored_otp(otp)
            send_otp_email(email, otp)
            return flask.render_template('otp_input.html', email=email)
        else:
            increment_failed_login_attempts(email)
            if is_user_locked_out(email):
                return flask.render_template('index.html', message='Account locked due to multiple unsuccessful login attempts. Please try again later.')
            else:
                return flask.render_template('index.html', message='Authentication failed. Please check your credentials.')
@app.route('/verify_otp', methods=['POST'])
@app.route('/verify_otp', methods=['POST'])
@app.route('/verify_otp_and_grant_access', methods=['POST'])
def verify_otp_and_grant_access():
    entered_otp = flask.request.form['otp']
    selected_resource = flask.request.form['resource']
    print(selected_resource)
    stored_otp = get_stored_otp()

    if entered_otp == stored_otp:
        # OTP verified, now check access
        if grant_access(selected_resource, EMAIL):
            return flask.render_template('access_granted.html', resource=selected_resource)
        else:
            return flask.render_template('access_denied.html', resource=selected_resource)
    else:
        return flask.render_template('index.html', message='Authentication failed due to Incorrect OTP')

# Utility Function for Authentication
def authenticate_user(email, password):
    users_info = get_attributes_dict()
    hashed_password = hashlib.sha3_256(password.encode()).hexdigest()
    for user_info in users_info:
        if user_info['email'] == email and user_info['password'] == hashed_password:
            return True
    return False

# Utility Function for getting user attributes
def get_attributes_dict():
    users_info = [
        {
            'email': 'zanwaar.bese20seecs@seecs.edu.pk',
            'password': hashlib.sha3_256('password'.encode()).hexdigest(),
            'Role': 'Project_Manager',
        },
        {
            'email': 'jbfjdhanwaar.bese20seecs@seecs.edu.pk',
            'password': hashlib.sha3_256('password'.encode()).hexdigest(),
            'Role': 'Project_Manager',
        },
        {
            'email': 'skdjskanwaar.bese20seecs@seecs.edu.pk',
            'password': hashlib.sha3_256('password'.encode()).hexdigest(),
            'Role': 'Project_Manager',
        },
        {
            'email': 'tanwaar.bese20seecs@seecs.edu.pk',
            'password': hashlib.sha3_256('password'.encode()).hexdigest(),
            'Role': 'SQA_Engineer',
        },
        {
            'email': 'sanwaar.bese20seecs@seecs.edu.pk',
            'password': hashlib.sha3_256('password'.encode()).hexdigest(),
            'Role': 'Developer',
        }
    ]
    return users_info

if __name__ == '__main__':
    app.run(debug=True)
