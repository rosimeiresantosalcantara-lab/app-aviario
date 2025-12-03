import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL PREMIUM ---
st.set_page_config(page_title="Gestor Aviário PRO", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    /* Botões Padrão App */
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 12px;
        margin-bottom: 8px;
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        color: #1f2937;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
    }
    /* Botões de Navegação (Voltar/Home) - Destaque Diferente */
    .nav-btn {
        border: 1px solid #ef4444 !important;
        color: #ef4444 !important;
    }
    
    /* Cabeçalhos e Métricas */
    h1 { font-size: 2.2rem; font-weight: 800; color: #111827; }
    h2 { font-size: 1.5rem; font-weight: 700; color: #374151; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
    
    /* Esconder menu padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE ARQUIVOS (DATABASE) ---
DB_FUNC = 'db_funcionarios.csv'
DB_VEICULOS = 'db_veiculos.csv' # Novo!
DB_MOVIMENTOS = 'db_financeiro.csv'
DB_OBRA = 'db_obra_config.csv'

def load_data(arquivo, colunas):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas).to_csv(arquivo, index=False)
    return pd.read_csv(arquivo)

def save_row(arquivo, df, row_data):
    novo = pd.DataFrame([row_data])
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(arquivo, index=False)

def save_full(arquivo, df):
    df.to_csv(arquivo, index=False)

# --- 3. NAVEGAÇÃO INTELIGENTE ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
if 'hist_voltar' not in st.session_state: st.session_state['hist_voltar'] = 'inicio' # Para saber pra onde voltar

def ir_para(tela, voltar_para='inicio'):
    st.session_state['hist_voltar'] = voltar_para
    st.session_state['tela'] = tela
    st.rerun()

def barra_navegacao(tela_anterior):
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ VOLTAR TELA"): 
            ir_para(tela_anterior)
    with c2:
        if st.button("🏠 MENU INICIAL"): 
            ir_para('inicio')

# ================= TELA 1: DASHBOARD (HOME) =================
def tela_inicio():
    st.image("https://cdn-icons-png.flaticon.com/512/2666/2666505.png", width=60) # Ícone ilustrativo
    st.title("Painel de Controle")
    
    # 1. KPIs (Indicadores Principais)
    df_mov = load_data(DB_MOVIMENTOS, ["Valor"])
    saldo = df_mov["Valor"].sum() if not df_mov.empty else 0.0
    
    df_obra = load_data(DB_OBRA, ["Valor_Total"])
    total_obra = float(df_obra["Valor_Total"].iloc[0]) if not df_obra.empty else 0.0
    recebido = df_mov[df_mov["Valor"] > 0]["Valor"].sum() if not df_mov.empty else 0.0
    falta_receber = total_obra - recebido

    # Cartões de Resumo
    col1, col2 = st.columns(2)
    col1.metric("Caixa (Saldo)", f"R$ {saldo:,.2f}", delta_color="normal")
    col2.metric("A Receber", f"R$ {falta_receber:,.2f}", delta_color="inverse")
    
    st.divider()
    
    # 2. Menu de Ações
    st.subheader("O que deseja acessar?")
    
    if st.button("👷 GESTÃO DE EQUIPE"): ir_para('menu_equipe', 'inicio')
    if st.button("🚛 FROTA & VEÍCULOS"): ir_para('menu_frota', 'inicio')
    if st.button("💰 FINANCEIRO DA OBRA"): ir_para('menu_financeiro', 'inicio')
    if st.button("⚙️ CONFIGURAÇÕES DA OBRA"): ir_para('config_obra', 'inicio')

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("👷 Equipe")
    
    if st.button("➕ CADASTRAR NOVO FUNCIONÁRIO"): ir_para('cad_func', 'menu_equipe')
    
    df = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria"])
    if df.empty:
        st.warning("Cadastre alguém primeiro.")
        barra_navegacao('inicio')
        return

    func = st.selectbox("Selecione o Colaborador:", df["Nome"].unique())
    st.session_state['func_atual'] = func
    
    # Dashboard do Funcionário
    dados = df[df["Nome"] == func].iloc[0]
    st.info(f"Cargo: {dados['Funcao']} | Diária: R$ {dados['Valor_Diaria']}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
        if st.button("💸 VALE"): ir_para('acao_vale', 'menu_equipe')
    with c2:
        if st.button("✅ PAGAMENTO"): ir_para('acao_pgto', 'menu_equipe')
        if st.button("📝 FALTAS/OBS"): ir_para('acao_obs', 'menu_equipe')

    barra_navegacao('inicio')

def tela_cad_func():
    st.header("Novo Cadastro")
    with st.form("form_func"):
        nome = st.text_input("Nome Completo")
        func = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Cozinheira", "Motorista"])
        val = st.number_input("Valor Diária (R$)", min_value=0.0)
        if st.form_submit_button("SALVAR"):
            df = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria"])
            save_row(DB_FUNC, df, {"Nome": nome, "Funcao": func, "Valor_Diaria": val})
            st.success("Cadastrado!")
            ir_para('menu_equipe')
    barra_navegacao('menu_equipe')

# --- Ações de Equipe ---
def acao_equipe_generica(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    if tipo == "Ponto":
        st.info("O registro de ponto serve para seu controle pessoal de dias trabalhados.")
        dt = st.date_input("Data", datetime.now())
        status = st.radio("Presença", ["Dia Completo", "Meio Dia", "Falta"])
        if st.button("CONFIRMAR PONTO"):
            # Lógica simples: Salva apenas registro visual no histórico financeiro com valor 0
            df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
            save_row(DB_MOVIMENTOS, df, {"Data": dt, "Categoria": "Ponto", "Descricao": f"Ponto {nome} - {status}", "Valor": 0})
            st.success("Registrado!")
            ir_para('menu_equipe')
            
    elif tipo == "Vale":
        val = st.number_input("Valor do Vale (R$)", min_value=0.0)
        obs = st.text_input("Motivo")
        if st.button("DAR VALE (SAÍDA DE CAIXA)"):
            df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
            save_row(DB_MOVIMENTOS, df, {
                "Data": datetime.now(), "Categoria": "Mão de Obra", 
                "Descricao": f"Vale {nome} ({obs})", "Valor": -val
            })
            st.success("Vale lançado!")
            ir_para('menu_equipe')

    elif tipo == "Pagamento":
        val = st.number_input("Valor Final (Acerto)", min_value=0.0)
        if st.button("PAGAR ACERTO"):
            df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
            save_row(DB_MOVIMENTOS, df, {
                "Data": datetime.now(), "Categoria": "Mão de Obra", 
                "Descricao": f"Pgto Final {nome}", "Valor": -val
            })
            st.success("Pago!")
            ir_para('menu_equipe')
            
    barra_navegacao('menu_equipe')

# ================= TELA 3: FROTA (NOVA FUNCIONALIDADE) =================
def tela_frota():
    st.title("🚛 Frota")
    
    if st.button("➕ CADASTRAR NOVO VEÍCULO"): ir_para('cad_veiculo', 'menu_frota')
    
    df_v = load_data(DB_VEICULOS, ["Veiculo", "Placa", "Km_Inicial"])
    
    if df_v.empty:
        st.warning("Nenhum veículo cadastrado.")
        barra_navegacao('inicio')
        return

    veiculo_escolhido = st.selectbox("Selecione o Veículo:", df_v["Veiculo"].unique())
    st.session_state['veiculo_atual'] = veiculo_escolhido
    
    # Recupera KM inicial
    km_ini = df_v[df_v["Veiculo"] == veiculo_escolhido]["Km_Inicial"].values[0]
    st.caption(f"KM de Registro: {km_ini}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⛽ ABASTECER"): ir_para('acao_abastecer', 'menu_frota')
    with c2:
        if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manutencao', 'menu_frota')
        
    barra_navegacao('inicio')

def tela_cad_veiculo():
    st.header("Cadastrar Veículo")
    with st.form("novo_carro"):
        modelo = st.text_input("Modelo (Ex: Hilux Prata)")
        placa = st.text_input("Placa (Opcional)")
        km = st.number_input("Quilometragem Atual", min_value=0)
        
        if st.form_submit_button("SALVAR"):
            nome_final = f"{modelo} ({placa})" if placa else modelo
            df = load_data(DB_VEICULOS, ["Veiculo", "Placa", "Km_Inicial"])
            save_row(DB_VEICULOS, df, {"Veiculo": nome_final, "Placa": placa, "Km_Inicial": km})
            st.success("Veículo salvo!")
            ir_para('menu_frota')
    barra_navegacao('menu_frota')

def acao_frota_generica(tipo):
    veiculo = st.session_state['veiculo_atual']
    st.header(f"{tipo}: {veiculo}")
    
    if tipo == "Abastecer":
        km_hoje = st.number_input("KM Atual (Painel)", min_value=0)
        litros = st.number_input("Litros", min_value=0.0)
        valor = st.number_input("Valor Total (R$)", min_value=0.0)
        
        if st.button("SALVAR ABASTECIMENTO"):
            df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
            save_row(DB_MOVIMENTOS, df, {
                "Data": datetime.now(), "Categoria": "Combustível", 
                "Descricao": f"{veiculo} ({litros}L | KM {km_hoje})", "Valor": -valor
            })
            st.success("Registrado!")
            ir_para('menu_frota')
            
    elif tipo == "Manutenção":
        item = st.text_input("O que foi feito? (Ex: Pneu, Óleo)")
        valor = st.number_input("Valor Gasto (R$)", min_value=0.0)
        
        if st.button("SALVAR MANUTENÇÃO"):
            df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
            save_row(DB_MOVIMENTOS, df, {
                "Data": datetime.now(), "Categoria": "Manutenção", 
                "Descricao": f"{veiculo} - {item}", "Valor": -valor
            })
            st.success("Registrado!")
            ir_para('menu_frota')
            
    barra_navegacao('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_financeiro():
    st.title("💰 Financeiro")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ RECEBER (ENTRADA)"): ir_para('fin_entrada', 'menu_financeiro')
    with c2:
        if st.button("➖ GASTO GERAL (MATERIAIS)"): ir_para('fin_saida', 'menu_financeiro')
        
    st.divider()
    st.subheader("📜 Extrato Recente")
    
    df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
    if not df.empty:
        # Mostra os ultimos 10, invertido
        df['idx_original'] = df.index
        df_show = df.sort_index(ascending=False).head(10)
        
        for i, row in df_show.iterrows():
            cor = "green" if row['Valor'] > 0 else "red"
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"**{row['Descricao']}**")
                st.caption(f"{row['Data']} | {row['Categoria']}")
                st.markdown(f"<span style='color:{cor}; font-weight:bold'>R$ {row['Valor']:,.2f}</span>", unsafe_allow_html=True)
            with cols[1]:
                if st.button("🗑️", key=f"del_{row['idx_original']}"):
                    df = df.drop(row['idx_original'])
                    save_full(DB_MOVIMENTOS, df)
                    st.rerun()
            st.write("---")
            
    barra_navegacao('inicio')

def tela_fin_movimento(tipo):
    st.header(f"Registrar {tipo}")
    
    desc = st.text_input("Descrição (Ex: Cimento, Pagamento Etapa 1)")
    valor = st.number_input("Valor (R$)", min_value=0.0)
    
    cat = "Receita" if tipo == "Entrada" else "Material/Outros"
    
    if st.button("SALVAR"):
        val_final = valor if tipo == "Entrada" else -valor
        df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
        save_row(DB_MOVIMENTOS, df, {
            "Data": datetime.now(), "Categoria": cat, 
            "Descricao": desc, "Valor": val_final
        })
        st.success("Salvo!")
        ir_para('menu_financeiro')
        
    barra_navegacao('menu_financeiro')

def tela_config_obra():
    st.title("⚙️ Configuração da Obra")
    st.info("Defina aqui o valor total do contrato para acompanhar quanto falta receber.")
    
    df = load_data(DB_OBRA, ["Valor_Total"])
    atual = float(df["Valor_Total"].iloc[0]) if not df.empty else 0.0
    
    novo_val = st.number_input("Valor Total do Contrato (R$)", value=atual)
    
    if st.button("ATUALIZAR CONTRATO"):
        pd.DataFrame([{"Valor_Total": novo_val}]).to_csv(DB_OBRA, index=False)
        st.success("Atualizado!")
        
    barra_navegacao('inicio')

# ================= ROTEADOR PRINCIPAL =================
def main():
    tela = st.session_state['tela']
    
    if tela == 'inicio': tela_inicio()
    
    # Equipe
    elif tela == 'menu_equipe': tela_equipe()
    elif tela == 'cad_func': tela_cad_func()
    elif tela == 'acao_ponto': acao_equipe_generica("Ponto")
    elif tela == 'acao_vale': acao_equipe_generica("Vale")
    elif tela == 'acao_pgto': acao_equipe_generica("Pagamento")
    elif tela == 'acao_obs': 
        st.info("Em breve: Bloco de notas para justificativas.")
        barra_navegacao('menu_equipe')
        
    # Frota
    elif tela == 'menu_frota': tela_frota()
    elif tela == 'cad_veiculo': tela_cad_veiculo()
    elif tela == 'acao_abastecer': acao_frota_generica("Abastecer")
    elif tela == 'acao_manutencao': acao_frota_generica("Manutenção")
    
    # Financeiro & Config
    elif tela == 'menu_financeiro': tela_financeiro()
    elif tela == 'fin_entrada': tela_fin_movimento("Entrada")
    elif tela == 'fin_saida': tela_fin_movimento("Saída")
    elif tela == 'config_obra': tela_config_obra()

if __name__ == "__main__":
    main()
