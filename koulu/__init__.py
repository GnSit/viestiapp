from email.mime import image
from flask import Flask, render_template, url_for, request, redirect, flash, abort
from flask_mail import Mail, Message
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from sqlalchemy import Integer
import koulu.config as config
import psycopg2
import smtplib
import imghdr
import secrets,os,json
from PIL import Image
from email.message import EmailMessage
from koulu.logic.forms import RegistrationForm, LoginForm, inlineloginform, ViestitForm

app = Flask(__name__)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
from koulu.logic.models import Members, Viesti
app.env = config.ENV
app.config['SECRET_KEY']=config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MIDIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

app.config['MAIL_SERVER']= config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = config.MAIL_ADDRESS
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return Members.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

@app.route('/test')
def test():
    users = Members.query.all()
    for user in users:
        print (user.username)
    return render_template('test.html', title='Social Home Demo',users=users)


@app.route('/', methods=['POST','GET'])
@app.route('/home', methods=['POST','GET'])
def home():
    title = 'Home'
    page = request.args.get('page', 1, type=int)
    tweets = Viesti.query.order_by(Viesti.date_posted.desc()).paginate(page=page, per_page=5)
    form = inlineloginform()
    
    if form.validate_on_submit():
        user = Members.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            
            #if current_user.is_authenticated:
            next_page = request.args.get('next')
            image_file = url_for('static', filename='profile_images/' + current_user.image_file)
            return redirect(next_page) if next_page else redirect(url_for('home', title='Social Home Demo', image_file=image_file, tweets=tweets))
        else:
            
            flash('Please check email and password', 'danger')
            
    return render_template('index.html', title=title, form=form, tweets=tweets)

@app.route('/sendemail')
def sendemail():
    msg = Message('Hello',sender ='noreply@gmail.com',recipients = ['il_driv@hotmail.com'])
    msg.body = 'Hello Flask message sent from Flask-Mail'
    msg.html="""
            <h1>Hi,</h1>
            <p>this is an example.</p>
        """
    mail.send(msg)

    flash(u'Email with activation information has been sent to the email you provided, please check your email for information and check span folder if you don\'t see our message', 'success')
    return redirect(url_for('home'))

def save_picture(form_picture):
    #to randomize the name of the pic and rename it
    random_hex = secrets.token_hex(8)
    # dealing with the file ext so we use the same ext of the pic
    _, f_ext = os.path.splitext(form_picture.filename) # the _ variable is for filename
    picture_fn = random_hex + f_ext
    pic_path = os.path.join(app.root_path, 'static/profile_images', picture_fn)
    
    # resize the image 
    output_size = (400,400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    i.save(pic_path)
    return picture_fn

@app.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        picture = save_picture(form.image_file.data)
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8','ignore')
        user = Members(username=form.username.data, email=form.email.data,password=hashed_password,image_file=picture,
                       neckname=form.neckname.data,gender=form.gender.data,location=form.location.data,description=form.description.data)
        db.session.add(user)
        db.session.commit()
        msg = Message('RGH Registration',sender ='noreply@gmail.com',recipients = ['il_driv@hotmail.com'])
        msg.body = 'Thank you for registering with us'
        msg.html="""
                <h1>Hi,</h1>
                <p>Thank you for registering with us</p>
            """
        mail.send(msg)
        flash(u'Account created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Members.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            # ternary conditional to direct the user to the page he came from if it is on the url get params
            # else if it doesn't exist on url redirect to home page
            flash('You are logged in', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Please check email and password', 'danger')
    return render_template('login.html', title='Social Home Demo-Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    image_file = url_for('static', filename='profile_images/' + current_user.image_file)
    return render_template('profile.html', title='Profile', image_file=image_file)

@app.route('/tweet/new', methods=['POST','GET'])
@login_required
def new_tweet():
    form = ViestitForm()
    if form.validate_on_submit():
        viesti = Viesti(title=form.title.data, content = form.content.data, author=current_user)
        db.session.add(viesti)
        db.session.commit()
        flash('Tweet has been added, Thank you', 'success')
        tweet_id = viesti.id
        return redirect(url_for('home'))
    
    return render_template('newviesti.html', title='Social Home Demo-New viesti', form=form)

@app.route("/tweet/<int:tweet_id>")
def tweet(tweet_id):
    tweet = Viesti.query.get_or_404(tweet_id)
    return render_template('tweet.html', title=tweet.title, tweet=tweet)


@app.route("/update/<int:tweet_id>", methods=['POST','GET'])
@login_required
def update_tweet(tweet_id):
    tweet = Viesti.query.get_or_404(tweet_id)
    if tweet.author != current_user:
        abort(403)
    form = ViestitForm()
    if form.validate_on_submit():
        tweet.title = form.title.data
        tweet.content = form.content.data
        db.session.commit()
        flash('The tweet has been Updated successfully','success')
        return redirect(url_for('tweet', tweet_id=tweet.id))
    elif request.method == 'GET':
        form.title.data = tweet.title
        form.content.data = tweet.content
        
    return render_template('tweeta.html', title='Update Tweet', form=form)


@app.route("/delete/<int:tweet_id>", methods=['POST'])
@login_required
def delete_tweet(tweet_id):
    tweet = Viesti.query.get_or_404(tweet_id)
    if tweet.author != current_user:
        abort(403)
    db.session.delete(tweet)
    db.session.commit()
    flash('The tweet has been Deleted successfully','success')
    return redirect(url_for('home'))
    

@app.route("/user/<string:username>")
@login_required
def user_viestit(username):
    page = request.args.get('page', 1, type=int)
    user = Members.query.filter_by(username=username).first_or_404()
    viestit = Viesti.query.filter_by(author=user).order_by(Viesti.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_viestit.html', viestit=viestit, user=user)

import random
@app.route('/my')
def test1():
    form = RegistrationForm()
    with open('females20.json') as f:
        data = json.load(f)
        

        for n in data['results']:
            gender = n['gender']
            name1 = n['name']
            email1 = n['email']
            location = n['location']['country']
            description = n['location']['timezone']            
            neckname1 = n['login']
            age = random.randint(18, 39)
            dob = n['dob']
            registered = n['registered']

            form.username.data =  name1['first']+' '+name1['last']
            form.neckname.data = neckname1['username']
            form.email.data = email1
            form.gender.data = gender
            form.location.data = location
            form.description.data = description['description']
            form.age.data = age
            
            
            hashed_password=bcrypt.generate_password_hash('testing').decode('utf-8','ignore')
            user = Members(username=form.username.data, email=form.email.data,password=hashed_password,
                        neckname=form.neckname.data,gender=form.gender.data,location=form.location.data,description=form.description.data)
            # db.session.add(user)
            # db.session.commit()
            return render_template('regfromjson.html', form=form)
    return render_template('index.html')


@app.route('/showthis', methods=['POST','GET'])
def showjson():
    source = request.args.get('source')
    form = RegistrationForm()
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = ("males20.json")
    data = json.load(open(json_url))
    
    d=data['results']
    form.username.data = d[int(source)]['name']['first'] +' '+ d[int(source)]['name']['last']
    form.gender.data = d[int(source)]['gender']
    form.location.data = d[int(source)]['location']['country']
    form.description.data = d[int(source)]['location']['timezone']['description']
    form.age.data = random.randint(17, 39)
    form.neckname.data = d[int(source)]['login']['username']
    form.email.data = d[int(source)]['email']
    form.password.data = d[int(source)]['login']['password']
    
    if form.validate_on_submit():
        picture = save_picture(form.image_file.data)
        hashed_password=bcrypt.generate_password_hash('testing').decode('utf-8','ignore')
        user = Members(username=form.username.data, gender = form.gender.data, location = form.location.data,
                       description=form.description.data, age = form.age.data, neckname = form.neckname.data,
                       email=form.email.data, password = hashed_password, image_file = picture)
        db.session.add(user)
        db.session.commit()
        
    return render_template('regfromjson.html',s=int(source), d=d, form=form)