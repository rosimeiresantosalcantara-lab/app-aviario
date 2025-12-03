import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO INICIAL (Obrigatório ser a primeira linha) ---
st.set_page_config(page_title="Aviário Control", layout="wide")

# --- 2. FUNÇÕES DE BANCO DE DADOS ---
FILE_DB = 'dados_v3.csv'

def carregar_dados():
    if not os.path.exists(FILE_DB):
        # Cria o arquivo vazio se não existir
        df = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descricao", "Valor", "Responsavel"])
        df.to_csv(FILE_DB, index=False)
        return df
    return pd.read_csv(FILE_DB)

def salvar_dados(novo_item):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame([novo_item])], ignore_index=True)
    df.to_csv(FILE_DB, index=False)

# --- 3. INTERFACE DO APLICATIVO ---
st.title("🚜 Gestão de Aviário")

# Abas Superiores
aba1, aba2, aba3 = st.tabs(["📝 LANÇAR GASTOS", "👷 PAGAR EQUIPE", "📊 VER CAIXA"])

# === ABA 1: GASTOS GERAIS ===
with aba1:
    st.header("Novo Lançamento")
    with st.form("form_gastos", clear_on_submit=True):
        data = st.date_input("Data", datetime.now())
        categoria = st.selectbox("O que é?", ["Ração/Insumos", "Material Construção", "Combustível", "Manutenção", "Outros"])
        desc = st.text_input("Descrição", placeholder="Ex: 50 sacos de cimento")
        valor = st.number_input("Valor R$", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("SALVAR DESPESA"):
            salvar_dados({
                "Data": data,
                "Tipo": "Despesa",
                "Categoria": categoria,
                "Descricao": desc,
                "Valor": -valor, # Despesa é negativo
                "Responsavel": "Geral"
            })
            st.success("Salvo com sucesso!")

# === ABA 2: EQUIPE (SIMPLIFICADA) ===
with aba2:
    st.header("Controle de Funcionários")
    
    # Lista simples de funcionários para não precisar de cadastro complexo agora
    equipe = ["João (Pedreiro)", "Maria (Cozinha)", "José (Servente)", "Motorista", "Outro"]
    quem = st.selectbox("Quem vai receber?", equipe)
    
    col_a, col_b = st.columns(2)
    tipo_pg = col_a.radio("É Vale ou Pagamento?", ["Vale (Adiantamento)", "Pagamento Final"])
    valor_pg = col_b.number_input("Valor a Pagar R$", min_value=0.0, format="%.2f")
    
    if st.button("CONFIRMAR PAGAMENTO"):
        if valor_pg > 0:
            salvar_dados({
                "Data": datetime.now(),
                "Tipo": "Mão de Obra",
                "Categoria": "Equipe",
                "Descricao": f"{tipo_pg} - {quem}",
                "Valor": -valor_pg,
                "Responsavel": quem
            })
            st.success(f"Pagamento para {quem} registrado!")
        else:
            st.warning("Digite um valor.")

    st.divider()
    st.write("🔻 **Últimos Pagamentos Feitos:**")
    df = carregar_dados()
    if not df.empty:
        # Filtra só o que é de equipe
        df_equipe = df[df["Tipo"] == "Mão de Obra"]
        st.dataframe(df_equipe[["Data", "Descricao", "Valor"]].sort_index(ascending=False), use_container_width=True)

# === ABA 3: RESUMO ===
with aba3:
    st.header("Resumo do Caixa")
    df = carregar_dados()
    
    if not df.empty:
        total = df["Valor"].sum()
        st.metric("SALDO ATUAL", f"R$ {total:,.2f}")
        
        st.write("Histórico Completo:")
        st.dataframe(df, use_container_width=True)
        
        # Botão de emergência para limpar tudo
        if st.checkbox("Mostrar botão de resetar"):
            if st.button("🗑️ APAGAR TUDO E RECOMEÇAR"):
                if os.path.exists(FILE_DB):
                    os.remove(FILE_DB)
                    st.experimental_rerun()
    else:
        st.info("Nenhum dado no sistema.")
