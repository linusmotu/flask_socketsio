import os
from flask import render_template, request, send_from_directory, url_for, redirect, flash, Response
from werkzeug.utils import secure_filename
from flask import current_app
import subprocess
import json
from sockets import app
from sockets import mqtt
from sockets import Camera

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'csv', 'jpg', 'jpeg', 'png'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('query.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'upload' not in request.files:
            flash('No file part')
            return redirect(url_for('index'))
            #redirect
        f = request.files['upload']
        if f.filename == '':
            flash('No selected file')
            return redirect(url_for('index'))
            #redirect
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename = filename))
        return redirect(url_for('index'))

@app.route('/update_configs', methods=['POST'])
def update_configs():
    changes = request.form['text']

    # check if key exists before updating
    # with open('configs.json') as json_data:
    #     d = json.load(json_data)

    if 'toMaster' in request.form:
        print(changes)
        os.chdir("/home/pi/random_pi_forest/distRF/bin/master_node/")
        command = 'jq \'. + {{{0}}}\' configs.json > configs.tmp && mv configs.tmp configs.json'.format(changes)
        os.system(command)
        mqtt.publish('master/config/flask', changes)
        flash('Successfully sent to master')
    elif 'toSlaves' in request.form:
        print(changes)
        # os.chdir("/home/pi/random_pi_forest/distRF/bin/slave_node/")
        # command = 'jq \'. + {{{0}}}\' configs.json > configs.tmp && mv configs.tmp configs.json'.format(changes)
        # os.system(command)
        mqtt.publish('slave/config', changes)
        flash('Successfully sent to slaves')
    else:
        return redirect(url_for('index'))
        # test

    # proc = subprocess.Popen(["cat /home/pi/random_pi_forest/distRF/bin/master_node/configs.json | tr '\n' ' '"], stdout=subprocess.PIPE, shell=False)
    proc = subprocess.Popen(["cat /home/pi/random_pi_forest/distRF/bin/master_node/configs.json"], stdout=subprocess.PIPE, shell=True)
    # proc = subprocess.Popen(["jq '.' mock.json"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()


    pairs = out.decode('utf-8').split('\n')
    # return render_template('json_response.html', pairs=pairs)
    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    uploads = os.path.join(current_app.root_path, 'uploads')
    print(uploads)
    return send_from_directory(directory = uploads, filename = filename)

@app.route('/live')
def live():
    return render_template('live.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
