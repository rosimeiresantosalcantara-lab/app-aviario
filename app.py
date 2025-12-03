import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gestor Aviário Gold", layout="centered", page_icon="🚜")

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
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        color: #212529;
    }
    .stButton>button:hover { border-color: #0d6efd; color: #0d6efd; }
    
    /* Destaque Vermelho para botões de perigo */
    .botao-perigo { color: red; border-color: red; }
    
    /* Métricas Grandes */
    [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; color: #2c3e50; }
    
    /* Esconder menu padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. FERRAMENTAS (Utils) ---

# Função Mágica para R$ Brasileiro
def format_brl(valor):
    if valor is None: return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Gerenciamento de Arquivos
DB_FUNC = 'db_funcionarios_v9.csv'
DB_VEICULOS = 'db_veiculos_v9.csv'
DB_MOVIMENTOS = 'db_financeiro_v9.csv'
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

# --- 3. NAVEGAÇÃO ---
if 'tela' not in st.session_state: st.session_state['tela'] = 'inicio'
if 'hist_voltar' not in st.session_state: st.session_state['hist_voltar'] = 'inicio'

def ir_para(tela, voltar_para='inicio'):
    st.session_state['hist_voltar'] = voltar_para
    st.session_state['tela'] = tela
    st.rerun()

def barra_navegacao(destino_voltar):
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ VOLTAR"): ir_para(destino_voltar)
    with c2:
        if st.button("🏠 MENU PRINCIPAL"): ir_para('inicio')

# ================= TELA 1: HOME (DASHBOARD) =================
def tela_inicio():
    st.title("🚜 Painel de Controle")
    
    # Cálculos Globais
    df_mov = load_data(DB_MOVIMENTOS, ["Valor"])
    saldo = df_mov["Valor"].sum() if not df_mov.empty else 0.0
    
    df_obra = load_data(DB_OBRA, ["Valor_Total"])
    total_contrato = float(df_obra["Valor_Total"].iloc[0]) if not df_obra.empty else 0.0
    
    recebido = df_mov[df_mov["Valor"] > 0]["Valor"].sum() if not df_mov.empty else 0.0
    falta_receber = total_contrato - recebido
    
    # Exibição Formatada
    c1, c2 = st.columns(2)
    c1.metric("Caixa Atual", format_brl(saldo))
    c2.metric("A Receber (Contrato)", format_brl(falta_receber))
    
    st.divider()
    st.subheader("Acesso Rápido")
    
    if st.button("👷 GESTÃO DE EQUIPE"): ir_para('menu_equipe', 'inicio')
    if st.button("🚛 FROTA E VEÍCULOS"): ir_para('menu_frota', 'inicio')
    if st.button("💰 FINANCEIRO GERAL"): ir_para('menu_financeiro', 'inicio')
    if st.button("⚙️ VALOR DO CONTRATO"): ir_para('config_obra', 'inicio')

# ================= TELA 2: EQUIPE =================
def tela_equipe():
    st.title("👷 Equipe")
    
    if st.button("➕ CADASTRAR NOVO FUNCIONÁRIO"): ir_para('cad_func', 'menu_equipe')
    
    df = load_data(DB_FUNC, ["Nome", "Funcao", "Valor_Diaria", "Data_Inicio"])
    
    if df.empty:
        st.info("Nenhum cadastro.")
        barra_navegacao('inicio')
        return

    st.write("Selecione para ver detalhes, pagar ou editar:")
    func_selecionado = st.selectbox("Colaborador:", df["Nome"].unique())
    st.session_state['func_atual'] = func_selecionado
    
    # Recupera dados
    dados = df[df["Nome"] == func_selecionado].iloc[0]
    
    # Cálculo Acumulado do Funcionário
    df_fin = load_data(DB_MOVIMENTOS, ["Descricao", "Valor"])
    # Filtra pagamentos onde a descrição contem o nome
    filtro = df_fin[df_fin["Descricao"].str.contains(func_selecionado, na=False)]
    total_pago = abs(filtro[filtro["Valor"] < 0]["Valor"].sum())
    
    st.info(f"**{dados['Funcao']}** | Diária: {format_brl(dados['Valor_Diaria'])} | Início: {dados['Data_Inicio']}")
    st.caption(f"💰 Total já pago a este funcionário na obra: {format_brl(total_pago)}")
    
    # Ações
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏰ PONTO"): ir_para('acao_ponto', 'menu_equipe')
        if st.button("💸 VALE"): ir_para('acao_vale', 'menu_equipe')
    with c2:
        if st.button("✅ PAGAMENTO"): ir_para('acao_pgto', 'menu_equipe')
        if st.button("📝 FALTAS"): ir_para('acao_obs', 'menu_equipe')

    # Área de Edição/Exclusão
    with st.expander(f"✏️ Editar ou Excluir {func_selecionado}"):
        st.write("Correção de Cadastro:")
        with st.form("edit_func"):
            novo_nome = st.text_input("Nome", value=dados['Nome'])
            nova_funcao = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Cozinheira", "Outro"], index=0)
            novo_valor = st.number_input("Valor Diária", value=float(dados['Valor_Diaria']))
            if st.form_submit_button("SALVAR CORREÇÃO"):
                # Atualiza linha
                df.loc[df["Nome"] == func_selecionado, ["Nome", "Funcao", "Valor_Diaria"]] = [novo_nome, nova_funcao, novo_valor]
                save_full(DB_FUNC, df)
                st.success("Atualizado!")
                st.rerun()
        
        st.divider()
        if st.button("🗑️ EXCLUIR CADASTRO DEFINITIVAMENTE"):
            df = df[df["Nome"] != func_selecionado]
            save_full(DB_FUNC, df)
            st.success("Excluído!")
            st.rerun()

    barra_navegacao('inicio')

def tela_cad_func():
    st.header("Novo Cadastro")
    st.write("Preencha os dados abaixo:")
    with st.form("form_cad_func"):
        nome = st.text_input("Nome Completo")
        dt_inicio = st.date_input("Data de Início", datetime.now())
        func = st.selectbox("Função", ["Pedreiro", "Servente", "Mestre", "Cozinheira", "Motorista"])
        
        # CAMPO LIMPO (value=None)
        val = st.number_input("Valor Diária (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
        
        if st.form_submit_button("💾 SALVAR"):
            if nome and val is not None:
                add_row(DB_FUNC, {"Nome": nome, "Funcao": func, "Valor_Diaria": val, "Data_Inicio": dt_inicio})
                st.success("Cadastrado!")
                ir_para('menu_equipe')
            else:
                st.error("Nome e Valor são obrigatórios.")
    barra_navegacao('menu_equipe')

# --- Ações Genéricas Equipe ---
def tela_acoes_equipe(tipo):
    nome = st.session_state['func_atual']
    st.header(f"{tipo}: {nome}")
    
    if tipo == "Ponto":
        dt = st.date_input("Data", datetime.now())
        status = st.radio("Presença", ["Dia Completo", "Meio Dia", "Falta"])
        if st.button("CONFIRMAR"):
            add_row(DB_MOVIMENTOS, {"Data": dt, "Categoria": "Ponto", "Descricao": f"Ponto {nome} ({status})", "Valor": 0})
            st.success("Ponto registrado!")
            ir_para('menu_equipe')

    elif tipo in ["Vale", "Pagamento"]:
        # CAMPO LIMPO
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
        obs = st.text_input("Obs (Opcional)") if tipo == "Vale" else "Acerto Final"
        
        if st.button("CONFIRMAR SAÍDA"):
            if val is not None:
                desc = f"{tipo} {nome}" + (f" ({obs})" if obs else "")
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Mão de Obra", "Descricao": desc, "Valor": -val})
                st.success("Lançado no financeiro!")
                ir_para('menu_equipe')
            else:
                st.warning("Digite o valor.")
                
    elif tipo == "Faltas":
        motivo = st.text_area("Motivo da Ocorrência")
        if st.button("SALVAR"):
            add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Ocorrência", "Descricao": f"Obs {nome}: {motivo}", "Valor": 0})
            st.success("Anotado.")
            ir_para('menu_equipe')
            
    barra_navegacao('menu_equipe')

# ================= TELA 3: FROTA =================
def tela_frota():
    st.title("🚛 Frota")
    
    if st.button("➕ CADASTRAR VEÍCULO"): ir_para('cad_veiculo', 'menu_frota')
    
    df = load_data(DB_VEICULOS, ["Veiculo", "Placa", "Km_Inicial"])
    if df.empty:
        st.warning("Nenhum veículo.")
        barra_navegacao('inicio')
        return

    veic = st.selectbox("Selecione o Veículo:", df["Veiculo"].unique())
    st.session_state['veiculo_atual'] = veic
    
    # Dados e Acumulado
    dados = df[df["Veiculo"] == veic].iloc[0]
    
    df_fin = load_data(DB_MOVIMENTOS, ["Descricao", "Valor"])
    filtro = df_fin[df_fin["Descricao"].str.contains(veic, na=False)]
    total_gasto = abs(filtro[filtro["Valor"] < 0]["Valor"].sum())
    
    st.info(f"Placa: {dados['Placa']} | KM Inicial: {dados['Km_Inicial']}")
    st.caption(f"💸 Custo total acumulado com este veículo: {format_brl(total_gasto)}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⛽ ABASTECER"): ir_para('acao_abastecer', 'menu_frota')
    with c2:
        if st.button("🔧 MANUTENÇÃO"): ir_para('acao_manutencao', 'menu_frota')

    # Editar/Excluir Veículo
    with st.expander(f"✏️ Editar {veic}"):
        with st.form("edit_veic"):
            n_mod = st.text_input("Modelo", value=dados['Veiculo'])
            n_placa = st.text_input("Placa", value=dados['Placa'])
            if st.form_submit_button("SALVAR CORREÇÃO"):
                df.loc[df["Veiculo"] == veic, ["Veiculo", "Placa"]] = [n_mod, n_placa]
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
        modelo = st.text_input("Modelo (Ex: Hilux)")
        placa = st.text_input("Placa")
        km = st.number_input("KM Atual", min_value=0, value=None, placeholder="Digite o KM...")
        if st.form_submit_button("SALVAR"):
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
        litros = st.number_input("Litros", min_value=0.0, value=None, placeholder="Litros...")
        val = st.number_input("Valor Total (R$)", min_value=0.0, value=None, placeholder="Valor pago...")
        
        if st.button("SALVAR"):
            if val is not None:
                desc = f"Abastec. {veic} ({litros}L | KM {km})"
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Combustível", "Descricao": desc, "Valor": -val})
                st.success("Salvo!")
                ir_para('menu_frota')
                
    elif tipo == "Manutenção":
        item = st.text_input("O que fez? (Ex: Pneu)")
        val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="Valor...")
        if st.button("SALVAR"):
            if val is not None:
                add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": "Manutenção", "Descricao": f"Manut. {veic} - {item}", "Valor": -val})
                st.success("Salvo!")
                ir_para('menu_frota')
                
    barra_navegacao('menu_frota')

# ================= TELA 4: FINANCEIRO =================
def tela_financeiro():
    st.title("💰 Financeiro")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ ENTRADA (RECEITA)"): ir_para('fin_entrada', 'menu_financeiro')
    with c2:
        if st.button("➖ SAÍDA (GASTO GERAL)"): ir_para('fin_saida', 'menu_financeiro')
        
    st.divider()
    st.subheader("📜 Extrato e Correções")
    
    df = load_data(DB_MOVIMENTOS, ["Data", "Categoria", "Descricao", "Valor"])
    
    if not df.empty:
        # Modo de edição
        if 'edit_idx' not in st.session_state: st.session_state['edit_idx'] = -1
        
        # Mostra lista inversa (mais recente primeiro)
        df['idx_real'] = df.index
        df_show = df.sort_index(ascending=False).head(20) # Ultimos 20
        
        for i, row in df_show.iterrows():
            idx_real = row['idx_real']
            
            # Layout Visual
            cor = "green" if row['Valor'] > 0 else "red"
            c_txt, c_act = st.columns([3, 1])
            
            with c_txt:
                st.markdown(f"**{row['Descricao']}**")
                st.caption(f"{row['Data']} | {row['Categoria']}")
                st.markdown(f"<span style='color:{cor}; font-weight:bold'>{format_brl(row['Valor'])}</span>", unsafe_allow_html=True)
                
            with c_act:
                # Botão Excluir
                if st.button("🗑️", key=f"del_{idx_real}"):
                    df = df.drop(idx_real)
                    save_full(DB_MOVIMENTOS, df)
                    st.rerun()
                # Botão Editar (Abre form abaixo)
                if st.button("✏️", key=f"ed_{idx_real}"):
                    st.session_state['edit_idx'] = idx_real
                    st.rerun()
            
            # Formulário de Edição (Só aparece se clicou no lápis)
            if st.session_state['edit_idx'] == idx_real:
                with st.container():
                    st.markdown("---")
                    st.write(f"**Editando item {idx_real}:**")
                    with st.form(f"form_edit_{idx_real}"):
                        n_desc = st.text_input("Descrição", value=row['Descricao'])
                        n_val = st.number_input("Valor", value=float(row['Valor']))
                        if st.form_submit_button("SALVAR ALTERAÇÃO"):
                            df.at[idx_real, "Descricao"] = n_desc
                            df.at[idx_real, "Valor"] = n_val
                            save_full(DB_MOVIMENTOS, df)
                            st.session_state['edit_idx'] = -1 # Fecha edição
                            st.rerun()
                    st.markdown("---")
                    
            st.divider()
    
    barra_navegacao('inicio')

def tela_fin_lancamento(tipo):
    st.header(f"Lançar {tipo}")
    desc = st.text_input("Descrição")
    val = st.number_input("Valor (R$)", min_value=0.0, value=None, placeholder="Digite o valor...")
    
    if st.button("SALVAR"):
        if val is not None:
            cat = "Receita" if tipo == "Entrada" else "Material/Outros"
            val_final = val if tipo == "Entrada" else -val
            add_row(DB_MOVIMENTOS, {"Data": datetime.now(), "Categoria": cat, "Descricao": desc, "Valor": val_final})
            st.success("Salvo!")
            ir_para('menu_financeiro')
            
    barra_navegacao('menu_financeiro')

def tela_config_obra():
    st.header("Configuração")
    df = load_data(DB_OBRA, ["Valor_Total"])
    atual = float(df["Valor_Total"].iloc[0]) if not df.empty else 0.0
    
    st.metric("Valor Atual do Contrato", format_brl(atual))
    
    novo = st.number_input("Definir Novo Valor", value=None, placeholder="Digite valor total...")
    if st.button("ATUALIZAR"):
        if novo is not None:
            pd.DataFrame([{"Valor_Total": novo}]).to_csv(DB_OBRA, index=False)
            st.success("Atualizado!")
            st.rerun()
            
    barra_navegacao('inicio')

# ================= ROTEADOR =================
def main():
    tela = st.session_state['tela']
    
    if tela == 'inicio': tela_inicio()
    
    # Equipe
    elif tela == 'menu_equipe': tela_equipe()
    elif tela == 'cad_func': tela_cad_func()
    elif tela == 'acao_ponto': tela_acoes_equipe("Ponto")
    elif tela == 'acao_vale': tela_acoes_equipe("Vale")
    elif tela == 'acao_pgto': tela_acoes_equipe("Pagamento")
    elif tela == 'acao_obs': tela_acoes_equipe("Faltas")
    
    # Frota
    elif tela == 'menu_frota': tela_frota()
    elif tela == 'cad_veiculo': tela_cad_veiculo()
    elif tela == 'acao_abastecer': tela_acao_frota("Abastecer")
    elif tela == 'acao_manutencao': tela_acao_frota("Manutenção")
    
    # Financeiro
    elif tela == 'menu_financeiro': tela_financeiro()
    elif tela == 'fin_entrada': tela_fin_lancamento("Entrada")
    elif tela == 'fin_saida': tela_fin_lancamento("Saída")
    elif tela == 'config_obra': tela_config_obra()

if __name__ == "__main__":
    main()
