from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Sailaja123@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
   

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def blog():
    blog_id = request.args.get('id')

    if blog_id == None:
         #posts = Blog.query.all() 
         posts = Blog.query.order_by(Blog.id.desc()).all()
         return render_template('blog.html', posts=posts)
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog') 
        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html')

if  __name__ == "__main__":
    app.run()
