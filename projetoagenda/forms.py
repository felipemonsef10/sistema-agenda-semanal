from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, DateField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class FormAgenda(FlaskForm):
    cidade_manha = StringField('Cidade', validators=[DataRequired()])
    cidade_tarde = StringField('Cidade', validators=[DataRequired()])
    
    atividade_1_manha = StringField('Atividade', validators=[DataRequired()])
    atividade_2_manha = StringField('Atividade', validators=[DataRequired()])
    atividade_3_manha = StringField('Atividade', validators=[DataRequired()])
    atividade_4_manha = StringField('Atividade', validators=[DataRequired()])

    atividade_1_tarde = StringField('Atividade', validators=[DataRequired()])
    atividade_2_tarde = StringField('Atividade', validators=[DataRequired()])
    atividade_3_tarde = StringField('Atividade', validators=[DataRequired()])
    atividade_4_tarde = StringField('Atividade', validators=[DataRequired()])
    
    # descricao = StringField('Descrição', validators=[DataRequired()])
    
    btn_submit = SubmitField('Enviar')
