import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gestor Aviário Enterprise", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    /* Botões Padrão: Grandes e Brancos/Cinza */
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 10px;
        margin-bottom: 8px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        color: #212529;
    }
    .stButton>button:hover {
        border-color: #0d6efd;
        color: #0d6efd;
        background-color: #ffffff;
    }
    
    /* Botões de Ação Específica (Destaques) */
    .btn-green { border: 2px solid #198754 !important; color: #198754 !important; }
    
    /* Métricas e Títulos */
    h1 { color: #2c3e50; font-size: 1.8rem; font-weight: 700; }
    h3 { color: #34495e; font-size: 1.3rem; }
    [data-testid="stMetricValue"] { font-size: 1.6rem; color: #2c3e50; }
    
    /* Esconder menu técnico */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. UTILITÁRIOS E FORMATAÇÃO ---

def format_brl(valor):
    """Ex: R$ 1.200,50"""
    if valor is None: return "R$ 0,00"
    try:
        val_float = float(valor)
        return f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def format_data_visual(data_input):
    """Exibe 25/12/2023 visualmente, mas mantém YYYY-MM-DD internamente"""
    if data_input is None: return ""
    try:
        # Se for string YYYY-MM-DD
        if isinstance(data_input, str):
            data_obj = datetime.strptime(data_input, '%Y-%m-%d')
            return data_obj.strftime('%d/%m/%Y')
        # Se for objeto date
        return data_input.strftime('%d/%m/%Y')
    except:
        return str(data_input)

# --- 3. BANCO DE DADOS (CSVs) ---
# Separamos o Ponto para cálculo exato de dias
DB_FUNC = 'db_funcionarios_v12.csv'
DB_PONTO = 'db_ponto_v12.csv' 
DB_VEICULOS = 'db_veiculos_v12.csv'
DB_FINANCEIRO = 'db_financeiro_v12.csv'
DB_CONFIG = 'db_config_v12.csv'

# Definição de colunas para Auto-Correção
COLS_FUNC = ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"]
COLS_PONTO = ["Data", "Nome", "Qtd_Dias", "Descricao"] # Qtd_Dias: 1.0 ou 0.5
COLS_VEIC = ["Veiculo", "Placa", "Km_Inicial"]
COLS_FIN = ["Data", "Categoria", "Descricao", "Valor", "Entidade"] # Entidade guarda o nome do func/veiculo
COLS_CONF = ["Valor_Total"]

def load_data(arquivo, colunas_padrao):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas_padrao).to_csv(arquivo, index=False)
        return pd.read_csv(arquivo)
    
    try:
        df = pd.read_csv(arquivo)
        # Auto-correção de colunas faltantes
        salvar = False
        for col in colunas_padrao:
            if col not in df.columns:
                df[col] = 0 if "Valor" in col or "Qtd" in col else ""
                salvar = True
        if salvar: df.to_csv(arquivo, index=False)
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

def add_row(arquivo, dados_dict, cols_padrao):
    df = load_data(arquivo, cols_padrao)
    df = pd.concat([df, pd.DataFrame([dados_dict])], ignore_index=True)
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

def barra_botoes_nav(destino_voltar):
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ VOLTAR"): ir_para(destino_voltar)
    with c2:
        if st.button("🏠 INÍCIO"): ir_para('inicio')

# ================= TELA 1: DASHBOARD =================
def tela_inicio():
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=70)
    st.title("Gestor Aviário Profissional")
    
    # KPIs
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    saldo = df_fin["Valor"].sum() if not df_fin.empty else 0.0
    
    df_conf = load_data(DB_CONFIG, COLS_CONF)
    total_obra = float(df_conf["Valor_Total"].iloc[0]) if not df_conf.empty else 0.0
    recebido = df_fin[df_fin["Valor"] > 0]["Valor"].sum() if not df_fin.empty else 0.0
    falta = total_obra - recebido
    
    col1, col2 = st.columns(2)
    col1.metric("Caixa Disponível", format_brl(saldo))
    col2.metric("A Receber (Obra)", format_brl(falta))
    
    st.write("---")
    st.subheader("Menu Principal")
    
    if st.button("👷 GESTÃO DE EQUIPE (Pontos e Vales)"): ir_para('menu_equipe', 'inicio')
    if st.button("🚛 FROTA & MÁQUINAS"): ir_para('menu_frota', 'inicio')
    if st.button("💰 FINANCEIRO GERAL"): ir_para('menu_fin', 'inicio')
    if st.button("⚙️ CONFIGURAR CONTRATO"): ir_para('menu_config', 'inicio')

# ================= TELA 2: EQUIPE (CORAÇÃO DO APP) =================
def tela_equipe():
    st.title("👷 Equipe")
    
    if st.button("➕ CADASTRAR NOVO FUNCIONÁRIO"): ir_para('cad_func', 'menu_equipe')
    
    df_func = load_data(DB_FUNC, COLS_FUNC)
    if df_func.empty:
        st.warning("Cadastre alguém primeiro.")
        barra_botoes_nav('inicio')
        return

    st.write("### Selecione o Colaborador:")
    lista_nomes = df_func["Nome"].unique()
    nome_sel = st.selectbox("Lista:", lista_nomes)
    st.session_state['func_atual'] = nome_sel
    
    # Dados do Funcionário
    dados = df_func[df_func["Nome"] == nome_sel].iloc[0]
    val_diaria = float(dados["Valor_Diaria"])
    
    # --- CÁLCULO INTELIGENTE (DIAS x VALOR - VALES) ---
    # 1. Busca Pontos
    df_ponto = load_data(DB_PONTO, COLS_PONTO)
    # Filtro por nome exato
    pontos_func = df_ponto[df_ponto["Nome"] == nome_sel]
    # Soma dias (1.0 para completo, 0.5 para meio)
    total_dias = pontos_func["Qtd_Dias"].sum() if not pontos_func.empty else 0.0
    bruto_receber = total_dias * val_diaria
    
    # 2. Busca Vales/Adiantamentos
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    # Filtra categoria 'Mão de Obra' e Entidade = Nome
    filtro_vales = df_fin[
        (df_fin["Categoria"] == "Mão de Obra") & 
        (df_fin["Entidade"] == nome_sel) & 
        (df_fin["Valor"] < 0) # Só saídas
    ]
    total_vales = abs(filtro_vales["Valor"].sum()) if not filtro_vales.empty else 0.0
    
    # 3. Saldo
    saldo_pagar = bruto_receber - total_vales
    
    # --- INTERFACE EM ABAS ---
    tab_resumo, tab_acoes, tab_hist = st.tabs(["📊 SALDO & CÁLCULO", "⚡ AÇÕES", "📜 EXTRATO"])
    
    with tab_resumo:
        st.info(f"Cargo: {dados['Funcao']} | Diária: {format_brl(val_diaria)}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Dias Trab.", f"{total_dias:g}") # :g remove zeros decimais desnecessários
        c2.metric("Bruto", format_brl(bruto_receber))
        c3.metric("Vales", format_brl(total_vales))
        
        st.divider()
        if saldo_pagar > 0:
            st.success(f"💰 **A PAGAR: {format_brl(saldo_pagar)}**")
        elif saldo_pagar < 0:
            st.error(f"⚠️ DEVEDOR: {format_brl(saldo_pagar)}")
        else:
            st.info("✅ Contas em dia (Zerado)")
            
    with tab_acoes:
        st.write("O que deseja lançar?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏰ MARCAR PONTO"): ir_para('acao_ponto', 'menu_equipe')
            if st.button("💸 DAR VALE"): ir_para('acao_vale', 'menu_equipe')
        with c2:
            if st.button("✅ PAGAR SALDO"): ir_para('acao_pgto', 'menu_equipe')
            if st.button("📝 JUSTIFICAR FALTA"): ir_para('acao_falta', 'menu_equipe')
            
    with tab_hist:
        st.write("**Histórico de Ponto:**")
        if not pontos_func.empty:
            st.dataframe(pontos_func[["Data", "Descricao", "Qtd_Dias"]].sort_values("Data", ascending=False), hide_index=True)
        else:
            st.caption("Sem pontos registrados.")
            
        st.write("**Histórico Financeiro:**")
        if not filtro_vales.empty:
            # Prepara visualização bonita
            view_vales = filtro_vales[["Data", "Descricao", "Valor"]].copy()
            view_vales["Data"] = view_vales["Data"].apply(format_data_visual)
            view_vales["Valor"] = view_vales["Valor"].apply(format_brl)
            st.dataframe(view_vales, hide_index=True)
        else:
            st.caption("Sem vales registrados.")

    # Edição
    with st.expander(f"⚙️ Configurar Cadastro de {nome_sel}"):
        with st.form("edit_func"):
            n_nome = st.text_input("Nome", value=nome_sel)
            n_funcao = st.text_input("Função", value=dados['Funcao'])
            n_valor = st.number_input("Valor Diária", value=float(dados['Valor_Diaria']))
            if st.form_submit_button("SALVAR ALTERAÇÕES"):
                # Atualiza DB_FUNC
                df_func.loc[df_func["Nome"] == nome_sel, ["Nome", "Funcao", "Valor_Diaria"]] = [n_nome, n_funcao, n_valor]
                save_full(DB_FUNC, df_func)
                # Atualiza históricos para não perder vínculo
                # (Opcional, mas recomendado em sistemas reais: atualizar nome nos outros DBs)
                st.success("Atualizado!")
                st.rerun()
        if st.button("🗑️ EXCLUIR CADASTRO"):
            df_func = df_func[df_func["Nome"] != nome_sel]
            save_full(DB_FUNC, df_func)
            st.success("Excluído.")
            st.rerun()

    barra_botoes_nav('inicio')

def tela_cad_func():
    st.header("Novo Funcionário")
    with st.form("cad_func"):
        nome = st.text_input("Nome Completo")
        func = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Cozinheira", "Motorista"])
        val = st.number_input("Valor Diária (R$)", min_value=0.0, value=None, placeholder="Digite...")
        inicio = st.date_input("Data Início", datetime.now())
        
        if st.form_submit_button("SALVAR"):
            if nome and val:
                add_row(DB_FUNC, {
                    "Nome": nome, "Funcao": func, "Valor_Diaria": val, "Data_Inicio": inicio
                }, COLS_FUNC)
                st.success("Salvo!")
                ir_para('menu_equipe')
            else:
                st.error("Preencha todos os campos.")
    barra_botoes_nav('menu_equipe')

def tela_acao_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    if tipo == "Ponto":
        dt = st.date_input("Data", datetime.now())
        opcao = st.radio("Selecione:", ["Dia Completo (1.0)", "Meio Dia (0.5)", "Falta (0.0)"])
        
        if st.button("CONFIRMAR PONTO"):
            qtd = 1.0 if "Completo" in opcao else (0.5 if "Meio" in opcao else 0.0)
            desc_p = "Dia Normal" if qtd == 1.0 else ("Meio Dia" if qtd == 0.5 else "Falta")
            
            # Salva no DB_PONTO
            add_row(DB_PONTO, {
                "Data": dt, "Nome": nome, "Qtd_Dias": qtd, "Descricao": desc_p
            }, COLS_PONTO)
            st.success("Ponto Computado!")
            ir_para('menu_equipe')

    elif tipo == "Vale":
        st.info("Isso registra uma saída de dinheiro do caixa.")
        val = st.number_input("Valor do Vale (R$)", min_value=0.0, value=None, placeholder="Valor...")
        obs = st.text_input("Motivo (Ex: Gasolina, Adiantamento)")
        
        if st.button("CONFIRMAR VALE"):
            if val:
                desc = f"Vale {nome}" + (f" - {obs}" if obs else "")
                # Salva no Financeiro
                add_row(DB_FINANCEIRO, {
                    "Data": datetime.now(), "Categoria": "Mão de Obra", 
                    "Descricao": desc, "Valor": -val, "Entidade": nome
                }, COLS_FIN)
                st.success("Vale Lançado!")
                ir_para('menu_equipe')

    elif tipo == "Pagamento":
        st.info("Pagamento final/semanal para zerar o saldo.")
        val = st.number_input("Valor a Pagar (R$)", min_value=0.0, value=None, placeholder="Valor...")
        
        if st.button("CONFIRMAR PAGAMENTO"):
            if val:
                add_row(DB_FINANCEIRO, {
                    "Data": datetime.now(), "Categoria": "Mão de Obra", 
                    "Descricao": f"Pagamento Final {nome}", "Valor": -val, "Entidade": nome
                }, COLS_FIN)
                st.success("Pago!")
                ir_para('menu_equipe')

    elif tipo == "Falta":
        motivo = st.text_area("Motivo da Falta/Ocorrência")
        if st.button("SALVAR"):
            # Salva no ponto com 0 dias
            add_row(DB_PONTO, {
                "Data": datetime.now(), "Nome": nome, "Qtd_Dias": 0.0, "Descricao": f"Falta Justif: {motivo}"
            }, COLS_PONTO)
            st.success("Registrado.")
            ir_para('menu_equipe')

    barra_botoes_nav('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("🚛 Frota")
    
    if st.button("➕ NOVO VEÍCULO"): ir_para('cad_veiculo', 'menu_frota')
    
    df_v = load_data(DB_VEICULOS, COLS_VEIC)
    if df_v.empty:
        st.warning("Cadastre um veículo.")
        barra_botoes_nav('inicio')
        return

    veic = st.selectbox("Selecione:", df_v["Veiculo"].unique())
    st.session_state['veiculo_atual'] = veic
    
    # Dados
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    # Filtra por Entidade = Veiculo
    filtro = df_fin[df_fin["Entidade"] == veic]
    total_gasto = abs(filtro[filtro["Valor"] < 0]["Valor"].sum())
    
    st.info(f"Veículo: **{veic}** | Custo Acumulado: {format_brl(total_gasto)}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⛽ ABASTECER"): ir_para('acao_abastecer', 'menu_frota')
    with c2:
        if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manut', 'menu_frota')
        
    st.write("---")
    st.write("**Extrato do Veículo:**")
    if not filtro.empty:
        # Tabela Bonita
        df_show = filtro[["Data", "Descricao", "Valor"]].copy()
        df_show["Data"] = df_show["Data"].apply(format_data_visual)
        df_show["Valor"] = df_show["Valor"].apply(format_brl)
        st.dataframe(df_show, hide_index=True, use_container_width=True)

    with st.expander("🗑️ Excluir Veículo"):
        if st.button("CONFIRMAR EXCLUSÃO"):
            df_v = df_v[df_v["Veiculo"] != veic]
            save_full(DB_VEICULOS, df_v)
            st.rerun()

    barra_botoes_nav('inicio')

def tela_cad_veiculo():
    st.header("Novo Veículo")
    with st.form("cad_v"):
        mod = st.text_input("Modelo (Ex: Hilux)")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0)
        if st.form_submit_button("SALVAR"):
            nome_f = f"{mod} {placa}"
            add_row(DB_VEICULOS, {"Veiculo": nome_f, "Placa": placa, "Km_Inicial": km}, COLS_VEIC)
            st.success("Salvo!")
            ir_para('menu_frota')
    barra_botoes_nav('menu_frota')

def tela_acao_frota(tipo):
    veic = st.session_state['veiculo_atual']
    st.header(f"{tipo}: {veic}")
    
    km = st.number_input("KM no Painel", min_value=0, value=None, placeholder="KM Atual...")
    val = st.number_input("Valor Total (R$)", min_value=0.0, value=None, placeholder="Valor Pago...")
    
    litros = 0.0
    item = ""
    
    if tipo == "Abastecer":
        litros = st.number_input("Litros", min_value=0.0, value=None, placeholder="Qtd Litros...")
    else:
        item = st.text_input("O que foi feito? (Ex: Pneu, Óleo)")
        
    if st.button("SALVAR"):
        if val:
            if tipo == "Abastecer":
                desc = f"Abast. {litros}L (KM {km})" if litros else f"Abastecimento (KM {km})"
                cat = "Combustível"
            else:
                desc = f"Manut: {item}"
                cat = "Manutenção"
                
            add_row(DB_FINANCEIRO, {
                "Data": datetime.now(), "Categoria": cat, 
                "Descricao": desc, "Valor": -val, "Entidade": veic
            }, COLS_FIN)
            st.success("Salvo!")
            ir_para('menu_frota')
            
    barra_botoes_nav('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_financeiro():
    st.title("💰 Financeiro Geral")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ RECEITA (ENTRADA)"): ir_para('fin_ent', 'menu_fin')
    with c2:
        if st.button("➖ DESPESA (MATERIAL)"): ir_para('fin_sai', 'menu_fin')
        
    st.write("---")
    st.subheader("Extrato Completo")
    
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    if not df.empty:
        # Filtros e Ordenação
        df = df.sort_values(by="Data", ascending=False)
        
        # Edição
        if 'edit_idx' not in st.session_state: st.session_state['edit_idx'] = -1
        
        for idx, row in df.iterrows():
            cor = "green" if row['Valor'] > 0 else "#e74c3c"
            
            # Container visual
            with st.container():
                c_txt, c_acts = st.columns([3, 1])
                with c_txt:
                    st.markdown(f"**{row['Descricao']}**")
                    st.caption(f"📅 {format_data_visual(row['Data'])} | {row['Categoria']}")
                    st.markdown(f"<span style='color:{cor};font-weight:bold'>{format_brl(row['Valor'])}</span>", unsafe_allow_html=True)
                with c_acts:
                    if st.button("✏️", key=f"e_{idx}"):
                        st.session_state['edit_idx'] = idx
                        st.rerun()
                    if st.button("🗑️", key=f"d_{idx}"):
                        df = df.drop(idx)
                        save_full(DB_FINANCEIRO, df)
                        st.rerun()
            
            # Form de Edição
            if st.session_state['edit_idx'] == idx:
                with st.form(f"form_ed_{idx}"):
                    n_desc = st.text_input("Desc", value=row['Descricao'])
                    n_val = st.number_input("Valor", value=float(row['Valor']))
                    if st.form_submit_button("SALVAR"):
                        df.at[idx, "Descricao"] = n_desc
                        df.at[idx, "Valor"] = n_val
                        save_full(DB_FINANCEIRO, df)
                        st.session_state['edit_idx'] = -1
                        st.rerun()
            st.divider()

    barra_botoes_nav('inicio')

def tela_fin_lanc(tipo):
    st.header(f"Lançar {tipo}")
    desc = st.text_input("Descrição (Ex: Cimento, Venda de Aves)")
    val = st.number_input("Valor R$", min_value=0.0, value=None, placeholder="Valor...")
    
    if st.button("CONFIRMAR"):
        if val:
            cat = "Receita" if tipo == "Receita" else "Material/Outros"
            v_final = val if tipo == "Receita" else -val
            add_row(DB_FINANCEIRO, {
                "Data": datetime.now(), "Categoria": cat, 
                "Descricao": desc, "Valor": v_final, "Entidade": "Geral"
            }, COLS_FIN)
            st.success("Salvo!")
            ir_para('menu_fin')
    barra_botoes_nav('menu_fin')

def tela_config():
    st.header("Configuração Contrato")
    df = load_data(DB_CONFIG, COLS_CONF)
    atual = float(df["Valor_Total"].iloc[0]) if not df.empty else 0.0
    st.metric("Valor Atual Contrato", format_brl(atual))
    
    novo = st.number_input("Novo Valor Total", value=None)
    if st.button("ATUALIZAR"):
        if novo:
            pd.DataFrame([{"Valor_Total": novo}]).to_csv(DB_CONFIG, index=False)
            st.success("Ok!")
            st.rerun()
    barra_botoes_nav('inicio')

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
    elif tela == 'cad_veiculo': tela_cad_veiculo()
    elif tela == 'acao_abastecer': tela_acao_frota("Abastecer")
    elif tela == 'acao_manut': tela_acao_frota("Manutenção")
    
    elif tela == 'menu_fin': tela_financeiro()
    elif tela == 'fin_ent': tela_fin_lanc("Receita")
    elif tela == 'fin_sai': tela_fin_lanc("Despesa")
    
    elif tela == 'menu_config': tela_config()

if __name__ == "__main__":
    main()
