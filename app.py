import streamlit as st
import sqlite3
import json
import io
import os
from datetime import date, datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.utils import ImageReader

DB_PATH = "orcamentos_dplay.db"
ROSA = colors.HexColor("#D4145A")
PRETO = colors.HexColor("#171717")
CINZA = colors.HexColor("#666666")
CINZA_CLARO = colors.HexColor("#F4F4F6")

st.set_page_config(page_title="Grupo Dplay | Orçamentos", page_icon="🎵", layout="wide")

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            data TEXT NOT NULL,
            orgao TEXT,
            processo TEXT,
            fornecedor TEXT,
            fornecedor_cnpj TEXT,
            produto TEXT,
            marca TEXT,
            fabricante TEXT,
            modelo TEXT,
            quantidade INTEGER,
            valor_unitario REAL,
            descricao TEXT,
            disponibilidade TEXT,
            prazo_entrega TEXT,
            validade TEXT,
            pagamento TEXT,
            garantia TEXT,
            observacoes TEXT,
            total REAL
        )
    """)
    conn.commit()
    return conn

def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_pdf(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=14*mm, bottomMargin=15*mm
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TituloDplay", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=19, leading=22, textColor=ROSA, alignment=TA_CENTER, spaceAfter=3))
    styles.add(ParagraphStyle(name="SubDplay", parent=styles["Normal"], fontSize=8, textColor=CINZA,
                              alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle(name="SecaoDplay", parent=styles["Heading2"], fontSize=10, leading=12,
                              textColor=ROSA, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="PequenoDplay", parent=styles["Normal"], fontSize=8, leading=11))
    story = []

    logo_file = "logo.png"
    header_data = []
    if os.path.exists(logo_file):
        logo = Image(logo_file, width=48*mm, height=35*mm, kind="proportional")
        company = Paragraph(
            "<b><font color='#D4145A' size='13'>GRUPO DPLAY</font></b><br/>"
            "<font size='7' color='#666666'>CNPJ: 11.950.831/0001-40</font><br/>"
            "<font size='7' color='#666666'>Rua Major Gabriel, 1666, Térreo — Praça 14 de Janeiro</font><br/>"
            "<font size='7' color='#666666'>Manaus – AM | CEP 69020-405</font><br/>"
            "<font size='7' color='#666666'>(92) 98177-3290 | www.dplaymusic.com.br</font>",
            styles["PequenoDplay"])
        ht = Table([[logo, company]], colWidths=[55*mm, 115*mm])
        ht.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (1,0), (1,0), "RIGHT"),
            ("LINEBELOW", (0,0), (-1,-1), 2, ROSA),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(ht)
    else:
        story.append(Paragraph("<b>GRUPO DPLAY</b>", styles["TituloDplay"]))

    story += [Spacer(1, 8), Paragraph("ORÇAMENTO COMERCIAL", styles["TituloDplay"]),
              Paragraph("COTAÇÃO PARA ANÁLISE E PROCESSO LICITATÓRIO", styles["SubDplay"])]

    meta = [
        ["Nº DO ORÇAMENTO", dados["numero"], "DATA", dados["data"]],
        ["PROCESSO / EDITAL", dados["processo"] or "—", "ÓRGÃO SOLICITANTE", dados["orgao"] or "—"]
    ]
    t = Table(meta, colWidths=[32*mm, 53*mm, 32*mm, 53*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), CINZA_CLARO), ("BACKGROUND", (2,0), (2,-1), CINZA_CLARO),
        ("TEXTCOLOR", (0,0), (0,-1), ROSA), ("TEXTCOLOR", (2,0), (2,-1), ROSA),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), 7),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6)
    ]))
    story += [t, Paragraph("1. IDENTIFICAÇÃO DO FORNECEDOR", styles["SecaoDplay"])]
    supplier = [
        ["EMPRESA", dados["fornecedor"] or "—", "CNPJ", dados["fornecedor_cnpj"] or "—"]
    ]
    t = Table(supplier, colWidths=[25*mm, 65*mm, 20*mm, 60*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), CINZA_CLARO), ("BACKGROUND", (2,0), (2,0), CINZA_CLARO),
        ("TEXTCOLOR", (0,0), (0,0), ROSA), ("TEXTCOLOR", (2,0), (2,0), ROSA),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#DDDDDD")),
        ("FONTSIZE", (0,0), (-1,-1), 7), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)
    ]))
    story += [t, Paragraph("2. PRODUTO OFERTADO", styles["SecaoDplay"])]
    prod = [
        ["PRODUTO", dados["produto"] or "—"],
        ["MARCA / FABRICANTE", f'{dados["marca"] or "—"} / {dados["fabricante"] or "—"}'],
        ["MODELO / VERSÃO", dados["modelo"] or "—"],
        ["QUANTIDADE", str(dados["quantidade"])],
        ["VALOR UNITÁRIO", moeda(dados["valor_unitario"])],
        ["VALOR TOTAL DO ITEM", moeda(dados["total"])]
    ]
    t = Table(prod, colWidths=[42*mm, 128*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), CINZA_CLARO), ("TEXTCOLOR", (0,0), (0,-1), ROSA),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#DDDDDD")),
        ("FONTSIZE", (0,0), (-1,-1), 8), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)
    ]))
    story += [t, Spacer(1, 5), Paragraph("DESCRIÇÃO TÉCNICA COMPLETA", styles["SecaoDplay"]),
              Paragraph((dados["descricao"] or "Não informada.").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"), styles["PequenoDplay"]),
              Spacer(1, 5)]
    avail = [
        ["DISPONIBILIDADE", dados["disponibilidade"] or "—"],
        ["PRAZO DE ENTREGA", dados["prazo_entrega"] or "—"],
        ["VALIDADE DA PROPOSTA", dados["validade"] or "—"],
        ["PAGAMENTO", dados["pagamento"] or "—"],
        ["GARANTIA", dados["garantia"] or "—"]
    ]
    t = Table(avail, colWidths=[42*mm, 128*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), CINZA_CLARO), ("TEXTCOLOR", (0,0), (0,-1), ROSA),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#DDDDDD")),
        ("FONTSIZE", (0,0), (-1,-1), 8), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)
    ]))
    story += [Paragraph("3. CONDIÇÕES COMERCIAIS", styles["SecaoDplay"]), t,
              Paragraph("4. OBSERVAÇÕES", styles["SecaoDplay"]),
              Paragraph((dados["observacoes"] or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"), styles["PequenoDplay"]),
              Spacer(1, 12)]
    total_t = Table([["VALOR TOTAL DO ORÇAMENTO", moeda(dados["total"])]], colWidths=[115*mm, 55*mm])
    total_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CINZA_CLARO), ("TEXTCOLOR", (0,0), (-1,-1), ROSA),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 10),
        ("ALIGN", (1,0), (1,0), "RIGHT"), ("BOX", (0,0), (-1,-1), .8, ROSA),
        ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9)
    ]))
    story += [total_t, Spacer(1, 25),
              Paragraph("____________________________________________", styles["SubDplay"]),
              Paragraph("<b>RESPONSÁVEL PELA COTAÇÃO</b><br/>GRUPO DPLAY", styles["SubDplay"])]
    doc.build(story)
    return buffer.getvalue()

conn = conectar()

st.markdown("""
<style>
.main {background-color: #FAFAFB;}
.block-container {padding-top: 1.5rem; max-width: 1200px;}
h1, h2, h3 {color: #171717;}
div[data-testid="stMetric"] {background: #F4F4F6; padding: 14px; border-radius: 12px; border-left: 4px solid #D4145A;}
.stButton button[kind="primary"] {background: #D4145A; border-color: #D4145A;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("### GRUPO DPLAY")
    st.caption("Sistema de Orçamentos")
    pagina = st.radio("NAVEGAÇÃO", ["Painel inicial", "Novo orçamento", "Histórico"])
    st.divider()
    st.caption("Protótipo interno • Versão 0.1")

st.title("Central de Orçamentos")
st.caption("Organização e geração de propostas comerciais para processos de cotação e licitação.")

if pagina == "Painel inicial":
    total = conn.execute("SELECT COUNT(*) FROM orcamentos").fetchone()[0]
    soma = conn.execute("SELECT COALESCE(SUM(total),0) FROM orcamentos").fetchone()[0]
    recentes = conn.execute("SELECT numero, data, orgao, produto, total FROM orcamentos ORDER BY id DESC LIMIT 5").fetchall()
    a,b,c = st.columns(3)
    a.metric("Orçamentos registrados", total)
    b.metric("Valor somado", moeda(soma))
    c.metric("Empresa", "GRUPO DPLAY")
    st.subheader("Acesso rápido")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Novo orçamento**\n\nCadastre os dados do órgão, fornecedor e produto para gerar um PDF padronizado.")
    with col2:
        st.info("**Histórico**\n\nConsulte os orçamentos que já foram registrados neste protótipo.")
    st.subheader("Orçamentos recentes")
    if recentes:
        st.dataframe(
            [{"Nº": r[0], "Data": r[1], "Órgão": r[2], "Produto": r[3], "Total": moeda(r[4])} for r in recentes],
            use_container_width=True, hide_index=True
        )
    else:
        st.write("Ainda não há orçamentos cadastrados. Acesse **Novo orçamento** para criar o primeiro.")

elif pagina == "Novo orçamento":
    st.subheader("Cadastrar novo orçamento")
    st.write("Preencha os campos abaixo. Os campos com * são necessários para gerar a proposta.")
    with st.form("form_orcamento"):
        c1,c2 = st.columns(2)
        with c1:
            numero = st.text_input("Número do orçamento *", value=f"DPLAY-{datetime.now().strftime('%Y%m%d-%H%M')}")
            data_orc = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            orgao = st.text_input("Órgão solicitante")
            processo = st.text_input("Processo / edital")
            fornecedor = st.text_input("Nome / razão social do fornecedor")
            fornecedor_cnpj = st.text_input("CNPJ do fornecedor")
        with c2:
            produto = st.text_input("Nome do produto *")
            marca = st.text_input("Marca")
            fabricante = st.text_input("Fabricante")
            modelo = st.text_input("Modelo / versão")
            quantidade = st.number_input("Quantidade *", min_value=1, value=1, step=1)
            valor_unitario = st.number_input("Valor unitário (R$) *", min_value=0.0, value=0.0, step=0.01, format="%.2f")
        descricao = st.text_area("Descrição técnica completa", height=120, placeholder="Informe características, especificações, compatibilidade, dimensões, potência, conexões etc.")
        disponibilidade = st.text_input("Disponibilidade do produto", placeholder="Ex.: Em estoque / Sob encomenda / 15 dias")
        c3,c4,c5 = st.columns(3)
        with c3:
            prazo_entrega = st.text_input("Prazo de entrega", placeholder="Ex.: 10 dias úteis")
        with c4:
            validade = st.text_input("Validade da proposta", value="30 dias")
        with c5:
            garantia = st.text_input("Garantia", placeholder="Ex.: 12 meses")
        pagamento = st.text_input("Condição de pagamento")
        observacoes = st.text_area("Observações adicionais")
        enviado = st.form_submit_button("Salvar orçamento e gerar PDF", type="primary", use_container_width=True)

    if enviado:
        if not numero.strip() or not produto.strip():
            st.error("Preencha o número do orçamento e o nome do produto.")
        else:
            total_item = int(quantidade) * float(valor_unitario)
            dados = {
                "numero": numero.strip(), "data": data_or.strftime("%d/%m/%Y"),
                "orgao": orgao, "processo": processo, "fornecedor": fornecedor,
                "fornecedor_cnpj": fornecedor_cnpj, "produto": produto, "marca": marca,
                "fabricante": fabricante, "modelo": modelo, "quantidade": int(quantidade),
                "valor_unitario": float(valor_unitario), "descricao": descricao,
                "disponibilidade": disponibilidade, "prazo_entrega": prazo_entrega,
                "validade": validade, "pagamento": pagamento, "garantia": garantia,
                "observacoes": observacoes, "total": total_item
            }
            conn.execute("""
                INSERT INTO orcamentos (
                    numero,data,orgao,processo,fornecedor,fornecedor_cnpj,produto,marca,
                    fabricante,modelo,quantidade,valor_unitario,descricao,disponibilidade,
                    prazo_entrega,validade,pagamento,garantia,observacoes,total
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                dados["numero"], dados["data"], dados["orgao"], dados["processo"],
                dados["fornecedor"], dados["fornecedor_cnpj"], dados["produto"],
                dados["marca"], dados["fabricante"], dados["modelo"], dados["quantidade"],
                dados["valor_unitario"], dados["descricao"], dados["disponibilidade"],
                dados["prazo_entrega"], dados["validade"], dados["pagamento"],
                dados["garantia"], dados["observacoes"], dados["total"]
            ))
            conn.commit()
            pdf = gerar_pdf(dados)
            st.success("Orçamento registrado com sucesso!")
            st.download_button("Baixar orçamento em PDF", data=pdf,
                               file_name=f"{numero.replace('/', '-')}.pdf",
                               mime="application/pdf", type="primary")
            st.caption(f"Valor total calculado: {moeda(total_item)}")

else:
    st.subheader("Histórico de orçamentos")
    linhas = conn.execute("""
        SELECT id, numero, data, orgao, fornecedor, produto, quantidade, total
        FROM orcamentos ORDER BY id DESC
    """).fetchall()
    if not linhas:
        st.info("Nenhum orçamento registrado até o momento.")
    else:
        st.dataframe([
            {"ID": r[0], "Nº": r[1], "Data": r[2], "Órgão": r[3], "Fornecedor": r[4],
             "Produto": r[5], "Qtd.": r[6], "Total": moeda(r[7])}
            for r in linhas
        ], use_container_width=True, hide_index=True)
        ids = [r[0] for r in linhas]
        escolhido = st.selectbox("Selecione um orçamento para consultar", ids,
                                 format_func=lambda x: next(f'{r[1]} — {r[5]}' for r in linhas if r[0] == x))
        if st.button("Gerar PDF novamente"):
            r = conn.execute("SELECT numero,data,orgao,processo,fornecedor,fornecedor_cnpj,produto,marca,fabricante,modelo,quantidade,valor_unitario,descricao,disponibilidade,prazo_entrega,validade,pagamento,garantia,observacoes,total FROM orcamentos WHERE id=?", (escolhido,)).fetchone()
            keys = ["numero","data","orgao","processo","fornecedor","fornecedor_cnpj","produto","marca","fabricante","modelo","quantidade","valor_unitario","descricao","disponibilidade","prazo_entrega","validade","pagamento","garantia","observacoes","total"]
            dados = dict(zip(keys, r))
            pdf = gerar_pdf(dados)
            st.download_button("Baixar PDF", data=pdf, file_name=f'{dados["numero"].replace("/", "-")}.pdf', mime="application/pdf")
st.divider()
st.caption("GRUPO DPLAY • CNPJ 11.950.831/0001-40 • Manaus – AM")
