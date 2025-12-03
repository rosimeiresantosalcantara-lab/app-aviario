import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(page_title="Gestor de Aviário PRO", layout="wide")

# --- CSS para botões grandes no celular ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        min-height: 55px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Gerenciamento de Arquivos (Banco de Dados) ---
DB_FINANCEIRO = 'financeiro_v5.csv'
DB_FUNCIONARIOS = 'funcionarios_v5.csv'
DB_PONTO = 'ponto_v5.csv'

def load_db(arquivo, colunas):
    if not os.path.exists(arquivo):
        df = pd.DataFrame(columns=colunas)
        df.to_csv(arquivo, index=False)
        return df
    return pd.read_csv(arquivo)

def save_db(arquivo, df):
    df.to_csv(arquivo, index=False)

# --- INTERFACE ---
st.title("🚜 Gestão Total: Aviário")

# Menu Principal
abas = st.tabs(["👷 PONTO & PAGAMENTO", "📝 DESPESAS GERAIS", "⚙️ CADASTROS", "📊 RELATÓRIOS"])

# ================= ABA 3: CADASTROS (Começar por aqui) =================
with abas[2]:
    st.header("Cadastro de Equipe")
    st.info("Primeiro passo: Cadastre seus funcionários e o valor da diária aqui.")
    
    df_func = load_db(DB_FUNCIONARIOS, ["Nome", "Funcao", "Valor_Diaria"])
    
    with st.form("novo_func"):
        c1, c2, c3 = st.columns([2, 2, 1])
        nome = c1.text_input("Nome do Funcionário")
        funcao = c2.selectbox("Função", ["Pedreiro", "Servente", "Eletricista", "Motorista", "Cozinheira", "Outro"])
        valor = c3.number_input("Valor Diária (R$)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("💾 SALVAR FUNCIONÁRIO"):
            if nome:
                # Verifica se já existe
                if nome in df_func["Nome"].values:
                    st.error("Esse nome já existe!")
                else:
                    novo = pd.DataFrame([{"Nome": nome, "Funcao": funcao, "Valor_Diaria": valor}])
                    df_func = pd.concat([df_func, novo], ignore_index=True)
                    save_db(DB_FUNCIONARIOS, df_func)
                    st.success(f"{nome} cadastrado!")
                    st.rerun()
            else:
                st.warning("Preencha o nome.")
    
    st.write("### Equipe Ativa:")
    st.dataframe(df_func, use_container_width=True)

# ================= ABA 1: PONTO E PAGAMENTO (O Coração) =================
with abas[0]:
    st.header("Controle de Mão de Obra")
    
    df_func = load_db(DB_FUNCIONARIOS, ["Nome", "Funcao", "Valor_Diaria"])
    
    if df_func.empty:
        st.warning("⚠️ Cadastre funcionários na aba 'CADASTROS' primeiro!")
    else:
        # Seletor de Funcionário
        lista_nomes = df_func["Nome"].unique()
        funcionario = st.selectbox("Selecione o Funcionário:", lista_nomes)
        
        # Recupera dados do funcionário selecionado
        dados_func = df_func[df_func["Nome"] == funcionario].iloc[0]
        valor_dia = float(dados_func["Valor_Diaria"])
        
        st.write(f"**{funcionario}** | Função: {dados_func['Funcao']} | Diária: **R$ {valor_dia:.2f}**")
        
        tab_p, tab_pag = st.tabs(["⏰ Marcar Ponto", "💰 Calcular Pagamento"])
        
        # --- SUB-ABA: MARCAR PONTO ---
        with tab_p:
            df_ponto = load_db(DB_PONTO, ["Data", "Nome", "Tipo_Presenca", "Valor_Calculado"])
            
            c1, c2 = st.columns(2)
            data_ponto = c1.date_input("Data", datetime.now())
            tipo_presenca = c2.radio("Presença", ["Dia Completo (1.0)", "Meio Dia (0.5)", "Falta (0.0)"], horizontal=True)
            
            if st.button("✅ REGISTRAR PONTO"):
                fator = 1.0
                if "Meio" in tipo_presenca: fator = 0.5
                if "Falta" in tipo_presenca: fator = 0.0
                
                valor_do_dia = valor_dia * fator
                
                novo_ponto = pd.DataFrame([{
                    "Data": data_ponto,
                    "Nome": funcionario,
                    "Tipo_Presenca": tipo_presenca,
                    "Valor_Calculado": valor_do_dia
                }])
                df_ponto = pd.concat([df_ponto, novo_ponto], ignore_index=True)
                save_db(DB_PONTO, df_ponto)
                st.success(f"Ponto registrado! Valor a somar: R$ {valor_do_dia:.2f}")
        
        # --- SUB-ABA: CALCULAR ACERTO ---
        with tab_pag:
            # 1. Carrega dados
            df_ponto = load_db(DB_PONTO, ["Data", "Nome", "Tipo_Presenca", "Valor_Calculado"])
            df_fin = load_db(DB_FINANCEIRO, ["Data", "Tipo", "Categoria", "Descricao", "Valor", "Responsavel"])
            
            # 2. Calcula Total Trabalhado (Soma dos dias marcados no ponto)
            pontos_func = df_ponto[df_ponto["Nome"] == funcionario]
            total_trabalhado = pontos_func["Valor_Calculado"].sum()
            
            # 3. Calcula Vales Já Pagos (Busca no financeiro)
            vales_func = df_fin[
                (df_fin["Categoria"] == "Mão de Obra") & 
                (df_fin["Responsavel"] == funcionario)
            ]
            total_vales = abs(vales_func[vales_func["Valor"] < 0]["Valor"].sum())
            
            # 4. Saldo
            saldo_pagar = total_trabalhado - total_vales
            
            # Mostrador
            colA, colB, colC = st.columns(3)
            colA.metric("Total Trabalhado (R$)", f"{total_trabalhado:,.2f}")
            colB.metric("Já Recebeu / Vales", f"{total_vales:,.2f}")
            colC.metric("SALDO A PAGAR", f"{saldo_pagar:,.2f}", delta=saldo_pagar)
            
            st.write("---")
            st.write("#### 💸 Ações de Pagamento")
            
            c_vale, c_pgto = st.columns(2)
            
            with c_vale:
                st.write("**Dar um Vale / Adiantamento**")
                valor_vale = st.number_input("Valor do Vale (R$)", min_value=0.0, step=50.0)
                obs_vale = st.text_input("Obs Vale", placeholder="Ex: Gasolina")
                if st.button("REGISTRAR VALE"):
                    novo_fin = pd.DataFrame([{
                        "Data": datetime.now(),
                        "Tipo": "Despesa",
                        "Categoria": "Mão de Obra",
                        "Descricao": f"Vale - {obs_vale}",
                        "Valor": -valor_vale,
                        "Responsavel": funcionario
                    }])
                    df_fin = pd.concat([df_fin, novo_fin], ignore_index=True)
                    save_db(DB_FINANCEIRO, df_fin)
                    st.success("Vale registrado!")
                    st.rerun()
            
            with c_pgto:
                st.write("**Pagamento Final (Acerto)**")
                if saldo_pagar > 0:
                    if st.button(f"PAGAR SALDO RESTANTE (R$ {saldo_pagar:.2f})"):
                        novo_fin = pd.DataFrame([{
                            "Data": datetime.now(),
                            "Tipo": "Despesa",
                            "Categoria": "Mão de Obra",
                            "Descricao": "Pagamento Final / Fechamento",
                            "Valor": -saldo_pagar,
                            "Responsavel": funcionario
                        }])
                        df_fin = pd.concat([df_fin, novo_fin], ignore_index=True)
                        save_db(DB_FINANCEIRO, df_fin)
                        st.balloons()
                        st.success("Pagamento realizado e saldo zerado!")
                        st.rerun()
                else:
                    st.info("Nada a pagar no momento.")

# ================= ABA 2: DESPESAS GERAIS =================
with abas[1]:
    st.header("Lançamento de Despesas e Receitas")
    df_fin = load_db(DB_FINANCEIRO, ["Data", "Tipo", "Categoria", "Descricao", "Valor", "Responsavel"])
    
    with st.form("lanc_geral", clear_on_submit=True):
        c1, c2 = st.columns(2)
        data = c1.date_input("Data", datetime.now())
        tipo = c2.radio("Tipo", ["Despesa (Saída)", "Receita (Entrada)"], horizontal=True)
        
        cat = st.selectbox("Categoria", ["Material Construção", "Combustível", "Manutenção", "Alimentação", "Outros"])
        desc = st.text_input("Descrição", placeholder="Ex: Cimento, Diesel Hilux...")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("💾 SALVAR LANÇAMENTO"):
            val_final = -valor if "Despesa" in tipo else valor
            novo = pd.DataFrame([{
                "Data": data, "Tipo": tipo, "Categoria": cat, 
                "Descricao": desc, "Valor": val_final, "Responsavel": "Geral"
            }])
            df_fin = pd.concat([df_fin, novo], ignore_index=True)
            save_db(DB_FINANCEIRO, df_fin)
            st.success("Registrado!")

# ================= ABA 4: RELATÓRIOS =================
with abas[3]:
    st.header("Visão Geral do Caixa")
    df_fin = load_db(DB_FINANCEIRO, ["Data", "Tipo", "Categoria", "Descricao", "Valor", "Responsavel"])
    
    if not df_fin.empty:
        saldo = df_fin["Valor"].sum()
        st.metric("SALDO EM CAIXA", f"R$ {saldo:,.2f}")
        
        st.write("Histórico de Movimentações:")
        st.dataframe(df_fin.sort_index(ascending=False), use_container_width=True)
        
        # Botão Reset Seguro
        with st.expander("Zona de Perigo"):
            if st.button("🗑️ LIMPAR TODO O SISTEMA"):
                if os.path.exists(DB_FINANCEIRO): os.remove(DB_FINANCEIRO)
                if os.path.exists(DB_FUNCIONARIOS): os.remove(DB_FUNCIONARIOS)
                if os.path.exists(DB_PONTO): os.remove(DB_PONTO)
                st.rerun()
    else:
        st.info("Sem dados financeiros.")
