import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Configuração Otimizada para Celular ---
st.set_page_config(page_title="Aviário Control", layout="centered", page_icon="🚜")

# --- CSS para "Look & Feel" de App Nativo ---
st.markdown("""
    <style>
    /* Botões grandes para dedos de quem trabalha na obra */
    .stButton>button {
        height: 3.5em;
        width: 100%;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
    }
    /* Esconder menu padrão do Streamlit para parecer app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Melhorar visualização de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Gerenciamento de Dados (CSV Local Simples) ---
FILE_PATH = 'dados_aviario.csv'

def get_data():
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Data", "Obra", "Tipo", "Categoria", "Descrição", "Valor", "Autor"])
        df.to_csv(FILE_PATH, index=False)
        return df
    return pd.read_csv(FILE_PATH)

def save_data(new_entry):
    df = get_data()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)

# --- Lógica da Interface ---
st.title("🚜 Aviário Control")

# Menu navegação inferior (simulado com abas)
tab1, tab2, tab3 = st.tabs(["➕ Lançar", "📊 Caixinha", "🛠️ Ajustes"])

# === ABA 1: LANÇAMENTO RÁPIDO ===
with tab1:
    st.write("### 📝 Novo Registro")
    with st.form("entry_form", clear_on_submit=True):
        
        # Linha 1: Data e Obra
        c1, c2 = st.columns(2)
        data = c1.date_input("Data", datetime.now())
        obra = c2.selectbox("Obra", ["Aviário 01", "Aviário 02", "Sede", "Geral"])
        
        # Linha 2: Tipo
        tipo = st.radio("Movimento", ["🔴 Pagamento (Saída)", "🟢 Recebimento (Entrada)"], horizontal=True)
        
        # Linha 3: Categoria (Inteligente)
        cat_options = [
            "Mão de Obra (Diária/Vale)", 
            "Material Construção", 
            "Combustível/Frota", 
            "Alimentação", 
            "Manutenção Equipamentos", 
            "Outros"
        ]
        categoria = st.selectbox("Categoria", cat_options)
        
        descricao = st.text_input("Descrição (Ex: 50 sacos cimento / Vale João)")
        
        # Valor com destaque
        valor = st.number_input("Valor R$", min_value=0.0, step=10.0, format="%.2f")
        
        submitted = st.form_submit_button("✅ SALVAR REGISTRO")
        
        if submitted:
            # Ajuste de sinal (Despesa vira negativo)
            val_final = -valor if "Saída" in tipo else valor
            
            entry = {
                "Data": data,
                "Obra": obra,
                "Tipo": "Despesa" if "Saída" in tipo else "Receita",
                "Categoria": categoria,
                "Descrição": descricao,
                "Valor": val_final,
                "Autor": "Admin"
            }
            save_data(entry)
            st.success("Lançamento salvo com sucesso!")

# === ABA 2: VISÃO DO DONO (CAIXA) ===
with tab2:
    st.write("### 💰 Resumo Financeiro")
    df = get_data()
    
    if not df.empty:
        # Métricas Topo
        total = df["Valor"].sum()
        entradas = df[df["Valor"] > 0]["Valor"].sum()
        saidas = df[df["Valor"] < 0]["Valor"].sum()
        
        col_a, col_b = st.columns(2)
        col_a.metric("Entradas", f"R$ {entradas:,.2f}")
        col_b.metric("Saídas", f"R$ {abs(saidas):,.2f}", delta_color="inverse")
        
        st.divider()
        st.metric("LUCRO / CAIXA ATUAL", f"R$ {total:,.2f}", delta=total)
        
        st.divider()
        st.write("📋 **Últimos 5 Lançamentos:**")
        st.dataframe(df.tail(5).sort_index(ascending=False)[["Data", "Descrição", "Valor"]], use_container_width=True)
    else:
        st.info("Nenhum dado lançado ainda.")

# === ABA 3: AJUSTES / DADOS ===
with tab3:
    st.write("### 📂 Banco de Dados")
    st.info("Use esta aba para ver tudo ou corrigir erros.")
    df = get_data()
    st.dataframe(df, use_container_width=True)
    
    # Botão para limpar dados (Cuidado)
    if st.checkbox("Habilitar Limpeza de Dados"):
        if st.button("🗑️ APAGAR TUDO (Resetar App)"):
            if os.path.exists(FILE_PATH):
                os.remove(FILE_PATH)
                st.rerun()
