from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '8c2b93336c3cc66ef84791ddaf5be051'

from projetoagenda.routes import home

if __name__ == '__main__':
    app.run(debug=True)