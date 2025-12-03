import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL (LAYOUT GRID MANTIDO) ---
st.set_page_config(page_title="GestorPRO", layout="centered", page_icon="💎")

st.markdown("""
    <style>
    /* CSS PARA FORÇAR GRID NO CELULAR */
    @media (max-width: 576px) {
        div[data-testid="column"] { width: 48% !important; flex: 0 0 48% !important; min-width: 10px !important; }
    }
    /* Estilo dos Botões Principais */
    .btn-main > button {
        width: 100%; height: 90px; font-size: 18px !important; font-weight: 700 !important;
        border-radius: 16px !important; background: white !important;
        border: 1px solid #cbd5e1 !important; color: #1e293b !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important; margin-bottom: 10px !important;
    }
    /* Estilo dos Botões de Ação */
    .btn-action > button { height: 60px; border-radius: 12px; font-weight: 600; background-color: #f8fafc; }
    
    /* Esconder menus técnicos */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. UTILITÁRIOS ---
def format_brl(valor):
    if valor is None: return "R$ 0,00"
    try:
        val = float(valor)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def format_data_visual(data_input):
    if data_input is None: return ""
    try:
        if isinstance(data_input, str):
            data_obj = datetime.strptime(data_input, '%Y-%m-%d')
            return data_obj.strftime('%d/%m/%Y')
        return data_input.strftime('%d/%m/%Y')
    except: return str(data_input)

# --- 3. BANCO DE DADOS (NOMES FIXOS) ---
DB_FUNC = 'db_funcionarios_final.csv'
DB_PONTO = 'db_ponto_final.csv'
DB_VEICULOS = 'db_veiculos_final.csv'
DB_FINANCEIRO = 'db_financeiro_final.csv'
DB_CONFIG = 'db_config_final.csv'

# Colunas
COLS_FUNC = ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio", "Chave_Pix", "Banco"]
COLS_PONTO = ["Data", "Nome", "Qtd_Dias", "Descricao"]
COLS_VEIC = ["Veiculo", "Placa", "Km_Inicial"]
COLS_FIN = ["Data", "Categoria", "Descricao", "Valor", "Entidade", "Metodo_Pagto"]
COLS_CONF = ["Valor_Total"]

def load_data(arquivo, colunas_padrao):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas_padrao).to_csv(arquivo, index=False)
        return pd.read_csv(arquivo)
    try:
        df = pd.read_csv(arquivo)
        for col in colunas_padrao:
            if col not in df.columns: df[col] = 0 if "Valor" in col else ""
        return df
    except: return pd.DataFrame(columns=colunas_padrao)

def add_row(arquivo, dados, cols):
    df = load_data(arquivo, cols)
    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    df.to_csv(arquivo, index=False)

def save_full(arquivo, df):
    df.to_csv(arquivo, index=False)

# --- FUNÇÃO ESPECIAL DE EXCLUSÃO (CORREÇÃO DE BUG) ---
def excluir_item_seguro(arquivo, coluna_id, valor_id, cols_padrao):
    """
    Remove uma linha baseada em uma coluna (ex: Nome) e salva imediatamente.
    """
    df = load_data(arquivo, cols_padrao)
    if not df.empty:
        # Mantém apenas as linhas que NÃO são o item que queremos excluir
        df = df[df[coluna_id] != valor_id]
        df.to_csv(arquivo, index=False)
        return True
    return False

def excluir_por_index(arquivo, index_real, cols_padrao):
    """
    Remove uma linha pelo número do index (para financeiro).
    """
    df = load_data(arquivo, cols_padrao)
    if index_real in df.index:
        df = df.drop(index_real)
        df.to_csv(arquivo, index=False)
        return True
    return False

# --- 4. NAVEGAÇÃO ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
if 'hist_voltar' not in st.session_state: st.session_state['hist_voltar'] = 'inicio'

def ir_para(tela, voltar_para='inicio'):
    st.session_state['hist_voltar'] = voltar_para
    st.session_state['tela'] = tela
    st.rerun()

def barra_nav(destino):
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ VOLTAR"): ir_para(destino)
    with c2: 
        if st.button("🏠 INÍCIO"): ir_para('inicio')

# ================= TELA 1: DASHBOARD =================
def tela_inicio():
    st.title("GestorPRO")
    st.caption(f"🗓️ {datetime.now().strftime('%d/%m/%Y')}")
    
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    saldo_real = df_fin["Valor"].sum() if not df_fin.empty else 0.0
    
    fatura_cartao = 0.0
    if not df_fin.empty:
        filtro = df_fin[(df_fin["Metodo_Pagto"] == "Cartão de Crédito") & (df_fin["Valor"] < 0)]
        fatura_cartao = abs(filtro["Valor"].sum())

    c1, c2 = st.columns(2)
    c1.metric("Caixa", format_brl(saldo_real))
    c2.metric("Cartão", format_brl(fatura_cartao), delta_color="inverse")
    
    st.write("") 
    st.subheader("Menu Principal")
    
    c_menu1, c_menu2 = st.columns(2)
    with c_menu1:
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("👷 EQUIPE\n& RH"): ir_para('menu_equipe', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("🚛 FROTA\n& Veículos"): ir_para('menu_frota', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)

    with c_menu2:
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("💰 CAIXA\n& Extrato"): ir_para('menu_fin', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="btn-main">', unsafe_allow_html=True)
        if st.button("💳 CARTÕES\n& Faturas"): ir_para('menu_cartao', 'inicio')
        st.markdown('</div>', unsafe_allow_html=True)

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("Gestão de Equipe")
    
    st.markdown('<div class="btn-action">', unsafe_allow_html=True)
    if st.button("➕ NOVO COLABORADOR"): ir_para('cad_func', 'menu_equipe')
    st.markdown('</div>', unsafe_allow_html=True)
    
    df_func = load_data(DB_FUNC, COLS_FUNC)
    if df_func.empty:
        st.info("Nenhum cadastro.")
        barra_nav('inicio'); return

    st.write("---")
    nome_sel = st.selectbox("Selecione:", df_func["Nome"].unique())
    st.session_state['func_atual'] = nome_sel
    
    # Dados
    linha = df_func[df_func["Nome"] == nome_sel].iloc[0]
    
    # Cálculos
    df_ponto = load_data(DB_PONTO, COLS_PONTO)
    dias = df_ponto[df_ponto["Nome"] == nome_sel]["Qtd_Dias"].sum()
    
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    pgtos = df_fin[(df_fin["Entidade"] == nome_sel) & (df_fin["Valor"] < 0)]
    total_pago = abs(pgtos["Valor"].sum())
    
    a_receber = (dias * float(linha["Valor_Diaria"])) - total_pago
    
    st.info(f"Função: **{linha['Funcao']}**")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Dias", f"{dias:g}")
    c2.metric("Pago", format_brl(total_pago))
    c3.metric("Saldo", format_brl(a_receber))
    
    tab1, tab2, tab3 = st.tabs(["AÇÕES", "EXTRATO", "CONFIG"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
            if st.button("💸 VALE"): ir_para('acao_vale', 'menu_equipe')
        with c2:
            if st.button("✅ PAGAR"): ir_para('acao_pgto', 'menu_equipe')
            if st.button("📝 FALTA"): ir_para('acao_falta', 'menu_equipe')
            
    with tab2:
        if not pgtos.empty:
            pgtos['idx_real'] = pgtos.index
            for i, row in pgtos.sort_index(ascending=False).iterrows():
                idx_real = row['idx_real']
                c_txt, c_del = st.columns([4, 1])
                with c_txt:
                    st.write(f"**{row['Descricao']}** | {format_brl(row['Valor'])}")
                    st.caption(format_data_visual(row['Data']))
                with c_del:
                    # Botão para excluir lançamento financeiro específico
                    if st.button("🗑️", key=f"del_fin_{idx_real}"):
                        excluir_por_index(DB_FINANCEIRO, idx_real, COLS_FIN)
                        st.toast("Item excluído!")
                        st.rerun()
                st.divider()
        else:
            st.caption("Sem histórico financeiro.")

    with tab3:
        # AQUI ESTÁ A CORREÇÃO DA EXCLUSÃO DO CADASTRO
        st.write("Zona de Perigo:")
        if st.button("🗑️ EXCLUIR ESTE FUNCIONÁRIO"):
            excluir_item_seguro(DB_FUNC, "Nome", nome_sel, COLS_FUNC)
            st.success("Funcionário excluído com sucesso!")
            st.rerun()

    barra_nav('inicio')

def tela_cad_func():
    st.header("Novo Cadastro")
    with st.form("cad_func", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        func = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Motorista", "Cozinheira", "Outro"])
        dt_ini = st.date_input("Admissão", datetime.now(), format="DD/MM/YYYY")
        val = st.number_input("Valor Diária (R$)", min_value=0.0, value=None, placeholder="0,00")
        st.caption("Dados Bancários (Opcional)")
        banco = st.text_input("Banco")
        pix = st.text_input("Chave PIX")
        
        if st.form_submit_button("SALVAR"):
            if nome and val:
                add_row(DB_FUNC, {"Nome": nome, "Funcao": func, "Valor_Diaria": val, "Data_Inicio": dt_ini, "Chave_Pix": pix, "Banco": banco}, COLS_FUNC)
                st.toast("Cadastrado!", icon="✅")
    barra_nav('menu_equipe')

def tela_acao_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    with st.form(f"form_{tipo}", clear_on_submit=True):
        if tipo == "Ponto":
            dt = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            op = st.radio("Registro", ["Dia Completo (1.0)", "Meio Dia (0.5)", "Falta (0.0)"])
            if st.form_submit_button("CONFIRMAR"):
                qtd = 1.0 if "Completo" in op else (0.5 if "Meio" in op else 0.0)
                desc = "Dia Normal" if qtd==1.0 else "Meio/Falta"
                add_row(DB_PONTO, {"Data": dt, "Nome": nome, "Qtd_Dias": qtd, "Descricao": desc}, COLS_PONTO)
                st.toast("Ponto Salvo!")
        elif tipo in ["Vale", "Pagamento"]:
            val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
            metodo = st.selectbox("Pago via", ["PIX", "Dinheiro", "Transferência"])
            obs = st.text_input("Obs")
            if st.form_submit_button("LANÇAR"):
                if val:
                    desc_final = f"{tipo} ({obs})" if obs else tipo
                    add_row(DB_FINANCEIRO, {"Data": datetime.now(), "Categoria": "Mão de Obra", "Descricao": desc_final, "Valor": -val, "Entidade": nome, "Metodo_Pagto": metodo}, COLS_FIN)
                    st.toast("Financeiro Atualizado!")
        elif tipo == "Falta":
            motivo = st.text_input("Motivo")
            if st.form_submit_button("SALVAR"):
                add_row(DB_PONTO, {"Data": datetime.now(), "Nome": nome, "Qtd_Dias": 0.0, "Descricao": f"Falta: {motivo}"}, COLS_PONTO)
                st.toast("Ok!")
    barra_nav('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("Frota")
    st.markdown('<div class="btn-action">', unsafe_allow_html=True)
    if st.button("➕ NOVO VEÍCULO"): ir_para('cad_veic', 'menu_frota')
    st.markdown('</div>', unsafe_allow_html=True)
    
    df_v = load_data(DB_VEICULOS, COLS_VEIC)
    if df_v.empty: barra_nav('inicio'); return

    st.write("---")
    veic = st.selectbox("Selecione:", df_v["Veiculo"].unique())
    st.session_state['veic_atual'] = veic
    
    df_fin = load_data(DB_FINANCEIRO, COLS_FIN)
    gastos = df_fin[df_fin["Entidade"] == veic]
    total = abs(gastos[gastos["Valor"] < 0]["Valor"].sum())
    
    st.metric("Custo Total", format_brl(total))
    
    tab1, tab2 = st.tabs(["AÇÕES", "EXTRATO VEÍCULO"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("⛽ ABASTECER"): ir_para('acao_abast', 'menu_frota')
        with c2: 
            if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manut', 'menu_frota')
        
        st.write("")
        if st.button("🗑️ EXCLUIR VEÍCULO"):
            excluir_item_seguro(DB_VEICULOS, "Veiculo", veic, COLS_VEIC)
            st.success("Veículo excluído.")
            st.rerun()

    with tab2:
        if not gastos.empty:
            gastos['idx_real'] = gastos.index
            for i, row in gastos.sort_index(ascending=False).iterrows():
                idx = row['idx_real']
                c_txt, c_del = st.columns([4, 1])
                with c_txt:
                    st.write(f"**{row['Descricao']}** | {format_brl(row['Valor'])}")
                    st.caption(format_data_visual(row['Data']))
                with c_del:
                    if st.button("🗑️", key=f"del_fr_{idx}"):
                        excluir_por_index(DB_FINANCEIRO, idx, COLS_FIN)
                        st.rerun()
                st.divider()

    barra_nav('inicio')

def tela_cad_veic():
    st.header("Novo Veículo")
    with st.form("cad_v", clear_on_submit=True):
        mod = st.text_input("Modelo")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0)
        if st.form_submit_button("SALVAR"):
            add_row(DB_VEICULOS, {"Veiculo": f"{mod} - {placa}", "Placa": placa, "Km_Inicial": km}, COLS_VEIC)
            st.toast("Salvo!")
    barra_nav('menu_frota')

def tela_acao_frota(tipo):
    veic = st.session_state['veic_atual']
    st.header(f"{tipo}: {veic}")
    with st.form("act_frota", clear_on_submit=True):
        if tipo == "Abastecer":
            lit = st.number_input("Litros", min_value=0.0)
            km = st.number_input("KM Painel", min_value=0)
        else:
            item = st.selectbox("Serviço", ["Mecânica", "Pneus", "Óleo", "Elétrica", "Peças"])
        val = st.number_input("Valor Pago (R$)", min_value=0.0, value=None, placeholder="0,00")
        pagto = st.selectbox("Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito"])
        
        if st.form_submit_button("LANÇAR"):
            if val:
                desc = f"Abast. {lit}L" if tipo=="Abastecer" else f"Manut: {item}"
                if tipo=="Abastecer": desc += f" (KM {km})"
                add_row(DB_FINANCEIRO, {"Data": datetime.now(), "Categoria": "Combustível" if tipo=="Abastecer" else "Manutenção", "Descricao": desc, "Valor": -val, "Entidade": veic, "Metodo_Pagto": pagto}, COLS_FIN)
                st.toast("Salvo!")
    barra_nav('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_fin():
    st.title("Financeiro")
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("➕ RECEITA"): ir_para('fin_receita', 'menu_fin')
    with c2: 
        if st.button("➖ DESPESA"): ir_para('fin_despesa', 'menu_fin')
        
    st.write("---")
    
    # NOVA ABA: EXTRATO COMPLETO
    tab_resumo, tab_extrato = st.tabs(["RESUMO RÁPIDO", "🔍 EXTRATO COMPLETO"])
    
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    
    with tab_resumo:
        if not df.empty:
            # Mostra últimos 5 lançamentos
            df_recent = df.sort_values("Data", ascending=False).head(5)
            for idx, row in df_recent.iterrows():
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    dt = pd.to_datetime(row['Data']).strftime('%d/%m/%Y')
                    with c1:
                        st.write(f"**{row['Descricao']}**")
                        st.caption(f"{dt} • {row['Metodo_Pagto']}")
                    with c2:
                        cor = "green" if row['Valor']>0 else "red"
                        st.markdown(f"<span style='color:{cor}'><b>{format_brl(row['Valor'])}</b></span>", unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("Sem lançamentos.")

    with tab_extrato:
        st.write("### Histórico Detalhado")
        st.caption("Aqui você pode apagar lançamentos errados.")
        
        if not df.empty:
            # Filtro de Categoria
            cats = st.multiselect("Filtrar Categoria", df["Categoria"].unique())
            df_show = df if not cats else df[df["Categoria"].isin(cats)]
            
            df_show['idx_real'] = df_show.index
            for i, row in df_show.sort_index(ascending=False).iterrows():
                idx_real = row['idx_real']
                with st.container():
                    c1, c2, c3 = st.columns([4, 2, 1])
                    with c1:
                        st.write(f"{row['Descricao']}")
                        st.caption(f"{format_data_visual(row['Data'])} | {row['Entidade']}")
                    with c2:
                         cor = "green" if row['Valor']>0 else "red"
                         st.markdown(f"<span style='color:{cor}'>{format_brl(row['Valor'])}</span>", unsafe_allow_html=True)
                    with c3:
                        # BOTÃO DE EXCLUIR DEFINITIVO
                        if st.button("🗑️", key=f"del_all_{idx_real}"):
                            excluir_por_index(DB_FINANCEIRO, idx_real, COLS_FIN)
                            st.toast("Lançamento excluído!")
                            st.rerun()
                    st.divider()
    barra_nav('inicio')

def tela_movimento(tipo):
    st.header(f"Lançar {tipo}")
    with st.form("mov", clear_on_submit=True):
        if tipo == "Receita":
            desc = st.text_input("Descrição")
            cat = "Receita"
        else:
            desc = st.selectbox("Item", ["Cimento", "Areia", "Tijolos", "Ferro", "Outros Materiais"])
            cat = "Material"
            
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="0,00")
        pagto = st.selectbox("Pagamento", ["Dinheiro", "PIX", "Cartão de Crédito", "Boleto"])
        
        if st.form_submit_button("SALVAR"):
            if val:
                v_final = val if tipo=="Receita" else -val
                add_row(DB_FINANCEIRO, {"Data": datetime.now(), "Categoria": cat, "Descricao": desc, "Valor": v_final, "Entidade": "Geral", "Metodo_Pagto": pagto}, COLS_FIN)
                st.toast("Sucesso!")
    barra_nav('menu_fin')

def tela_cartoes():
    st.title("Cartões de Crédito")
    df = load_data(DB_FINANCEIRO, COLS_FIN)
    if df.empty: st.info("Sem dados."); barra_nav('inicio'); return
        
    credito = df[(df["Metodo_Pagto"] == "Cartão de Crédito") & (df["Valor"] < 0)]
    total = abs(credito["Valor"].sum())
    st.metric("Fatura Acumulada", format_brl(total))
    
    if not credito.empty:
        st.write("---")
        credito['idx_real'] = credito.index
        for i, row in credito.iterrows():
            idx = row['idx_real']
            c1, c2 = st.columns([4, 1])
            with c1:
                st.write(f"**{row['Descricao']}** | {format_brl(row['Valor'])}")
                st.caption(format_data_visual(row['Data']))
            with c2:
                if st.button("🗑️", key=f"del_card_{idx}"):
                    excluir_por_index(DB_FINANCEIRO, idx, COLS_FIN)
                    st.rerun()
            st.divider()
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
    elif tela == 'fin_receita': tela_movimento("Receita")
    elif tela == 'fin_despesa': tela_movimento("Despesa")
    elif tela == 'menu_cartao': tela_cartoes()

if __name__ == "__main__":
    main()
