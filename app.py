from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ampken-2026-secret-key'

# ── Heroku Force HTTPS Hook ──────────────────
@app.before_request
def force_https():
    # Heroku forwards the original protocol in this header
    if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# ── Existing routes ──────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/executive')
def executive():
    return render_template('executive.html')

@app.route('/membership')
def membership():
    return render_template('membership.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

# ── Registration ─────────────────────────────

REGISTRATIONS_CSV = 'registrations.csv'

def save_registration(data):
    file_exists = os.path.isfile(REGISTRATIONS_CSV)
    with open(REGISTRATIONS_CSV, 'a', newline='', encoding='utf-8') as f:
        fieldnames = [
            'timestamp', 'first_name', 'last_name', 'email',
            'phone', 'organisation', 'profession', 'attendance',
            'dietary', 'message'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def send_confirmation_email(to_email, first_name):
    SMTP_USER = 'medicalphysicskenya@gmail.com'
    SMTP_PASS = 'YOUR_GMAIL_APP_PASSWORD'  # Replace with Gmail App Password

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Registration Confirmed — AMPKen 1st Medical Physics Conference 2026'
    msg['From'] = f'AMPKen <{SMTP_USER}>'
    msg['To'] = to_email

    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:#0d1b2a;padding:2rem;text-align:center;">
        <h2 style="color:#d4a017;margin:0;">AMPKen</h2>
        <p style="color:rgba(255,255,255,0.7);margin:.5rem 0 0;font-size:.9rem;">
          Association of Medical Physicists of Kenya
        </p>
      </div>
      <div style="padding:2rem;border:1px solid #e2e8f0;">
        <h3 style="color:#0d1b2a;">Dear {first_name},</h3>
        <p style="color:#3d4f61;line-height:1.7;">
          Thank you for registering for the <strong>1st AMPKen Medical Physics Conference 2026</strong>.
          Your registration has been received successfully.
        </p>
        <div style="background:#f6f8fb;border-left:4px solid #d4a017;padding:1rem 1.5rem;margin:1.5rem 0;border-radius:4px;">
          <p style="margin:0;color:#0d1b2a;font-weight:600;">Conference Details</p>
          <p style="margin:.5rem 0 0;color:#3d4f61;font-size:.9rem;line-height:1.7;">
            📅 <strong>Date:</strong> November 5–7, 2026<br>
            📍 <strong>Venue:</strong> Nairobi, Kenya<br>
            🌐 <strong>Website:</strong> www.ampken.org
          </p>
        </div>
        <p style="color:#3d4f61;line-height:1.7;">
          We will send further details including the programme and venue closer to the event.
          For enquiries contact
          <a href="mailto:medicalphysicskenya@gmail.com" style="color:#b8860b;">medicalphysicskenya@gmail.com</a>.
        </p>
        <p style="color:#0d1b2a;font-weight:600;">The AMPKen Team</p>
      </div>
      <div style="background:#f6f8fb;padding:1rem;text-align:center;font-size:.8rem;color:#7a8fa3;">
        © 2026 AMPKen · www.ampken.org
      </div>
    </div>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            server.sendmail(SMTP_USER, SMTP_USER, msg.as_string())
    except Exception as e:
        print(f"Email error: {e}")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'timestamp':    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'first_name':   request.form.get('first_name', '').strip(),
            'last_name':    request.form.get('last_name', '').strip(),
            'email':        request.form.get('email', '').strip(),
            'phone':        request.form.get('phone', '').strip(),
            'organisation': request.form.get('organisation', '').strip(),
            'profession':   request.form.get('profession', '').strip(),
            'attendance':   request.form.get('attendance', '').strip(),
            'dietary':      request.form.get('dietary', '').strip(),
            'message':      request.form.get('message', '').strip(),
        }

        required = ['first_name', 'last_name', 'email', 'phone', 'organisation', 'profession', 'attendance']
        for field in required:
            if not data[field]:
                flash('Please fill in all required fields.', 'error')
                return render_template('register.html')

        save_registration(data)

        try:
            send_confirmation_email(data['email'], data['first_name'])
        except Exception as e:
            print(f"Email error: {e}")

        flash(f"Thank you {data['first_name']}! Your registration has been received. Check your email for confirmation.", 'success')
        return redirect(url_for('register'))

    return render_template('register.html')


# ── Admin: view registrations ─────────────────

@app.route('/admin/registrations')
def view_registrations():
    registrations = []
    if os.path.isfile(REGISTRATIONS_CSV):
        with open(REGISTRATIONS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            registrations = list(reader)
    return render_template('admin_registrations.html',
                           registrations=registrations,
                           total=len(registrations))


if __name__ == '__main__':
    app.run(debug=False)
