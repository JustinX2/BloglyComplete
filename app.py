"""Blogly application."""

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.debug = True

connect_db(app)
app.app_context().push() 

toolbar = DebugToolbarExtension(app)

@app.route('/')
def homepage():
    return redirect('/users')

@app.route('/users')
def list_users():
    users = User.query.all()
    return render_template('list.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        new_user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            image_url=request.form['image_url'] or None
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/users')
    return render_template('new.html')

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form.get('image_url') or user.image_url
        db.session.commit()
        return redirect('/users')
    return render_template('edit.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')

"""Expand on adding a post and also include tags"""

@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def new_post(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_post = Post(
            title=request.form['title'],
            content=request.form['content'],
            user_id=user_id
        )
        db.session.add(new_post)
        db.session.commit()

        tag_ids = request.form.getlist('tags')
        for tag_id in tag_ids:
            new_post_tag = PostTag(post_id=new_post.id, tag_id=int(tag_id))
            db.session.add(new_post_tag)
        db.session.commit()
        return redirect(f'/users/{user_id}')

    tags = Tag.query.all()
    return render_template('new_post.html', user=user, tags=tags)

"""Expand on showing a post"""
@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

"""Expand on editing a post and adding a tag"""
@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']

        new_tag_ids = [int(tag_id) for tag_id in request.form.getlist('tags')]
        existing_tag_ids = [tag.id for tag in post.tags]

        for tag_id in existing_tag_ids:
            if tag_id not in new_tag_ids:
                PostTag.query.filter_by(post_id=post_id, tag_id=tag_id).delete()

        for tag_id in new_tag_ids:
            if tag_id not in existing_tag_ids:
                db.session.add(PostTag(post_id=post_id, tag_id=tag_id))

        db.session.commit()
        return redirect(f'/posts/{post_id}')

    tags = Tag.query.all()
    return render_template('edit_post.html', post=post, tags=tags)

"""Expand on deleting a post"""
@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/users')

"""Expand on tags"""
@app.route('/tags')
def tags_index():
    tags=Tag.query.all()
    return render_template('list_tag.html', tags=tags)

@app.route('/tags/new', methods=['GET', 'POST'])
def new_tag():
    if request.method=='POST':
        name=request.form['name']
        tag=Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        return redirect('/tags')
    return render_template('add_tag.html')

@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == 'POST':
        tag.name = request.form['name']
        db.session.commit()
        return redirect('/tags')
    return render_template('edit_tag.html', tag=tag)


@app.route('/tags/<int:tag_id>/delete', methods=['GET', 'POST'])
def delete_tag(tag_id):
    Tag.query.filter_by(id=tag_id).delete()
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:tag_id>')
def show_tag(tag_id):
    tag=Tag.query.get_or_404(tag_id)
    return render_template('show_tag.html', tag=tag)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
