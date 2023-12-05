from flask import Flask, render_template, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
import subprocess, platform
from datetime import datetime
from markupsafe import Markup


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'  # Use SQLite as the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
db = SQLAlchemy(app)

def get_hostname(ip_address):
    # Try using dig on Unix-like systems (Linux, macOS)
    if platform.system() in ('Linux', 'Darwin'):
        try:
            result = subprocess.check_output(['dig', '-x', ip_address], universal_newlines=True)
            hostname = result.split('\t')[-1].strip()
            return hostname
        except subprocess.CalledProcessError as e:
            print(f"Error executing dig: {e}")
    
    # Try using nslookup on Windows
    elif platform.system() == 'Windows':
        try:
            result = subprocess.check_output(['nslookup', ip_address], universal_newlines=True)
            hostname_index = result.find('Name:')
            if hostname_index != -1:
                hostname = result[hostname_index + 6:].strip()
                return hostname
        except subprocess.CalledProcessError as e:
            print(f"Error executing nslookup: {e}")

    # Return None if both dig and nslookup fail
    return None


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hardware = db.Column(db.String(50))
    ip_address = db.Column(db.String(15))
    client_hostname = db.Column(db.String(50))
    submission_time = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(10), default='open')
    comments = db.Column(db.String(255))
    phone = db.Column(db.String(15))   

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tickets = Ticket.query.all()
    return render_template('index.html', tickets=tickets)

@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    ip_address = request.remote_addr
    
    # Retrieve JSON data from the request body
    data = request.json

    selected_hardware = data.get('hardware')
    # comments = data.get('comments')
    # phone = data.get('phone')
    comments = Markup.escape(data.get('comments'))  # Sanitize comments to prevent XSS
    phone = Markup.escape(data.get('phone'))  # Sanitize phone to prevent XSS
    # Use the get_hostname function to get the hostname associated with the client's IP
    client_hostname = get_hostname(ip_address)

    # Create a new Ticket instance and add it to the database
    ticket = Ticket(
        hardware=selected_hardware, 
        ip_address=ip_address, 
        client_hostname=client_hostname,
        comments=comments,
        phone=phone
    )
    db.session.add(ticket)
    db.session.commit()

    return jsonify({'message': f"Ticket submitted successfully with ID: {ticket.id}"})

@app.route('/get_tickets')
def get_tickets():
    tickets = Ticket.query.all()
    return render_template('tickets.html', tickets=tickets)

@app.route('/update_status', methods=['POST'])
def update_status():
    ticket_id = request.form.get('ticket_id')
    status = request.form.get('status')

    ticket = Ticket.query.get(ticket_id)
    if ticket:
        ticket.status = status
        db.session.commit()

    return redirect('/get_tickets')           

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5555, debug=True)
