from flask_wtf import FlaskForm
from wtforms import FieldList, Form, FormField, StringField, PasswordField, SubmitField, FileField, DateField, EmailField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from projetoagenda.models import Usuario


class FormCadastroUsuario(FlaskForm):
    nome_completo = StringField(
        'Nome', 
        validators=[
            DataRequired(),
            Length(
                min=10,
                max=50,
                message='Coloque seu nome e sobrenome.'
            )
        ],
        filters=[]
    )
    
    email = EmailField(
        'E-mail',
        validators=[
            DataRequired(),
            Email(message='Digite um endereço de e-mail válido.')
        ],
        filters=[lambda x: x.strip().lower() if x else None]
    )
    
    senha = PasswordField(
        'Senha',
        validators=[
            DataRequired(),
            Length(6, 20)
        ],
        filters=[lambda x: x.strip() if x else None]
    )
    
    is_admin = BooleanField('Admin')
    
    funcao = SelectField(
        'Função',
        choices=[
            ('', 'Selecionar...'),
            ('Supervisor Trade', 'Supervisor Trade'),
            ('Supervisor Comercial', 'Supervisor Comercial'),
            ('Gerente Comercial', 'Gerente Comercial')
        ],
        validators=[Optional()]
    )
    
    btn_submit = SubmitField('Cadastrar')
    
    
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado!')


class FormLoginUsuario(FlaskForm):
    email = EmailField(
        'E-mail',
        validators=[
            DataRequired(),
            Email(message='Digite um endereço de e-mail válido.')
        ],
        filters=[lambda x: x.strip().lower() if x else None]
    )
    
    senha = PasswordField(
        'Senha', validators=[
            DataRequired(message="Preencha sua senha."),
            Length(6, 10, message='Preencha uma senha válida.')
        ],
        filters=[lambda x: x.strip() if x else None]
    )
    
    lembrar_login = BooleanField('Lembrar-me')
    
    btn_submit = SubmitField('Fazer Login')


class RegiaoForm(FlaskForm):
    regiao = StringField(
        'Região',
        validators=[DataRequired()],
        filters=[lambda x: x.strip().title() if x else None]
    )
    
    area = SelectField(
        'Área',
        choices=[
            ('', 'Selecionar...'),
            ('MGCL', 'MGCL'),
            ('MGCO', 'MGCO'),
            ('INTSP', 'INTSP'),
        ],
        validators=[DataRequired()],  
    )
    
    submit = SubmitField('Cadastrar')
    
    
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
    
    descricao = StringField(
        'Descrição', 
        validators=[Optional()],
        filters=[lambda x: x.strip() if x else None]
    )


class FormAgenda(FlaskForm):
    cidade_manha = FieldList(
        StringField(
            'Cidade',
            validators=[DataRequired()],
            filters=[lambda x: x.strip().title() if x else None]
        ),
        min_entries=5,
        max_entries=5,
    )
    
    cidade_tarde = FieldList(
        StringField(
            'Cidade',
            validators=[DataRequired()],
            filters=[lambda x: x.strip().title() if x else None]
        ),
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