import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL E CSS ---
st.set_page_config(page_title="Gestor Aviário Platinum", layout="centered", page_icon="🚜")

st.markdown("""
    <style>
    /* Botões Grandes, Limpos e Fáceis de Tocar */
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
    
    /* Cores Específicas para Navegação */
    div[data-testid="column"] > div > div > div > button {
        border-left: 4px solid transparent; 
    }
    
    /* Títulos e Métricas */
    h1 { color: #2c3e50; font-size: 2rem; }
    [data-testid="stMetricValue"] { font-size: 1.7rem; color: #2c3e50; }
    
    /* Ocultar menu técnico do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNÇÕES DE UTILIDADE (A Mágica acontece aqui) ---

def format_brl(valor):
    """Transforma números em Dinheiro Brasileiro (R$ 1.000,00)"""
    if valor is None: return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_data_br(data_str):
    """Transforma 2025-12-25 em 25/12/2025"""
    try:
        if isinstance(data_str, str):
            data_obj = datetime.strptime(data_str, '%Y-%m-%d')
            return data_obj.strftime('%d/%m/%Y')
        return data_str.strftime('%d/%m/%Y')
    except:
        return data_str

# Gerenciamento de Arquivos CSV (Banco de Dados)
DB_FUNC = 'db_funcionarios_v10.csv'
DB_VEICULOS = 'db_veiculos_v10.csv'
DB_MOVIMENTOS = 'db_financeiro_v10.csv'
DB_OBRA = 'db_obra_config.csv'

def load_data(arquivo, colunas):
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas).to_csv(arquivo, index=False)
    return pd.read_csv(arquivo)

def save_full(arquivo, df):
    df.to_csv(arquivo, index=False)

def add_row(arquivo, row_data):
    df = load_data(arquivo, list(row_data.keys()))
    df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    df.to_csv(arquivo, index=False)

# --- 3. NAVEGAÇÃO SEGURA ---
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

# ================= TELA 1: HOME (DASHBOARD) =================
def tela_inicio():
    st.title("🚜 Painel Aviário")
    
    # Cálculos Globais
    df_mov = load_data(DB_MOVIMENTOS, ["Valor"])
    saldo = df_mov["Valor"].sum() if not df_mov.empty else 0.0
    
    df_obra = load_data(DB_OBRA, ["Valor_Total"])
    total_contrato = float(df_obra["Valor_Total"].iloc[0]) if not df_obra.empty else 0.0
    
    recebido = df_mov[df_mov["Valor"] > 0]["Valor"].sum() if not df_mov.empty else 0.0
    falta_receber = total_contrato - recebido
    
    # Exibição
    c1, c2 = st.columns(2)
    c1.metric("Caixa Disponível", format_brl(saldo))
    c2.metric("Falta Receber", format_brl(falta_receber))
    
    st.write("---")
    st.subheader("Menu Principal")
    
    if st.button("👷 GESTÃO DE EQUIPE"): ir_para('menu_equipe', 'inicio')
    if st.button("🚛 FROTA & VEÍCULOS"): ir_para('menu_frota', 'inicio')
    if st.button("💰 FINANCEIRO GERAL"): ir_para('menu_financeiro', 'inicio')
    if st.button("⚙️ CONFIGURAR CONTRATO"): ir_para('config_obra', 'inicio')

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("👷 Equipe")
    
    if st.button("➕ CADASTRAR NOVO FUNCIONÁRIO"): ir_para('cad_func', 'menu_equipe')
    
    df = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"])
    
    if df.empty:
        st.warning("Nenhum funcionário cadastrado.")
        barra_navegacao('inicio')
        return

    st.markdown("### Gerenciar Colaborador")
    func_selecionado = st.selectbox("Selecione:", df["Nome"].unique())
    st.session_state['func_atual'] = func_selecionado
    
    # Dados
    dados = df[df["Nome"] == func_selecionado].iloc[0]
    
    # Cálculo Inteligente (Ignora maiúsculas/minúsculas)
    df_fin = load_data(DB_MOVIMENTOS, ["Descricao", "Valor"])
    filtro = df_fin[df_fin["Descricao"].str.contains(func_selecionado, case=False, na=False)]
    total_pago = abs(filtro[filtro["Valor"] < 0]["Valor"].sum())
    
    # Cartão de Informação
    st.info(
        f"**Cargo:** {dados['Funcao']}\n\n"
        f"**Diária:** {format_brl(dados['Valor_Diaria'])}\n\n"
        f"**Total Pago na Obra:** {format_brl(total_pago)}"
    )
    
    # Ações
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
        if st.button("💸 VALE"): ir_para('acao_vale', 'menu_equipe')
    with c2:
        if st.button("✅ PAGAMENTO"): ir_para('acao_pgto', 'menu_equipe')
        if st.button("📝 FALTAS/OBS"): ir_para('acao_obs', 'menu_equipe')

    # Edição
    with st.expander(f"🛠️ Editar Cadastro de {func_selecionado}"):
        with st.form("edit_func"):
            n_nome = st.text_input("Corrigir Nome", value=dados['Nome'])
            n_funcao = st.selectbox("Corrigir Função", ["Pedreiro", "Servente", "Mestre", "Cozinheira", "Outro"])
            n_valor = st.number_input("Corrigir Diária", value=float(dados['Valor_Diaria']))
            if st.form_submit_button("SALVAR ALTERAÇÕES"):
                df.loc[df["Nome"] == func_selecionado, ["Nome", "Funcao", "Valor_Diaria"]] = [n_nome, n_funcao, n_valor]
                save_full(DB_FUNC, df)
                st.success("Atualizado!")
                st.rerun()
        
        st.write("")
        if st.button("🗑️ EXCLUIR ESTE FUNCIONÁRIO"):
            df = df[df["Nome"] != func_selecionado]
            save_full(DB_FUNC, df)
            st.warning("Funcionário excluído.")
            st.rerun()

    barra_navegacao('inicio')

def tela_cad_func():
    st.header("Novo Cadastro")
    with st.form("form_cad_func"):
        nome = st.text_input("Nome Completo")
        dt_inicio = st.date_input("Data de Início", datetime.now())
        func = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Cozinheira", "Motorista"])
        
        # Campo vazio para não precisar apagar o zero
        val = st.number_input("Valor Diária (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
        
        if st.form_submit_button("💾 SALVAR"):
            if nome and val is not None:
                add_row(DB_FUNC, {"Nome": nome, "Funcao": func, "Valor_Diaria": val, "Data_Inicio": dt_inicio})
                st.success("Cadastrado!")
                ir_para('menu_equipe')
            else:
                st.error("Preencha Nome e Valor.")
    barra_navegacao('menu_equipe')

# --- Ações Genéricas Equipe ---
def tela_acoes_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    if tipo == "Ponto":
        dt = st.date_input("Data", datetime.now())
        status = st.radio("Selecione:", ["Dia Completo", "Meio Dia", "Falta"])
        if st.button("CONFIRMAR PONTO"):
            # Salva histórico visual
            add_row(DB_MOVIMENTOS, {"Data": dt, "Categoria": "Ponto", "Descricao": f"Ponto {nome} ({status})", "Valor": 0})
            st.success("Ponto registrado!")
            ir_para('menu_equipe')

    elif tipo in ["Vale", "Pagamento"]:
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
        obs = st.text_input("Obs (Opcional)") if tipo == "Vale" else "Acerto Final"
        
        if st.button("CONFIRMAR SAÍDA DE CAIXA"):
            if val is not None:
                desc = f"{tipo} {nome}" + (f" ({obs})" if obs else "")
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Mão de Obra", "Descricao": desc, "Valor": -val})
                st.success("Lançado!")
                ir_para('menu_equipe')
            else:
                st.warning("Digite o valor.")
                
    elif tipo == "Faltas":
        motivo = st.text_area("Descreva o motivo:")
        if st.button("SALVAR"):
            add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Ocorrência", "Descricao": f"Obs {nome}: {motivo}", "Valor": 0})
            st.success("Salvo.")
            ir_para('menu_equipe')
            
    barra_navegacao('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("🚛 Frota")
    
    if st.button("➕ CADASTRAR NOVO VEÍCULO"): ir_para('cad_veiculo', 'menu_frota')
    
    df = load_data(DB_VEICULOS, ["Veiculo", "Placa", "Km_Inicial"])
    if df.empty:
        st.warning("Nenhum veículo cadastrado.")
        barra_navegacao('inicio')
        return

    st.markdown("### Selecionar Veículo")
    veic = st.selectbox("Veículo:", df["Veiculo"].unique())
    st.session_state['veiculo_atual'] = veic
    
    # Dados
    dados = df[df["Veiculo"] == veic].iloc[0]
    
    # Acumulado
    df_fin = load_data(DB_MOVIMENTOS, ["Descricao", "Valor"])
    filtro = df_fin[df_fin["Descricao"].str.contains(veic, case=False, na=False)]
    total_gasto = abs(filtro[filtro["Valor"] < 0]["Valor"].sum())
    
    st.info(f"**Veículo:** {dados['Veiculo']} | **Placa:** {dados['Placa']}\n\n💰 **Gasto Total:** {format_brl(total_gasto)}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⛽ ABASTECER"): ir_para('acao_abastecer', 'menu_frota')
    with c2:
        if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manutencao', 'menu_frota')

    # Edição Veículo
    with st.expander(f"🛠️ Editar {veic}"):
        with st.form("edit_veic"):
            n_mod = st.text_input("Modelo", value=dados['Veiculo'])
            n_placa = st.text_input("Placa", value=dados['Placa'])
            n_km = st.number_input("KM Inicial", value=int(dados['Km_Inicial']))
            if st.form_submit_button("SALVAR ALTERAÇÕES"):
                df.loc[df["Veiculo"] == veic, ["Veiculo", "Placa", "Km_Inicial"]] = [n_mod, n_placa, n_km]
                save_full(DB_VEICULOS, df)
                st.success("Salvo!")
                st.rerun()
                
        if st.button("🗑️ EXCLUIR VEÍCULO"):
            df = df[df["Veiculo"] != veic]
            save_full(DB_VEICULOS, df)
            st.rerun()

    barra_navegacao('inicio')

def tela_cad_veiculo():
    st.header("Novo Veículo")
    with st.form("cad_veic"):
        modelo = st.text_input("Modelo (Ex: Hilux, Trator)")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0, value=None, placeholder="Digite KM...")
        if st.form_submit_button("💾 SALVAR"):
            if modelo:
                nome_f = f"{modelo} {placa}"
                add_row(DB_VEICULOS, {"Veiculo": nome_f, "Placa": placa, "Km_Inicial": km if km else 0})
                st.success("Salvo!")
                ir_para('menu_frota')
    barra_navegacao('menu_frota')

def tela_acao_frota(tipo):
    veic = st.session_state['veiculo_atual']
    st.header(f"{tipo}: {veic}")
    
    if tipo == "Abastecer":
        km = st.number_input("KM no Painel", min_value=0, value=None, placeholder="KM atual...")
        litros = st.number_input("Litros", min_value=0.0, value=None, placeholder="Qtd Litros...")
        val = st.number_input("Valor Total (R$)", min_value=0.0, value=None, placeholder="Valor pago...")
        
        if st.button("CONFIRMAR"):
            if val is not None:
                desc = f"Abastec. {veic} ({litros}L | KM {km})"
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Combustível", "Descricao": desc, "Valor": -val})
                st.success("Salvo!")
                ir_para('menu_frota')
            else: st.warning("Digite o valor.")
                
    elif tipo == "Manutenção":
        item = st.text_input("O que foi feito? (Ex: Pneu, Óleo)")
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="Valor total...")
        if st.button("CONFIRMAR"):
            if val is not None:
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Manutenção", "Descricao": f"Manut. {veic} - {item}", "Valor": -val})
                st.success("Salvo!")
                ir_para('menu_frota')
            else: st.warning("Digite o valor.")
                
    barra_navegacao('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_financeiro():
    st.title("💰 Financeiro")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ ENTRADA (RECEITA)"): ir_para('fin_entrada', 'menu_financeiro')
    with c2:
        if st.button("➖ SAÍDA (GASTO)"): ir_para('fin_saida', 'menu_financeiro')
        
    st.write("---")
    st.subheader("📜 Extrato de Movimentações")
    st.caption("Você pode editar ou excluir lançamentos abaixo.")
    
    df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
    
    if not df.empty:
        if 'edit_idx' not in st.session_state: st.session_state['edit_idx'] = -1
        
        # Ordena: Mais recente primeiro
        df['idx_real'] = df.index
        df_show = df.sort_index(ascending=False).head(30)
        
        for i, row in df_show.iterrows():
            idx_real = row['idx_real']
            
            # Formatação Visual da Linha
            cor = "green" if row['Valor'] > 0 else "#e74c3c"
            data_fmt = format_data_br(row['Data'])
            
            # Layout em Colunas
            col_txt, col_act = st.columns([3, 1])
            
            with col_txt:
                st.markdown(f"**{row['Descricao']}**")
                st.caption(f"📅 {data_fmt} | 🏷️ {row['Categoria']}")
                st.markdown(f"<span style='color:{cor}; font-weight:bold; font-size:1.1rem'>{format_brl(row['Valor'])}</span>", unsafe_allow_html=True)
                
            with col_act:
                # Botões compactos
                c_edit, c_del = st.columns(2)
                with c_edit:
                    if st.button("✏️", key=f"ed_{idx_real}"):
                        st.session_state['edit_idx'] = idx_real
                        st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"del_{idx_real}"):
                        df = df.drop(idx_real)
                        save_full(DB_MOVIMENTOS, df)
                        st.rerun()
            
            # Formulário de Edição (Abre ao clicar no lápis)
            if st.session_state['edit_idx'] == idx_real:
                with st.container():
                    st.info("Editando item acima:")
                    with st.form(f"form_edit_{idx_real}"):
                        n_desc = st.text_input("Descrição", value=row['Descricao'])
                        # Permite qualquer valor (positivo ou negativo)
                        n_val = st.number_input("Valor", value=float(row['Valor']))
                        
                        if st.form_submit_button("💾 SALVAR CORREÇÃO"):
                            df.at[idx_real, "Descricao"] = n_desc
                            df.at[idx_real, "Valor"] = n_val
                            save_full(DB_MOVIMENTOS, df)
                            st.session_state['edit_idx'] = -1
                            st.success("Corrigido!")
                            st.rerun()
            
            st.divider()
    
    barra_navegacao('inicio')

def tela_fin_lancamento(tipo):
    st.header(f"Lançar {tipo}")
    desc = st.text_input("Descrição (Ex: Cimento, Pagamento)")
    val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
    
    if st.button("CONFIRMAR"):
        if val is not None:
            cat = "Receita" if tipo == "Entrada" else "Material/Outros"
            val_final = val if tipo == "Entrada" else -val
            add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": cat, "Descricao": desc, "Valor": val_final})
            st.success("Salvo!")
            ir_para('menu_financeiro')
        else:
            st.warning("Preencha o valor.")
            
    barra_navegacao('menu_financeiro')

def tela_config_obra():
    st.header("Configuração")
    df = load_data(DB_OBRA, ["Valor_Total"])
    atual = float(df["Valor_Total"].iloc[0]) if not df.empty else 0.0
    
    st.metric("Valor Atual do Contrato", format_brl(atual))
    
    novo = st.number_input("Novo Valor Total", value=None, placeholder="Digite o valor total da obra...")
    if st.button("ATUALIZAR CONTRATO"):
        if novo is not None:
            pd.DataFrame([{"Valor_Total": novo}]).to_csv(DB_OBRA, index=False)
            st.success("Atualizado!")
            st.rerun()
            
    barra_navegacao('inicio')

# ================= ROTEADOR =================
def main():
    tela = st.session_state['tela']
    
    # Roteamento Simples
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
