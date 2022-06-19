from app import app
from app.models import User, db, Grid, Post
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.profileforms import BioForm, GridForm, FollowForm, PostForm
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
    post_form = PostForm()
    pg_owner= User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(user_id=pg_owner.id).order_by(Post.timestamp.desc()).all()
    grid = Grid.query.filter_by(user_id=pg_owner.id).order_by(
        Grid.grid_position).all()
    artist_track = []
    for i in range(9):
        if grid[i].artist != None:
            artist_track.append(grid[i].artist)
            artist_track.append(grid[i].track)
    print(artist_track)
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post Successful!')
        return redirect(url_for('user', username=current_user.username))
    user = User.query.filter_by(username=username).first_or_404()
    follow_form = FollowForm()
    return render_template('user.html', user=user, posts=posts, follow_form=follow_form, post_form=post_form, artist_track=artist_track, grid=grid)


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


@app.route('/explore')
@login_required
def explore():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    post_form = PostForm()
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post Successful!')
        return redirect(url_for('user', username=current_user.username))
    return render_template('feed.html', title='Explore', posts=posts, user=user, post_form=post_form)
