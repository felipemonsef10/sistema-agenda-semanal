from projetoagenda import app, db, bcrypt
from projetoagenda.forms import FormAgenda, FormCadastroUsuario, FormLoginUsuario
from projetoagenda.models import Agenda, Usuario
from projetoagenda.utils import calcular_dias_semana, gerar_agenda_pdf
from projetoagenda.caminhos import CAMINHO_PDFS

from flask import render_template, redirect, flash, request, url_for, send_file
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import update

from secrets import token_hex
from datetime import date


dias_semana, intervalo_semana = calcular_dias_semana()


def carregar_dados_agenda(id_usuario, intervalo_semana):
    dados_iniciais = {
        'cidade_manha': [],
        'cidade_tarde': [],
        'atividade_manha': [],
        'atividade_tarde': []
    }
    
    agenda_atual = Agenda.query.filter_by(id_usuario=id_usuario, intervalo_semana=intervalo_semana).all()

    if agenda_atual:
        for registro in agenda_atual:
            dados_iniciais['cidade_manha'].append(registro.cidade_manha)
            dados_iniciais['cidade_tarde'].append(registro.cidade_tarde)
            
            for count in range(4):
                dados_iniciais['atividade_manha'].append({
                    'atividade': registro.atividade_manha.split(';')[count],
                    'descricao': registro.descricao_manha.split(';')[count],
                })
                dados_iniciais['atividade_tarde'].append({
                    'atividade': registro.atividade_tarde.split(';')[count],
                    'descricao': registro.descricao_tarde.split(';')[count],
                })
    
    return dados_iniciais, agenda_atual


def buscar_agenda(id_usuario: int, intervalo_semana: str):
    dados_agenda = {
        'data': [],
        'cidade_manha': [],
        'cidade_tarde': [],
        'atividade_manha': [],
        'atividade_tarde': []
    }


    registros_agenda = Agenda.query.filter_by(id_usuario=id_usuario, intervalo_semana=intervalo_semana).all()
    
    if registros_agenda:
        for registro in registros_agenda:
            dados_agenda['data'].append(registro.data.strftime('%d/%m/%Y'))
            dados_agenda['cidade_manha'].append(registro.cidade_manha)
            dados_agenda['cidade_tarde'].append(registro.cidade_tarde)
            
            for count in range(4):
                dados_agenda['atividade_manha'].append({
                    'atividade': registro.atividade_manha.split(';')[count],
                    'descricao': registro.descricao_manha.split(';')[count],
                })
                dados_agenda['atividade_tarde'].append({
                    'atividade': registro.atividade_tarde.split(';')[count],
                    'descricao': registro.descricao_tarde.split(';')[count],
                })
    
        return dados_agenda
    
    else:
        return {}


def cadastrar_agenda(dias_semana: dict, form_agenda: FormAgenda, intervalo_semana: str, id_usuario: int):
    count = 0
    
    for idx, data in enumerate(dias_semana.values()):
        cidade_manha = form_agenda.cidade_manha.data[idx]
        cidade_tarde = form_agenda.cidade_tarde.data[idx]
        
        lista_atividades_manha = form_agenda.atividade_manha.data[count:count + 4]
        lista_atividades_tarde = form_agenda.atividade_tarde.data[count:count + 4]
        
        atividade_manha = ';'.join([atividade['atividade'].strip() for atividade in lista_atividades_manha])
        atividade_tarde = ';'.join([descricao['atividade'].strip() for descricao in lista_atividades_tarde])
        descricao_manha = ';'.join([atividade['descricao'].strip() for atividade in lista_atividades_manha])
        descricao_tarde = ';'.join([descricao['descricao'].strip() for descricao in lista_atividades_tarde])
        
        registro_dia = {
            'data': data,
            'cidade_manha': cidade_manha,
            'cidade_tarde': cidade_tarde,
            'atividade_manha': atividade_manha,
            'atividade_tarde': atividade_tarde,
            'descricao_manha': descricao_manha,
            'descricao_tarde': descricao_tarde,
            'id_usuario': id_usuario,
            'intervalo_semana': intervalo_semana
        }
        
        
        with app.app_context():
            registro_agenda = Agenda(**registro_dia)
            
            db.session.add(registro_agenda)
            db.session.commit()
        
        count += 4
        
        
def atualizar_agenda(dias_semana: dict, form_agenda: FormAgenda, agenda_atual):
    count = 0
    
    for idx, data in enumerate(dias_semana.values()):
        cidade_manha = form_agenda.cidade_manha.data[idx]
        cidade_tarde = form_agenda.cidade_tarde.data[idx]
        
        lista_atividades_manha = form_agenda.atividade_manha.data[count:count + 4]
        lista_atividades_tarde = form_agenda.atividade_tarde.data[count:count + 4]
        
        atividade_manha = ';'.join([atividade['atividade'].strip() for atividade in lista_atividades_manha])
        atividade_tarde = ';'.join([descricao['atividade'].strip() for descricao in lista_atividades_tarde])
        descricao_manha = ';'.join([atividade['descricao'].strip() for atividade in lista_atividades_manha])
        descricao_tarde = ';'.join([descricao['descricao'].strip() for descricao in lista_atividades_tarde])
        
        registro_dia = {
            'data': data,
            'cidade_manha': cidade_manha,
            'cidade_tarde': cidade_tarde,
            'atividade_manha': atividade_manha,
            'atividade_tarde': atividade_tarde,
            'descricao_manha': descricao_manha,
            'descricao_tarde': descricao_tarde,
        }
        
        
        with app.app_context():
            stmt = (
                update(Agenda)
                .where(Agenda.id == agenda_atual[idx].id)
                .values(**registro_dia)
            )
            
            db.session.execute(stmt)
            db.session.commit()
        
        count += 4
        

def cadastrar_usuario(form_cadastro_usuario: FormCadastroUsuario):
    usuario = Usuario(
        nome_completo = form_cadastro_usuario.nome_completo.data,
        email = form_cadastro_usuario.email.data,
        senha = bcrypt.generate_password_hash(form_cadastro_usuario.senha.data).decode('utf-8'),
        funcao = form_cadastro_usuario.funcao.data,
        is_admin = form_cadastro_usuario.is_admin.data,
    )
    
    with app.app_context():
        db.session.add(usuario)
        db.session.commit()


@app.route('/supervisor/agenda', methods=['GET', 'POST'])
@login_required
def home():
    if current_user.is_admin:
        return redirect(url_for('tela_admin'))
    
    dados_iniciais_agenda, agenda_atual = carregar_dados_agenda(current_user.id, intervalo_semana)
    
    form_agenda = FormAgenda(data=dados_iniciais_agenda)
    
    if form_agenda.validate_on_submit():
        if not agenda_atual:
            cadastrar_agenda(dias_semana, form_agenda, intervalo_semana, current_user.id)
            flash('Agenda enviada com sucesso!', category='theme-success')
        else:
            atualizar_agenda(dias_semana, form_agenda, agenda_atual)
            flash('Agenda atualizada com sucesso!', category='theme-info')
            
        return redirect(url_for('home'))

    return render_template('home_agenda.html', form=form_agenda, dias_semana=dias_semana, intervalo=intervalo_semana)


@app.route('/supervisor/agenda/baixar', methods=['GET', 'POST'])
@login_required
def baixar_agenda():
    if current_user.is_admin:
        return redirect(url_for('home'))
    
    agenda = buscar_agenda(current_user.id, intervalo_semana=intervalo_semana)
    if agenda:
        nome_arquivo_pdf = f"{current_user.nome_completo.replace(' ', '_')}_{intervalo_semana.replace('/', '_')}.pdf"
        caminho_agenda_pdf = str(CAMINHO_PDFS / nome_arquivo_pdf)
        
        gerar_agenda_pdf(agenda, caminho_agenda_pdf, current_user.nome_completo)
        
        flash('Agenda baixada com sucesso!', 'theme-success')
        return send_file(caminho_agenda_pdf, as_attachment=True, download_name=nome_arquivo_pdf)
    
    flash('Agenda não encontrada!', 'theme-info')
    return '', 204


@app.route('/adm', methods=['GET', 'POST'])
@login_required
def tela_admin():
    return render_template('tela_admin.html')


@app.route('/adm/cadastro-user', methods=['GET', 'POST'])
@login_required
def cadastro_usuario():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    form_cadastro_usuario = FormCadastroUsuario(data={'nome_completo': None})
    
    if form_cadastro_usuario.validate_on_submit():
        cadastrar_usuario(form_cadastro_usuario)
        flash('Usuário cadastrado com sucesso!', category='theme-success')
        
        return redirect(url_for('cadastro_usuario'))
    
    return render_template('tela_cadastro.html', form=form_cadastro_usuario)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form_login = FormLoginUsuario()
    
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            flash('Login feito com sucesso. Email: {}'.format(form_login.email.data), 'theme-success')
            
            param_next = request.args.get('next')

            if param_next:
                return redirect(param_next)
            else:
                return redirect(url_for('home'))
            
        else:
            flash('Falha no Login. E-mail ou senha incorretos', 'theme-danger')
        
    
    return render_template('tela_login.html', form=form_login)


@app.route('/logout')
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'theme-success')
    return redirect(url_for('login'))


@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    return redirect(url_for('home'))


@app.route('/teste', methods=['GET', 'POST'])
def teste():
    return render_template('teste.html')