from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, NumberRange

import config as config

stats = config.stats

class NewCharacterForm(FlaskForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    gender = SelectField(u'Gender', choices=config.gender_choices)
    profession = SelectField(u'Profession', choices=config.profession_choices)
    
    stats = {}
    
    submit = SubmitField('Create Character')
    
for stat in stats:
    setattr(NewCharacterForm, stat, IntegerField(stat, [DataRequired(), NumberRange(min=20, max=100)], default=u'Between 20 and 100'))
    
    
class Skills(FlaskForm):
    pass
