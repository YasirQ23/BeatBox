from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import BioForm, GridForm, FollowForm, PostForm, CommentForm
from app.models import User, db, Grid, Post, Likes, Comment
from app.main import bp


@bp.route('/profile-editor', methods=['GET', 'POST'])
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
            flash('Bio Edit Successful!', category='info')
            return redirect(url_for('main.user', username=current_user.username))
        if grid_form.validate_on_submit():
            tile = Grid.query.filter_by(
                user_id=current_user.id, grid_position=grid_form.data['location']).first()
            tile.artist = grid_form.data['artist']
            tile.track = grid_form.data['track']
            tile.track_img = grid_form.data['img']
            tile.grid_position = grid_form.data['location']
            db.session.commit()
            flash('Grid Edit Successful!', category='info')
            return redirect(url_for('main.profile_editor'))
    return render_template('profile_editor.html', bio_form=bio_form, grid_form=grid_form, grid=grid, Secret=current_app.config['CLIENT_SECRET'])


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    session['url'] = url_for('main.user', username=username)
    post_form = PostForm()
    pg_owner = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(location_id=pg_owner.id).order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', username=current_user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=current_user.username, page=posts.prev_num) \
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
        flash('Post Successful!', category='info')
        return redirect(url_for('main.user', username=username))
    user = User.query.filter_by(username=username).first_or_404()
    follow_form = FollowForm()
    loadedposts = [i.id for i in posts.items]
    like = Likes.query.filter(Likes.post_id.in_(
        loadedposts)).filter_by(user_id=current_user.id).all()
    liked_posts = [i.post_id for i in like]
    return render_template('user.html', user=user, posts=posts.items, follow_form=follow_form, post_form=post_form, artist_track=artist_track, grid=grid, next_url=next_url, prev_url=prev_url, liked_posts=liked_posts, Secret=current_app.config['CLIENT_SECRET'])


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Follow and un follow routes


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.', category='danger')
            return redirect(url_for('main.user', username=current_user.username))
        if user == current_user:
            flash('You cannot follow yourself!', category='danger')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {username}!', category='info')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.user', username=current_user.username))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = FollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.', category='danger')
            return redirect(url_for('main.user', username=current_user.username))
        if user == current_user:
            flash('You cannot unfollow yourself!', category='danger')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You have unfollowed {username}.', category='info')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.user', username=current_user.username))

# Route for Feed page so public can find users to follow!


@bp.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    session['url'] = url_for('main.explore')
    user = User.query.filter_by(username=current_user.username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    post_form = PostForm()
    loadedposts = [i.id for i in posts.items]
    like = Likes.query.filter(Likes.post_id.in_(
        loadedposts)).filter_by(user_id=current_user.id).all()
    liked_posts = [i.post_id for i in like]
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data,
                    user_id=current_user.id, location_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post Successful!', category='info')
        return redirect(url_for('main.explore'))
    if request.method == "POST":
        uname = request.form.get("uname")
        return redirect(url_for('main.searchFor', uname=uname))
    return render_template('feed.html', title='Explore', posts=posts.items, user=user, post_form=post_form, next_url=next_url, prev_url=prev_url, liked_posts=liked_posts)


@bp.route('/followingfeed', methods=['GET', 'POST'])
@login_required
def following():
    session['url'] = url_for('main.following')
    user = User.query.filter_by(username=current_user.username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.following', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.following', page=posts.prev_num) \
        if posts.has_prev else None
    post_form = PostForm()
    loadedposts = [i.id for i in posts.items]
    like = Likes.query.filter(Likes.post_id.in_(
        loadedposts)).filter_by(user_id=current_user.id).all()
    liked_posts = [i.post_id for i in like]
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data,
                    user_id=current_user.id, location_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post Successful!', category='info')
        return redirect(url_for('main.following'))
    return render_template('following_feed.html', title='Explore', posts=posts.items, user=user, post_form=post_form, next_url=next_url, prev_url=prev_url, liked_posts=liked_posts)


@bp.route('/delete/<id>')
@login_required
def removePost(id):
    post = Post.query.filter_by(id=id).first()
    if post.user_id == current_user.id or post.location_id == current_user.id:
        Comment.query.filter_by(post_id=id).delete()
        Likes.query.filter_by(post_id=id).delete()
        db.session.delete(post)
        db.session.commit()
        flash(f'Post Removed', category='danger')
        return redirect(session['url'])
    else:
        flash(f'Sorry, You can only remove posts which you have created or are on your page.', category='danger')
        return redirect(session['url'])


@bp.route('/like/<id>')
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
        flash(f'Post Unliked', category='danger')
    else:
        post.likes += 1
        db.session.add(like)
        db.session.commit()
        flash(f'Post Liked', category='info')
    return redirect(session['url'])


@bp.route('/<id>/likes')
@login_required
def postLikes(id):
    try:
        if request.referrer[-8:] != 'comments' and request.referrer[-5:] != 'likes':
            session['back'] = (request.referrer)
    except:
        session['back'] = url_for('main.postLikes', id=id)
    session['url'] = url_for('main.postLikes', id=id)
    post = Post.query.filter_by(id=id)
    postlikers = Likes.query.filter_by(post_id=post[0].id).all()
    likes = [i.user_id for i in postlikers]
    likers = User.query.filter(User.id.in_(likes)).all()
    likers_id = [i.id for i in likers]
    comments = Comment.query.filter_by(
        post_id=post[0].id).order_by(Comment.timestamp.desc())
    return render_template('display_users.html', post=post, likers=likers, likers_id=likers_id, back=session['back'], comments=comments)


@bp.route('/<id>/comments', methods=['GET', 'POST'])
@login_required
def postComments(id):
    try:
        if request.referrer[-8:] != 'comments' and request.referrer[-5:] != 'likes':
            session['back'] = (request.referrer)
    except:
        session['back'] = url_for('main.postComments', id=id)
    session['url'] = url_for('main.postComments', id=id)
    post = Post.query.filter_by(id=id)
    comments = Comment.query.filter_by(
        post_id=post[0].id).order_by(Comment.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=post[0].id).order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.postComments', id=id, page=comments.next_num) \
        if comments.has_next else None
    prev_url = url_for('main.postComments', id=id, page=comments.prev_num) \
        if comments.has_prev else None
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(body=comment_form.comment.data,
                          user_id=current_user.id, post_id=id)
        post[0].comments += 1
        db.session.add(comment)
        db.session.commit()
        flash('Comment Successful!', category='info')
        return redirect(url_for('main.postComments', id=id))
    postlikers = Likes.query.filter_by(post_id=post[0].id).all()
    likes = [i.user_id for i in postlikers]
    likers = User.query.filter(User.id.in_(likes)).all()
    likers_id = [i.id for i in likers]
    return render_template('comments.html', post=post, likers=likers, likers_id=likers_id, comment_form=comment_form, comments=comments.items, back=session['back'], next_url=next_url, prev_url=prev_url)


@bp.route('/deletecomment/<id>')
@login_required
def removeComment(id):
    comment = Comment.query.filter_by(id=id).first()
    post = Post.query.filter_by(id=comment.post_id).first()
    if comment.comment_author.id == current_user.id or comment.post_owner.user_id == current_user.id:
        post.comments -= 1
        db.session.delete(comment)
        db.session.commit()
        flash(f'Comment Removed', category='danger')
        return redirect(session['url'])
    else:
        flash(f'Sorry, You can only remove comments which you have created or are on your post.', category='danger')
        return redirect(session['url'])


@bp.route('/<username>/<listname>')
@login_required
def viewFollows(username, listname):
    viewinguser = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    if listname == 'following':
        users = viewinguser.followed.paginate(
            page, current_app.config['USERS_PER_PAGE'], False)
        viewing = 'Following'
        next_url = url_for('main.viewFollows', username=username, listname='following', page=users.next_num) \
            if users.has_next else None
        prev_url = url_for('main.viewFollows', username=username, listname='following', page=users.prev_num) \
            if users.has_prev else None
    if listname == 'followers':
        users = viewinguser.followers.paginate(
            page, current_app.config['USERS_PER_PAGE'], False)
        viewing = 'Followers'
        next_url = url_for('main.viewFollows', username=username, listname='followers', page=users.next_num) \
            if users.has_next else None
        prev_url = url_for('main.viewFollows', username=username, listname='followers', page=users.prev_num) \
            if users.has_prev else None
    session['back'] = url_for('main.user', username=username)
    session['url'] = url_for('main.user', username=current_user.username)
    return render_template('followingers.html', users=users.items, back=session['back'], viewinguser=viewinguser, viewing=viewing, username=username, next_url=next_url, prev_url=prev_url)


@bp.route('/searchfor/<uname>')
@login_required
def searchFor(uname):
    session['url'] = url_for('main.explore')
    page = request.args.get('page', 1, type=int)
    users = User.query.filter(User.username_id.ilike(f'%{uname.lower().strip()}%')).paginate(
        page, current_app.config['USERS_PER_PAGE'], False)
    next_url = url_for('main.Search', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('main.Search', page=users.prev_num) \
        if users.has_prev else None
    return render_template('search.html', back=session['url'], users=users.items, uname=uname, prev_url=prev_url, next_url=next_url)
