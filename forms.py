from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField

import config as config

stats = config.stats

class NewCharacterForm(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    gender = SelectField(u'Gender', choices=config.gender_choices)
    profession = SelectField(u'Profession', choices=config.profession_choices)
    
    stats = {}
    
    submit = SubmitField('Create Character')
    
for stat in stats:
    setattr(NewCharacterForm, stat, IntegerField(stat))
