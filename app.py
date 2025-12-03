import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="App Aviário Fácil", layout="centered")

st.markdown("""
    <style>
    /* Estilo dos Botões Grandes */
    .stButton>button {
        width: 100%;
        height: 65px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        margin-bottom: 8px;
    }
    /* Cores Específicas */
    .btn-voltar { border: 2px solid red; color: red; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
DB_FUNC = 'funcionarios_v6.csv'
DB_MOVIMENTO = 'movimentos_v6.csv'
DB_OBRA = 'config_obra.csv'

def load_data(arquivo, colunas):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas).to_csv(arquivo, index=False)
    return pd.read_csv(arquivo)

def save_data(arquivo, df):
    df.to_csv(arquivo, index=False)

# --- NAVEGAÇÃO ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
def navegar_para(tela): st.session_state['tela'] = tela; st.rerun()

# ================= TELA 1: MENU PRINCIPAL =================
def tela_inicio():
    st.title("🚜 Menu Principal")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👷 EQUIPE\n(Cadastro, Ponto, Pgto)"): navegar_para('menu_equipe')
    with col2:
        if st.button("🚛 VEÍCULOS\n(Gasolina, Oficina)"): navegar_para('menu_frota')
            
    if st.button("💰 FINANCEIRO DA OBRA"): navegar_para('menu_financeiro')

    # Rodapé com Saldo
    st.divider()
    df = load_data(DB_MOVIMENTO, ["Valor"])
    saldo = df["Valor"].sum() if not df.empty else 0.0
    cor = "green" if saldo >= 0 else "red"
    st.markdown(f"<h3 style='text-align: center; color: {cor};'>Caixa: R$ {saldo:,.2f}</h3>", unsafe_allow_html=True)

# ================= TELA 2: GESTÃO DE EQUIPE (CORRIGIDA) =================
def tela_equipe():
    st.title("👷 Controle de Equipe")
    
    # 1. Botão Gigante para Cadastrar Novo (Sempre visível)
    if st.button("➕ CADASTRAR NOVO FUNCIONÁRIO"):
        navegar_para('cadastro_funcionario')
    
    st.divider()
    
    # 2. Carregar Lista
    df_func = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"])
    
    if df_func.empty:
        st.info("Nenhum funcionário ativo. Clique no botão acima para cadastrar.")
        if st.button("⬅️ VOLTAR"): navegar_para('inicio')
        return

    # 3. Selecionar Funcionário para Ações
    lista_nomes = df_func["Nome"].unique()
    func_selecionado = st.selectbox("Selecione quem você quer gerenciar:", lista_nomes)
    
    # Recupera dados para mostrar na tela
    dados = df_func[df_func["Nome"] == func_selecionado].iloc[0]
    st.info(f"Cargo: {dados['Funcao']} | Diária: R$ {dados['Valor_Diaria']} | Início: {dados['Data_Inicio']}")
    
    # Ações
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"⏰ PONTO ({func_selecionado})"):
            st.session_state['func_sel'] = func_selecionado
            navegar_para('acao_ponto')
        if st.button(f"💸 VALE ({func_selecionado})"):
            st.session_state['func_sel'] = func_selecionado
            navegar_para('acao_vale')
            
    with c2:
        if st.button(f"✅ PAGAR ({func_selecionado})"):
            st.session_state['func_sel'] = func_selecionado
            navegar_para('acao_pagamento')
        
        # Botão de Excluir (Com proteção)
        if st.button("🗑️ EXCLUIR CADASTRO"):
            st.session_state['func_sel'] = func_selecionado
            navegar_para('confirmar_exclusao')

    st.markdown("---")
    if st.button("⬅️ VOLTAR AO INÍCIO"): navegar_para('inicio')

# --- TELA DE CADASTRO (VALIDADA) ---
def tela_cadastro_funcionario():
    st.header("Novo Cadastro")
    
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo (Obrigatório)")
        data_inicio = st.date_input("Data de Início", datetime.now())
        funcao = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre de Obras", "Cozinheira", "Outro"])
        valor = st.number_input("Valor da Diária (R$)", min_value=0.0, step=10.0)
        
        submitted = st.form_submit_button("💾 SALVAR FUNCIONÁRIO")
        
        if submitted:
            # VALIDAÇÃO: Impede salvar se faltar dados
            if nome == "" or valor == 0:
                st.error("⚠️ ERRO: O Nome e o Valor da Diária são obrigatórios!")
            else:
                df = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"])
                
                # Verifica se já existe
                if nome in df["Nome"].values:
                    st.error("Já existe alguém com esse nome!")
                else:
                    novo = pd.DataFrame([{
                        "Nome": nome, 
                        "Funcao": funcao, 
                        "Valor_Diaria": valor,
                        "Data_Inicio": data_inicio
                    }])
                    df = pd.concat([df, novo], ignore_index=True)
                    save_data(DB_FUNC, df)
                    st.success("Cadastrado com sucesso!")
                    navegar_para('menu_equipe')

    if st.button("Cancelar"): navegar_para('menu_equipe')

# --- TELA DE EXCLUSÃO ---
def tela_exclusao():
    nome = st.session_state['func_sel']
    st.warning(f"Tem certeza que deseja apagar **{nome}** do sistema?")
    st.write("Isso não apaga o histórico financeiro dele, apenas o cadastro atual.")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("SIM, EXCLUIR"):
            df = load_data(DB_FUNC, ["Nome"])
            # Filtra removendo o nome selecionado
            df = df[df["Nome"] != nome]
            save_data(DB_FUNC, df)
            st.success("Excluído!")
            navegar_para('menu_equipe')
    with c2:
        if st.button("NÃO, VOLTAR"): navegar_para('menu_equipe')

# --- TELAS DE AÇÃO (PONTO, VALE, ETC) ---
def tela_acao_ponto():
    nome = st.session_state['func_sel']
    st.header(f"Ponto: {nome}")
    dt = st.date_input("Data", datetime.now())
    tipo = st.radio("Presença", ["Dia Completo", "Meio Dia", "Falta"])
    if st.button("CONFIRMAR"):
        st.success("Ponto Registrado (Simulação)") 
        # Aqui entraria a lógica de salvar no banco de ponto
        if st.button("Voltar"): navegar_para('menu_equipe')
    if st.button("Cancelar"): navegar_para('menu_equipe')

def tela_acao_vale():
    nome = st.session_state['func_sel']
    st.header(f"Vale para {nome}")
    val = st.number_input("Valor R$", min_value=0.0)
    obs = st.text_input("Motivo")
    if st.button("DAR VALE"):
        df = load_data(DB_MOVIMENTO, ["Data"])
        novo = {"Data": datetime.now(), "Categoria": "Mão de Obra", "Descricao": f"Vale {nome} - {obs}", "Valor": -val}
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        save_data(DB_MOVIMENTO, df)
        st.success("Vale registrado no caixa!")
        navegar_para('menu_equipe')
    if st.button("Cancelar"): navegar_para('menu_equipe')

def tela_acao_pagamento():
    nome = st.session_state['func_sel']
    st.header(f"Pagamento Final: {nome}")
    val = st.number_input("Valor do Acerto R$", min_value=0.0)
    if st.button("REALIZAR PAGAMENTO"):
        df = load_data(DB_MOVIMENTO, ["Data"])
        novo = {"Data": datetime.now(), "Categoria": "Mão de Obra", "Descricao": f"Pgto Final {nome}", "Valor": -val}
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        save_data(DB_MOVIMENTO, df)
        st.balloons()
        st.success("Pago!")
        navegar_para('menu_equipe')
    if st.button("Cancelar"): navegar_para('menu_equipe')

# --- OUTRAS TELAS (FROTA E FINANCEIRO - Simplificadas) ---
def tela_frota():
    st.title("🚛 Veículos")
    st.info("Aqui você controla combustível e manutenção.")
    if st.button("⬅️ VOLTAR"): navegar_para('inicio')

def tela_financeiro():
    st.title("💰 Financeiro")
    df = load_data(DB_MOVIMENTO, ["Data", "Descricao", "Valor"])
    st.dataframe(df, use_container_width=True)
    if st.button("⬅️ VOLTAR"): navegar_para('inicio')

# --- CONTROLADOR ---
def main():
    if st.session_state['tela'] == 'inicio': tela_inicio()
    elif st.session_state['tela'] == 'menu_equipe': tela_equipe()
    elif st.session_state['tela'] == 'cadastro_funcionario': tela_cadastro_funcionario()
    elif st.session_state['tela'] == 'confirmar_exclusao': tela_exclusao()
    elif st.session_state['tela'] == 'acao_ponto': tela_acao_ponto()
    elif st.session_state['tela'] == 'acao_vale': tela_acao_vale()
    elif st.session_state['tela'] == 'acao_pagamento': tela_acao_pagamento()
    elif st.session_state['tela'] == 'menu_frota': tela_frota()
    elif st.session_state['tela'] == 'menu_financeiro': tela_financeiro()

if __name__ == "__main__":
    main()
