from projetoagenda import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    senha = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    
    funcao = db.Column(db.String(50), nullable=True)
    regiao_id = db.Column(
        db.Integer, db.ForeignKey('regioes.id'), nullable=True
    )
    agendas = db.relationship('Agenda', backref='usuario', lazy=True)


class Regiao(db.Model):
    __tablename__ = 'regioes'
    
    id = db.Column(db.Integer, primary_key=True)
    regiao = db.Column(db.String(60), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    
    usuario = db.relationship('Usuario', backref='regiao', lazy=True)
    

class Agenda(db.Model):
    __tablename__ = 'agendas'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    cidade_manha = db.Column(db.String, nullable=False)
    cidade_tarde = db.Column(db.String, nullable=False)
    descricao_manha = db.Column(db.String, nullable=True)
    descricao_tarde = db.Column(db.String, nullable=True)
    atividade_manha = db.Column(db.String, nullable=True)
    atividade_tarde = db.Column(db.String, nullable=True)
    intervalo_semana = db.Column(db.String, nullable=False)
    
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)