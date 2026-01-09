from flask import Flask, request, jsonify, g
from flask_mail import Mail, Message
from flask_cors import CORS
import smtplib
import mysql.connector

app = Flask(__name__)
cors = CORS(app, resources={r"/send-email": {"origins": "http://127.0.0.1:5502/"}})

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',       # Change to your MySQL server
    'user': 'contact',   # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'contact_form_db'  # Replace with your MySQL database name
}

def get_db():
    """Establish a database connection."""
    if not hasattr(g, 'contact'):
        g.contact = mysql.connector.connect(**DB_CONFIG)
        g.db_cursor = g.contact.cursor()
    return g.contact, g.db_cursor

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection."""
    contact = getattr(g, 'contact', None)
    if contact is not None:
        contact.close()

def ensure_table_exists():
    """Check if the 'contacts' table exists and create it if missing."""
    db, cursor = get_db()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            message TEXT NOT NULL
        )
    """)
    db.commit()

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'aryanahmad478@gmail.com'  # Your Gmail address
app.config['MAIL_PASSWORD'] = 'aryanahmad.2004'  # **Use an App Password!**
app.config['MAIL_DEFAULT_SENDER'] = 'aryanahmad478@gmail.com'

mail = Mail(app)

@app.route('/send-email', methods=['POST'])
def send_email():
    """Handles email sending and saves data to MySQL database."""
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        message = data.get("message")

        if not name or not email or not subject or not message:
            return jsonify({"error": "All fields are required"}), 400

        # Save data to MySQL
        db, cursor = get_db()
        cursor.execute("INSERT INTO contacts (name, email, subject, message) VALUES (%s, %s, %s, %s)", 
                       (name, email, subject, message))
        db.commit()

        # Prepare Email
        msg = Message(subject, recipients=['aryanahmad478@gmail.com'])  # Your email
        msg.html = f"""
        <h2>New Contact Form Message</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong></p>
        <p>{message}</p>
        """

        # Send Email
        try:
            mail.send(msg)
            return jsonify({"message": "Message sent successfully!"}), 200
        except smtplib.SMTPAuthenticationError:
            print("SMTP Error: Authentication failed. Check your email/password.")
            return jsonify({"error": "SMTP Authentication Error"}), 500
        except smtplib.SMTPConnectError:
            print("SMTP Error: Unable to connect to the email server.")
            return jsonify({"error": "SMTP Connection Error"}), 500
        except smtplib.SMTPException as e:
            print("SMTP Error:", str(e))
            return jsonify({"error": f"SMTP Error: {str(e)}"}), 500

    except Exception as e:
        print("General Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            ensure_table_exists()
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
    app.run(debug=True, host='0.0.0.0', port=5000)
@app.route("/")
def home():
    return "Server running"

if __name__ == "__main__":
    app.run(debug=True)

