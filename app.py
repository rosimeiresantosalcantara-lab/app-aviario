import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL (BRANDING GENÉRICO) ---
st.set_page_config(page_title="GestorPRO", layout="centered", page_icon="📈")

st.markdown("""
    <style>
    /* Estilo Corporativo Limpo */
    .stButton>button {
        width: 100%;
        height: 55px;
        font-size: 18px;
        font-weight: 500;
        border-radius: 8px;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        color: #31333F;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        background-color: #ffffff;
    }
    
    /* Remover formatação de Markdown crua se houver */
    p { font-size: 16px; }
    
    /* Esconder menu de desenvolvedor */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. LISTAS PADRONIZADAS (EVITA DIGITAÇÃO) ---
LISTA_FUNCOES = ["Pedreiro", "Servente", "Mestre de Obras", "Pintor", "Eletricista", "Motorista", "Cozinheira", "Administrativo"]
LISTA_MATERIAIS = ["Cimento", "Areia/Pedra", "Tijolos/Blocos", "Ferro/Aço", "Madeira", "Telhas", "Tintas", "Tubos/Conexões", "Fios/Elétrica", "EPIs", "Ferramentas", "Outros"]
LISTA_MANUTENCAO = ["Troca de Óleo", "Pneus", "Filtros", "Mecânica Geral", "Elétrica Auto", "Funilaria", "Peças de Reposição", "Lavagem/Limpeza"]
LISTA_VALES = ["Adiantamento Salarial", "Combustível Próprio", "Almoço/Refeição", "Farmácia", "Emergência Pessoal"]
LISTA_FALTAS = ["Doença/Atestado", "Problema Pessoal", "Chuva/Tempo", "Falta sem Aviso", "Folga Combinada"]

# --- 3. UTILITÁRIOS ---

def format_brl(valor):
    if valor is None: return "R$ 0,00"
    try:
        val_float = float(valor)
        return f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def format_data_br_coluna(series):
    """Converte uma coluna inteira do Pandas para DD/MM/AAAA"""
    return pd.to_datetime(series).dt.strftime('%d/%m/%Y')

# --- 4. BANCO DE DADOS ---
DB_FUNC = 'db_funcionarios_v13.csv'
DB_PONTO = 'db_ponto_v13.csv'
DB_VEICULOS = 'db_veiculos_v13.csv'
DB_FINANCEIRO = 'db_financeiro_v13.csv'
DB_CONFIG = 'db_config_v13.csv'

# Colunas padrão para Auto-Correção
COLS_FUNC = ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"]
COLS_PONTO = ["Data", "Nome", "Qtd_Dias", "Descricao"]
COLS_VEIC = ["Veiculo", "Placa", "Km_Inicial"]
COLS_FIN = ["Data", "Categoria", "Descricao", "Valor", "Entidade"]
COLS_CONF = ["Valor_Total"]

def load_data(arquivo, colunas_padrao):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas_padrao).to_csv(arquivo, index=False)
        return pd.read_csv(arquivo)
    try:
        df = pd.read_csv(arquivo)
        # Auto-correção silenciosa
        for col in colunas_padrao:
            if col not in df.columns:
                df[col] = 0 if "Valor" in col else ""
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

def add_row(arquivo, dados_dict, cols_padrao):
    df = load_data(arquivo, cols_padrao)
    df = pd.concat([df, pd.DataFrame([dados_dict])], ignore_index=True)
    df.to_csv(arquivo, index=False)

def save_full(arquivo, df):
    df.to_csv(arquivo, index=False)

# --- 5. NAVEGAÇÃO ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
if 'hist_voltar' not in st.session_state: st.session_state['hist_voltar'] = 'inicio'

def ir_para(tela, voltar_para='inicio'):
    st.session_state['hist_voltar'] = voltar_para
    st.session_state['tela'] = tela
    st.rerun()

def barra_nav(destino_voltar):
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ VOLTAR"): ir_para(destino_voltar)
    with c2:
        if st.button("🏠 INÍCIO"): ir_para('inicio')

# ================= TELA 1: HOME =================
def tela_inicio():
    st.title("GestorPRO")
    st.caption("Sistema de Controle Integrado")
    
    # KPIs
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    saldo = df_fin["Valor"].sum() if not df_fin.empty else 0.0
    
    df_conf = load_data(DB_CONFIG, COLS_CONF)
    total_contrato = float(df_conf["Valor_Total"].iloc[0]) if not df_conf.empty else 0.0
    recebido = df_fin[df_fin["Valor"] > 0]["Valor"].sum() if not df_fin.empty else 0.0
    falta = total_contrato - recebido
    
    c1, c2 = st.columns(2)
    c1.metric("Caixa Atual", format_brl(saldo))
    c2.metric("Saldo de Contrato", format_brl(falta))
    
    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("👷 EQUIPE"): ir_para('menu_equipe', 'inicio')
        if st.button("💰 FINANCEIRO"): ir_para('menu_fin', 'inicio')
    with c2:
        if st.button("🚛 FROTA"): ir_para('menu_frota', 'inicio')
        if st.button("⚙️ CONTRATO"): ir_para('menu_config', 'inicio')

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("Gestão de Pessoas")
    
    if st.button("➕ NOVO COLABORADOR"): ir_para('cad_func', 'menu_equipe')
    
    df_func = load_data(DB_FUNC, COLS_FUNC)
    if df_func.empty:
        st.info("Nenhum colaborador cadastrado.")
        barra_nav('inicio')
        return

    # Seletor
    lista = df_func["Nome"].unique()
    nome_sel = st.selectbox("Selecione o Colaborador:", lista)
    st.session_state['func_atual'] = nome_sel
    
    # Cálculos
    dados = df_func[df_func["Nome"] == nome_sel].iloc[0]
    val_diaria = float(dados["Valor_Diaria"])
    
    # Dias trabalhados
    df_ponto = load_data(DB_PONTO, COLS_PONTO)
    pontos = df_ponto[df_ponto["Nome"] == nome_sel]
    total_dias = pontos["Qtd_Dias"].sum() if not pontos.empty else 0.0
    
    # Vales
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    vales = df_fin[(df_fin["Categoria"]=="Mão de Obra") & (df_fin["Entidade"]==nome_sel) & (df_fin["Valor"]<0)]
    total_vales = abs(vales["Valor"].sum()) if not vales.empty else 0.0
    
    # Saldo
    a_receber = (total_dias * val_diaria) - total_vales
    
    # Abas
    t1, t2, t3 = st.tabs(["RESUMO", "LANÇAMENTOS", "HISTÓRICO"])
    
    with t1:
        st.write(f"**Cargo:** {dados['Funcao']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dias", f"{total_dias:g}")
        c2.metric("Vales", format_brl(total_vales))
        c3.metric("A Pagar", format_brl(a_receber))
        
    with t2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
            if st.button("💸 VALE"): ir_para('acao_vale', 'menu_equipe')
        with c2:
            if st.button("✅ PAGAR"): ir_para('acao_pgto', 'menu_equipe')
            if st.button("📝 FALTA"): ir_para('acao_falta', 'menu_equipe')
            
    with t3:
        if not vales.empty:
            df_view = vales[["Data", "Descricao", "Valor"]].copy()
            # Formatação de Data Brasileira
            df_view["Data"] = format_data_br_coluna(df_view["Data"])
            df_view["Valor"] = df_view["Valor"].apply(format_brl)
            st.dataframe(df_view, hide_index=True, use_container_width=True)
        else:
            st.caption("Sem histórico financeiro.")

    with st.expander("Opções de Cadastro"):
        if st.button("EXCLUIR COLABORADOR"):
            df_func = df_func[df_func["Nome"] != nome_sel]
            save_full(DB_FUNC, df_func)
            st.rerun()

    barra_nav('inicio')

def tela_cad_func():
    st.header("Cadastro de Colaborador")
    # clear_on_submit=True LIMPA OS CAMPOS DEPOIS DE SALVAR
    with st.form("form_cad_func", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        func = st.selectbox("Função", LISTA_FUNCOES)
        val = st.number_input("Valor Diária (R$)", min_value=0.0, value=None, placeholder="0,00")
        inicio = st.date_input("Data de Admissão", datetime.now())
        
        if st.form_submit_button("SALVAR CADASTRO"):
            if nome and val:
                add_row(DB_FUNC, {"Nome": nome, "Funcao": func, "Valor_Diaria": val, "Data_Inicio": inicio}, COLS_FUNC)
                st.toast("Colaborador Cadastrado!", icon="✅")
            else:
                st.error("Preencha o nome e o valor.")
    barra_nav('menu_equipe')

def tela_acao_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    with st.form(f"form_{tipo}", clear_on_submit=True):
        if tipo == "Ponto":
            dt = st.date_input("Data", datetime.now())
            op = st.radio("Tipo", ["Dia Completo (1.0)", "Meio Dia (0.5)", "Falta (0.0)"])
            if st.form_submit_button("CONFIRMAR PONTO"):
                qtd = 1.0 if "Completo" in op else (0.5 if "Meio" in op else 0.0)
                desc = "Dia Normal" if qtd==1.0 else ("Meio Dia" if qtd==0.5 else "Falta")
                add_row(DB_PONTO, {"Data": dt, "Nome": nome, "Qtd_Dias": qtd, "Descricao": desc}, COLS_PONTO)
                st.toast("Ponto Registrado!", icon="⏰")

        elif tipo == "Vale":
            val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
            # Dropdown ao invés de digitar
            motivo = st.selectbox("Motivo", LISTA_VALES)
            if st.form_submit_button("LANÇAR VALE"):
                if val:
                    add_row(DB_FINANCEIRO, {
                        "Data": datetime.now(), "Categoria": "Mão de Obra", 
                        "Descricao": f"Vale ({motivo})", "Valor": -val, "Entidade": nome
                    }, COLS_FIN)
                    st.toast("Vale Lançado!", icon="💸")

        elif tipo == "Pagamento":
            val = st.number_input("Valor do Pagamento (R$)", min_value=0.0, value=None, placeholder="0,00")
            if st.form_submit_button("CONFIRMAR PAGAMENTO"):
                if val:
                    add_row(DB_FINANCEIRO, {
                        "Data": datetime.now(), "Categoria": "Mão de Obra", 
                        "Descricao": "Pagamento de Salário", "Valor": -val, "Entidade": nome
                    }, COLS_FIN)
                    st.toast("Pagamento Efetuado!", icon="✅")

        elif tipo == "Falta":
            motivo = st.selectbox("Motivo da Falta", LISTA_FALTAS)
            if st.form_submit_button("REGISTRAR OCORRÊNCIA"):
                add_row(DB_PONTO, {"Data": datetime.now(), "Nome": nome, "Qtd_Dias": 0.0, "Descricao": f"Falta: {motivo}"}, COLS_PONTO)
                st.toast("Falta Registrada.", icon="📝")

    barra_nav('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("Frota e Equipamentos")
    if st.button("➕ CADASTRAR VEÍCULO"): ir_para('cad_veic', 'menu_frota')
    
    df_v = load_data(DB_VEICULOS, COLS_VEIC)
    if df_v.empty:
        st.info("Cadastre seu primeiro veículo.")
        barra_nav('inicio')
        return

    veic = st.selectbox("Selecione:", df_v["Veiculo"].unique())
    st.session_state['veic_atual'] = veic
    
    # Gasto total
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    gastos = df_fin[df_fin["Entidade"] == veic]
    total = abs(gastos[gastos["Valor"] < 0]["Valor"].sum())
    
    st.metric("Custo Acumulado", format_brl(total))
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⛽ ABASTECER"): ir_para('acao_abast', 'menu_frota')
    with c2:
        if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manut', 'menu_frota')
        
    st.write("---")
    st.write("**Histórico Recente:**")
    if not gastos.empty:
        view = gastos[["Data", "Descricao", "Valor"]].sort_values("Data", ascending=False).head(5)
        view["Data"] = format_data_br_coluna(view["Data"])
        view["Valor"] = view["Valor"].apply(format_brl)
        st.table(view) # Table é mais limpo que dataframe as vezes

    barra_nav('inicio')

def tela_cad_veic():
    st.header("Novo Veículo")
    with st.form("cad_v", clear_on_submit=True):
        mod = st.text_input("Modelo (Ex: Fiat Strada)")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0)
        if st.form_submit_button("SALVAR"):
            nome = f"{mod} - {placa}"
            add_row(DB_VEICULOS, {"Veiculo": nome, "Placa": placa, "Km_Inicial": km}, COLS_VEIC)
            st.toast("Veículo Salvo!", icon="🚛")
    barra_nav('menu_frota')

def tela_acao_frota(tipo):
    veic = st.session_state['veic_atual']
    st.header(f"{tipo}: {veic}")
    
    with st.form(f"form_{tipo}", clear_on_submit=True):
        if tipo == "Abastecer":
            km = st.number_input("KM Painel", min_value=0)
            lit = st.number_input("Litros", min_value=0.0)
            val = st.number_input("Valor Pago (R$)", min_value=0.0, value=None, placeholder="0,00")
            if st.form_submit_button("LANÇAR ABASTECIMENTO"):
                if val:
                    add_row(DB_FINANCEIRO, {
                        "Data": datetime.now(), "Categoria": "Combustível", 
                        "Descricao": f"Abast. {lit}L (KM {km})", "Valor": -val, "Entidade": veic
                    }, COLS_FIN)
                    st.toast("Salvo!", icon="⛽")
                    
        elif tipo == "Manutenção":
            item = st.selectbox("Serviço Realizado", LISTA_MANUTENCAO)
            val = st.number_input("Valor Pago (R$)", min_value=0.0, value=None, placeholder="0,00")
            if st.form_submit_button("LANÇAR MANUTENÇÃO"):
                if val:
                    add_row(DB_FINANCEIRO, {
                        "Data": datetime.now(), "Categoria": "Manutenção", 
                        "Descricao": item, "Valor": -val, "Entidade": veic
                    }, COLS_FIN)
                    st.toast("Salvo!", icon="🔧")
    barra_nav('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_fin():
    st.title("Financeiro Geral")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ RECEITA"): ir_para('fin_ent', 'menu_fin')
    with c2:
        if st.button("➖ DESPESA"): ir_para('fin_sai', 'menu_fin')
        
    st.subheader("Extrato")
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    
    if not df.empty:
        df = df.sort_values("Data", ascending=False)
        
        # Edição
        if 'edit_idx' not in st.session_state: st.session_state['edit_idx'] = -1
        
        for idx, row in df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 1])
                # Limpeza visual: Sem asteriscos, data formatada
                data_fmt = pd.to_datetime(row['Data']).strftime('%d/%m/%Y')
                
                with c1:
                    st.write(f"**{row['Descricao']}**")
                    st.caption(f"{data_fmt} • {row['Categoria']}")
                with c2:
                    color = "green" if row['Valor'] > 0 else "red"
                    st.markdown(f"<span style='color:{color};font-weight:bold'>{format_brl(row['Valor'])}</span>", unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️", key=f"del_{idx}"):
                        df = df.drop(idx)
                        save_full(DB_FINANCEIRO, df)
                        st.rerun()
                st.divider()
    barra_nav('inicio')

def tela_fin_mov(tipo):
    st.header(f"Lançar {tipo}")
    with st.form(f"form_{tipo}", clear_on_submit=True):
        if tipo == "Receita":
            desc = st.text_input("Descrição (Ex: Medição 1, Sinal)")
            cat = "Receita"
        else:
            # Lista para evitar digitação
            desc = st.selectbox("Item", LISTA_MATERIAIS)
            cat = "Material/Geral"
            
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
        
        if st.form_submit_button("CONFIRMAR"):
            if val:
                v_final = val if tipo == "Receita" else -val
                add_row(DB_FINANCEIRO, {
                    "Data": datetime.now(), "Categoria": cat, 
                    "Descricao": desc, "Valor": v_final, "Entidade": "Geral"
                }, COLS_FIN)
                st.toast("Lançamento Salvo!", icon="💰")
    barra_nav('menu_fin')

def tela_config():
    st.header("Configuração de Contrato")
    df = load_data(DB_CONFIG, COLS_CONF)
    atual = float(df["Valor_Total"].iloc[0]) if not df.empty else 0.0
    st.metric("Valor Total do Contrato", format_brl(atual))
    
    with st.form("conf_obra", clear_on_submit=True):
        novo = st.number_input("Novo Valor Total (R$)", min_value=0.0, value=None)
        if st.form_submit_button("ATUALIZAR"):
            if novo:
                pd.DataFrame([{"Valor_Total": novo}]).to_csv(DB_CONFIG, index=False)
                st.toast("Atualizado!", icon="⚙️")
                st.rerun()
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
    elif tela == 'fin_ent': tela_fin_mov("Receita")
    elif tela == 'fin_sai': tela_fin_mov("Despesa")
    elif tela == 'menu_config': tela_config()

if __name__ == "__main__":
    main()
