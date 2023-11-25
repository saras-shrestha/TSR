from flask import Flask,render_template, redirect,session, request,url_for 
import os
from werkzeug.utils import secure_filename
from keras.models import load_model
import numpy as np
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt

db=SQLAlchemy()
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///traffic.db"
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///traffic.db'
app.config['SECRET_KEY']='!tiS$@#$%^&*iT!'
# initialize the app with the extension
db.init_app(app)

class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    email=db.Column(db.String(50), nullable=False)
    username=db.Column(db.String(20), nullable=False)
    password=db.Column(db.String(50), nullable=False)

    def __init__(self,name, email, username, password):
        self.name=name
        self.email=email
        self.username=username
        self.password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
with app.app_context():
    db.create_all()

# Classes of trafic signs
classes = { 0:'Speed limit (20km/h)',
            1:'Speed limit (30km/h)',
            2:'Speed limit (50km/h)',
            3:'Speed limit (60km/h)',
            4:'Speed limit (70km/h)',
            5:'Speed limit (80km/h)',
            6:'End of speed limit (80km/h)',
            7:'Speed limit (100km/h)',
            8:'Speed limit (120km/h)',
            9:'No passing',
            10:'No passing veh over 3.5 tons',
            11:'Right-of-way at intersection',
            12:'Priority road',
            13:'Yield',
            14:'Stop',
            15:'No vehicles',
            16:'Vehicle > 3.5 tons prohibited',
            17:'No entry',
            18:'General caution',
            19:'Dangerous curve left',
            20:'Dangerous curve right',
            21:'Double curve',
            22:'Bumpy road',
            23:'Slippery road',
            24:'Road narrows on the right',
            25:'Road work',
            26:'Traffic signals',
            27:'Pedestrians',
            28:'Children crossing',
            29:'Bicycles crossing',
            30:'Beware of ice/snow',
            31:'Wild animals crossing',
            32:'End speed + passing limits',
            33:'Turn right ahead',
            34:'Turn left ahead',
            35:'Ahead only',
            36:'Go straight or right',
            37:'Go straight or left',
            38:'Keep right',
            39:'Keep left',
            40:'Roundabout mandatory',
            41:'End of no passing',
            42:'End no passing vehicle > 3.5 tons' }


def image_processing(img):
    model = load_model('./model/TSR.h5')
    data=[]
    image = Image.open(img)
    image = image.resize((30,30))
    data.append(np.array(image))
    X_test=np.array(data)
    
    # Y_pred = model.predict_classes(X_test)
    Y_pred = np.argmax(model.predict(X_test), axis=-1)

    # Y_pred=(model.predict(X_test) > 0.5).astype("int32")
    print("hfh",Y_pred)
    return Y_pred

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        #handle request
        name=request.form['name']
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']

        new_user=User(name=name, email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        #handle request
        username=request.form['username']
        password=request.form['password']
        
        user=User.query.filter_by(username=username).first()
        print("jjsgkhduavbskldgvb")
        session['name']=user.name
        session['username']=user.username
        session['email']=user.email
        return redirect('/dashboard')
        # if user and user.check_password(password):
            # session['name']=user.name
            # session['username']=user.username
            # session['email']=user.email
        #     return redirect('/dashboard')
        # else:
        #     return render_template('home.html',error='Invalid User')
    
@app.route('/dashboard')
def dashboard():
    if session['username']:
        return render_template('dashboard.html')
    return redirect('/')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method=='POST':
        imagefile=request.files['imagefile']
        image_path="./image_predict/"+imagefile.filename
        imagefile.save(image_path)

        #Make predicion
        result = image_processing(image_path)

        s = [str(i) for i in result]
        a = int("".join(s))
        result = "Predicted Traffic Symbol is: " +classes[a]
        # os.remove(image_path)
        return result
    return None

if __name__=='__main__':
    app.run(port=3000, debug=True)