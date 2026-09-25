from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    department = StringField('Department', validators=[DataRequired(), Length(2, 100)])
    level = SelectField('Level of Study', choices=[
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
    ], validators=[DataRequired()])
    cgpa = DecimalField('CGPA', places=2,
                        validators=[DataRequired(), NumberRange(min=0, max=5)])
    skills = TextAreaField('Skills (comma-separated)', validators=[Length(max=500)])
    interests = TextAreaField('Interests (comma-separated)', validators=[Length(max=500)])
    location = StringField('Location', validators=[Length(max=100)])
    submit = SubmitField('Save Profile')