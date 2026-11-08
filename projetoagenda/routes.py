from flask import render_template
from projetoagenda import app
from projetoagenda.forms import FormAgenda
import pandas as pd


@app.route('/', methods=['GET', 'POST'])
def home():
    form_agenda = FormAgenda()

    # form_teste = TabelaForm()
    dias_semana = {
        '02/11/2026': 'Segunda',
        '03/11/2026': 'Terça',
        '04/11/2026': 'Quarta',
        '05/11/2026': 'Quinta',
        '06/11/2026': 'Sexta',
    }
    
    
    if form_agenda.validate_on_submit():
        count = 0
        
        for idx, data in enumerate(dias_semana.keys()):
            cidade_manha = form_agenda.cidade_manha.data[idx]
            cidade_tarde = form_agenda.cidade_tarde.data[idx]
            
            lista_atividades_manha = form_agenda.atividade_manha.data[count:count + 4]
            lista_atividades_tarde = form_agenda.atividade_tarde.data[count:count + 4]
            
            print(
                pd.DataFrame({
                    'Data': [data],
                    'CidadeManha': [cidade_manha],
                    'CidadeTarde': [cidade_tarde],
                    'AtividadesManha': [';'.join([atividade['atividade'].strip() for atividade in lista_atividades_manha])],
                    'DescricaoManha': [';'.join([descricao['descricao'].strip() for descricao in lista_atividades_manha])],
                    'AtividadesTarde': [';'.join([atividade['atividade'].strip() for atividade in lista_atividades_tarde])],
                    'DescricaoTarde': [';'.join([descricao['descricao'].strip() for descricao in lista_atividades_tarde])],
                })
            )
            
            # break
            
            count += 4
        
    else:
        print('Inválido!')
    
    return render_template('home_agenda.html', form=form_agenda, dias_semana=dias_semana)