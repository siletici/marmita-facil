import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

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

# ---------- LOGIN ADMIN ----------
elif menu == "Login Admin":
    st.title("🔐 Login do Administrador")
    login = st.text_input("Usuário", key="login_login")
    senha = st.text_input("Senha", type="password", key="senha_login")
    if st.button("Entrar", key="btn_entrar"):
        df_usuarios = get_usuarios()
        usuario = df_usuarios[(df_usuarios["login"] == login) & (df_usuarios["senha"] == senha)]
        if not usuario.empty:
            st.success(f"Bem-vindo(a), {usuario.iloc[0]['nome']}!")
            st.session_state.autenticado = True
            st.session_state.usuario = usuario.iloc[0]['nome']
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

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
                try:
                    add_usuario(nome_novo, login_novo, senha_nova)
                    st.success("✅ Usuário cadastrado com sucesso!")
                except sqlite3.IntegrityError:
                    st.warning("⚠️ Este login já está em uso.")
            else:
                st.warning("Preencha todos os campos para cadastrar o usuário.")

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

# ---------- LOGOUT ----------
elif menu == "Logout":
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.success("Logout realizado com sucesso!")
    st.rerun()

# ---------- CADASTRO DO PRIMEIRO ADMIN SE BANCO ESTIVER VAZIO ----------
def existe_usuario():
    conn = sqlite3.connect("marmita_facil.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    qtd = c.fetchone()[0]
    conn.close()
    return qtd > 0

if not existe_usuario():
    st.title("👤 Cadastro do Primeiro Administrador")
    nome = st.text_input("Nome completo", key="primeiro_nome")
    login = st.text_input("Login", key="primeiro_login")
    senha = st.text_input("Senha", type="password", key="primeiro_senha")
    if st.button("Cadastrar Admin", key="primeiro_admin"):
        if nome and login and senha:
            add_usuario(nome, login, senha)
            st.success("Administrador cadastrado com sucesso! Faça login para acessar o sistema.")
            st.experimental_rerun()
        else:
            st.warning("Preencha todos os campos para cadastrar o administrador.")
