from flask import Flask, request, render_template
import os
import json
import time
from vercel_serverless import VercelResponse  # Custom wrapper for Vercel

app = Flask(__name__, template_folder="../templates", static_folder="../static")
UPLOAD_FOLDER = 'uploads'
SCRIPTS_DB = 'scripts/running_scripts.json'

# Ensure directories exist (Vercel’s /tmp for writable storage)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('scripts', exist_ok=True)
if not os.path.exists(SCRIPTS_DB):
    with open(SCRIPTS_DB, 'w') as f:
        json.dump({}, f)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_running_scripts():
    try:
        with open(SCRIPTS_DB, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_running_scripts(scripts):
    with open(SCRIPTS_DB, 'w') as f:
        json.dump(scripts, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html', output=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', output="No file uploaded.")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', output="No file selected.")
    
    if file and file.filename.endswith('.py'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Simulate running the script (Vercel serverless can’t run persistent processes)
        try:
            # Store script info (no actual background process in Vercel)
            running_scripts = load_running_scripts()
            running_scripts[file.filename] = {
                'file_path': file_path,
                'started_at': time.ctime()
            }
            save_running_scripts(running_scripts)
            output = f"Script {file.filename} uploaded. Note: Continuous execution requires external service."
        except Exception as e:
            output = f"Error processing script: {str(e)}"
        
        return render_template('index.html', output=output)
    
    return render_template('index.html', output="Invalid file. Please upload a .py file.")

# Vercel serverless handler
def handler(event, context):
    return VercelResponse(app)
