import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Gestor Aviário 3.0", layout="wide", page_icon="🚜")

# --- CSS para Estilo de Aplicativo ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 55px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 10px;
    }
    .big-font { font-size: 20px !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Gerenciamento de Arquivos (3 Bancos de Dados Separados) ---
ARQUIVO_FINANCEIRO = 'financeiro.csv'
ARQUIVO_FUNCIONARIOS = 'funcionarios.csv'
ARQUIVO_PONTO = 'ponto.csv'

# Função genérica para carregar/salvar
def load_data(arquivo, colunas):
    if not os.path.exists(arquivo):
        df = pd.DataFrame(columns=colunas)
        df.to_csv(arquivo, index=False)
        return df
    return pd.read_csv(arquivo)

def save_data(arquivo, df_novo):
    # Salva sobrescrevendo o arquivo com o dataframe atualizado
    df_novo.to_csv(arquivo, index=False)

# --- INÍCIO DO APP ---
st.title("🚜 Gestão Total: Aviário & Obras")

# Navegação Principal
menu = st.sidebar.radio("Navegar", ["📌 Ponto & Equipe", "💰 Financeiro da Obra", "⚙️ Cadastrar Funcionários"])

# ================= MÓDULO 1: CADASTRO DE FUNCIONÁRIOS =================
if menu == "⚙️ Cadastrar Funcionários":
    st.header("Cadastro de Equipe")
    st.info("Cadastre aqui quem trabalha na obra e quanto ganha por dia.")
    
    # Carregar Funcionários
    df_func = load_data(ARQUIVO_FUNCIONARIOS, ["Nome", "Função", "Valor_Diaria", "Status"])
    
    with st.form("form_func"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Completo")
        funcao = c2.selectbox("Função", ["Pedreiro", "Servente", "Eletricista", "Motorista", "Cozinheira"])
        valor = st.number_input("Valor da Diária (R$)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("💾 Salvar Funcionário"):
            if nome:
                novo_func = pd.DataFrame([{"Nome": nome, "Função": funcao, "Valor_Diaria": valor, "Status": "Ativo"}])
                df_func = pd.concat([df_func, novo_func], ignore_index=True)
                save_data(ARQUIVO_FUNCIONARIOS, df_func)
                st.success(f"{nome} cadastrado com sucesso!")
                st.rerun()
            else:
                st.warning("O nome é obrigatório.")
    
    st.divider()
    st.write("### Equipe Atual")
    st.dataframe(df_func, use_container_width=True)


# ================= MÓDULO 2: PONTO E PAGAMENTOS (O CORAÇÃO DO RH) =================
elif menu == "📌 Ponto & Equipe":
    st.header("Controle de Ponto e Pagamentos")
    
    # Carrega dados necessários
    df_func = load_data(ARQUIVO_FUNCIONARIOS, ["Nome", "Função", "Valor_Diaria", "Status"])
    df_ponto = load_data(ARQUIVO_PONTO, ["Data", "Nome", "Presenca", "Obs"])
    df_fin = load_data(ARQUIVO_FINANCEIRO, ["Data", "Obra", "Categoria", "Detalhe", "Valor", "Tipo"])
    
    if df_func.empty:
        st.warning("⚠️ Vá na aba 'Cadastrar Funcionários' primeiro!")
    else:
        lista_nomes = df_func["Nome"].unique()
        funcionario_selecionado = st.selectbox("Selecione o Funcionário:", lista_nomes)
        
        # Pega o valor da diária desse funcionário
        dados_func = df_func[df_func["Nome"] == funcionario_selecionado].iloc[0]
        valor_dia = dados_func["Valor_Diaria"]
        
        tab_ponto, tab_pagar = st.tabs(["⏰ Marcar Ponto", "💸 Calcular Pagamento"])
        
        # --- SUB-ABA: MARCAR PONTO ---
        with tab_ponto:
            st.write(f"Marcar presença para **{funcionario_selecionado}**")
            
            c1, c2 = st.columns(2)
            data_ponto = c1.date_input("Data do Ponto", datetime.now())
            status_ponto = c2.radio("Situação", ["Presente (1 Diária)", "Meio Dia (0.5 Diária)", "Falta"], horizontal=True)
            
            if st.button("✅ Confirmar Presença"):
                qtd = 1.0 if "Presente" in status_ponto else (0.5 if "Meio" in status_ponto else 0.0)
                novo_ponto = pd.DataFrame([{
                    "Data": data_ponto, 
                    "Nome": funcionario_selecionado, 
                    "Presenca": qtd, 
                    "Obs": status_ponto
                }])
                df_ponto = pd.concat([df_ponto, novo_ponto], ignore_index=True)
                save_data(ARQUIVO_PONTO, df_ponto)
                st.success("Ponto registrado!")
            
            # Histórico do funcionário
            st.write("Histórico de Presença:")
            filtro_ponto = df_ponto[df_ponto["Nome"] == funcionario_selecionado]
            st.dataframe(filtro_ponto.sort_values("Data", ascending=False).head(5), use_container_width=True)

        # --- SUB-ABA: CALCULAR ACERTO ---
        with tab_pagar:
            # 1. Total trabalhado
            dias_trabalhados = df_ponto[df_ponto["Nome"] == funcionario_selecionado]["Presenca"].sum()
            total_a_receber = dias_trabalhados * valor_dia
            
            # 2. Total já pago (Vales)
            # Filtra no financeiro tudo que for "Mão de Obra" e tiver o nome do funcionário na descrição ou detalhe
            filtro_vales = df_fin[
                (df_fin["Categoria"] == "Mão de Obra") & 
                (df_fin["Detalhe"].str.contains(funcionario_selecionado, na=False))
            ]
            total_vales = abs(filtro_vales[filtro_vales["Valor"] < 0]["Valor"].sum())
            
            saldo_final = total_a_receber - total_vales
            
            # Mostrador (Dashboard Pessoal)
            colA, colB, colC = st.columns(3)
            colA.metric("Dias Trabalhados", f"{dias_trabalhados}", f"Diária: R$ {valor_dia}")
            colB.metric("Bruto a Receber", f"R$ {total_a_receber:,.2f}")
            colC.metric("Já Pegou (Vales)", f"R$ {total_vales:,.2f}", delta_color="inverse")
            
            st.divider()
            
            if saldo_final > 0:
                st.success(f"💰 **Saldo a PAGAR:** R$ {saldo_final:,.2f}")
                if st.button("Registrar Pagamento Final (Zerar Saldo)"):
                    # Lança no financeiro
                    pgto = pd.DataFrame([{
                        "Data": datetime.now(),
                        "Obra": "Geral",
                        "Categoria": "Mão de Obra",
                        "Detalhe": f"Pgto Final - {funcionario_selecionado}",
                        "Valor": -saldo_final,
                        "Tipo": "Despesa"
                    }])
                    df_fin = pd.concat([df_fin, pgto], ignore_index=True)
                    save_data(ARQUIVO_FINANCEIRO, df_fin)
                    st.balloons()
                    st.rerun()
            else:
                st.info("Funcionário está com saldo devedor ou zerado.")


# ================= MÓDULO 3: FINANCEIRO (LANÇAMENTOS GERAIS) =================
elif menu == "💰 Financeiro da Obra":
    st.header("Lançamentos Gerais (Materiais, Combustível)")
    
    df_fin = load_data(ARQUIVO_FINANCEIRO, ["Data", "Obra", "Categoria", "Detalhe", "Valor", "Tipo"])
    
    with st.form("form_fin"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data", datetime.now())
        tipo = col2.radio("Tipo", ["Despesa (Saída)", "Receita (Entrada)"], horizontal=True)
        
        categoria = st.selectbox("Categoria", ["Material Construção", "Combustível", "Manutenção", "Alimentação", "Outros"])
        detalhe = st.text_input("Descrição", placeholder="Ex: 1000 tijolos")
        valor = st.number_input("Valor R$", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Salvar Lançamento"):
            val_final = -valor if "Despesa" in tipo else valor
            novo_lanc = pd.DataFrame([{
                "Data": data, "Obra": "Geral", "Categoria": categoria, 
                "Detalhe": detalhe, "Valor": val_final, "Tipo": "Despesa" if val_final < 0 else "Receita"
            }])
            df_fin = pd.concat([df_fin, novo_lanc], ignore_index=True)
            save_data(ARQUIVO_FINANCEIRO, df_fin)
            st.success("Salvo!")
            
    st.write("### Extrato Geral")
    st.dataframe(df_fin.sort_index(ascending=False), use_container_width=True)
    
    saldo = df_fin["Valor"].sum()
    st.metric("Caixa Atual", f"R$ {saldo:,.2f}")
