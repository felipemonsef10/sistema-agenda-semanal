from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pathlib import Path
from projetoagenda.utils import calcular_dias_semana, criar_caminho_pdfs


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
app.config['SECRET_KEY'] = '8c2b93336c3cc66ef84791ddaf5be051'

dias_semana, intervalo_semana = calcular_dias_semana()
CAMINHO_PDFS = Path(app.root_path) / Path('static/agendas_semanais')
CAMINHO_PDFS.mkdir(exist_ok=True, parents=True)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para continuar!'
login_manager.login_message_category = 'theme-danger'


from projetoagenda import routes
from projetoagenda import models

if __name__ == '__main__':
    app.run(debug=True)