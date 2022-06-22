from xml.etree.ElementTree import Comment
from app import app
from app.models import User, db, Grid, Post, Likes, Comment
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app.profileforms import BioForm, GridForm, FollowForm, PostForm, CommentForm
from datetime import datetime


@app.route('/profile-editor', methods=['GET', 'POST'])
@login_required
def profile_editor():
    bio_form = BioForm()
    grid_form = GridForm()
    grid = Grid.query.filter_by(user_id=current_user.id).order_by(
        Grid.grid_position).all()
    if request.method == 'POST':
        if bio_form.validate_on_submit():
            user = User.query.get(current_user.id)
            user.bio = bio_form.bio.data
            db.session.commit()
            flash('Bio Edit Successful!')
            return redirect(url_for('user', username=current_user.username))
        if grid_form.validate_on_submit():
            tile = Grid.query.filter_by(
                user_id=current_user.id, grid_position=grid_form.data['location']).first()
            tile.artist = grid_form.data['artist']
            tile.track = grid_form.data['track']
            tile.track_img = grid_form.data['img']
            tile.grid_position = grid_form.data['location']
            db.session.commit()
            flash('Grid Edit Successful!')
            return redirect(url_for('user', username=current_user.username))
    return render_template('profile_editor.html', bio_form=bio_form, grid_form=grid_form, grid=grid)


@app.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    session['url'] = url_for('user', username=username)
    post_form = PostForm()
    page = request.args.get('page', 1, type=int)
    pg_owner = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(location_id=pg_owner.id).order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=current_user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=current_user.username, page=posts.prev_num) \
        if posts.has_prev else None
    grid = Grid.query.filter_by(user_id=pg_owner.id).order_by(
        Grid.grid_position).all()
    artist_track = []
    for i in range(9):
        if grid[i].artist != None:
            artist_track.append([grid[i].artist, grid[i].track])
        else:
            artist_track.append([0, 0])
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data,
                    user_id=current_user.id, location_id=pg_owner.id)
        db.session.add(post)
        db.session.commit()
        flash('Post Successful!')
        return redirect(url_for('user', username=username))
    user = User.query.filter_by(username=username).first_or_404()
    follow_form = FollowForm()
    loadedposts = [i.id for i in posts.items]
    like = Likes.query.filter(Likes.post_id.in_(
        loadedposts)).filter_by(user_id=current_user.id).all()
    liked_posts = [i.post_id for i in like]
    return render_template('user.html', user=user, posts=posts.items, follow_form=follow_form, post_form=post_form, artist_track=artist_track, grid=grid, next_url=next_url, prev_url=prev_url, liked_posts=liked_posts)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# error handeling


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Follow and un follow routes


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('user', username=current_user.username))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are now following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('user', username=current_user.username))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('user', username=current_user.username))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You have unfollowed {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('user', username=current_user.username))

# Route for Feed page so public can find users to follow!


@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    session['url'] = url_for('explore')
    user = User.query.filter_by(username=current_user.username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    post_form = PostForm()
    loadedposts = [i.id for i in posts.items]
    like = Likes.query.filter(Likes.post_id.in_(
        loadedposts)).filter_by(user_id=current_user.id).all()
    liked_posts = [i.post_id for i in like]
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post Successful!')
        return redirect(url_for('explore'))
    return render_template('feed.html', title='Explore', posts=posts.items, user=user, post_form=post_form, next_url=next_url, prev_url=prev_url, liked_posts=liked_posts)


@app.route('/followingfeed', methods=['GET', 'POST'])
@login_required
def following():
    session['url'] = url_for('following')
    user = User.query.filter_by(username=current_user.username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('following', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('following', page=posts.prev_num) \
        if posts.has_prev else None
    post_form = PostForm()
    loadedposts = [i.id for i in posts.items]
    like = Likes.query.filter(Likes.post_id.in_(
        loadedposts)).filter_by(user_id=current_user.id).all()
    liked_posts = [i.post_id for i in like]
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post Successful!')
        return redirect(url_for('following'))
    return render_template('following_feed.html', title='Explore', posts=posts.items, user=user, post_form=post_form, next_url=next_url, prev_url=prev_url, liked_posts=liked_posts)


@app.route('/delete/<id>')
@login_required
def removePost(id):
    post = Post.query.filter_by(id=id[:36]).first()
    if post.user_id == current_user.id or post.location_id == current_user.id:
        db.session.delete(post)
        db.session.commit()
        flash(f'Post Removed', 'danger')
        return redirect(session['url'])
    else:
        flash(f'Sorry, You can only remove posts which you have created or are on your page.', 'danger')
        return redirect(url_for('user', username=current_user.username))


@app.route('/like/<id>')
@login_required
def likePost(id):
    like = Likes(current_user.id, id)
    post = Post.query.filter_by(id=id).first()
    if Likes.query.filter_by(user_id=current_user.id).filter_by(post_id=post.id).first():
        like = Likes.query.filter_by(
            user_id=current_user.id).filter_by(post_id=post.id).first()
        post.likes -= 1
        db.session.delete(like)
        db.session.commit()
        flash(f'Post Unliked')
    else:
        post.likes += 1
        db.session.add(like)
        db.session.commit()
        flash(f'Post Liked')
    return redirect(session['url'])


@app.route('/<id>/likes')
@login_required
def postLikes(id):
    try:
        if request.referrer[-5:] != 'likes':
            session['back'] = (request.referrer)
    except:
        session['back'] = url_for('postLikes', id=id)
    session['url'] = url_for('postLikes', id=id)
    post = Post.query.filter_by(id=id)
    postlikers = Likes.query.filter_by(post_id=post[0].id).all()
    likes = [i.user_id for i in postlikers]
    likers = User.query.filter(User.id.in_(likes)).all()
    likers_id = [i.id for i in likers]
    comments = Comment.query.filter_by(post_id=post[0].id).order_by(Comment.timestamp.desc())
    return render_template('display_users.html', post=post, likers=likers, likers_id=likers_id, back=session['back'], comments=comments)

@app.route('/<id>/comments', methods=['GET', 'POST'])
@login_required
def postComments(id):
    try:
        if request.referrer[-8:] != 'comments':
            session['back'] = (request.referrer)
    except:
        session['back'] = url_for('postComments', id=id)
    session['url'] = url_for('postComments', id=id)
    post = Post.query.filter_by(id=id)
    comments = Comment.query.filter_by(post_id=post[0].id).order_by(Comment.timestamp.desc())
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(body=comment_form.comment.data,
                    user_id=current_user.id, post_id=id)
        post[0].comments += 1
        db.session.add(comment)
        db.session.commit()
        flash('Comment Successful!')
        return redirect(url_for('postComments', id=id))
    postlikers = Likes.query.filter_by(post_id=post[0].id).all()
    likes = [i.user_id for i in postlikers]
    likers = User.query.filter(User.id.in_(likes)).all()
    likers_id = [i.id for i in likers]
    return render_template('comments.html', post=post, likers=likers, likers_id=likers_id, comment_form=comment_form, comments=comments, back=session['back'])
