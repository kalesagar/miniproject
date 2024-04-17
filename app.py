
from flask import Flask, render_template, request, redirect, url_for, flash
from users.create_user_pool import create_user, validate_user
from storage.create_s3_bucket import upload_file, retrieve_files, get_presigned_url
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        response = validate_user(username=username, password=password)
        if response:
            flash('Login successful', "success")
            return render_template('upload.html', username=username)
        else:
            flash('Login failed', "error")
            return render_template('login.html', login_failed=True)
    registration_success = False 
    return render_template('login.html', registration_success=registration_success)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user_id = create_user(username, password, email)
        if user_id:
            registration_success = True  # Set this flag to True after successful registration
            flash('Registration successful', 'success')
            return redirect(url_for('login', registration_success=registration_success))
    else:
        return render_template('registration.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(filename)
        try:
            upload_file("ccgroup18-bucket", filename)
            flash('Upload successful')
        except Exception as e:
            flash(str(e), 'error')
        finally:
            os.remove(filename)
        return render_template('upload.html', upload_success=True)

@app.route('/photos')
def photos():
    try:
        response = retrieve_files("ccgroup18-bucket")
        photos = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith(('.png', '.jpg', '.jpeg'))]
        photo_urls = []
        for photo in photos:
            photo_urls.append(get_presigned_url("ccgroup18-bucket", photo))
        return render_template('photos.html', photos=photo_urls)
    except Exception as e:
        return str(e)
    
# main driver function
if __name__ == '__main__':
    app.run()