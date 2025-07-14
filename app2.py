import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import uuid
import os
from utils.pdf_export import mostrar_comprovante_pedido  # Certifique-se do caminho correto

# ========================
# CONFIGURAÇÃO E CSS
# ========================
st.set_page_config(page_title="Marmita Fácil", layout="centered")

st.markdown("""
    <style>
    body, .main, .block-container, .stApp { background: #18191A !important; }
    .stSidebar, .css-18ni7ap.e8zbici2 { background: #191C1F !important; }
    .stButton > button {
        background: linear-gradient(90deg, #ED212B 40%, #FFC300 100%);
        color: #fff !important;
        border-radius: 18px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        margin: 10px 0;
        border: none;
        transition: 0.2s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.18);
    }
    .stTextInput>div>div>input, .stTextArea textarea, .stNumberInput input, .stDateInput input {
        background: transparent !important;
        color: #fff !important;
        border-radius: 10px !important;
        border: 1.5px solid #ED212B !important;
    }
    .stDataFrame, .stTable, .stMarkdown {
        background: transparent !important;
        color: #fff !important;
    }
    .stImage img {
        border-radius: 14px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        object-fit: cover;
        background: #eee;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #fff !important;
        font-weight: bold !important;
    }
    .card-marmita {
        background: #23272B;
        border-radius: 22px;
        box-shadow: 0 8px 36px rgba(50,50,50,0.12);
        margin-bottom: 32px;
        padding: 22px;
        color: #fff;
        text-align: center;
        transition: box-shadow 0.2s;
    }
    .card-marmita:hover {
        box-shadow: 0 12px 36px rgba(255, 195, 0, 0.18);
        border: 2px solid #FFC300;
    }
    </style>
""", unsafe_allow_html=True)

# ========================
# BANCO DE DADOS SQLITE
# ========================
DB_PATH = "marmita_facil.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS marmitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            estoque INTEGER NOT NULL,
            saldo_atual INTEGER NOT NULL,
            data_cadastro TEXT,
            imagem TEXT
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            nome TEXT,
            matricula TEXT,
            unidade TEXT,
            destino TEXT,
            lider TEXT,
            centro_custo TEXT,
            marmita_id INTEGER,
            marmita_nome TEXT,
            quantidade INTEGER,
            observacoes TEXT,
            status TEXT,
            FOREIGN KEY (marmita_id) REFERENCES marmitas(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datahora TEXT,
            pedido_id INTEGER,
            status_antigo TEXT,
            status_novo TEXT,
            usuario TEXT
        );
    """)
    conn.commit()
    conn.close()

init_db()

# ========================
# LOGO (sempre público)
# ========================
def exibe_logo_topo():
    url = "https://marmita-facil-dados.s3.us-east-2.amazonaws.com/imagens/logo-marmitafacil.png"
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(url, use_container_width=True)

# ========================
# SIDEBAR/MENU
# ========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

menu_itens = {
    "Fazer Pedido": "📝 Fazer Pedido",
    "Histórico de Pedidos": "📋 Histórico de Pedidos",
}
if st.session_state.autenticado:
    menu_itens.update({
        "Gestão de Pedidos": "🕒 Gestão de Pedidos",
        "Histórico de Alterações": "📝 Histórico de Alterações",
        "Administração": "👨‍🍳 Administração",
        "Cadastrar Usuário": "👤 Cadastrar Usuário",
        "Logout": "🚪 Logout"
    })
else:
    menu_itens["Login Admin"] = "🔐 Login Admin"

menu = st.sidebar.selectbox(
    "Menu",
    list(menu_itens.keys()),
    format_func=lambda k: menu_itens[k],
    key="menu_selectbox"
)

# ========================
# FUNÇÕES AUXILIARES BANCO
# ========================
def get_usuarios():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM usuarios", conn)
    conn.close()
    return df

def add_usuario(nome, login, senha):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (nome, login, senha) VALUES (?, ?, ?)", (nome, login, senha))
    conn.commit()
    conn.close()

def get_marmitas():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM marmitas", conn)
    conn.close()
    return df

def add_marmita(nome, estoque, imagem, data_cadastro=None):
    if not data_cadastro:
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO marmitas (nome, estoque, saldo_atual, data_cadastro, imagem) VALUES (?, ?, ?, ?, ?)",
        (nome, estoque, estoque, data_cadastro, imagem)
    )
    conn.commit()
    conn.close()

def atualizar_marmita(id_marmita, estoque, imagem=None):
    conn = get_conn()
    c = conn.cursor()
    if imagem:
        c.execute(
            "UPDATE marmitas SET estoque=?, saldo_atual=?, imagem=? WHERE id=?",
            (estoque, estoque, imagem, id_marmita)
        )
    else:
        c.execute(
            "UPDATE marmitas SET estoque=?, saldo_atual=? WHERE id=?",
            (estoque, estoque, id_marmita)
        )
    conn.commit()
    conn.close()

def get_pedidos():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM pedidos", conn)
    conn.close()
    return df

def add_pedido(pedido):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO pedidos 
        (data, nome, matricula, unidade, destino, lider, centro_custo, marmita_id, marmita_nome, quantidade, observacoes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pedido["data"], pedido["nome"], pedido["matricula"], pedido["unidade"], pedido["destino"], pedido["lider"], pedido["centro_custo"],
            pedido["marmita_id"], pedido["marmita_nome"], pedido["quantidade"], pedido["observacoes"], pedido["status"]
        )
    )
    conn.commit()
    conn.close()

def atualizar_saldo_marmita(marmita_id, quantidade):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE marmitas SET saldo_atual = saldo_atual - ? WHERE id = ?", (quantidade, marmita_id))
    conn.commit()
    conn.close()

def atualizar_status_pedidos(ids, novo_status):
    conn = get_conn()
    c = conn.cursor()
    for pedido_id in ids:
        c.execute("SELECT status FROM pedidos WHERE id=?", (pedido_id,))
        old = c.fetchone()
        if old:
            c.execute(
                "INSERT INTO historico (datahora, pedido_id, status_antigo, status_novo, usuario) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pedido_id, old[0], novo_status, st.session_state.usuario)
            )
        c.execute("UPDATE pedidos SET status=? WHERE id=?", (novo_status, pedido_id))
    conn.commit()
    conn.close()

def get_historico():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM historico", conn)
    conn.close()
    return df

def existe_usuario():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    qtd = c.fetchone()[0]
    conn.close()
    return qtd > 0

# ========================
# FUNÇÕES TELA
# ========================

# ---------- FAZER PEDIDO ----------
if menu == "Fazer Pedido":
    exibe_logo_topo()
    st.header("Faça seu pedido!")

    nome = st.text_input("Seu nome", key="nome_pedido")
    matricula = st.text_input("Sua matrícula", key="matricula_pedido")
    unidade = st.text_input("Unidade de atuação", key="unidade_pedido")
    destino = st.text_input("Local de destino da entrega", key="destino_pedido")
    lider = st.text_input("Líder", key="lider_pedido")
    centro_custo = st.text_input("Centro de custo", key="cc_pedido")

    marmitas_disponiveis = get_marmitas()
    marmitas_disponiveis = marmitas_disponiveis[marmitas_disponiveis["saldo_atual"] > 0]

    if not marmitas_disponiveis.empty:
        st.markdown("<h4 style='color:#fff;margin-top:2em;'>Escolha sua marmita:</h4>", unsafe_allow_html=True)
        n_colunas = 2 if len(marmitas_disponiveis) > 1 else 1
        if "escolha_cardapio" not in st.session_state:
            st.session_state["escolha_cardapio"] = None

        for i in range(0, len(marmitas_disponiveis), n_colunas):
            cols = st.columns(n_colunas)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(marmitas_disponiveis):
                    item = marmitas_disponiveis.iloc[idx]
                    with col:
                        st.markdown('<div class="card-marmita">', unsafe_allow_html=True)
                        if item["imagem"]:
                            st.image(item["imagem"], use_container_width=True)
                        else:
                            st.image("https://cdn-icons-png.flaticon.com/512/2921/2921827.png", width=120)
                        st.markdown(f"""
                            <h5 style='margin-bottom:5px;font-size:1.4rem;'>{item['nome']}</h5>
                            <p style='margin:0 0 4px 0;color:#eee;font-size:1.06rem;'>Estoque: {item['saldo_atual']}</p>
                        """, unsafe_allow_html=True)
                        if st.button(f"Selecionar {item['nome']}", key=f"btn_sel_{item['id']}"):
                            st.session_state["escolha_cardapio"] = idx
                        st.markdown('</div>', unsafe_allow_html=True)

        escolhido = st.session_state.get("escolha_cardapio")
        if escolhido is not None:
            selecionada = marmitas_disponiveis.iloc[escolhido]
            st.success(f"Selecionado: {selecionada['nome']}")
            quantidade = st.number_input("Quantidade", min_value=1, max_value=50, value=1, key="quantidade_pedido")
            observacoes = st.text_area("Alguma observação? (opcional)", key="obs_pedido")
            if st.button("Fazer pedido", key="btn_fazer_pedido"):
                estoque_disponivel = int(selecionada["saldo_atual"])
                if nome and estoque_disponivel >= quantidade:
                    pedido = {
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "nome": nome,
                        "matricula": str(matricula),
                        "unidade": unidade,
                        "destino": destino,
                        "lider": lider,
                        "centro_custo": centro_custo,
                        "marmita_id": selecionada["id"],
                        "marmita_nome": selecionada["nome"],
                        "quantidade": quantidade,
                        "observacoes": observacoes,
                        "status": "Recebido pela Cozinha"
                    }
                    add_pedido(pedido)
                    atualizar_saldo_marmita(selecionada["id"], quantidade)
                    st.success(f"✅ Pedido feito com sucesso, {nome}! Você pediu {quantidade} marmita(s) de {selecionada['nome']}.")
                    mostrar_comprovante_pedido(pedido)
                    st.session_state["escolha_cardapio"] = None
                else:
                    st.error("Preencha seu nome e confira o estoque disponível.")
    else:
        st.warning("⚠️ Nenhuma marmita disponível com saldo.")

# ---------- HISTÓRICO DE PEDIDOS ----------
elif menu == "Histórico de Pedidos":
    exibe_logo_topo()
    st.title("📑 Histórico de Pedidos")
    df = get_pedidos()
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"], errors='coerce')
        busca_matricula = st.text_input("Filtrar por matrícula (deixe em branco para mostrar tudo):")
        data_min = df["data"].min().date() if not df["data"].isnull().all() else datetime.now().date()
        data_max = df["data"].max().date() if not df["data"].isnull().all() else datetime.now().date()
        data_inicio = st.date_input("De:", value=data_min, key="data_inicio")
        data_fim = st.date_input("Até:", value=data_max, key="data_fim")
        filtro = (
            (df["data"] >= pd.to_datetime(data_inicio)) &
            (df["data"] <= pd.to_datetime(data_fim) + pd.Timedelta(days=1))
        )
        df_filtrado = df.loc[filtro]
        if busca_matricula:
            df_filtrado = df_filtrado[
                df_filtrado["matricula"].astype(str).str.contains(busca_matricula, case=False, na=False)
            ]
        st.dataframe(df_filtrado, use_container_width=True)
        st.success(f"{len(df_filtrado)} pedidos exibidos.")
        csv_export = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Exportar como CSV",
            data=csv_export,
            file_name="historico_pedidos.csv",
            mime="text/csv",
            key="btn_exportar_csv"
        )
    else:
        st.info("Nenhum pedido registrado ainda.")

# ---------- GESTÃO DE PEDIDOS EM MASSA ----------
elif menu == "Gestão de Pedidos":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para acessar esta tela.")
    else:
        exibe_logo_topo()
        st.title("🕒 Gestão de Pedidos - Alteração em Massa")

        df_pedidos = get_pedidos()
        status_abertos = ["Recebido pela Cozinha", "Em preparo", "Enviado"]

        pendentes = df_pedidos[df_pedidos["status"].isin(status_abertos)].copy()
        if not pendentes.empty:
            pendentes["Descrição"] = pendentes.apply(
                lambda row: f"{row['id']} | {row['nome']} | {row['marmita_nome']} | {row['quantidade']}", axis=1
            )
            opcoes = pendentes["Descrição"].tolist()

            col1, col2 = st.columns([1, 2])
            if "pedidos_selecionados" not in st.session_state:
                st.session_state["pedidos_selecionados"] = []
            with col1:
                if st.button("Selecionar todos"):
                    st.session_state["pedidos_selecionados"] = opcoes
                    st.rerun()
            with col2:
                if st.button("Limpar seleção"):
                    st.session_state["pedidos_selecionados"] = []
                    st.rerun()

            selecionados = st.multiselect(
                "Pedidos pendentes para atualizar",
                opcoes,
                default=st.session_state.get("pedidos_selecionados", [])
            )
            st.session_state["pedidos_selecionados"] = selecionados

            novo_status = st.selectbox(
                "Novo status",
                ["Recebido pela Cozinha", "Em preparo", "Enviado", "Entregue", "Cancelado"],
                key="novo_status_massa"
            )

            if st.button("Atualizar status selecionados"):
                ids = [int(x.split("|")[0].strip()) for x in selecionados]
                atualizar_status_pedidos(ids, novo_status)
                st.success(f"Status atualizado para {novo_status}!")
                st.session_state["pedidos_selecionados"] = []
                st.rerun()

            def cor_status(s):
                if s == "Entregue":
                    return "background-color: #3cb371; color: white;"
                if s == "Cancelado":
                    return "background-color: #d9534f; color: white;"
                if s in status_abertos:
                    return "background-color: #ffcc00; color: black;"
                return ""
            cols = ["id", "data", "nome", "marmita_nome", "quantidade", "status"]
            if not all(c in pendentes.columns for c in cols):
                cols = pendentes.columns
            st.dataframe(
                pendentes[cols].style.applymap(cor_status, subset=["status"]),
                use_container_width=True
            )
        else:
            st.info("Nenhum pedido pendente para alterar.")

# ---------- HISTÓRICO DE ALTERAÇÕES ----------
elif menu == "Histórico de Alterações":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para acessar esta tela.")
    else:
        st.title("📝 Histórico de Alterações de Status")
        df_hist = get_historico()
        if df_hist.empty:
            st.info("Nenhuma alteração registrada ainda.")
        else:
            busca_id = st.text_input("Filtrar por ID do Pedido (opcional):")
            busca_usuario = st.text_input("Filtrar por usuário (opcional):")
            data_min = pd.to_datetime(df_hist["datahora"]).min().date()
            data_max = pd.to_datetime(df_hist["datahora"]).max().date()
            data_inicio = st.date_input("De:", value=data_min, key="data_inicio_hist")
            data_fim = st.date_input("Até:", value=data_max, key="data_fim_hist")
            df_hist["datahora"] = pd.to_datetime(df_hist["datahora"])
            filtro = (
                (df_hist["datahora"] >= pd.to_datetime(data_inicio)) &
                (df_hist["datahora"] <= pd.to_datetime(data_fim) + pd.Timedelta(days=1))
            )
            df_filtrado = df_hist.loc[filtro]
            if busca_id:
                df_filtrado = df_filtrado[df_filtrado["pedido_id"].astype(str).str.contains(busca_id, case=False, na=False)]
            if busca_usuario:
                df_filtrado = df_filtrado[df_filtrado["usuario"].astype(str).str.contains(busca_usuario, case=False, na=False)]
            st.dataframe(df_filtrado.sort_values("datahora", ascending=False), use_container_width=True)
            st.success(f"{len(df_filtrado)} alterações exibidas.")
            csv_export = df_filtrado.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Exportar log como CSV",
                data=csv_export,
                file_name="historico_alteracoes.csv",
                mime="text/csv",
                key="btn_exportar_hist_csv"
            )

# ---------- ADMINISTRAÇÃO ----------
elif menu == "Administração":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para acessar esta tela.")
    else:
        exibe_logo_topo()
        st.title("📦 Administração de Marmitas")

        st.subheader("📋 Marmitas em Estoque com Saldo Atual")
        df_marmitas = get_marmitas()
        if df_marmitas.empty:
            st.info("Nenhuma marmita cadastrada ainda.")
        else:
            st.dataframe(df_marmitas, use_container_width=True)

        st.subheader("➕ Novo Cadastro ou Atualização de Estoque")
        nova_marmita = st.text_input("Nome da marmita", key="nome_marmita")
        novo_estoque = st.number_input("Quantidade em estoque", min_value=0, step=1, key="quantidade_marmita")
        foto_url = st.text_input("URL da foto do prato (S3, imgur, etc)", key="foto_marmita")
        if st.button("Salvar marmita", key="btn_salvar_marmita"):
            if not nova_marmita:
                st.warning("Informe o nome da marmita.")
            else:
                ja_existe = df_marmitas[df_marmitas["nome"] == nova_marmita]
                if not ja_existe.empty:
                    atualizar_marmita(ja_existe.iloc[0]["id"], novo_estoque, foto_url)
                    st.success(f"Estoque da marmita '{nova_marmita}' atualizado para {novo_estoque}.")
                else:
                    add_marmita(nova_marmita, novo_estoque, foto_url)
                    st.success(f"Marmita '{nova_marmita}' cadastrada com estoque {novo_estoque}.")
            st.rerun()

        if st.button("Zerar todos os saldos", key="btn_zerar_saldos"):
            conn = get_conn()
            c = conn.cursor()
            c.execute("UPDATE marmitas SET saldo_atual=0")
            conn.commit()
            conn.close()
            st.success("Todos os saldos foram zerados.")
            st.rerun()

# ---------- CADASTRAR USUÁRIO ----------
elif menu == "Cadastrar Usuário":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para cadastrar novos usuários.")
    else:
        st.title("👤 Cadastrar Novo Administrador")
        nome_novo = st.text_input("Nome completo", key="nome_admin")
        login_novo = st.text_input("Login", key="login_admin")
        senha_nova = st.text_input("Senha", type="password", key="senha_admin")
        if st.button("Cadastrar", key="btn_cadastrar"):
            if nome_novo and login_novo and senha_nova:
                df_usuarios = get_usuarios()
                if login_novo in df_usuarios["login"].values:
                    st.warning("⚠️ Este login já está em uso.")
                else:
                    add_usuario(nome_novo, login_novo, senha_nova)
                    st.success("✅ Usuário cadastrado com sucesso!")
            else:
                st.warning("Preencha todos os campos para cadastrar o usuário.")

# ---------- LOGIN ADMIN / CADASTRO INICIAL ----------
elif menu == "Login Admin":
    if not existe_usuario():
        st.title("👤 Cadastro do Primeiro Administrador")
        nome = st.text_input("Nome completo")
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")
        if st.button("Cadastrar Admin"):
            if nome and login and senha:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome, login, senha) VALUES (?, ?, ?)", (nome, login, senha))
                conn.commit()
                conn.close()
                st.success("Administrador cadastrado com sucesso! Faça login para acessar o sistema.")
                st.experimental_rerun()
            else:
                st.warning("Preencha todos os campos para cadastrar o administrador.")
    else:
        st.title("🔐 Login do Administrador")
        login_user = st.text_input("Login")
        senha_user = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT * FROM usuarios WHERE login=? AND senha=?", (login_user, senha_user))
            user = c.fetchone()
            conn.close()
            if user:
                st.success(f"Bem-vindo(a), {user[1]}!")
                st.session_state.autenticado = True
                st.session_state.usuario = user[1]
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")

# ---------- LOGOUT ----------
elif menu == "Logout":
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.success("Logout realizado com sucesso!")
    st.rerun()
