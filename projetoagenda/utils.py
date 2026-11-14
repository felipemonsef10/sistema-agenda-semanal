from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple
from math import ceil
from datetime import datetime, date, timedelta

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

# --------------------------------------------------------------------------- #
# Constantes visuais (extraídas do PDF modelo)
# --------------------------------------------------------------------------- #
PAGE_W, PAGE_H = landscape(A4)          # 841.89 x 595.28 pt

MARGEM_ESQ = 41.28
LARGURA_TABELA = 764.28                  # 41.28 .. 805.56
MARGEM_SUP = PAGE_H - 566.40             # topo da barra azul
MARGEM_INF = 41.28

COR_TITULO = HexColor("#2F75B5")         # azul da barra do título
COR_CINZA = HexColor("#F2F2F2")          # cabeçalhos / célula DATA
COR_AMARELO = HexColor("#FFD966")        # faixa CIDADE
COR_TEXTO = black

FONTE = "Courier"
FONTE_B = "Courier-Bold"

# Alturas fixas do modelo
H_TITULO = 15.96
H_NOME = 13.08
GAP_TITULO_NOME = 2.04
GAP_NOME_TABELA = 9.00
H_CAB_PERIODO = 12.00                    # linha "MANHÃ" / "TARDE"
H_CAB_2LINHAS = 22.68                    # "ATIVIDADE/SELECIONAR" e "CIDADE/cidade"
H_LINHA = 11.28                          # altura padrão da linha de atividade
H_FILLER = 8.20                          # linha fina no pé do bloco
H_LINHA_MIN = 7.60

FS_PADRAO = 8.64
FS_TITULO = 10.92

ESPESSURA_GROSSA = 1.44
ESPESSURA_FINA = 0.72

# Larguras das colunas (a soma é LARGURA_TABELA)
COL = {
    "data": 63.14,
    "dia": 45.60,
    "gap1": 5.04,
    "seq": 24.12,
    "ativ": 68.55,
    "cid": 237.38,
    "gap2": 3.60,
    "seq2": 22.80,
    "ativ2": 68.52,
    "cid2": 225.53,
}

DIAS_SEMANA = (
    "SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SÁBADO", "DOMINGO",
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _texto(valor: Any) -> str:
    """Normaliza qualquer valor para string segura (sem None / espaços sobrando)."""
    if valor is None:
        return ""
    return str(valor).replace("\n", " ").replace("\r", " ").strip()


def _dia_semana(data: str) -> str:
    """'16/11/2026' -> 'SEGUNDA'. Se a data for inválida, devolve ''."""
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return DIAS_SEMANA[datetime.strptime(_texto(data), fmt).weekday()]
        except (ValueError, TypeError):
            continue
    return ""


def _normalizar_atividade(item: Any) -> Tuple[str, str]:
    """Aceita dict, tupla/lista ou string e devolve (atividade, descricao)."""
    if isinstance(item, Mapping):
        return _texto(item.get("atividade")), _texto(item.get("descricao"))
    if isinstance(item, (tuple, list)):
        if not item:
            return "", ""
        if len(item) == 1:
            return _texto(item[0]), ""
        return _texto(item[0]), _texto(item[1])
    return _texto(item), ""


def _lista_atividades(itens: Any) -> List[Tuple[str, str]]:
    """Normaliza a lista de atividades (aceita list ou dict com chaves 1..n)."""
    if itens is None:
        return []
    if isinstance(itens, Mapping):
        # Ordena por chave numérica quando possível
        def _chave(k):
            try:
                return (0, float(k))
            except (TypeError, ValueError):
                return (1, str(k))
        itens = [itens[k] for k in sorted(itens, key=_chave)]
    return [_normalizar_atividade(i) for i in itens]


def _ajustar_texto(texto: str, fonte: str, tamanho: float,
                   largura_max: float, tamanho_min: float = 5.0
                   ) -> Tuple[str, float]:
    """Reduz o corpo da fonte (e, se preciso, trunca com reticências)
    para que o texto caiba em ``largura_max``."""
    if not texto or largura_max <= 0:
        return "", tamanho
    size = tamanho
    while size > tamanho_min and stringWidth(texto, fonte, size) > largura_max:
        size = round(size - 0.2, 2)
    if stringWidth(texto, fonte, size) <= largura_max:
        return texto, size

    ell = "..."
    corte = texto
    while corte and stringWidth(corte + ell, fonte, size) > largura_max:
        corte = corte[:-1]
    return (corte.rstrip() + ell) if corte else "", size


def _y_base(y_bottom: float, altura: float, tamanho: float) -> float:
    """Baseline aproximada para centralizar verticalmente o texto na célula."""
    return y_bottom + (altura - tamanho) / 2.0 + tamanho * 0.28


def _texto_celula(c: canvas.Canvas, texto: str, fonte: str, tamanho: float,
                  x: float, w: float, y_bottom: float, h: float,
                  alinhamento: str = "center", padding: float = 3.0) -> None:
    """Escreve o texto dentro de uma célula (sem borda), centralizado ou à esquerda."""
    if not texto:
        return
    texto, size = _ajustar_texto(texto, fonte, tamanho, w - 2 * padding)
    if not texto:
        return
    if alinhamento == "center":
        x_txt = x + (w - stringWidth(texto, fonte, size)) / 2.0
    else:
        x_txt = x + padding
    c.setFillColor(COR_TEXTO)
    c.setFont(fonte, size)
    c.drawString(x_txt, _y_base(y_bottom, h, size), texto)


def _fill(c: canvas.Canvas, cor, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(cor)
    c.rect(x, y, w, h, stroke=0, fill=1)


def _hlinha(c: canvas.Canvas, x1: float, x2: float, y: float,
            esp: float = ESPESSURA_FINA, cor=black) -> None:
    """Linha horizontal desenhada como retângulo preenchido (como no modelo)."""
    c.setFillColor(cor)
    c.rect(x1, y - esp / 2.0, x2 - x1, esp, stroke=0, fill=1)


def _vlinha(c: canvas.Canvas, x: float, y1: float, y2: float,
            esp: float = ESPESSURA_FINA, cor=black) -> None:
    """Linha vertical desenhada como retângulo preenchido."""
    c.setFillColor(cor)
    c.rect(x - esp / 2.0, y1, esp, y2 - y1, stroke=0, fill=1)


# --------------------------------------------------------------------------- #
# Blocos de desenho
# --------------------------------------------------------------------------- #
def _desenhar_cabecalho(c: canvas.Canvas, nome_supervisor: str,
                        y_topo: float,
                        titulo: str = "AGENDA PLANEJAMENTO SEMANAL DE ATIVIDADES - SUPERVISOR"
                        ) -> float:
    """Barra azul do título + campo 'Nome Supervisor:'. Devolve o y do fim."""
    x0, w = MARGEM_ESQ, LARGURA_TABELA

    # ---- Barra do título -------------------------------------------------- #
    y_titulo = y_topo - H_TITULO
    _fill(c, COR_TITULO, x0, y_titulo, w, H_TITULO)

    esp = 0.048
    largura = stringWidth(titulo, FONTE, FS_TITULO) + esp * (len(titulo) - 1)
    c.setFillColor(white)
    c.setFont(FONTE, FS_TITULO)
    t = c.beginText(x0 + (w - largura) / 2.0,
                    _y_base(y_titulo, H_TITULO, FS_TITULO))
    t.setCharSpace(esp)
    t.textOut(titulo)
    c.drawText(t)

    # ---- Campo Nome Supervisor ------------------------------------------- #
    y_nome = y_titulo - GAP_TITULO_NOME - H_NOME
    _fill(c, white, x0, y_nome, w, H_NOME)
    _texto_celula(c, "Nome Supervisor:", FONTE, FS_PADRAO,
                  x0, COL["data"] + COL["dia"], y_nome, H_NOME,
                  alinhamento="center")
    _texto_celula(c, nome_supervisor, FONTE, FS_PADRAO,
                  x0 + COL["data"] + COL["dia"], w - COL["data"] - COL["dia"],
                  y_nome, H_NOME, alinhamento="left", padding=1.8)

    # Bordas (mais grossas, como no modelo)
    _hlinha(c, x0, x0 + w, y_topo, ESPESSURA_GROSSA)
    _hlinha(c, x0, x0 + w, y_nome, ESPESSURA_GROSSA)
    _hlinha(c, x0, x0 + w, y_nome + H_NOME, ESPESSURA_GROSSA)
    _vlinha(c, x0, y_nome, y_nome + H_NOME, ESPESSURA_GROSSA)
    _vlinha(c, x0 + w, y_nome, y_nome + H_NOME, ESPESSURA_GROSSA)
    _vlinha(c, x0 + COL["data"] + COL["dia"], y_nome, y_nome + H_NOME,
            ESPESSURA_GROSSA)

    return y_nome - GAP_NOME_TABELA


def _desenhar_bloco_dia(c: canvas.Canvas, x0: float, y_topo: float,
                        data: str, cidade_manha: str, cidade_tarde: str,
                        atividades_manha: Sequence[Tuple[str, str]],
                        atividades_tarde: Sequence[Tuple[str, str]],
                        rh: float = H_LINHA,
                        fs: float = FS_PADRAO) -> float:
    """Desenha um bloco (um dia) e devolve o y da base do bloco."""
    w_total = LARGURA_TABELA

    # Coordenadas das colunas
    x_data = x0
    x_dia = x_data + COL["data"]
    x_pan1 = x_dia + COL["dia"] + COL["gap1"]          # início painel MANHÃ
    x_seq1 = x_pan1
    x_ativ1 = x_seq1 + COL["seq"]
    x_cid1 = x_ativ1 + COL["ativ"]
    x_pan1_fim = x_cid1 + COL["cid"]
    x_pan2 = x_pan1_fim + COL["gap2"]                  # início painel TARDE
    x_seq2 = x_pan2
    x_ativ2 = x_seq2 + COL["seq2"]
    x_cid2 = x_ativ2 + COL["ativ2"]
    x_fim = x_cid2 + COL["cid2"]

    n_linhas = max(len(atividades_manha), len(atividades_tarde), 1)
    h_cab = H_CAB_PERIODO + H_CAB_2LINHAS
    h_bloco = h_cab + n_linhas * rh + H_FILLER
    y_base = y_topo - h_bloco

    # ------------------------------------------------------------------ #
    # 1) Preenchimentos
    # ------------------------------------------------------------------ #
    # Célula DATA / DIA SEM (cinza, altura inteira)
    _fill(c, COR_CINZA, x_data, y_base, COL["data"] + COL["dia"], h_bloco)

    for x_pan, x_seq, x_ativ, x_cid, x_fim_pan in (
        (x_pan1, x_seq1, x_ativ1, x_cid1, x_pan1_fim),
        (x_pan2, x_seq2, x_ativ2, x_cid2, x_fim),
    ):
        # linha de cabeçalho do período (cinza)
        _fill(c, COR_CINZA, x_pan, y_topo - H_CAB_PERIODO,
              x_fim_pan - x_pan, H_CAB_PERIODO)
        # "ATIVIDADE/SELECIONAR" (cinza) e "CIDADE/cidade" (amarelo)
        y_cab2 = y_topo - h_cab
        _fill(c, COR_CINZA, x_ativ, y_cab2, x_cid - x_ativ, H_CAB_2LINHAS)
        _fill(c, COR_AMARELO, x_cid, y_cab2, x_fim_pan - x_cid, H_CAB_2LINHAS)

    # ------------------------------------------------------------------ #
    # 2) Textos
    # ------------------------------------------------------------------ #
    y_cab1 = y_topo - H_CAB_PERIODO
    y_cab2 = y_topo - h_cab
    meio_cab1 = y_cab1 + H_CAB_PERIODO / 2.0
    meio_cab2 = y_cab2 + H_CAB_2LINHAS / 2.0
    h_meia = H_CAB_2LINHAS / 2.0

    # DATA / DIA SEM (centralizados na área das linhas de atividade)
    _texto_celula(c, _texto(data), FONTE, fs, x_data, COL["data"],
                  y_base, h_bloco - h_cab, "center")
    _texto_celula(c, _dia_semana(data), FONTE, fs, x_dia, COL["dia"],
                  y_base, h_bloco - h_cab, "center")

    # Rótulos das colunas da esquerda (centralizados nas duas linhas de cabeçalho)
    _texto_celula(c, "DATA", FONTE_B, fs, x_data, COL["data"],
                  y_cab2, h_cab, "center")
    _texto_celula(c, "DIA SEM", FONTE_B, fs, x_dia, COL["dia"],
                  y_cab2, h_cab, "center")

    for (x_pan, x_seq, x_ativ, x_cid, x_fim_pan,
         titulo, cidade, atividades) in (
        (x_pan1, x_seq1, x_ativ1, x_cid1, x_pan1_fim,
         "MANHÃ", cidade_manha, atividades_manha),
        (x_pan2, x_seq2, x_ativ2, x_cid2, x_fim,
         "TARDE", cidade_tarde, atividades_tarde),
    ):
        # "MANHÃ" / "TARDE" (centralizado sobre ATIVIDADE+CIDADE)
        _texto_celula(c, titulo, FONTE_B, fs, x_ativ, x_fim_pan - x_ativ,
                      y_cab1, H_CAB_PERIODO, "center")

        # "SEQ" (verticalmente centralizado nas duas linhas de cabeçalho)
        _texto_celula(c, "SEQ", FONTE_B, fs, x_seq, x_ativ - x_seq,
                      y_cab2, h_cab, "center")
        # ATIVIDADE / SELECIONAR
        _texto_celula(c, "ATIVIDADE", FONTE_B, fs, x_ativ, x_cid - x_ativ,
                      meio_cab2, h_meia, "center")
        _texto_celula(c, "SELECIONAR", FONTE_B, fs, x_ativ, x_cid - x_ativ,
                      y_cab2, h_meia, "left", padding=9.2)
        # CIDADE / cidade
        _texto_celula(c, "CIDADE", FONTE_B, fs, x_cid, x_fim_pan - x_cid,
                      meio_cab2, h_meia, "center")
        _texto_celula(c, cidade, FONTE_B, fs, x_cid, x_fim_pan - x_cid,
                      y_cab2, h_meia, "center")

        # Linhas de atividade
        for i in range(n_linhas):
            y_linha = y_cab2 - (i + 1) * rh
            atividade, descricao = (atividades[i] if i < len(atividades)
                                    else ("", ""))
            _texto_celula(c, str(i + 1), FONTE, fs, x_seq,
                          x_ativ - x_seq, y_linha, rh, "center")
            _texto_celula(c, atividade, FONTE_B, fs, x_ativ, x_cid - x_ativ,
                          y_linha, rh, "center")
            _texto_celula(c, descricao, FONTE, fs, x_cid, x_fim_pan - x_cid,
                          y_linha, rh, "left", padding=3.0)

    # ------------------------------------------------------------------ #
    # 3) Bordas
    # ------------------------------------------------------------------ #
    # Verticais grossas (limites do bloco e divisões entre painéis)
    for xv in (x_data, x_dia + COL["dia"], x_pan1, x_pan1_fim, x_pan2, x_fim):
        _vlinha(c, xv, y_base, y_topo, ESPESSURA_GROSSA)
    # Verticais finas
    _vlinha(c, x_dia, y_base, y_topo, ESPESSURA_FINA)
    for xv in (x_ativ1, x_cid1, x_ativ2, x_cid2):
        _vlinha(c, xv, y_base, y_topo, ESPESSURA_FINA)

    # Horizontais
    _hlinha(c, x0, x0 + w_total, y_topo, ESPESSURA_GROSSA)
    _hlinha(c, x0, x0 + w_total, y_base, ESPESSURA_GROSSA)

    # Linha abaixo de MANHÃ/TARDE (apenas nos painéis)
    _hlinha(c, x_pan1, x_pan1_fim, y_cab1, ESPESSURA_FINA)
    _hlinha(c, x_pan2, x_fim, y_cab1, ESPESSURA_FINA)
    # Linha entre ATIVIDADE/SELECIONAR e CIDADE/cidade
    _hlinha(c, x_pan1, x_pan1_fim, meio_cab2, ESPESSURA_FINA)
    _hlinha(c, x_pan2, x_fim, meio_cab2, ESPESSURA_FINA)
    # Linhas entre as atividades
    for i in range(n_linhas):
        y_linha = y_cab2 - (i + 1) * rh
        _hlinha(c, x_pan1, x_pan1_fim, y_linha, ESPESSURA_FINA)
        _hlinha(c, x_pan2, x_fim, y_linha, ESPESSURA_FINA)
    # Linha acima da faixa fina final
    y_filler = y_base + H_FILLER
    _hlinha(c, x_pan1, x_pan1_fim, y_filler, ESPESSURA_FINA)
    _hlinha(c, x_pan2, x_fim, y_filler, ESPESSURA_FINA)

    return y_base


# --------------------------------------------------------------------------- #
# Função principal
# --------------------------------------------------------------------------- #
def gerar_agenda_pdf(
    dados: Mapping[str, Any],
    caminho_saida: str = "agenda.pdf",
    nome_supervisor: str = "",
    linhas_por_dia: int | None = None,
    titulo: str = "AGENDA PLANEJAMENTO SEMANAL DE ATIVIDADES - SUPERVISOR",
) -> str:
    """Gera o PDF da agenda semanal a partir do dicionário ``dados``.

    Parâmetros
    ----------
    dados : dict
        Dicionário com as chaves ``data``, ``cidade_manha``, ``cidade_tarde``,
        ``atividade_manha`` e ``atividade_tarde``.
    caminho_saida : str
        Caminho (ou nome) do arquivo .pdf a ser criado.
    nome_supervisor : str
        Texto exibido em "Nome Supervisor:" (opcional).
    linhas_por_dia : int, opcional
        Quantidade de linhas de atividade por dia/período. Se omitido, é
        calculado dividindo as atividades entre os dias (20 itens / 5 dias = 4).
    titulo : str
        Texto da barra azul superior.

    Retorna
    -------
    str
        O caminho do arquivo gerado.
    """
    datas = [_texto(d) for d in (dados.get("data") or [])]
    cidades_manha = list(dados.get("cidade_manha") or [])
    cidades_tarde = list(dados.get("cidade_tarde") or [])
    ativ_manha = _lista_atividades(dados.get("atividade_manha"))
    ativ_tarde = _lista_atividades(dados.get("atividade_tarde"))

    n_dias = max(len(datas), 1)
    if not datas:
        datas = [""] * n_dias

    # Quantidade de linhas por dia
    if linhas_por_dia is None:
        maior = max(len(ativ_manha), len(ativ_tarde))
        linhas_por_dia = max(1, ceil(maior / n_dias))
    linhas_por_dia = max(1, int(linhas_por_dia))

    def _fatiar(lista):
        return [lista[i * linhas_por_dia:(i + 1) * linhas_por_dia]
                for i in range(n_dias)]

    manha_por_dia = _fatiar(ativ_manha)
    tarde_por_dia = _fatiar(ativ_tarde)

    def _cidade(lista, i):
        return _texto(lista[i]) if i < len(lista) else ""

    # ------------------------------------------------------------------ #
    # Paginação
    # ------------------------------------------------------------------ #
    y_inicio = PAGE_H - MARGEM_SUP - (H_TITULO + GAP_TITULO_NOME + H_NOME
                                      + GAP_NOME_TABELA)
    altura_disponivel = y_inicio - MARGEM_INF
    h_cab = H_CAB_PERIODO + H_CAB_2LINHAS

    def _h_bloco(rh):
        return h_cab + linhas_por_dia * rh + H_FILLER

    # Ajusta a altura da linha para caber o maior número de dias por página
    rh = H_LINHA
    while rh > H_LINHA_MIN and int(altura_disponivel // _h_bloco(rh)) < min(5, n_dias):
        rh = round(rh - 0.2, 2)
    # Se nem um dia inteiro couber, divide as linhas em várias páginas
    max_linhas_bloco = int((altura_disponivel - h_cab - H_FILLER) // rh)
    linhas_por_bloco = max(1, min(linhas_por_dia, max_linhas_bloco))
    fs = min(FS_PADRAO, rh * 0.76)

    c = canvas.Canvas(caminho_saida, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Agenda Planejamento Semanal de Atividades")
    c.setAuthor(_texto(nome_supervisor))
    c.setSubject("Agenda semanal - Supervisor")

    y = _desenhar_cabecalho(c, nome_supervisor, PAGE_H - MARGEM_SUP, titulo)

    for i in range(n_dias):
        manha = list(manha_por_dia[i])
        tarde = list(tarde_por_dia[i])

        # Divide o dia em partes, caso não caiba em uma página
        inicio = 0
        primeiro = True
        while inicio < linhas_por_dia:
            fim = min(inicio + linhas_por_bloco, linhas_por_dia)
            parte_m = manha[inicio:fim]
            parte_t = tarde[inicio:fim]
            h_bloco = h_cab + (fim - inicio) * rh + H_FILLER

            if y - h_bloco < MARGEM_INF - 0.01:
                c.showPage()
                y = _desenhar_cabecalho(c, nome_supervisor,
                                        PAGE_H - MARGEM_SUP, titulo)

            y = _desenhar_bloco_dia(
                c, MARGEM_ESQ, y,
                data=datas[i],
                cidade_manha=_cidade(cidades_manha, i),
                cidade_tarde=_cidade(cidades_tarde, i),
                atividades_manha=parte_m,
                atividades_tarde=parte_t,
                rh=rh, fs=fs,
            )
            inicio = fim
            primeiro = False

    c.showPage()
    c.save()
    return caminho_saida


def calcular_dias_semana():
    data_hoje = date.today()
    
    lista_dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
    
    if data_hoje.weekday() >= 3:
        segunda = (data_hoje - timedelta(days=data_hoje.weekday())) + timedelta(days=7)
        dias_semana = {dia_semana: segunda if dia_semana == 0 else segunda + timedelta(days=idx) for idx, dia_semana in enumerate(lista_dias_semana)}
    else:
        segunda = (data_hoje - timedelta(days=data_hoje.weekday()))
        dias_semana = {dia_semana: segunda if dia_semana == 0 else segunda + timedelta(days=idx) for idx, dia_semana in enumerate(lista_dias_semana)}
    
    intervalo = f'{dias_semana['Segunda'].strftime('%d/%m/%Y')}_a_{dias_semana['Sexta'].strftime('%d/%m/%Y')}'
    
    return dias_semana, intervalo


if __name__ == '__main__':
    dados = {
        'data': ['16/11/2026', '17/11/2026', '18/11/2026', '19/11/2026', '20/11/2026'],
        'cidade_manha': ['Araguari', 'Araguari', 'Araguari', 'Araguari', 'Patos'],
        'cidade_tarde': ['Araguari', 'Araguari', 'Araguari', 'Araguari', 'Patos'],
        'atividade_manha': [
            {'atividade': 'Visita', 'descricao': 'Teste'},
            {'atividade': 'Rota', 'descricao': 'União'},
        ] + [{'atividade': '', 'descricao': ''}] * 18,
        'atividade_tarde': [{'atividade': '', 'descricao': ''}] * 20,
    }

    gerar_agenda_pdf(dados, r"C:\Users\User\Downloads\agenda_exemplo.pdf", nome_supervisor="TESTE")
    print("PDF gerado: agenda_exemplo.pdf")
    # print(calcular_dias_semana())