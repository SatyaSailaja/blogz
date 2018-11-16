from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#from hashutils import make_pw_hash,check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Sailaja123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'uMfu3ZAN7LQVnsWv'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body,owner,pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
       
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
   
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    #pw_hash = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
   
    def __init__(self, username, password):
        self.username = username
        self.password= password
        #self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login','blog','signup','index','static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#home
@app.route('/index')
def index():
     users = User.query.all() 
     return render_template('index.html', users=users)

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/index')

@app.route('/login',methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['user-name']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""

        if (len(username) >30) or (len(username) < 3) or username.isspace():
            username_error= True
            flash('Username is not  valid ')
            username = ""
        if len(password) > 30 or len(password) < 3 or password.isspace():
           password_error= True
           flash('Password is not valid')
           password = ""
        if not existing_user:
           flash("Need to signUp not an existingUser")
           username = ""
           password = ""

        if existing_user and existing_user.password == password and not username_error and not password_error:
               
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
        
            return render_template("login.html", username=username,password=password)



    return render_template('login.html')
  

   

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verifypassword']
        existing_user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verifypassword_error = ""
        
        
        if (len(username) >30) or (len(username) < 3) or username.isspace():
            username_error= True
            flash('Username is not  valid ')
            username = ""

        if len(password) > 30 or len(password) < 3 or password.isspace():
           password_error= True
           flash('Password is not valid')
           password = ""

        if password != verifypassword:
           verifypassword_error = True
           flash("Passwords don't match")
           verifypassword = "" 

        if existing_user:
            flash('Already existing User')
            
        if not username_error and not password_error and not verifypassword_error and not existing_user:
                
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            
            return render_template('signup.html',username=username,password=password,verifypassword=verifypassword)

    return render_template('signup.html')
#all posts
@app.route('/blog')
def blog():
    
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    print("**************************")
    print(user_id)
    print(blog_id)
    page = 1
       # page, app.config['POSTS_PER_PAGE'], False)
    #posts = Blog.query.order_by(Blog.id.desc()).paginate(
    #    page, 5, False)
    posts = Blog.query.order_by(Blog.id.desc()).paginate(per_page=5)
    
    
    
    if blog_id :
         post = Blog.query.filter_by(id=blog_id).first()        
         return render_template('entry.html', title=post.title,body=post.body,user=post.owner.username, 
                            pub_date=post.pub_date, userid=post.owner_id)
    if user_id:
        users = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', users=users)

    return render_template('blog.html', posts=posts)


@app.route('/newpost', methods=['POST','GET'])
def new_post():
   
    
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        owner = User.query.filter_by(username=session['username']).first()
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body,owner)     
            db.session.add(new_entry)
            db.session.commit() 
            page_id = new_entry.id
            return redirect("/blog?id={0}".format(page_id))
        else:
             return render_template('newpost.html', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    return render_template('newpost.html') 
@app.route('/delete-post', methods=['POST'])
def delete_post():

    task_id = int(request.form['id'])
    task = Blog.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

if  __name__ == "__main__":
    app.run()
