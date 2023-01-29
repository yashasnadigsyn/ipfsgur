from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests, os
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'IMAGES'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webm', 'tiff'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form["ipfsgur"] == "upload":
            return redirect(url_for('upload_page'))
        if request.form["ipfsgur"] == "find":
            return redirect(url_for('find_page'))
        return None

    elif request.method == 'GET':
        url = 'https://ipfsgur.pythonanywhere.com/'
        #gateway = 'https://w3s.link/ipfs/'

        r = requests.get(url+'images')
        cids = r.json()['cids']

        return render_template('index.html', len=len(cids), cids=cids, url='http://cloudflare-ipfs.com/ipfs/')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'No file uploaded!'
        file1 = request.files['file1']

        if file1.filename == '':
            return 'No file uploaded!'
        if not file1.filename.split('.')[-1] in ALLOWED_EXTENSIONS:
            return 'Only images allowed!'
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        if request.form.get('public_name') == 'on':
            public = 'true'
        else:
            public = 'false'
        img = Image.open(f'IMAGES/{file1.filename}')
        img.save(f'IMAGES/{file1.filename}', optimize=True, quality=20)
        url = 'http://ipfsgur.pythonanywhere.com/ipfsgur'
        my_img = {'image': open(f'IMAGES/{file1.filename}', 'rb')}
        payload = {'public':public}
        r = requests.post(url, files=my_img, data=payload)
        print(r)
        cid = r.json()['Content_ID']
        os.remove(f'IMAGES/{file1.filename}')
        return f'The Content ID is: {cid} <br> Your image link is: <a href="http://cloudflare-ipfs.com/ipfs/{cid}">link</a>'
    return render_template('upload.html')

@app.route('/find', methods=['GET', 'POST'])
def find_page():
    if request.method == 'POST':
        cid = request.form.get('cid_name')
        url= 'http://cloudflare-ipfs.com/ipfs/'
        return redirect(url+cid.strip(), code=302)
    elif request.method == 'GET':
        return render_template('find.html')

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, port=8200)