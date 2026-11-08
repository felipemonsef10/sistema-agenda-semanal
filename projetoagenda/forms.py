from flask_wtf import FlaskForm
from wtforms import FieldList, Form, FormField, StringField, PasswordField, SubmitField, FileField, DateField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional


class LinhaItemForm(Form):
    atividade = SelectField(
        'Atividades',
        choices=[
            ('', 'Selecione...'),
            ('Visita', 'Visita'),
            ('Rota', 'Rota'),
            ('Acompanhamento', 'Acompanhamento'),
            ('Outros', 'Outros'),
        ],
        validators=[Optional()],
    )
    descricao = StringField('Descrição', validators=[Optional()])


class FormAgenda(FlaskForm):
    cidade_manha = FieldList(
        StringField('Cidade', validators=[DataRequired()]),
        min_entries=5,
        max_entries=5
    )
    
    cidade_tarde = FieldList(
        StringField('Cidade', validators=[DataRequired()]),
        min_entries=5,
        max_entries=5
    )
    
    
    atividade_manha = FieldList(
        FormField(LinhaItemForm),
        min_entries=20,
        max_entries=20,
    )
    
    atividade_tarde = FieldList(
        FormField(LinhaItemForm),
        min_entries=20,
        max_entries=20,
    )
  
    submit = SubmitField('Salvar')