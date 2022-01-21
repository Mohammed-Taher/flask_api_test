import os
from flask import Flask, request, send_from_directory
from flask.json import jsonify
from actions import bp as actionsbp
from filters import bp as filtersbp
from android import bp as androidbp
from helpers import allowed_extension, upload_to_s3
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

app.config['S3_BUCKET'] = 'image-storage-api'
app.config['S3_KEY'] = 'AKIA2Y4VVY3L5BZJWWD4'
app.config['S3_SECRET'] = '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'
app.config['S3_LOCATION'] = 'https://image-storage-api.s3.eu-west-3.amazonaws.com/uploads'

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DOWNLOAD_FOLDER = 'downloads/'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.secret_key = 'SECRET_KEY'
app.register_blueprint(actionsbp)
app.register_blueprint(filtersbp)
app.register_blueprint(androidbp)


@app.route('/images', methods=['POST'])
def upload_image():
    if request.method == 'POST':

        if 'file' not in request.files:
            return jsonify({'error': 'No file was selected'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file was selected'}), 400

        if not allowed_extension(file.filename):
            return jsonify({'error': 'The extension is not supported.'}), 400

        # filename, filepath = get_secure_filename_filepath(file.filename)

        output = upload_to_s3(file, app.config['S3_BUCKET'])
        # file.save(filepath)

        return jsonify({
            'message': 'File successfully uploaded',
            'filename': output,
        }), 201


@app.route('/downloads/<name>')
def download_file(name):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], name)
