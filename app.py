import os
import cv2, imutils
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import time
now = datetime.now()

UPLOAD_FOLDER = os.getcwd()+ r'\uploads'
DOWNLOAD_FOLDER =os.getcwd()+ r'\downloads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg','png','jpe','jfif'}
OUTPUT_FOLDER = r'\static'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.secret_key = 'super secret key'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
O_file= []
output = []
style = []

@app.route('/')
def upload_file():
    global O_file, output
    O_file = r"/static/Tiger_original.jpg"
    output = os.listdir("static/")
    for i in range(len(output)):
        if output[i] == "Tiger_original.jpg":
            pass
        else:
            output[i]=os.path.join(OUTPUT_FOLDER,output[i])
    output.remove('Tiger_original.jpg')
    return render_template('__init__.html', O_file=O_file , output = output   )


@app.route('/get-text', methods=['GET', 'POST'])
def foo():
    global O_file, output, style
    if request.method == 'POST':
        style = None
        style = request.form.get('Style')
        if style == None:
            return render_template('__init__.html',O_file=O_file , output =output)
        return render_template('upload.html',style=style)


@app.route('/upload', methods=['GET', 'POST'])
def action():
    global style, O_file, output
    if request.method == 'POST':
        file = request.files['f']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(style)
            Transform(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename,style)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('__init__.html',O_file=O_file , output =output)

def Transform(path, filename, style):
    image = cv2.imread(path,1)
    image = imutils.resize(image, width=1000)
    (h, w) = image.shape[:2]
    model=style.split("\\")[-1].split(".")[0] +".t7"
    net = cv2.dnn.readNetFromTorch(model)
    blob = cv2.dnn.blobFromImage(image, 1.0, (w, h),(103.939, 116.779, 123.680), swapRB=False, crop=False)
    net.setInput(blob)
    output = net.forward()
    output = output.reshape((3, output.shape[2], output.shape[3]))
    output[0] += 103.939
    output[1] += 116.779
    output[2] += 123.680
    output = output.transpose(1, 2, 0)
    pap=DOWNLOAD_FOLDER+ "\\" + filename 
    cv2.imwrite(pap,output)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
