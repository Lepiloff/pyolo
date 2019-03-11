import os, sys
from flask import Flask, request, redirect, url_for, render_template, flash, jsonify, session
from config import Configuration
from werkzeug.utils import secure_filename
import uuid
import json


basedir = os.path.abspath(os.path.join(os.path.dirname( __file__ )))

UPLOAD_FOLDER = basedir + '/uploads'
ALLOWED_EXTENSIONS = set(["jpg"])

app = Flask(__name__)
app.config.from_object(Configuration)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# Added pyolo folder
base = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(base)
from pyolo.detect import run

#Connect to redis DB
from redis import Redis
from rq import Queue
print(sys.path)
q = Queue(connection=Redis())


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/done/")
def result():
    result = session['result']
    return jsonify(result)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        result = {}
        # check if the post request has the file part
        if 'file' not in request.files:
            result['response'] = 'No file part'
            return jsonify(result)
        #Check that file type jpg
        for f in request.files.getlist('file'):
            if not allowed_file(f.filename):
                result['responce'] = 'Only JPG file can be used'
                return jsonify(result)
        else:
            new_file_folder = uuid.uuid4().hex
            os.makedirs(UPLOAD_FOLDER + "/" + new_file_folder)
            for f in request.files.getlist('file'):
                filename = secure_filename(f.filename)
                f.save(os.path.join(UPLOAD_FOLDER, new_file_folder, filename))
            # Add new image folder
            f_img = os.path.join(UPLOAD_FOLDER, new_file_folder)

            #job queue, add RUN function to thread
            job = q.enqueue(run, f_img)
            if job.status == "failed":
                result['response'] = 'Job failed'
                return jsonify(result)
            while job.result is None:
                pass
            else:
                result_img = job.result
                session['result'] = result_img #Add dict  of all images with each count values to session
                #return redirect(url_for("result", count=count))
                return redirect(url_for("result"))
    #return render_template("index.html")
    return ('', 204)

"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ### check if the post request has the file part
        result = {}
        ###check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            # return redirect(request.url)
            result['responce'] = 'No file part'
            return jsonify(result)
        file = request.files['file']
        ### if user does not select file, browser also
        ### submit a empty part without filename
        if file.filename == '':
            # flash('NO selected file')
            result['responce'] = 'No file selected'
            return jsonify(result)
            # return redirect(request.url)
        if not allowed_file(file.filename):
            # flash("Only JPG file is used")
            result['responce'] = 'Only JPG file can be used'
            return jsonify(result)
            # return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            #img = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #count = run(img)
            #return redirect(url_for("result", count=count))
            
            img = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ###job queue, add RUN function to thread
            job = q.enqueue(run, img)
            while job.result is None:
                pass

            else:
                count = job.result
                session['count'] = count
                return redirect(url_for("result"))

    #return render_template("index.html")
    return ('', 204)
"""

