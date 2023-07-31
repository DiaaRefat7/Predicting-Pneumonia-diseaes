from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np
from tensorflow.keras import models
import matplotlib.pyplot as plt
from skimage.segmentation import slic, mark_boundaries
from lime import lime_image


UPLOAD_FOLDER = 'received_files'
ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'png') # add any other photo extensions
PHOTO_DIMS = (128,128,3) # (height, width, channels)
SECRET_KEY = 'secretkey'
PREDICTION_MODEL_PATH = 'code\effecentnet.h5'
SEGMENTATION_MODEL_PATH = 'code\effecentnet.h5'
SEGMENTED_PHOTOS_FOLDER = 'static\segmented_photos'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def range_val(checkbox,value):
    if checkbox == 'on':
        return value
    else:
        return -1
    
def to_text(value):
    if value == 'on':
        return 'on'
    else:
        return 'off'
    
def predict(file_path):
    model = models.load_model(PREDICTION_MODEL_PATH)
    image=Image.open(file_path)
    image=image.resize((128,128))
    image_arr = np.array(image.convert('RGB'))
    image_arr.shape = (1, 128, 128, 3)
    result = model.predict(image_arr)
    ind = np.argmax(result)
    answer = ""
    if ind == 0:
        answer = "Normal"
    elif ind == 1:
        answer = "Pneumonia"
    return answer

def segmentation (image,filename):
    model = models.load_model(SEGMENTATION_MODEL_PATH)
    image=Image.open(image)   
    image=image.resize((128,128))
    image_arr = np.array(image)
    plt.figure()
    image_arr = image_arr / 255
    explainer = lime_image.LimeImageExplainer()
    explanation = explainer.explain_instance(image_arr.astype('double'), model.predict,  
                                       top_labels=10, hide_color=0, num_samples=1000)
    temp, mask = explanation.get_image_and_mask(explanation.top_labels[0], positive_only=True, num_features=10, hide_rest=False)
    fig,ax = plt.subplots()
    ax.imshow(mark_boundaries(temp, mask))
    ax.axis('off')
    plt.axis('off')
    plt.savefig(os.path.join(SEGMENTED_PHOTOS_FOLDER,filename),transparent=True,format='png')
    #plt.show()
    return os.path.join(SEGMENTED_PHOTOS_FOLDER,filename)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class FormData(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    number = db.Column(db.String(), nullable=False)
    age = db.Column(db.Integer(), nullable=False)
    gender = db.Column(db.String(), nullable=False)
    marital_status = db.Column(db.String(), nullable=False)
    message = db.Column(db.String(), nullable=False)
    
    cough_val = db.Column(db.Integer(), nullable=False)
    fever_val = db.Column(db.Integer(), nullable=False)
    breath_shortness_val = db.Column(db.Integer(), nullable=False)
    chest_pain_val = db.Column(db.Integer(), nullable=False)
    chills_val = db.Column(db.Integer(), nullable=False)
    headache_val = db.Column(db.Integer(), nullable=False)
    muscle_aches_val = db.Column(db.Integer(), nullable=False)
    nausea_val = db.Column(db.Integer(), nullable=False)
    confusion_val = db.Column(db.Integer(), nullable=False)
    
    file_name = db.Column(db.String(), nullable=False)
    result = db.Column(db.String(), nullable=False)


#uncomment in first run, then comment afterwards

#------------------------

#with app.app_context():
 # db.create_all()

#------------------------



@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact_us.html')


@app.route('/form', methods=['GET', 'POST'])
def form_page():
    file_name = ""
    result = "nothing"
    if request.method == 'POST' :
        # first set of data
        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        age = request.form['age']
        gender = request.form['gender']
        marital_status = request.form['marital-status']
        message = request.form['message']

        # second set of data

        #checkbox selections
        c1 = to_text(request.form.get('c1'))
        c2 = to_text(request.form.get('c2'))
        c3 = to_text(request.form.get('c3'))
        c4 = to_text(request.form.get('c4'))
        c5 = to_text(request.form.get('c5'))
        c6 = to_text(request.form.get('c6'))
        c7 = to_text(request.form.get('c7'))
        c8 = to_text(request.form.get('c8'))
        c9 = to_text(request.form.get('c9'))

        #checkbox values
        c1_val = range_val(c1,request.form['c1-val'])
        c2_val = range_val(c2,request.form['c2-val'])
        c3_val = range_val(c3,request.form['c3-val'])
        c4_val = range_val(c4,request.form['c4-val'])
        c5_val = range_val(c5,request.form['c5-val'])
        c6_val = range_val(c6,request.form['c6-val'])
        c7_val = range_val(c7,request.form['c7-val'])
        c8_val = range_val(c8,request.form['c8-val'])
        c9_val = range_val(c9,request.form['c9-val'])

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #received_data = (name,number,email,age,gender,marital_status,message,c1,c2,c3,c4,c5,c6,c7,c8,c9,c1_val,c2_val,c3_val,c4_val,c5_val,c6_val,c7_val,c8_val,c9_val,file_name)
        result = predict(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        form_entry = FormData(  name = name,
                                number = number,
                                email = email,
                                age = int(age),
                                gender = gender,
                                marital_status = marital_status,
                                message = message,
                                cough_val = c1_val,
                                fever_val = c2_val,
                                breath_shortness_val = c3_val,
                                chest_pain_val = c4_val,
                                chills_val = c5_val,
                                headache_val = c6_val,
                                muscle_aches_val = c7_val,
                                nausea_val = c8_val,
                                confusion_val = c9_val,
                                file_name = filename,
                                result = result
                              )
        db.session.add(form_entry)
        db.session.commit()
        if result == "Normal":
            return redirect(url_for('negative_result_page'))
        elif result == "Pneumonia":
            # do segmentation
            # get segmented image
            # segmented_image
            segmented_image = segmentation(os.path.join(app.config['UPLOAD_FOLDER'], filename),filename)
            session['segmented_image'] = segmented_image
            return redirect(url_for('positive_result_page'))

        

            
    return render_template('form.html')

#@app.route('/results')
#def results_page():
#    pass
@app.route('/negative')
def negative_result_page():
    return render_template('negative.html')


@app.route('/positive')
def positive_result_page():
    img = session['segmented_image']
    return render_template('positive.html', segmented_image = img)
app.run()