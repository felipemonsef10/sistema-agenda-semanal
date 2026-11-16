from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pathlib import Path


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
app.config['SECRET_KEY'] = '8c2b93336c3cc66ef84791ddaf5be051'

CAMINHO_PDFS = Path(app.root_path) / Path('static/agendas_semanais')
CAMINHO_PDFS.mkdir(exist_ok=True, parents=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para continuar!'
login_manager.login_message_category = 'theme-danger'


from projetoagenda.routes import home
from projetoagenda.models import Usuario

if __name__ == '__main__':
    app.run(debug=True)