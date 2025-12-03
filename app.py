import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gestor Aviário Blindado", layout="centered", page_icon="🚜")

st.markdown("""
    <style>
    /* Botões Grandes e Robustos */
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 12px;
        margin-bottom: 8px;
        background-color: #ffffff;
        border: 1px solid #ced4da;
        color: #2c3e50;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        border-color: #2980b9;
        color: #2980b9;
        background-color: #f8f9fa;
    }
    
    /* Esconder elementos técnicos */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE BANCO DE DADOS (AUTO-CORREÇÃO) ---

# Definição das Colunas Padrão (Isso evita o erro de Key Error)
COLS_MOVIMENTOS = ["Data", "Categoria", "Descricao", "Valor"]
COLS_FUNC = ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"]
COLS_VEICULOS = ["Veiculo", "Placa", "Km_Inicial"]
COLS_OBRA = ["Valor_Total"]

# Nomes dos Arquivos
DB_FUNC = 'db_funcionarios_v11.csv'
DB_VEICULOS = 'db_veiculos_v11.csv'
DB_MOVIMENTOS = 'db_financeiro_v11.csv'
DB_OBRA = 'db_obra_config.csv'

def load_data(arquivo, colunas_padrao):
    """
    Carrega o CSV e garante que todas as colunas existam.
    Se faltar alguma coluna (causa do erro anterior), ele cria ela na hora.
    """
    if not os.path.exists(arquivo):
        df = pd.DataFrame(columns=colunas_padrao)
        df.to_csv(arquivo, index=False)
        return df
    
    try:
        df = pd.read_csv(arquivo)
        # --- AUTO-CORREÇÃO (O Segredo) ---
        mudou_algo = False
        for col in colunas_padrao:
            if col not in df.columns:
                df[col] = 0 if "Valor" in col else "" # Preenche com vazio ou zero
                mudou_algo = True
        
        if mudou_algo:
            df.to_csv(arquivo, index=False) # Salva a correção
            
        return df
    except Exception as e:
        # Se o arquivo estiver muito corrompido, recria
        st.error(f"Arquivo {arquivo} recuperado.")
        df = pd.DataFrame(columns=colunas_padrao)
        df.to_csv(arquivo, index=False)
        return df

def save_full(arquivo, df):
    df.to_csv(arquivo, index=False)

def add_row(arquivo, row_data, colunas_padrao):
    df = load_data(arquivo, colunas_padrao)
    df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    df.to_csv(arquivo, index=False)

# Formatação Brasileira
def format_brl(valor):
    if valor is None: return "R$ 0,00"
    try:
        valor = float(valor)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def format_data_br(data_val):
    if data_val is None: return ""
    try:
        # Tenta converter se for string
        if isinstance(data_val, str):
            obj = datetime.strptime(data_val, '%Y-%m-%d')
            return obj.strftime('%d/%m/%Y')
        # Se for objeto date
        return data_val.strftime('%d/%m/%Y')
    except:
        return str(data_val)

# --- 3. NAVEGAÇÃO ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
if 'hist_voltar' not in st.session_state: st.session_state['hist_voltar'] = 'inicio'

def ir_para(tela, voltar_para='inicio'):
    st.session_state['hist_voltar'] = voltar_para
    st.session_state['tela'] = tela
    st.rerun()

def barra_navegacao(destino_voltar):
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ VOLTAR TELA"): ir_para(destino_voltar)
    with c2:
        if st.button("🏠 MENU INICIAL"): ir_para('inicio')

# ================= TELA 1: HOME =================
def tela_inicio():
    st.title("🚜 Painel Aviário")
    
    # Carrega usando as colunas padrão (Isso previne o erro)
    df_mov = load_data(DB_MOVIMENTOS, COLS_MOVIMENTOS)
    saldo = df_mov["Valor"].sum() if not df_mov.empty else 0.0
    
    df_obra = load_data(DB_OBRA, COLS_OBRA)
    total_contrato = float(df_obra["Valor_Total"].iloc[0]) if not df_obra.empty else 0.0
    
    recebido = df_mov[df_mov["Valor"] > 0]["Valor"].sum() if not df_mov.empty else 0.0
    falta = total_contrato - recebido
    
    c1, c2 = st.columns(2)
    c1.metric("Caixa Disponível", format_brl(saldo))
    c2.metric("Falta Receber", format_brl(falta))
    
    st.write("---")
    st.subheader("Acesso Rápido")
    
    if st.button("👷 GESTÃO DE EQUIPE"): ir_para('menu_equipe', 'inicio')
    if st.button("🚛 FROTA & VEÍCULOS"): ir_para('menu_frota', 'inicio')
    if st.button("💰 FINANCEIRO GERAL"): ir_para('menu_financeiro', 'inicio')
    if st.button("⚙️ CONFIGURAR CONTRATO"): ir_para('config_obra', 'inicio')

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("👷 Equipe")
    
    if st.button("➕ CADASTRAR NOVO FUNCIONÁRIO"): ir_para('cad_func', 'menu_equipe')
    
    df = load_data(DB_FUNC, COLS_FUNC)
    
    if df.empty:
        st.warning("Nenhum funcionário cadastrado.")
        barra_navegacao('inicio')
        return

    st.markdown("### Selecione o Colaborador:")
    func_selecionado = st.selectbox("Lista:", df["Nome"].unique())
    st.session_state['func_atual'] = func_selecionado
    
    dados = df[df["Nome"] == func_selecionado].iloc[0]
    
    # Cálculo Seguro
    df_fin = load_data(DB_MOVIMENTOS, COLS_MOVIMENTOS)
    # Filtra com segurança (converte para string para evitar erro)
    filtro = df_fin[df_fin["Descricao"].astype(str).str.contains(func_selecionado, case=False, na=False)]
    total_pago = abs(filtro[filtro["Valor"] < 0]["Valor"].sum())
    
    st.info(f"**Cargo:** {dados['Funcao']} | **Diária:** {format_brl(dados['Valor_Diaria'])}")
    st.caption(f"💰 Total já pago acumulado: {format_brl(total_pago)}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
        if st.button("💸 VALE"): ir_para('acao_vale', 'menu_equipe')
    with c2:
        if st.button("✅ PAGAMENTO"): ir_para('acao_pgto', 'menu_equipe')
        if st.button("📝 FALTAS"): ir_para('acao_obs', 'menu_equipe')

    with st.expander(f"⚙️ Opções para {func_selecionado}"):
        if st.button("🗑️ EXCLUIR CADASTRO"):
            df = df[df["Nome"] != func_selecionado]
            save_full(DB_FUNC, df)
            st.success("Excluído!")
            st.rerun()

    barra_navegacao('inicio')

def tela_cad_func():
    st.header("Novo Cadastro")
    with st.form("cad_func"):
        nome = st.text_input("Nome Completo")
        dt_ini = st.date_input("Data Início", datetime.now())
        func = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Cozinheira", "Motorista"])
        val = st.number_input("Valor Diária (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
        
        if st.form_submit_button("SALVAR"):
            if nome and val is not None:
                add_row(DB_FUNC, {
                    "Nome": nome, "Funcao": func, "Valor_Diaria": val, "Data_Inicio": dt_ini
                }, COLS_FUNC)
                st.success("Salvo!")
                ir_para('menu_equipe')
            else:
                st.error("Preencha Nome e Valor.")
    barra_navegacao('menu_equipe')

def tela_acoes_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    if tipo == "Ponto":
        dt = st.date_input("Data", datetime.now())
        status = st.radio("Presença", ["Dia Completo", "Meio Dia", "Falta"])
        if st.button("CONFIRMAR"):
            add_row(DB_MOVIMENTOS, {
                "Data": dt, "Categoria": "Ponto", "Descricao": f"Ponto {nome} ({status})", "Valor": 0
            }, COLS_MOVIMENTOS)
            st.success("Registrado!")
            ir_para('menu_equipe')

    elif tipo in ["Vale", "Pagamento"]:
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
        obs = st.text_input("Obs") if tipo == "Vale" else "Acerto Final"
        
        if st.button("CONFIRMAR SAÍDA"):
            if val is not None:
                desc = f"{tipo} {nome}" + (f" ({obs})" if obs else "")
                add_row(DB_MOVIMENTOS, {
                    "Data": datetime.now(), "Categoria": "Mão de Obra", "Descricao": desc, "Valor": -val
                }, COLS_MOVIMENTOS)
                st.success("Lançado!")
                ir_para('menu_equipe')
    
    elif tipo == "Faltas":
        motivo = st.text_area("Motivo")
        if st.button("SALVAR"):
            add_row(DB_MOVIMENTOS, {
                "Data": datetime.now(), "Categoria": "Ocorrência", "Descricao": f"Obs {nome}: {motivo}", "Valor": 0
            }, COLS_MOVIMENTOS)
            st.success("Salvo.")
            ir_para('menu_equipe')
            
    barra_navegacao('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("🚛 Frota")
    if st.button("➕ CADASTRAR VEÍCULO"): ir_para('cad_veiculo', 'menu_frota')
    
    df = load_data(DB_VEICULOS, COLS_VEICULOS)
    if df.empty:
        st.warning("Nenhum veículo.")
        barra_navegacao('inicio')
        return

    veic = st.selectbox("Selecione:", df["Veiculo"].unique())
    st.session_state['veiculo_atual'] = veic
    
    # Dados e Acumulado
    dados = df[df["Veiculo"] == veic].iloc[0]
    df_fin = load_data(DB_MOVIMENTOS, COLS_MOVIMENTOS)
    filtro = df_fin[df_fin["Descricao"].astype(str).str.contains(veic, case=False, na=False)]
    total = abs(filtro[filtro["Valor"] < 0]["Valor"].sum())
    
    st.info(f"**Veículo:** {dados['Veiculo']} | **Placa:** {dados['Placa']}\n\n💸 **Gasto Total:** {format_brl(total)}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⛽ ABASTECER"): ir_para('acao_abastecer', 'menu_frota')
    with c2:
        if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manutencao', 'menu_frota')
        
    with st.expander(f"🗑️ Excluir {veic}"):
        if st.button("CONFIRMAR EXCLUSÃO"):
            df = df[df["Veiculo"] != veic]
            save_full(DB_VEICULOS, df)
            st.rerun()

    barra_navegacao('inicio')

def tela_cad_veiculo():
    st.header("Novo Veículo")
    with st.form("cad_veic"):
        mod = st.text_input("Modelo")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0, value=None, placeholder="KM...")
        if st.form_submit_button("SALVAR"):
            nome_f = f"{mod} {placa}"
            add_row(DB_VEICULOS, {"Veiculo": nome_f, "Placa": placa, "Km_Inicial": km if km else 0}, COLS_VEICULOS)
            st.success("Salvo!")
            ir_para('menu_frota')
    barra_navegacao('menu_frota')

def tela_acao_frota(tipo):
    veic = st.session_state['veiculo_atual']
    st.header(f"{tipo}: {veic}")
    
    if tipo == "Abastecer":
        km = st.number_input("KM Painel", min_value=0, value=None, placeholder="KM...")
        lit = st.number_input("Litros", min_value=0.0, value=None, placeholder="Litros...")
        val = st.number_input("Valor R$", min_value=0.0, value=None, placeholder="Valor...")
        if st.button("SALVAR"):
            if val:
                desc = f"Abastec. {veic} ({lit}L | KM {km})"
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Combustível", "Descricao": desc, "Valor": -val}, COLS_MOVIMENTOS)
                st.success("Salvo!")
                ir_para('menu_frota')
                
    elif tipo == "Manutenção":
        item = st.text_input("O que fez?")
        val = st.number_input("Valor R$", min_value=0.0, value=None, placeholder="Valor...")
        if st.button("SALVAR"):
            if val:
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Manutenção", "Descricao": f"Manut. {veic} - {item}", "Valor": -val}, COLS_MOVIMENTOS)
                st.success("Salvo!")
                ir_para('menu_frota')
                
    barra_navegacao('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_financeiro():
    st.title("💰 Financeiro")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ ENTRADA"): ir_para('fin_entrada', 'menu_financeiro')
    with c2:
        if st.button("➖ SAÍDA"): ir_para('fin_saida', 'menu_financeiro')
        
    st.subheader("📜 Extrato")
    df = load_data(DB_MOVIMENTOS, COLS_MOVIMENTOS)
    
    if not df.empty:
        # Edição
        if 'edit_idx' not in st.session_state: st.session_state['edit_idx'] = -1
        
        df['idx_real'] = df.index
        df_show = df.sort_index(ascending=False).head(30)
        
        for i, row in df_show.iterrows():
            idx = row['idx_real']
            cor = "green" if row['Valor'] > 0 else "#e74c3c"
            
            c_txt, c_btn = st.columns([3, 1])
            with c_txt:
                st.markdown(f"**{row['Descricao']}**")
                st.caption(f"{format_data_br(row['Data'])} | {row['Categoria']}")
                st.markdown(f"<span style='color:{cor};font-weight:bold'>{format_brl(row['Valor'])}</span>", unsafe_allow_html=True)
            with c_btn:
                if st.button("✏️", key=f"ed_{idx}"):
                    st.session_state['edit_idx'] = idx
                    st.rerun()
                if st.button("🗑️", key=f"del_{idx}"):
                    df = df.drop(idx)
                    save_full(DB_MOVIMENTOS, df)
                    st.rerun()
            
            # Form Edição
            if st.session_state['edit_idx'] == idx:
                with st.form(f"f_ed_{idx}"):
                    n_desc = st.text_input("Desc", value=row['Descricao'])
                    n_val = st.number_input("Valor", value=float(row['Valor']))
                    if st.form_submit_button("SALVAR"):
                        df.at[idx, "Descricao"] = n_desc
                        df.at[idx, "Valor"] = n_val
                        save_full(DB_MOVIMENTOS, df)
                        st.session_state['edit_idx'] = -1
                        st.rerun()
            st.divider()

    barra_navegacao('inicio')

def tela_fin_lancamento(tipo):
    st.header(f"Lançar {tipo}")
    desc = st.text_input("Descrição")
    val = st.number_input("Valor R$", min_value=0.0, value=None, placeholder="Valor...")
    
    if st.button("CONFIRMAR"):
        if val:
            cat = "Receita" if tipo == "Entrada" else "Material/Outros"
            v_final = val if tipo == "Entrada" else -val
            add_row(DB_MOVIMENTOS, {
                "Data": datetime.now(), "Categoria": cat, "Descricao": desc, "Valor": v_final
            }, COLS_MOVIMENTOS)
            st.success("Salvo!")
            ir_para('menu_financeiro')
            
    barra_navegacao('menu_financeiro')

def tela_config_obra():
    st.header("Contrato")
    df = load_data(DB_OBRA, COLS_OBRA)
    atual = float(df["Valor_Total"].iloc[0]) if not df.empty else 0.0
    st.metric("Valor Atual", format_brl(atual))
    
    novo = st.number_input("Novo Valor Total", value=None, placeholder="Valor...")
    if st.button("ATUALIZAR"):
        if novo:
            pd.DataFrame([{"Valor_Total": novo}]).to_csv(DB_OBRA, index=False)
            st.success("Ok!")
            st.rerun()
    barra_navegacao('inicio')

# ================= ROTEADOR =================
def main():
    tela = st.session_state['tela']
    
    if tela == 'inicio': tela_inicio()
    
    elif tela == 'menu_equipe': tela_equipe()
    elif tela == 'cad_func': tela_cad_func()
    elif tela == 'acao_ponto': tela_acoes_equipe("Ponto")
    elif tela == 'acao_vale': tela_acoes_equipe("Vale")
    elif tela == 'acao_pgto': tela_acoes_equipe("Pagamento")
    elif tela == 'acao_obs': tela_acoes_equipe("Faltas")
    
    elif tela == 'menu_frota': tela_frota()
    elif tela == 'cad_veiculo': tela_cad_veiculo()
    elif tela == 'acao_abastecer': tela_acao_frota("Abastecer")
    elif tela == 'acao_manutencao': tela_acao_frota("Manutenção")
    
    elif tela == 'menu_financeiro': tela_financeiro()
    elif tela == 'fin_entrada': tela_fin_lancamento("Entrada")
    elif tela == 'fin_saida': tela_fin_lancamento("Saída")
    elif tela == 'config_obra': tela_config_obra()

if __name__ == "__main__":
    main()
