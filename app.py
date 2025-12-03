import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL PREMIUM ---
st.set_page_config(page_title="Gestor Aviário Premium", layout="centered", page_icon="🚜")

st.markdown("""
    <style>
    /* Estilo de App Nativo - Botões Grandes e Fáceis */
    .stButton>button {
        width: 100%;
        height: 65px;
        font-size: 19px;
        font-weight: 600;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    /* Destaque para valores em dinheiro */
    .metric-value { font-size: 26px; font-weight: bold; }
    
    /* Esconder elementos desnecessários da tela */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE BANCO DE DADOS (CSVs) ---
DB_FUNC = 'funcionarios_v7.csv'
DB_MOVIMENTO = 'movimentos_v7.csv'
DB_OBRA = 'config_obra.csv'

# Função para carregar dados sem dar erro
def load_data(arquivo, colunas):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas).to_csv(arquivo, index=False)
    return pd.read_csv(arquivo)

# Função para salvar nova linha
def save_row(arquivo, df, row_data):
    novo = pd.DataFrame([row_data])
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(arquivo, index=False)

# Função para salvar o dataframe inteiro (usado em edições/exclusões)
def save_full_df(arquivo, df):
    df.to_csv(arquivo, index=False)

# --- 3. NAVEGAÇÃO ENTRE TELAS ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
if 'veiculo_sel' not in st.session_state: st.session_state['veiculo_sel'] = ''
if 'func_sel' not in st.session_state: st.session_state['func_sel'] = ''

def navegar(tela):
    st.session_state['tela'] = tela
    st.rerun()

# ================= TELA 1: MENU INICIAL =================
def tela_inicio():
    st.title("🚜 Menu Principal")
    st.write("Selecione a área que deseja gerenciar:")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("👷 EQUIPE\n(Ponto, Vales)"): navegar('menu_equipe')
    with c2:
        if st.button("🚛 VEÍCULOS\n(Diesel, Peças)"): navegar('menu_frota')
    
    if st.button("💰 FINANCEIRO DA OBRA\n(Recebimentos e Gastos)"): navegar('menu_financeiro')

    # Resumo Financeiro no Rodapé
    st.markdown("---")
    df = load_data(DB_MOVIMENTO, ["Valor"])
    saldo = df["Valor"].sum() if not df.empty else 0.0
    cor = "#2ecc71" if saldo >= 0 else "#e74c3c"
    st.markdown(f"<div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px;'>"
                f"<h3>Caixa Atual</h3><h1 style='color: {cor};'>R$ {saldo:,.2f}</h1></div>", unsafe_allow_html=True)

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("👷 Gestão de Equipe")
    
    # Botão de Cadastro (Destaque)
    if st.button("➕ CADASTRAR NOVO FUNCIONÁRIO"): navegar('cadastro_func')
    
    st.divider()
    
    df_func = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"])
    
    if df_func.empty:
        st.info("Ninguém cadastrado ainda.")
        if st.button("⬅️ VOLTAR"): navegar('inicio')
        return

    # Seletor de Funcionário
    lista = df_func["Nome"].unique()
    selecionado = st.selectbox("Selecione o Funcionário:", lista)
    
    # Mostra dados do funcionário selecionado
    dados = df_func[df_func["Nome"] == selecionado].iloc[0]
    st.info(f"📋 **{dados['Funcao']}** | Diária: **R$ {dados['Valor_Diaria']}** | Desde: {dados['Data_Inicio']}")
    
    # Botões de Ação para o Funcionário
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"⏰ MARCAR PONTO"):
            st.session_state['func_sel'] = selecionado
            navegar('acao_ponto')
            
        if st.button(f"💸 DAR VALE"):
            st.session_state['func_sel'] = selecionado
            navegar('acao_vale')
            
    with c2:
        if st.button(f"✅ PAGAR ACERTO"):
            st.session_state['func_sel'] = selecionado
            navegar('acao_pagamento')
            
        if st.button(f"📝 JUSTIFICAR FALTA"):
            st.session_state['func_sel'] = selecionado
            navegar('acao_justificativa')
            
    # Botão de Excluir Funcionário
    with st.expander(f"⚙️ Opções Avançadas para {selecionado}"):
        if st.button("🗑️ EXCLUIR CADASTRO DO SISTEMA"):
            df_func = df_func[df_func["Nome"] != selecionado]
            save_full_df(DB_FUNC, df_func)
            st.success("Excluído!")
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ VOLTAR AO MENU"): navegar('inicio')

# --- FORMULÁRIOS DE EQUIPE ---
def tela_cadastro_func():
    st.header("Novo Funcionário")
    with st.form("cad_func"):
        nome = st.text_input("Nome Completo")
        funcao = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre de Obras", "Cozinheira", "Motorista", "Outro"])
        valor = st.number_input("Valor da Diária (R$)", min_value=0.0)
        inicio = st.date_input("Data de Início", datetime.now())
        
        if st.form_submit_button("💾 SALVAR"):
            if nome and valor > 0:
                df = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"])
                save_row(DB_FUNC, df, {"Nome": nome, "Funcao": funcao, "Valor_Diaria": valor, "Data_Inicio": inicio})
                st.success("Cadastrado!")
                navegar('menu_equipe')
            else:
                st.error("Preencha Nome e Valor corretamente.")
    if st.button("Cancelar"): navegar('menu_equipe')

def tela_acao_ponto():
    nome = st.session_state['func_sel']
    st.header(f"Ponto: {nome}")
    
    # Lógica de Ponto (Simples: Gera custo mas não mexe no caixa ainda)
    c1, c2 = st.columns(2)
    dt = c1.date_input("Data", datetime.now())
    tipo = c2.radio("Presença", ["Dia Completo (100%)", "Meio Dia (50%)", "Falta (0%)"])
    
    if st.button("CONFIRMAR PONTO"):
        # Aqui apenas registramos visualmente, pois o foco do app é financeiro/caixa
        # Para um app simples, salvar ponto pode ser apenas um registro de "histórico"
        # Futuramente podemos criar um DB_PONTO só para isso.
        st.success(f"Ponto registrado para {nome} em {dt} ({tipo})")
        if st.button("Voltar"): navegar('menu_equipe')
        
    if st.button("Cancelar"): navegar('menu_equipe')

def tela_acao_vale():
    nome = st.session_state['func_sel']
    st.header(f"Vale para {nome}")
    val = st.number_input("Valor do Vale (R$)", min_value=0.0)
    obs = st.text_input("Motivo", "Adiantamento")
    
    if st.button("📉 RETIRAR DO CAIXA (DAR VALE)"):
        df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
        save_row(DB_MOVIMENTO, df, {
            "Data": datetime.now(), "Categoria": "Mão de Obra", 
            "Descricao": f"Vale {nome} ({obs})", "Valor": -val
        })
        st.success("Vale lançado!")
        navegar('menu_equipe')
    if st.button("Cancelar"): navegar('menu_equipe')

def tela_acao_pagamento():
    nome = st.session_state['func_sel']
    st.header(f"Acerto Final: {nome}")
    val = st.number_input("Valor a Pagar (R$)", min_value=0.0)
    
    if st.button("📉 PAGAR E RETIRAR DO CAIXA"):
        df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
        save_row(DB_MOVIMENTO, df, {
            "Data": datetime.now(), "Categoria": "Mão de Obra", 
            "Descricao": f"Pagamento Final {nome}", "Valor": -val
        })
        st.balloons()
        st.success("Pagamento realizado!")
        navegar('menu_equipe')
    if st.button("Cancelar"): navegar('menu_equipe')

def tela_acao_justificativa():
    nome = st.session_state['func_sel']
    st.header(f"Justificativa: {nome}")
    motivo = st.text_area("Descreva o motivo da falta ou ocorrência:")
    
    if st.button("SALVAR OBSERVAÇÃO"):
        # Salva num log de movimentos com valor 0 apenas para registro
        df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
        save_row(DB_MOVIMENTO, df, {
            "Data": datetime.now(), "Categoria": "Mão de Obra", 
            "Descricao": f"Obs {nome}: {motivo}", "Valor": 0
        })
        st.success("Observação salva no histórico.")
        navegar('menu_equipe')
    if st.button("Cancelar"): navegar('menu_equipe')


# ================= TELA 3: VEÍCULOS (RESTAURADA) =================
def tela_frota():
    st.title("🚛 Veículos e Máquinas")
    
    veiculo = st.selectbox("Selecione o Veículo:", 
                          ["Hilux", "Caminhão Baú", "Trator", "Carreta", "Carro de Passeio", "Outro"])
    st.session_state['veiculo_sel'] = veiculo
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⛽ ABASTECER"): navegar('acao_combustivel')
    with c2:
        if st.button("🔧 MANUTENÇÃO/PEÇAS"): navegar('acao_manutencao')
            
    st.markdown("---")
    
    # Histórico do Veículo (Recurso Premium)
    st.write(f"📜 Últimos gastos com **{veiculo}**:")
    df = load_data(DB_MOVIMENTO, ["Descricao", "Valor", "Data"])
    if not df.empty:
        # Filtra tudo que tem o nome do veículo na descrição
        df_v = df[df["Descricao"].str.contains(veiculo, case=False, na=False)]
        st.dataframe(df_v[["Data", "Descricao", "Valor"]].tail(5), use_container_width=True)
        
    if st.button("⬅️ VOLTAR AO MENU"): navegar('inicio')

def tela_acao_combustivel():
    veiculo = st.session_state['veiculo_sel']
    st.header(f"Abastecer {veiculo}")
    
    with st.form("form_diesel"):
        km = st.number_input("KM Atual", min_value=0)
        litros = st.number_input("Quantos Litros?", min_value=0.0)
        valor = st.number_input("Valor Total (R$)", min_value=0.0)
        
        if st.form_submit_button("📉 SALVAR ABASTECIMENTO"):
            df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
            save_row(DB_MOVIMENTO, df, {
                "Data": datetime.now(), "Categoria": "Combustível", 
                "Descricao": f"Abastec. {veiculo} ({litros}L - {km}km)", "Valor": -valor
            })
            st.success("Salvo!")
            navegar('menu_frota')
    if st.button("Cancelar"): navegar('menu_frota')

def tela_acao_manutencao():
    veiculo = st.session_state['veiculo_sel']
    st.header(f"Manutenção {veiculo}")
    
    with st.form("form_mecanica"):
        tipo = st.selectbox("Tipo", ["Mecânica", "Elétrica", "Pneus", "Troca de Óleo", "Funilaria"])
        detalhe = st.text_input("O que foi feito? (Peça/Serviço)")
        valor = st.number_input("Valor Total (R$)", min_value=0.0)
        
        if st.form_submit_button("📉 SALVAR MANUTENÇÃO"):
            df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
            save_row(DB_MOVIMENTO, df, {
                "Data": datetime.now(), "Categoria": "Manutenção", 
                "Descricao": f"Manut. {veiculo} - {tipo} ({detalhe})", "Valor": -valor
            })
            st.success("Salvo!")
            navegar('menu_frota')
    if st.button("Cancelar"): navegar('menu_frota')


# ================= TELA 4: FINANCEIRO (RESTAURADA E MELHORADA) =================
def tela_financeiro():
    st.title("💰 Financeiro da Obra")
    
    # 1. Configurar Obra
    st.write("### 🏗️ Contrato")
    df_obra = load_data(DB_OBRA, ["Valor_Total"])
    val_total = float(df_obra["Valor_Total"].iloc[0]) if not df_obra.empty else 0.0
    
    if val_total == 0:
        val_input = st.number_input("Qual o valor TOTAL do contrato da obra?", min_value=0.0)
        if st.button("Salvar Valor do Contrato"):
            pd.DataFrame([{"Valor_Total": val_input}]).to_csv(DB_OBRA, index=False)
            st.rerun()
    
    # 2. Registrar Recebimento
    with st.expander("➕ REGISTRAR ENTRADA DE DINHEIRO (RECEBIMENTO)", expanded=False):
        with st.form("receber"):
            val_rec = st.number_input("Valor Recebido (R$)", min_value=0.0)
            quem = st.text_input("Quem pagou? / Qual etapa?")
            if st.form_submit_button("💰 SALVAR ENTRADA"):
                df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
                save_row(DB_MOVIMENTO, df, {
                    "Data": datetime.now(), "Categoria": "Receita", 
                    "Descricao": f"Recebimento - {quem}", "Valor": val_rec
                })
                st.balloons()
                st.success("Dinheiro registrado no caixa!")
                st.rerun()

    # 3. Registrar Outras Despesas (Material)
    with st.expander("➖ REGISTRAR COMPRA DE MATERIAL / DIVERSOS", expanded=False):
        with st.form("gastar"):
            val_gasto = st.number_input("Valor Gasto (R$)", min_value=0.0)
            item = st.text_input("O que comprou?")
            cat = st.selectbox("Categoria", ["Material Construção", "Alimentação", "Equipamentos", "Outros"])
            if st.form_submit_button("📉 SALVAR DESPESA"):
                df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
                save_row(DB_MOVIMENTO, df, {
                    "Data": datetime.now(), "Categoria": cat, 
                    "Descricao": f"{item}", "Valor": -val_gasto
                })
                st.success("Gasto registrado!")
                st.rerun()

    st.divider()

    # 4. Extrato com Opção de Excluir (NOVO)
    st.write("### 📜 Extrato de Lançamentos")
    df = load_data(DB_MOVIMENTO, ["Data", "Categoria", "Descricao", "Valor"])
    
    if not df.empty:
        # Mostra saldo recebido vs contrato
        total_rec = df[df["Valor"] > 0]["Valor"].sum()
        falta = val_total - total_rec
        st.progress(min(total_rec / val_total if val_total > 0 else 0, 1.0))
        st.caption(f"Recebido: R$ {total_rec:,.2f} / Contrato: R$ {val_total:,.2f} (Falta R$ {falta:,.2f})")

        # Tabela de Extrato com índice para exclusão
        # Invertemos a ordem para ver o último primeiro
        df['Index'] = df.index
        df_show = df.sort_index(ascending=False)
        
        for i, row in df_show.iterrows():
            # Layout de cartão para cada item (melhor no celular)
            cor_txt = "green" if row['Valor'] > 0 else "red"
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{row['Descricao']}**")
                st.caption(f"{row['Data']} | {row['Categoria']}")
                st.markdown(f"<span style='color:{cor_txt}'>R$ {row['Valor']:,.2f}</span>", unsafe_allow_html=True)
            with c2:
                if st.button("🗑️", key=f"del_{i}"):
                    df = df.drop(i) # Remove pelo índice original
                    save_full_df(DB_MOVIMENTO, df)
                    st.success("Apagado!")
                    st.rerun()
            st.divider()
    else:
        st.info("Nenhuma movimentação financeira ainda.")

    if st.button("⬅️ VOLTAR AO MENU"): navegar('inicio')

# --- ROTEADOR CENTRAL ---
def main():
    if st.session_state['tela'] == 'inicio': tela_inicio()
    elif st.session_state['tela'] == 'menu_equipe': tela_equipe()
    elif st.session_state['tela'] == 'cadastro_func': tela_cadastro_func()
    elif st.session_state['tela'] == 'acao_ponto': tela_acao_ponto()
    elif st.session_state['tela'] == 'acao_vale': tela_acao_vale()
    elif st.session_state['tela'] == 'acao_pagamento': tela_acao_pagamento()
    elif st.session_state['tela'] == 'acao_justificativa': tela_acao_justificativa()
    elif st.session_state['tela'] == 'menu_frota': tela_frota()
    elif st.session_state['tela'] == 'acao_combustivel': tela_acao_combustivel()
    elif st.session_state['tela'] == 'acao_manutencao': tela_acao_manutencao()
    elif st.session_state['tela'] == 'menu_financeiro': tela_financeiro()

if __name__ == "__main__":
    main()
