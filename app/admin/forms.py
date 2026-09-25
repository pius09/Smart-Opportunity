from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class OpportunityForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(3, 150)])
    category = SelectField('Category', choices=[
        ('scholarship', 'Scholarship'),
        ('internship', 'Internship'),
        ('grant', 'Grant'),
        ('competition', 'Competition'),
        ('conference', 'Conference'),
        ('exchange', 'Exchange Programme'),
        ('training', 'Training'),
    ])
    description = TextAreaField('Description',
                                validators=[DataRequired(), Length(20, 5000)])
    provider = StringField('Provider', validators=[DataRequired(), Length(2, 150)])
    min_cgpa = DecimalField('Minimum CGPA', places=2,
                            validators=[Optional(), NumberRange(min=0, max=5)])
    eligible_department = StringField('Eligible Department(s)',
                                      validators=[Optional(), Length(max=100)])
    eligible_level = StringField('Eligible Level(s)',
                                 validators=[Optional(), Length(max=20)])
    deadline = DateField('Application Deadline', validators=[DataRequired()])
    submit = SubmitField('Save Opportunity')