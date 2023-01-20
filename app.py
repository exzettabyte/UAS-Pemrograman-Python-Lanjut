from flask import Flask, request
from source.file_upload.watermark import page, execute

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return execute(request)
    return page()

