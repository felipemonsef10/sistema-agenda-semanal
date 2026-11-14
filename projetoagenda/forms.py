from flask_wtf import FlaskForm
from wtforms import FieldList, Form, FormField, StringField, PasswordField, SubmitField, FileField, DateField, EmailField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from projetoagenda.models import Usuario


class FormCadastroUsuario(FlaskForm):
    nome_completo = StringField('Nome', validators=[
        DataRequired(),
        Length(min=10, max=50, message='Coloque seu nome e sobrenome.')]
    )
    email = EmailField('E-mail', validators=[
        DataRequired(),
        Email(message='Digite um endereço de e-mail válido.')]
    )
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    is_admin = BooleanField('Admin')
    funcao = SelectField(
        'Função',
        choices=[
            ('', 'Selecionar...'),
            ('Supervisor', 'Supervisor'),
            ('Gerente', 'Gerente')
        ],
        validators=[Optional()]
    )
    
    btn_submit = SubmitField('Cadastrar')
    
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado!')


class FormLoginUsuario(FlaskForm):
    email = EmailField('E-mail', validators=[
        DataRequired(),
        Email(message='Digite um endereço de e-mail válido.')],
    )
    senha = PasswordField('Senha', validators=[
        DataRequired(message="Preencha sua senha."),
        Length(6, 10, message='Preencha uma senha válida.')
    ])
    lembrar_login = BooleanField('Lembrar-me')
    
    btn_submit = SubmitField('Fazer Login')
    
    
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