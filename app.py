from flask import Flask, request, redirect, url_for, send_file, render_template, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "super secret key"  # Necessary for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def create_master_schedule(file_path):
    schedules_df = pd.read_excel(file_path, sheet_name=None)
    master_schedule = pd.DataFrame()
    for student, df in schedules_df.items():
        df['Student'] = student
        master_schedule = pd.concat([master_schedule, df], ignore_index=True)
    return master_schedule

def generate_class_rosters(master_schedule):
    class_rosters = master_schedule.groupby('Class')['Student'].apply(list).reset_index()
    class_rosters.columns = ['Class', 'Students']
    return class_rosters

def save_to_excel(master_schedule, class_rosters, output_file_path):
    with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
        master_schedule.to_excel(writer, sheet_name='Master Schedule', index=False)
        class_rosters.to_excel(writer, sheet_name='Class Rosters', index=False)
    return output_file_path

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        master_schedule = create_master_schedule(file_path)
        class_rosters = generate_class_rosters(master_schedule)
        output_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'output_schedules.xlsx')
        save_to_excel(master_schedule, class_rosters, output_file_path)
        return redirect(url_for('download_file', filename='output_schedules.xlsx'))

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

import logging

# Set up logging
logging.basicConfig(filename='error.log', level=logging.DEBUG)

@app.route('/')
def upload_form():
    app.logger.info('Upload form accessed')
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('No file part')
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected file')
        flash('No selected file')
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        master_schedule = create_master_schedule(file_path)
        class_rosters = generate_class_rosters(master_schedule)
        output_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'output_schedules.xlsx')
        save_to_excel(master_schedule, class_rosters, output_file_path)
        app.logger.info(f'File processed and saved to {output_file_path}')
        return redirect(url_for('download_file', filename='output_schedules.xlsx'))

@app.route('/downloads/<filename>')
def download_file(filename):
    app.logger.info(f'File {filename} downloaded')
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)



