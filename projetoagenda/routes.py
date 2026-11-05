from flask import render_template
from projetoagenda import app
from projetoagenda.forms import FormAgenda


@app.route('/', methods=['GET', 'POST'])
def home():
    form_agenda = FormAgenda()
    dias_semana = {
        '02/11/2026': 'Segunda',
        '03/11/2026': 'Terça',
        '04/11/2026': 'Quarta',
        '05/11/2026': 'Quinta',
        '06/11/2026': 'Sexta',
    }
    
    
    # if form_agenda.validate_on_submit():
    #     print(form_agenda.periodo.data)
    # else:
    #     print('Nada')
    
    return render_template('teste.html', form=form_agenda, dias_semana=dias_semana)