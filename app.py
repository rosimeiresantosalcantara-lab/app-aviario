import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL E CSS AVANÇADO ---
st.set_page_config(page_title="GestorPRO", layout="centered", page_icon="💎")

st.markdown("""
    <style>
    /* 1. FORÇAR GRID 2x2 NO CELULAR (O CÓDIGO MÁGICO) */
    @media (max-width: 576px) {
        /* Obriga as colunas a ficarem lado a lado */
        div[data-testid="column"] {
            width: 48% !important;
            flex: 0 0 48% !important;
            min-width: 10px !important;
        }
        /* Ajusta o espaçamento entre elas */
        div[data-testid="column"] > div {
            width: 100% !important;
        }
    }

    /* 2. ESTILO DOS BOTÕES (MENU PRINCIPAL) */
    .btn-main > button {
        width: 100%;
        height: 100px;
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        background: white !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
        margin-bottom: 10px !important;
    }
    .btn-main > button:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
        transform: translateY(-2px);
    }
    
    /* 3. BOTÕES DE AÇÃO (MENORES) */
    .btn-action > button {
        height: 60px;
        border-radius: 12px;
        font-weight: 600;
        background-color: #f8fafc;
    }
    
    /* 4. REMOVER ESPAÇOS EXTRAS DO TOPO */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    
    /* Esconder menus técnicos */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. UTILITÁRIOS DE FORMATAÇÃO ---
def format_brl(valor):
    if valor is None: return "R$ 0,00"
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def format_data_visual(data_input):
    """Converte datas para DD/MM/AAAA apenas para MOSTRAR na tela"""
    if data_input is None: return ""
    try:
        if isinstance(data_input, str):
            # Se vier do CSV (YYYY-MM-DD)
            data_obj = datetime.strptime(data_input, '%Y-%m-%d')
            return data_obj.strftime('%d/%m/%Y')
        # Se vier do Date Input (datetime.date)
        return data_input.strftime('%d/%m/%Y')
    except: return str(data_input)

# --- 3. BANCO DE DADOS ---
DB_FUNC = 'db_funcionarios_v18.csv'
DB_PONTO = 'db_ponto_v18.csv'
DB_VEICULOS = 'db_veiculos_v18.csv'
DB_FINANCEIRO = 'db_financeiro_v18.csv'
DB_CONFIG = 'db_config_v18.csv'

# Colunas
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
    except: return pd.DataFrame(columns=colunas_padrao)

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
    # Usa classes CSS específicas para não bugar o layout grid
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ VOLTAR"): ir_para(destino)
    with c2: 
        if st.button("🏠 INÍCIO"): ir_para('inicio')

# ================= TELA 1: DASHBOARD (LAYOUT NOVO) =================
def tela_inicio():
    st.title("GestorPRO")
    st.caption(f"🗓️ Hoje: {datetime.now().strftime('%d/%m/%Y')}")
    
    # KPIs
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    saldo_real = df_fin["Valor"].sum() if not df_fin.empty else 0.0
    
    fatura_cartao = 0.0
    if not df_fin.empty:
        filtro_cartao = df_fin[(df_fin["Metodo_Pagto"] == "Cartão de Crédito") & (df_fin["Valor"] < 0)]
        fatura_cartao = abs(filtro_cartao["Valor"].sum())

    c1, c2 = st.columns(2)
    c1.metric("Caixa Atual", format_brl(saldo_real))
    c2.metric("Fatura Cartão", format_brl(fatura_cartao), delta_color="inverse")
    
    st.write("") 
    st.subheader("Menu Principal")
    
    # --- AQUI ESTÁ A CLASSE CSS MÁGICA ---
    # Colocamos 'st.markdown' com divs vazias apenas para aplicar o estilo se necessário
    # mas o CSS global já cuida do 'div[data-testid="column"]'
    
    c_menu1, c_menu2 = st.columns(2)
    
    with c_menu1:
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("👷 EQUIPE\n& Ponto"): ir_para('menu_equipe', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("🚛 FROTA\n& Máquinas"): ir_para('menu_frota', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)

    with c_menu2:
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("💰 CAIXA\n& Extrato"): ir_para('menu_fin', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("💳 CARTÕES\n& Faturas"): ir_para('menu_cartao', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("Gestão de Pessoas")
    
    # Botão de Cadastro
    st.markdown('<div class="btn-action">', unsafe_allow_html=True)
    if st.button("➕ NOVO COLABORADOR"): ir_para('cad_func', 'menu_equipe')
    st.markdown('</div>', unsafe_allow_html=True)
    
    df_func = load_data(DB_FUNC, COLS_FUNC)
    if df_func.empty:
        st.info("Nenhum cadastro encontrado.")
        barra_nav('inicio'); return

    st.write("---")
    nome_sel = st.selectbox("Selecione o Colaborador:", df_func["Nome"].unique())
    st.session_state['func_atual'] = nome_sel
    
    # Dados
    linha_dados = df_func[df_func["Nome"] == nome_sel].iloc[0]
    idx_dados = df_func[df_func["Nome"] == nome_sel].index[0]
    
    # Cálculos
    df_ponto = load_data(DB_PONTO, COLS_PONTO)
    dias = df_ponto[df_ponto["Nome"] == nome_sel]["Qtd_Dias"].sum()
    
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    pagos = df_fin[(df_fin["Entidade"] == nome_sel) & (df_fin["Valor"] < 0)]["Valor"].sum()
    
    a_receber = (dias * float(linha_dados["Valor_Diaria"])) - abs(pagos)
    
    # Info
    st.info(f"Função: **{linha_dados['Funcao']}**")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dias", f"{dias:g}")
    c2.metric("Pago", format_brl(abs(pagos)))
    c3.metric("Saldo", format_brl(a_receber))
    
    tab1, tab2 = st.tabs(["⚡ AÇÕES", "✏️ EDITAR"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
            if st.button("💸 VALE"): ir_para('acao_vale', 'menu_equipe')
        with c2:
            if st.button("✅ PAGAR"): ir_para('acao_pgto', 'menu_equipe')
            if st.button("📝 FALTA"): ir_para('acao_falta', 'menu_equipe')

    with tab2:
        with st.form("edit_func"):
            novo_nome = st.text_input("Nome", value=linha_dados['Nome'])
            
            # Data formatada para DD/MM/YYYY
            try: dt_obj = datetime.strptime(str(linha_dados['Data_Inicio']), '%Y-%m-%d').date()
            except: dt_obj = datetime.now()
            
            nova_data = st.date_input("Admissão", value=dt_obj, format="DD/MM/YYYY")
            novo_valor = st.number_input("Diária (R$)", min_value=0.0, value=float(linha_dados['Valor_Diaria']))
            
            if st.form_submit_button("SALVAR ALTERAÇÕES"):
                df_func.at[idx_dados, "Nome"] = novo_nome
                df_func.at[idx_dados, "Data_Inicio"] = nova_data
                df_func.at[idx_dados, "Valor_Diaria"] = novo_valor
                save_full(DB_FUNC, df_func)
                st.toast("Atualizado!")
                st.rerun()
                
        if st.button("🗑️ EXCLUIR CADASTRO"):
            df_func = df_func.drop(idx_dados)
            save_full(DB_FUNC, df_func)
            st.rerun()

    barra_nav('inicio')

def tela_cad_func():
    st.header("Novo Cadastro")
    with st.form("cad_func", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        func = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Motorista", "Cozinheira", "Outro"])
        
        # O FORMATO DD/MM/YYYY ESTÁ AQUI
        dt_ini = st.date_input("Data de Admissão", datetime.now(), format="DD/MM/YYYY")
        
        val = st.number_input("Valor da Diária (R$)", min_value=0.0, value=None, placeholder="0,00")
        
        st.caption("Bancário (Opcional)")
        banco = st.text_input("Banco")
        pix = st.text_input("Chave PIX")
        
        if st.form_submit_button("SALVAR"):
            if nome and val:
                add_row(DB_FUNC, {
                    "Nome": nome, "Funcao": func, "Valor_Diaria": val, 
                    "Data_Inicio": dt_ini, "Chave_Pix": pix, "Banco": banco
                }, COLS_FUNC)
                st.toast("Cadastrado!", icon="✅")
    barra_nav('menu_equipe')

def tela_acao_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    with st.form(f"form_{tipo}", clear_on_submit=True):
        if tipo == "Ponto":
            dt = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            op = st.radio("Registro", ["Dia Completo (1.0)", "Meio Dia (0.5)", "Falta (0.0)"])
            if st.form_submit_button("CONFIRMAR"):
                qtd = 1.0 if "Completo" in op else (0.5 if "Meio" in op else 0.0)
                desc = "Dia Normal" if qtd==1.0 else "Meio/Falta"
                add_row(DB_PONTO, {"Data": dt, "Nome": nome, "Qtd_Dias": qtd, "Descricao": desc}, COLS_PONTO)
                st.toast("Ponto Salvo!")

        elif tipo in ["Vale", "Pagamento"]:
            val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
            metodo = st.selectbox("Pago via", ["PIX", "Dinheiro", "Transferência"])
            obs = st.text_input("Obs")
            if st.form_submit_button("LANÇAR"):
                if val:
                    desc_final = f"{tipo} ({obs})" if obs else tipo
                    add_row(DB_FINANCEIRO, {
                        "Data": datetime.now(), "Categoria": "Mão de Obra", 
                        "Descricao": desc_final, "Valor": -val, "Entidade": nome, "Metodo_Pagto": metodo
                    }, COLS_FIN)
                    st.toast("Financeiro Atualizado!")
                    
        elif tipo == "Falta":
            motivo = st.text_input("Motivo da falta")
            if st.form_submit_button("SALVAR"):
                add_row(DB_PONTO, {"Data": datetime.now(), "Nome": nome, "Qtd_Dias": 0.0, "Descricao": f"Falta: {motivo}"}, COLS_PONTO)
                st.toast("Ok!")
    barra_nav('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("Frota")
    st.markdown('<div class="btn-action">', unsafe_allow_html=True)
    if st.button("➕ NOVO VEÍCULO"): ir_para('cad_veic', 'menu_frota')
    st.markdown('</div>', unsafe_allow_html=True)
    
    df_v = load_data(DB_VEICULOS, COLS_VEIC)
    if df_v.empty:
        barra_nav('inicio'); return

    st.write("---")
    veic = st.selectbox("Selecione:", df_v["Veiculo"].unique())
    st.session_state['veic_atual'] = veic
    
    # Dados Veículo
    idx_veic = df_v[df_v["Veiculo"] == veic].index[0]
    dados_veic = df_v.iloc[idx_veic]
    
    # Gasto
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    gastos = df_fin[df_fin["Entidade"] == veic]
    total = abs(gastos[gastos["Valor"] < 0]["Valor"].sum())
    
    st.metric("Custo Total", format_brl(total))
    
    tab1, tab2 = st.tabs(["AÇÕES", "EDITAR"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("⛽ ABASTECER"): ir_para('acao_abast', 'menu_frota')
        with c2: 
            if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manut', 'menu_frota')
            
    with tab2:
        with st.form("edit_veic"):
            n_mod = st.text_input("Modelo", value=str(dados_veic['Veiculo']).split(' - ')[0])
            n_placa = st.text_input("Placa", value=str(dados_veic['Placa']))
            n_km = st.number_input("KM Inicial", value=int(dados_veic['Km_Inicial']))
            
            if st.form_submit_button("SALVAR"):
                nome_formatado = f"{n_mod} - {n_placa}"
                df_v.at[idx_veic, "Veiculo"] = nome_formatado
                df_v.at[idx_veic, "Placa"] = n_placa
                df_v.at[idx_veic, "Km_Inicial"] = n_km
                save_full(DB_VEICULOS, df_v)
                st.toast("Atualizado!")
                st.rerun()

    barra_nav('inicio')

def tela_cad_veic():
    st.header("Novo Veículo")
    with st.form("cad_v", clear_on_submit=True):
        mod = st.text_input("Modelo (Ex: Strada)")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0)
        if st.form_submit_button("SALVAR"):
            nome = f"{mod} - {placa}"
            add_row(DB_VEICULOS, {"Veiculo": nome, "Placa": placa, "Km_Inicial": km}, COLS_VEIC)
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
            item = st.selectbox("Serviço", ["Mecânica", "Pneus", "Óleo", "Elétrica", "Peças", "Funilaria"])
            
        val = st.number_input("Valor Pago (R$)", min_value=0.0, value=None, placeholder="0,00")
        pagto = st.selectbox("Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito"])
        
        if st.form_submit_button("LANÇAR"):
            if val:
                desc = f"Abast. {lit}L" if tipo=="Abastecer" else f"Manut: {item}"
                if tipo=="Abastecer": desc += f" (KM {km})"
                
                add_row(DB_FINANCEIRO, {
                    "Data": datetime.now(), "Categoria": "Combustível" if tipo=="Abastecer" else "Manutenção", 
                    "Descricao": desc, "Valor": -val, "Entidade": veic, "Metodo_Pagto": pagto
                }, COLS_FIN)
                st.toast("Salvo!")
    barra_nav('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_fin():
    st.title("Financeiro")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("➕ RECEITA"): ir_para('fin_receita', 'menu_fin')
    with c2: 
        if st.button("➖ DESPESA"): ir_para('fin_despesa', 'menu_fin')
        
    st.write("---")
    st.subheader("Extrato")
    
    filtro = st.selectbox("Filtrar:", ["Todos", "Cartão de Crédito", "PIX", "Dinheiro"])
    
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    if not df.empty:
        df = df.sort_values("Data", ascending=False)
        if filtro != "Todos":
            df = df[df["Metodo_Pagto"] == filtro]
            
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
                    if st.button("🗑️", key=f"d{idx}"):
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
            desc = st.selectbox("Item", ["Cimento", "Areia", "Tijolos", "Ferro", "Madeira", "Telhas", "Tintas", "Elétrica", "Hidráulica"])
            cat = "Material"
            
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
        pagto = st.selectbox("Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito", "Boleto"])
        
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
    st.title("Cartões de Crédito")
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    if df.empty:
        st.info("Sem dados."); barra_nav('inicio'); return
        
    credito = df[(df["Metodo_Pagto"] == "Cartão de Crédito") & (df["Valor"] < 0)]
    total = abs(credito["Valor"].sum())
    
    st.metric("Fatura Acumulada", format_brl(total))
    
    if not credito.empty:
        st.write("---")
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
