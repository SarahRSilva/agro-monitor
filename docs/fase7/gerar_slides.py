"""
Gera docs/fase7/AgroSmart_Pitch.pptx — apresentação do produto (pitch) da Fase 7.

Uso:
    pip install python-pptx==1.0.2
    python docs/fase7/gerar_slides.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "AgroSmart_Pitch.pptx"

VERDE = RGBColor(0x1B, 0x5E, 0x20)
VERDE_CLARO = RGBColor(0xE8, 0xF5, 0xE9)
AMBAR = RGBColor(0xF9, 0xA8, 0x25)
VERMELHO = RGBColor(0xC6, 0x28, 0x28)
CINZA = RGBColor(0x45, 0x5A, 0x64)
CINZA_CLARO = RGBColor(0xF5, 0xF5, 0xF5)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)
PRETO = RGBColor(0x21, 0x21, 0x21)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
VAZIO = prs.slide_layouts[6]


def texto(slide, x, y, w, h, conteudo, tam=18, cor=PRETO, negrito=False, alinhamento=PP_ALIGN.LEFT,
          ancora=MSO_ANCHOR.TOP, fonte="Calibri"):
    caixa = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = caixa.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = ancora
    tf.margin_left = tf.margin_right = Inches(0.05)
    linhas = conteudo if isinstance(conteudo, list) else [conteudo]
    for i, linha in enumerate(linhas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinhamento
        partes = linha if isinstance(linha, list) else [(linha, negrito)]
        for trecho, bold in partes:
            run = p.add_run()
            run.text = trecho
            run.font.size = Pt(tam)
            run.font.bold = bold
            run.font.color.rgb = cor
            run.font.name = fonte
        p.space_after = Pt(tam * 0.45)
    return caixa


def retangulo(slide, x, y, w, h, cor, borda=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE):
    r = slide.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid()
    r.fill.fore_color.rgb = cor
    if borda:
        r.line.color.rgb = borda
        r.line.width = Pt(1.25)
    else:
        r.line.fill.background()
    r.shadow.inherit = False
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        r.adjustments[0] = 0.08
    return r


def novo_slide(titulo, subtitulo=None, numero=None):
    s = prs.slides.add_slide(VAZIO)
    retangulo(s, 0, 0, 13.333, 0.12, VERDE, forma=MSO_SHAPE.RECTANGLE)
    texto(s, 0.6, 0.35, 12, 0.8, titulo, tam=32, cor=VERDE, negrito=True)
    if subtitulo:
        texto(s, 0.6, 1.1, 12, 0.5, subtitulo, tam=16, cor=CINZA)
    if numero:
        texto(s, 12.2, 6.95, 0.9, 0.4, str(numero), tam=11, cor=CINZA, alinhamento=PP_ALIGN.RIGHT)
    texto(s, 0.6, 6.95, 6, 0.4, "AgroSmart · FIAP 4ESOA · Fase 7", tam=11, cor=CINZA)
    return s


def cartao(slide, x, y, w, h, titulo, corpo, cor_titulo=VERDE, fundo=VERDE_CLARO, tam=15, icone=None):
    retangulo(slide, x, y, w, h, fundo)
    cab = f"{icone}  {titulo}" if icone else titulo
    texto(slide, x + 0.2, y + 0.15, w - 0.4, 0.55, cab, tam=tam + 4, cor=cor_titulo, negrito=True)
    texto(slide, x + 0.2, y + 0.75, w - 0.4, h - 0.9, corpo, tam=tam, cor=PRETO)


def imagem(slide, caminho, x, y, largura=None, altura=None):
    kw = {}
    if largura:
        kw["width"] = Inches(largura)
    if altura:
        kw["height"] = Inches(altura)
    return slide.shapes.add_picture(str(caminho), Inches(x), Inches(y), **kw)


# 1 — Capa
s = prs.slides.add_slide(VAZIO)
retangulo(s, 0, 0, 13.333, 7.5, VERDE, forma=MSO_SHAPE.RECTANGLE)
retangulo(s, 0.8, 4.35, 1.6, 0.08, AMBAR, forma=MSO_SHAPE.RECTANGLE)
texto(s, 0.8, 1.7, 11, 1.2, "AgroSmart", tam=66, cor=BRANCO, negrito=True)
texto(s, 0.8, 2.95, 11.5, 1.2, "Do sensor à decisão em minutos, não em dias.", tam=30, cor=BRANCO)
texto(s, 0.8, 4.65, 11.5, 1.2,
      ["Plataforma de monitoramento agrícola que mede, prevê, decide e age",
       "FIAP · Engenharia de Software · 4ESOA · Fase 7 — entrega final"], tam=18, cor=VERDE_CLARO)

# 2 — Problema
s = novo_slide("O problema: o produtor descobre tarde demais", numero=2)
problemas = [
    ("💧", "Seca silenciosa", "A bomba de irrigação quebra e o solo seca por dias até alguém passar pelo talhão."),
    ("❄️", "Clima extremo", "Geada de madrugada e ondas de calor causam perdas em poucas horas, quando ninguém está olhando."),
    ("🐛", "Pragas", "A infestação só é notada quando as folhas doentes já passam de 30% da área."),
    ("📊", "Dados sem decisão", "Sensores mostram números, não dizem o que fazer, e o excesso de avisos faz o produtor parar de olhar."),
]
for i, (ic, t, c) in enumerate(problemas):
    cartao(s, 0.6 + i * 3.1, 1.75, 2.9, 3.9, t, c, icone=ic, tam=14,
           fundo=CINZA_CLARO if i < 3 else RGBColor(0xFF, 0xF3, 0xE0), cor_titulo=VERDE if i < 3 else VERMELHO)
texto(s, 0.6, 5.95, 12.1, 0.8, [[("Resultado: ", True), ("perda de produtividade, desperdício de água e insumos, "
                                "e decisões tomadas no escuro.", False)]], tam=18, cor=CINZA)

# 3 — Solução
s = novo_slide("A solução: AgroSmart mede, decide e age", "Uma plataforma que transforma leituras de campo em ação", 3)
etapas = [
    ("1. Mede", "Sensores de solo, clima, câmera e chuva em cada talhão (Arduino + simulador em escala)."),
    ("2. Decide", "Motor de regras agronômicas + Machine Learning que prevê o evento crítico 6h antes."),
    ("3. Age", "Liga a irrigação, abre ordem de manutenção, avisa o gestor e gera relatório com IA."),
    ("4. Melhora", "Mineração de processos mostra onde as ocorrências travam e o que automatizar a seguir."),
]
for i, (t, c) in enumerate(etapas):
    x = 0.6 + i * 3.1
    cartao(s, x, 1.9, 2.8, 3.6, t, c, tam=16)
    if i < 3:
        seta = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.83), Inches(3.5), Inches(0.24), Inches(0.4))
        seta.fill.solid()
        seta.fill.fore_color.rgb = AMBAR
        seta.line.fill.background()
texto(s, 0.6, 5.85, 12.1, 0.8, "Tudo em um painel web, rodando sozinho em ciclos contínuos, com autocontrole de saúde.",
      tam=18, cor=CINZA)

# 4 — Como funciona
s = novo_slide("Como funciona: arquitetura em 5 camadas", numero=4)
imagem(s, AQUI / "arquitetura_final.png", 1.35, 1.15, altura=5.75)

# 5 — Diferencial
s = novo_slide("Diferencial competitivo", "Os concorrentes mostram dados; o AgroSmart entrega a decisão e executa a primeira ação", 5)
linhas = [
    ("", "Visita a campo / planilha", "Telemetria comum", "AgroSmart"),
    ("Quando detecta", "dias depois", "quando já aconteceu", "até 6h antes (ML)"),
    ("Diz o que fazer", "não", "não", "recomendação + relatório IA"),
    ("Age sozinho", "não", "parcial", "irrigação · manutenção · aviso"),
    ("Mostra onde o processo trava", "não", "não", "mineração de processos"),
    ("Confiabilidade operacional", "—", "variável", "autocontrole + DevSecOps"),
]
tabela = s.shapes.add_table(len(linhas), 4, Inches(0.6), Inches(1.85), Inches(12.1), Inches(4.4)).table
larguras = [3.1, 2.8, 2.8, 3.4]
for j, w in enumerate(larguras):
    tabela.columns[j].width = Inches(w)
for i, linha in enumerate(linhas):
    for j, valor in enumerate(linha):
        cel = tabela.cell(i, j)
        run = cel.text_frame.paragraphs[0].add_run()
        run.text = valor
        run.font.size = Pt(17)
        run.font.bold = i == 0 or j == 0 or j == 3
        run.font.color.rgb = BRANCO if i == 0 else (VERDE if j == 3 else PRETO)
        cel.fill.solid()
        cel.fill.fore_color.rgb = VERDE if i == 0 else (VERDE_CLARO if j == 3 else (CINZA_CLARO if i % 2 else BRANCO))
        cel.vertical_anchor = MSO_ANCHOR.MIDDLE

# 6 — Resultados
s = novo_slide("Resultados na simulação", "5 talhões × 7 dias · 1.706 leituras · cenários de seca, calor, praga e geada", 6)
kpis = [
    ("0,95", "F1 do modelo preditivo", "contra 0,89 da regra reativa"),
    ("61%", "dos eventos críticos previstos", "com 4,7h de antecedência média"),
    ("~3h", "para normalizar o déficit hídrico", "com irrigação automática (mediana)"),
    ("0", "vulnerabilidades HIGH/CRITICAL", "na imagem publicada (eram 38)"),
]
for i, (num, t, c) in enumerate(kpis):
    x = 0.6 + i * 3.1
    retangulo(s, x, 1.95, 2.9, 3.4, CINZA_CLARO)
    texto(s, x, 2.15, 2.9, 1.3, num, tam=54, cor=VERDE, negrito=True, alinhamento=PP_ALIGN.CENTER)
    texto(s, x + 0.15, 3.55, 2.6, 0.9, t, tam=17, negrito=True, alinhamento=PP_ALIGN.CENTER)
    texto(s, x + 0.15, 4.45, 2.6, 0.8, c, tam=14, cor=CINZA, alinhamento=PP_ALIGN.CENTER)
texto(s, 0.6, 5.7, 12.1, 0.9, "Cada leitura inválida é rejeitada com o motivo registrado (5 de 1.706), "
      "duplicadas são removidas e campos vazios são imputados, para que a decisão use só dado confiável.", tam=16, cor=CINZA)

# 7 — Mineração de processos
s = novo_slide("Mineração de processos: onde as ocorrências travam", "55 ocorrências · 246 eventos · 16 variantes", 7)
imagem(s, AQUI / "evidencias" / "processo" / "dfg_operacional.png", 0.5, 1.6, largura=7.6)
achados = [
    [("Gargalo: ", True), ("ocorrência escalada leva 10h para normalizar (temperatura: a ação só avisa).", False)],
    [("Gargalo: ", True), ("falha de irrigação leva 45h (depende de manutenção manual, sem SLA).", False)],
    [("Variação: ", True), ("déficit hídrico resolve em 3h com bomba boa e em 47h com bomba quebrada.", False)],
    [("Oportunidade: ", True), ("61% dos críticos foram previstos pelo ML, mas nada age sobre a previsão → ação preventiva.", False)],
    [("Oportunidade: ", True), ("53% dos casos são movimento noturno repetitivo → suprimir alertas repetidos.", False)],
]
texto(s, 8.35, 1.65, 4.5, 5.2, achados, tam=14)

# 8 — Pronto para o mercado
s = novo_slide("Pronto para operar como produto", "Execução automatizada · monitoramento · DevSecOps", 8)
cartao(s, 0.6, 1.85, 3.9, 4.6, "Execução contínua",
       ["Docker Compose: pipeline + dashboard", "1 ciclo completo a cada 5 min",
        "Falha isolada: o ciclo seguinte segue", "Containers sem root, read-only, com limites"], tam=15)
cartao(s, 4.7, 1.85, 3.9, 4.6, "Monitoramento",
       ["Log estruturado (JSON)", "Status e duração de cada etapa", "Disponibilidade e indicadores de negócio",
        "Healthcheck: falha detectada em 1 ciclo"], tam=15)
cartao(s, 8.8, 1.85, 3.9, 4.6, "Pipeline DevSecOps",
       ["Lint + 19 testes automatizados", "SAST, dependências e segredos", "Scan da imagem (Trivy)",
        "Barrou 38 CVEs e containers root antes de publicar"], tam=15)

# 9 — Público-alvo
s = novo_slide("Público-alvo", numero=9)
cartao(s, 0.6, 1.5, 5.9, 2.4, "Produtores pequenos e médios",
       "Grãos, hortifrúti e café, de 5 a 200 talhões. Usuário direto: quer menos perda e menos idas a campo.", icone="🌱")
cartao(s, 6.8, 1.5, 5.9, 2.4, "Cooperativas agrícolas",
       "Canal de escala: contratam para os associados e recebem a visão consolidada da região.", icone="🤝")
cartao(s, 0.6, 4.15, 5.9, 2.4, "Seguradoras e crédito rural",
       "Score de risco por talhão a partir do histórico confiável da plataforma.", icone="🛡️",
       fundo=CINZA_CLARO)
cartao(s, 6.8, 4.15, 5.9, 2.4, "Agroindústria e pesquisa",
       "Rastreabilidade das condições de cultivo e dados anonimizados para estudos.", icone="🔬",
       fundo=CINZA_CLARO)

# 10 — Proposta de valor e receita
s = novo_slide("Proposta de valor e modelo de receita", numero=10)
retangulo(s, 0.6, 1.4, 12.1, 1.5, VERDE)
texto(s, 0.9, 1.5, 11.5, 1.3,
      ["“Antecipamos a perda, executamos a primeira resposta sozinhos e mostramos ao produtor exatamente o que fazer,",
       "com histórico confiável para negociar seguro e crédito.”"], tam=19, cor=BRANCO, ancora=MSO_ANCHOR.MIDDLE)
cartao(s, 0.6, 3.2, 3.9, 3.4, "SaaS por talhão",
       ["Básico: alertas + painel", "Avançado: ML preditivo, IA, histórico e mineração de processos"], tam=15)
cartao(s, 4.7, 3.2, 3.9, 3.4, "Kit de sensores",
       ["Hardware homologado", "Venda ou comodato", "Integra sensores que o produtor já tem"], tam=15)
cartao(s, 8.8, 3.2, 3.9, 3.4, "Produtos de dados",
       ["Score de risco para seguro e crédito", "Relatórios regionais", "API de insights para ERPs"], tam=15)

# 11 — Roadmap e equipe
s = novo_slide("Próximos passos e equipe", numero=11)
cartao(s, 0.6, 1.5, 6.2, 5.0, "Roadmap",
       ["Sensores físicos via MQTT / LoRaWAN", "Ação preventiva disparada pelo ML",
        "Verificação automática do efeito da irrigação", "SLA de manutenção integrado ao app",
        "App mobile + notificação por WhatsApp", "Piloto com uma cooperativa"], tam=16)
cartao(s, 7.1, 1.5, 5.6, 5.0, "Equipe — 4ESOA",
       ["Gabriel Genaro Dalaqua — RM 551986", "Alairton Rocha Scabelli — RM 551454",
        "Carolina Nascimento Amorim — RM 97930", "Eduardo Marins — RM 551892",
        "Sarah Ribeiro da Silva — RM 97747"], tam=16, fundo=CINZA_CLARO)

prs.save(SAIDA)
print(f"{len(prs.slides)} slides salvos em {SAIDA}")


def verificar_limites():
    """Confere se alguma forma passa da borda do slide."""
    w, h = prs.slide_width, prs.slide_height
    for i, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if sh.left + sh.width > w + Emu(5000) or sh.top + sh.height > h + Emu(5000):
                print(f"  aviso: slide {i} — forma '{sh.name}' passa da borda")


verificar_limites()
