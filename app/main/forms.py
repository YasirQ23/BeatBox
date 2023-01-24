from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class BioForm(FlaskForm):
    bio = TextAreaField('BIO', validators=[
                        DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Save New Bio')


class GridForm(FlaskForm):
    artist = StringField('Track', validators=[DataRequired()])
    track = StringField('Artist', validators=[DataRequired()])
    img = StringField('Img', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Add To Your Grid')


class FollowForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(validators=[DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment = TextAreaField(
        validators=[DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Submit')
