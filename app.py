from flask import Flask, request, render_template
import os
import subprocess
import json
import time
import signal

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
SCRIPTS_DB = 'scripts/running_scripts.json'

# Ensure directories and files exist
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
        
        # Start the script in the background
        try:
            process = subprocess.Popen(
                ['python3', file_path],
                stdout=open(f'logs/{file.filename}.log', 'w'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid  # Create a new process group
            )
            # Store process info
            running_scripts = load_running_scripts()
            running_scripts[file.filename] = {
                'pid': process.pid,
                'file_path': file_path,
                'started_at': time.ctime()
            }
            save_running_scripts(running_scripts)
            output = f"Script {file.filename} uploaded and running (PID: {process.pid}). Check logs at logs/{file.filename}.log."
        except Exception as e:
            output = f"Error running script: {str(e)}"
        
        return render_template('index.html', output=output)
    
    return render_template('index.html', output="Invalid file. Please upload a .py file.")

# Optional: Stop a script (for future expansion)
@app.route('/stop/<filename>')
def stop_script(filename):
    running_scripts = load_running_scripts()
    if filename in running_scripts:
        pid = running_scripts[filename]['pid']
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)  # Terminate process group
            del running_scripts[filename]
            save_running_scripts(running_scripts)
            return render_template('index.html', output=f"Script {filename} stopped.")
        except Exception as e:
            return render_template('index.html', output=f"Error stopping script: {str(e)}")
    return render_template('index.html', output="Script not found.")

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
