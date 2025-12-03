import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="GestorPRO Financeiro", layout="centered", page_icon="💳")

st.markdown("""
    <style>
    /* Design Clean e Profissional */
    .stButton>button {
        width: 100%;
        height: 55px;
        border-radius: 8px;
        font-weight: 600;
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        color: #2c3e50;
    }
    .stButton>button:hover {
        border-color: #0d6efd;
        color: #0d6efd;
        background-color: #ffffff;
    }
    
    /* Destaque para área de PIX */
    .pix-box {
        padding: 15px;
        background-color: #e8f5e9;
        border: 1px solid #4caf50;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. LISTAS E UTILITÁRIOS ---
LISTA_FUNCOES = ["Pedreiro", "Servente", "Mestre de Obras", "Motorista", "Cozinheira", "Administrativo"]
LISTA_MATERIAIS = ["Cimento", "Areia", "Tijolos", "Ferro", "Madeira", "Telhas", "Tintas", "Elétrica", "Hidráulica"]
LISTA_MANUTENCAO = ["Mecânica", "Pneus", "Óleo", "Elétrica", "Peças", "Funilaria"]
LISTA_PAGAMENTO = ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito", "Boleto"]

def format_brl(valor):
    if valor is None: return "R$ 0,00"
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def format_data_br_coluna(series):
    return pd.to_datetime(series).dt.strftime('%d/%m/%Y')

# --- 3. BANCO DE DADOS ---
DB_FUNC = 'db_funcionarios_v14.csv'
DB_PONTO = 'db_ponto_v14.csv'
DB_VEICULOS = 'db_veiculos_v14.csv'
DB_FINANCEIRO = 'db_financeiro_v14.csv'
DB_CONFIG = 'db_config_v14.csv'
DB_CARTAO = 'db_cartao_v14.csv' # Novo para controle de faturas

# Colunas (Adicionado Chave_Pix)
COLS_FUNC = ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio", "Chave_Pix", "Banco"]
COLS_PONTO = ["Data", "Nome", "Qtd_Dias", "Descricao"]
COLS_VEIC = ["Veiculo", "Placa", "Km_Inicial"]
COLS_FIN = ["Data", "Categoria", "Descricao", "Valor", "Entidade", "Metodo_Pagto"]
COLS_CONF = ["Valor_Total"]

def load_data(arquivo, colunas_padrao):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas_padrao).to_csv(arquivo, index=False)
        return pd.read_csv(arquivo)
    try:
        df = pd.read_csv(arquivo)
        for col in colunas_padrao:
            if col not in df.columns:
                df[col] = 0 if "Valor" in col else ""
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

def add_row(arquivo, dados, cols):
    df = load_data(arquivo, cols)
    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    df.to_csv(arquivo, index=False)

def save_full(arquivo, df):
    df.to_csv(arquivo, index=False)

# --- 4. NAVEGAÇÃO ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
if 'hist_voltar' not in st.session_state: st.session_state['hist_voltar'] = 'inicio'

def ir_para(tela, voltar_para='inicio'):
    st.session_state['hist_voltar'] = voltar_para
    st.session_state['tela'] = tela
    st.rerun()

def barra_nav(destino):
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ VOLTAR"): ir_para(destino)
    with c2: 
        if st.button("🏠 INÍCIO"): ir_para('inicio')

# ================= TELA 1: HOME =================
def tela_inicio():
    st.title("GestorPRO")
    
    # KPIs Financeiros
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    
    # Saldo Real (Considera tudo que já foi pago/recebido)
    saldo_real = df_fin["Valor"].sum() if not df_fin.empty else 0.0
    
    # Gasto Cartão Crédito (A Pagar)
    fatura_cartao = 0.0
    if not df_fin.empty:
        filtro_cartao = df_fin[(df_fin["Metodo_Pagto"] == "Cartão de Crédito") & (df_fin["Valor"] < 0)]
        fatura_cartao = abs(filtro_cartao["Valor"].sum())

    c1, c2 = st.columns(2)
    c1.metric("Saldo em Caixa", format_brl(saldo_real))
    c2.metric("Fatura Cartão (A Pagar)", format_brl(fatura_cartao), delta_color="inverse")
    
    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("👷 EQUIPE & PIX"): ir_para('menu_equipe', 'inicio')
        if st.button("💰 FINANCEIRO"): ir_para('menu_fin', 'inicio')
    with c2:
        if st.button("🚛 FROTA"): ir_para('menu_frota', 'inicio')
        if st.button("💳 CARTÕES"): ir_para('menu_cartao', 'inicio')

# ================= TELA 2: EQUIPE COM PIX =================
def tela_equipe():
    st.title("Gestão de Pessoas")
    if st.button("➕ NOVO COLABORADOR"): ir_para('cad_func', 'menu_equipe')
    
    df_func = load_data(DB_FUNC, COLS_FUNC)
    if df_func.empty:
        st.info("Cadastre alguém primeiro.")
        barra_nav('inicio')
        return

    nome_sel = st.selectbox("Selecione:", df_func["Nome"].unique())
    st.session_state['func_atual'] = nome_sel
    
    dados = df_func[df_func["Nome"] == nome_sel].iloc[0]
    
    # Cálculo Financeiro
    df_ponto = load_data(DB_PONTO, COLS_PONTO)
    dias = df_ponto[df_ponto["Nome"] == nome_sel]["Qtd_Dias"].sum()
    
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    pagos = df_fin[(df_fin["Entidade"] == nome_sel) & (df_fin["Valor"] < 0)]["Valor"].sum()
    
    a_receber = (dias * float(dados["Valor_Diaria"])) - abs(pagos)
    
    # Área PIX (Segurança)
    with st.expander("🔑 Ver Chave PIX / Dados Bancários", expanded=False):
        pix = dados.get("Chave_Pix", "Não cadastrado")
        banco = dados.get("Banco", "-")
        st.markdown(f"""
            <div class='pix-box'>
                <b>Banco:</b> {banco}<br>
                <b>Chave PIX:</b> <h3>{pix}</h3>
                <small>Copie a chave acima e pague no seu app bancário.</small>
            </div>
        """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Dias", f"{dias:g}")
    c2.metric("Já Pago", format_brl(abs(pagos)))
    c3.metric("Saldo", format_brl(a_receber))
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
        if st.button("💸 VALE (PIX)"): ir_para('acao_vale', 'menu_equipe')
    with c2:
        if st.button("✅ PAGAR (PIX)"): ir_para('acao_pgto', 'menu_equipe')
        if st.button("📝 FALTA"): ir_para('acao_falta', 'menu_equipe')
        
    barra_nav('inicio')

def tela_cad_func():
    st.header("Cadastro Completo")
    with st.form("cad_func", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        func = st.selectbox("Função", LISTA_FUNCOES)
        val = st.number_input("Diária (R$)", min_value=0.0, value=None, placeholder="0,00")
        
        st.markdown("---")
        st.caption("Dados para Pagamento (Segurança)")
        banco = st.text_input("Nome do Banco")
        pix = st.text_input("Chave PIX (CPF, Celular, Email)")
        
        if st.form_submit_button("SALVAR"):
            if nome and val:
                add_row(DB_FUNC, {
                    "Nome": nome, "Funcao": func, "Valor_Diaria": val, 
                    "Data_Inicio": datetime.now(), "Chave_Pix": pix, "Banco": banco
                }, COLS_FUNC)
                st.toast("Salvo!", icon="✅")
    barra_nav('menu_equipe')

def tela_acao_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    # Recupera PIX para mostrar na hora de pagar
    if tipo in ["Vale", "Pagamento"]:
        df = load_data(DB_FUNC, COLS_FUNC)
        dados = df[df["Nome"] == nome].iloc[0]
        pix = dados.get("Chave_Pix", "")
        if pix:
            st.info(f"🔑 Chave PIX de {nome}: **{pix}**")
    
    with st.form(f"form_{tipo}", clear_on_submit=True):
        if tipo == "Ponto":
            dt = st.date_input("Data", datetime.now())
            op = st.radio("Presença", ["Dia Completo", "Meio Dia", "Falta"])
            if st.form_submit_button("CONFIRMAR"):
                qtd = 1.0 if "Completo" in op else (0.5 if "Meio" in op else 0.0)
                desc = "Dia Normal" if qtd==1.0 else "Meio/Falta"
                add_row(DB_PONTO, {"Data": dt, "Nome": nome, "Qtd_Dias": qtd, "Descricao": desc}, COLS_PONTO)
                st.toast("Registrado!")

        elif tipo in ["Vale", "Pagamento"]:
            val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
            metodo = st.selectbox("Como você pagou?", ["PIX", "Dinheiro", "Transferência"])
            obs = st.text_input("Obs (Opcional)")
            
            if st.form_submit_button("CONFIRMAR PAGAMENTO"):
                if val:
                    desc = f"{tipo} ({obs})" if obs else f"{tipo}"
                    add_row(DB_FINANCEIRO, {
                        "Data": datetime.now(), "Categoria": "Mão de Obra", 
                        "Descricao": desc, "Valor": -val, "Entidade": nome, "Metodo_Pagto": metodo
                    }, COLS_FIN)
                    st.toast("Financeiro Atualizado!", icon="💸")
                    
        elif tipo == "Falta":
            motivo = st.text_input("Motivo")
            if st.form_submit_button("SALVAR"):
                add_row(DB_PONTO, {"Data": datetime.now(), "Nome": nome, "Qtd_Dias": 0.0, "Descricao": f"Falta: {motivo}"}, COLS_PONTO)
                st.toast("Ok!")
                
    barra_nav('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("Frota")
    if st.button("➕ NOVO VEÍCULO"): ir_para('cad_veic', 'menu_frota')
    
    df_v = load_data(DB_VEICULOS, COLS_VEIC)
    if df_v.empty:
        barra_nav('inicio'); return

    veic = st.selectbox("Selecione:", df_v["Veiculo"].unique())
    st.session_state['veic_atual'] = veic
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⛽ ABASTECER"): ir_para('acao_abast', 'menu_frota')
    with c2: 
        if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manut', 'menu_frota')
    
    st.caption("O custo será lançado no Financeiro automaticamente.")
    barra_nav('inicio')

def tela_cad_veic():
    st.header("Cadastro Veículo")
    with st.form("cad_v"):
        mod = st.text_input("Modelo")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0)
        if st.form_submit_button("SALVAR"):
            add_row(DB_VEICULOS, {"Veiculo": f"{mod} {placa}", "Placa": placa, "Km_Inicial": km}, COLS_VEIC)
            st.toast("Salvo!")
    barra_nav('menu_frota')

def tela_acao_frota(tipo):
    veic = st.session_state['veic_atual']
    st.header(f"{tipo}: {veic}")
    with st.form("act_frota", clear_on_submit=True):
        if tipo == "Abastecer":
            lit = st.number_input("Litros", min_value=0.0)
            km = st.number_input("KM Painel", min_value=0)
        else:
            item = st.selectbox("Serviço", LISTA_MANUTENCAO)
            
        val = st.number_input("Valor Pago (R$)", min_value=0.0, value=None, placeholder="0,00")
        pagto = st.selectbox("Forma Pagamento", LISTA_PAGAMENTO)
        
        if st.form_submit_button("LANÇAR"):
            if val:
                desc = f"Abast. {lit}L" if tipo=="Abastecer" else f"Manut: {item}"
                if tipo=="Abastecer": desc += f" (KM {km})"
                
                add_row(DB_FINANCEIRO, {
                    "Data": datetime.now(), "Categoria": "Combustível" if tipo=="Abastecer" else "Manutenção", 
                    "Descricao": desc, "Valor": -val, "Entidade": veic, "Metodo_Pagto": pagto
                }, COLS_FIN)
                st.toast("Lançado!")
    barra_nav('menu_frota')

# ================= TELA 4: FINANCEIRO & CARTÕES =================
def tela_fin():
    st.title("Financeiro")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("➕ RECEITA"): ir_para('fin_receita', 'menu_fin')
    with c2: 
        if st.button("➖ DESPESA"): ir_para('fin_despesa', 'menu_fin')
        
    st.write("---")
    st.subheader("Extrato")
    
    # Filtros
    filtro_pagto = st.selectbox("Filtrar por Pagamento:", ["Todos", "Cartão de Crédito", "PIX", "Dinheiro"])
    
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    if not df.empty:
        df = df.sort_values("Data", ascending=False)
        if filtro_pagto != "Todos":
            df = df[df["Metodo_Pagto"] == filtro_pagto]
            
        for idx, row in df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 1])
                dt = pd.to_datetime(row['Data']).strftime('%d/%m/%Y')
                with c1:
                    st.write(f"**{row['Descricao']}**")
                    st.caption(f"{dt} • {row['Metodo_Pagto']}")
                with c2:
                    cor = "green" if row['Valor']>0 else "red"
                    st.markdown(f"<span style='color:{cor}'><b>{format_brl(row['Valor'])}</b></span>", unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️", key=f"del_{idx}"):
                        df = df.drop(idx)
                        save_full(DB_FINANCEIRO, df)
                        st.rerun()
                st.divider()
    barra_nav('inicio')

def tela_movimento(tipo):
    st.header(f"Lançar {tipo}")
    with st.form("mov", clear_on_submit=True):
        if tipo == "Receita":
            desc = st.text_input("Descrição")
            cat = "Receita"
        else:
            desc = st.selectbox("Item", LISTA_MATERIAIS)
            cat = "Material"
            
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
        pagto = st.selectbox("Forma Pagamento", LISTA_PAGAMENTO)
        
        if st.form_submit_button("SALVAR"):
            if val:
                v_final = val if tipo=="Receita" else -val
                add_row(DB_FINANCEIRO, {
                    "Data": datetime.now(), "Categoria": cat, 
                    "Descricao": desc, "Valor": v_final, "Entidade": "Geral", "Metodo_Pagto": pagto
                }, COLS_FIN)
                st.toast("Sucesso!")
    barra_nav('menu_fin')

def tela_cartoes():
    st.title("Controle de Cartão")
    st.info("Aqui você vê tudo que foi pago no Crédito e ainda vai cair na fatura.")
    
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    if df.empty:
        st.write("Sem dados.")
        barra_nav('inicio'); return
        
    credito = df[(df["Metodo_Pagto"] == "Cartão de Crédito") & (df["Valor"] < 0)]
    total = abs(credito["Valor"].sum())
    
    st.metric("Total Fatura (Acumulado)", format_brl(total))
    
    st.write("---")
    st.write("**Compras no Crédito:**")
    if not credito.empty:
        view = credito[["Data", "Descricao", "Valor"]].copy()
        view["Data"] = pd.to_datetime(view["Data"]).dt.strftime('%d/%m/%Y')
        view["Valor"] = view["Valor"].apply(format_brl)
        st.table(view)
        
    barra_nav('inicio')

# ================= ROTEADOR =================
def main():
    tela = st.session_state['tela']
    
    if tela == 'inicio': tela_inicio()
    elif tela == 'menu_equipe': tela_equipe()
    elif tela == 'cad_func': tela_cad_func()
    elif tela == 'acao_ponto': tela_acao_equipe("Ponto")
    elif tela == 'acao_vale': tela_acao_equipe("Vale")
    elif tela == 'acao_pgto': tela_acao_equipe("Pagamento")
    elif tela == 'acao_falta': tela_acao_equipe("Falta")
    
    elif tela == 'menu_frota': tela_frota()
    elif tela == 'cad_veic': tela_cad_veic()
    elif tela == 'acao_abast': tela_acao_frota("Abastecer")
    elif tela == 'acao_manut': tela_acao_frota("Manutenção")
    
    elif tela == 'menu_fin': tela_fin()
    elif tela == 'fin_receita': tela_movimento("Receita")
    elif tela == 'fin_despesa': tela_movimento("Despesa")
    
    elif tela == 'menu_cartao': tela_cartoes()

if __name__ == "__main__":
    main()
