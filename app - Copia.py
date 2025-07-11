import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

from utils.pdf_export import gerar_pdf

st.set_page_config(page_title="Marmita Fácil", layout="centered")

caminho_csv = "data/pedidos.csv"
caminho_marmitas = "data/marmitas.csv"
caminho_usuarios = "data/usuarios.csv"
caminho_historico = "data/historico_status.csv"

st.markdown("""
    <style>
    @media (max-width: 600px) {
        .block-container {padding-left: 0.2rem; padding-right: 0.2rem;}
        .stButton button {font-size: 20px;}
        .stDataFrame, .stTable {font-size: 16px;}
    }
    .stImage img {border-radius:18px;}
    </style>
""", unsafe_allow_html=True)

os.makedirs("imagens", exist_ok=True)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

def registrar_historico(id_pedido, status_antigo, status_novo, usuario):
    registro = {
        "DataHora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ID Pedido": id_pedido,
        "Status Antigo": status_antigo,
        "Status Novo": status_novo,
        "Usuario": usuario
    }
    if not os.path.exists(caminho_historico):
        pd.DataFrame(columns=registro.keys()).to_csv(caminho_historico, index=False)
    df_hist = pd.read_csv(caminho_historico)
    df_hist = pd.concat([df_hist, pd.DataFrame([registro])], ignore_index=True)
    df_hist.to_csv(caminho_historico, index=False)

def fazer_logout():
    st.session_state.autenticado = False
    st.session_state.usuario = ""

def gerar_id_pedido():
    if os.path.exists(caminho_csv):
        df = pd.read_csv(caminho_csv, dtype={"Matrícula": str})
        if not df.empty and "ID Pedido" in df.columns:
            last_id = df["ID Pedido"].max()
            try:
                return f"PED{int(str(last_id).replace('PED', ''))+1:04d}"
            except:
                return f"PED{len(df)+1:04d}"
        else:
            return "PED0001"
    else:
        return "PED0001"

def gerar_id_marmita(df_marmitas):
    if "ID Marmita" in df_marmitas.columns and not df_marmitas.empty:
        return int(df_marmitas["ID Marmita"].max()) + 1
    else:
        return 1

def cor_status(status):
    cores = {
        "Recebido pela Cozinha": "orange",
        "Em preparo": "orange",
        "Enviado": "orange",
        "Entregue": "limegreen",
        "Cancelado": "red",
    }
    return f"<span style='color: {cores.get(status, 'yellow')}; font-weight: bold'>{status}</span>"

with st.sidebar:
    st.markdown("## Navegar")
    opcoes_menu = ["📋 Fazer Pedido", "📑 Histórico de Pedidos"]
    if st.session_state.autenticado:
        opcoes_menu += ["📝 Histórico de Alterações", "👨‍🍳 Administração", "👤 Cadastrar Usuário", "🚪 Logout"]
    else:
        opcoes_menu += ["🔐 Login Admin"]
    menu = st.selectbox("Menu", opcoes_menu, key="menu_selectbox")

if menu == "🚪 Logout":
    fazer_logout()
    st.success("Logout realizado com sucesso!")
    st.stop()

# ==== FAZER PEDIDO ====
if menu == "📋 Fazer Pedido":
    st.title("🍱 Marmita Fácil")
    st.subheader("Faça seu pedido de forma rápida e prática!")

    nome = st.text_input("Seu nome", key="nome_pedido")
    matricula = st.text_input("Sua matrícula", key="matricula_pedido")
    unidade = st.text_input("Unidade de atuação", key="unidade_pedido")
    destino = st.text_input("Local de destino da entrega", key="destino_pedido")
    lider = st.text_input("Líder", key="lider_pedido")
    centro_custo = st.text_input("Centro de custo", key="cc_pedido")

    marmitas_disponiveis = []
    if os.path.exists(caminho_marmitas):
        df_marmitas = pd.read_csv(caminho_marmitas)
        if not df_marmitas.empty and "Saldo Atual" in df_marmitas.columns:
            marmitas_com_saldo = df_marmitas[df_marmitas["Saldo Atual"] > 0].reset_index(drop=True)
            marmitas_disponiveis = marmitas_com_saldo.to_dict(orient="records")

    if marmitas_disponiveis:
        st.markdown("#### Escolha sua marmita:")
        n_colunas = 2
        if st.session_state.get("forcar_mobile"):
            n_colunas = 1

        if "escolha_cardapio" not in st.session_state:
            st.session_state["escolha_cardapio"] = None

        for i in range(0, len(marmitas_disponiveis), n_colunas):
            cols = st.columns(n_colunas)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(marmitas_disponiveis):
                    item = marmitas_disponiveis[idx]
                    with col:
                        if item.get("Imagem") and os.path.exists(str(item["Imagem"])):
                            st.image(str(item["Imagem"]), use_container_width=True, caption=item["Marmita"])
                        elif item.get("Imagem", "").startswith("http"):
                            st.image(item["Imagem"], use_container_width=True, caption=item["Marmita"])
                        else:
                            st.markdown(f"**{item['Marmita']}**")
                        st.markdown(f"<div style='text-align:center'><b>{item['Marmita']}</b><br><span style='color:gray'>Estoque: {item['Saldo Atual']}</span></div>", unsafe_allow_html=True)
                        if st.button(f"Selecionar {item['Marmita']}", key=f"btn_sel_{item['ID Marmita']}"):
                            st.session_state["escolha_cardapio"] = idx

        escolhido = st.session_state.get("escolha_cardapio")
        if escolhido is not None:
            selecionada = marmitas_disponiveis[escolhido]
            st.success(f"Selecionado: {selecionada['Marmita']}")
            quantidade = st.number_input("Quantidade", min_value=1, max_value=50, value=1, key="quantidade_pedido")
            observacoes = st.text_area("Alguma observação? (opcional)", key="obs_pedido")
            if st.button("Fazer pedido", key="btn_fazer_pedido"):
                estoque_disponivel = int(selecionada["Saldo Atual"])
                if nome and estoque_disponivel >= quantidade:
                    id_pedido = gerar_id_pedido()
                    pedido = {
                        "ID Pedido": id_pedido,
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Nome": nome,
                        "Matrícula": str(matricula),
                        "Unidade": unidade,
                        "Destino da Entrega": destino,
                        "Líder": lider,
                        "Centro de Custo": centro_custo,
                        "ID Marmita": selecionada["ID Marmita"],
                        "Marmita": selecionada["Marmita"],
                        "Quantidade": quantidade,
                        "Observações": observacoes,
                        "Status": "Recebido pela Cozinha"
                    }
                    nome_arquivo = f"{id_pedido}_{nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                    caminho_pdf = gerar_pdf(pedido, nome_arquivo)
                    st.success(f"📄 PDF gerado: {caminho_pdf}")

                    with open(caminho_pdf, "rb") as file:
                        st.download_button(
                            label="📥 Baixar comprovante em PDF",
                            data=file,
                            file_name=nome_arquivo,
                            mime="application/pdf",
                            key="btn_baixar_pdf"
                        )

                    if not os.path.exists(caminho_csv):
                        pd.DataFrame(columns=pedido.keys()).to_csv(caminho_csv, index=False)
                    df = pd.read_csv(caminho_csv, dtype={"Matrícula": str})
                    df = pd.concat([df, pd.DataFrame([pedido])], ignore_index=True)
                    df.to_csv(caminho_csv, index=False)

                    df_marmitas.loc[df_marmitas["ID Marmita"] == selecionada["ID Marmita"], "Saldo Atual"] -= quantidade
                    df_marmitas.to_csv(caminho_marmitas, index=False)

                    st.success(f"✅ Pedido feito com sucesso, {nome}! Você pediu {quantidade} marmita(s) de {selecionada['Marmita']}.")
                    st.info(f"ID do Pedido: {id_pedido}")
                    if observacoes:
                        st.write(f"Obs: {observacoes}")
                    st.session_state["escolha_cardapio"] = None
                else:
                    st.error("Preencha seu nome e confira o estoque disponível.")
    else:
        st.warning("⚠️ Nenhuma marmita disponível com saldo.")

# ==== LOGIN ADMIN ====
elif menu == "🔐 Login Admin":
    st.title("🔐 Login do Administrador")
    login = st.text_input("Usuário", key="login_login")
    senha = st.text_input("Senha", type="password", key="senha_login")

    if st.button("Entrar", key="btn_entrar"):
        if os.path.exists(caminho_usuarios):
            df_usuarios = pd.read_csv(caminho_usuarios)
            usuario = df_usuarios[(df_usuarios["login"] == login) & (df_usuarios["senha"] == senha)]
            if not usuario.empty:
                st.success(f"Bem-vindo(a), {usuario.iloc[0]['nome']}!")
                st.session_state.autenticado = True
                st.session_state.usuario = usuario.iloc[0]['nome']
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
        else:
            st.warning("Nenhum usuário cadastrado. Cadastre usuários manualmente no CSV.")

# ==== CADASTRAR USUÁRIO ====
elif menu == "👤 Cadastrar Usuário":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para cadastrar novos usuários.")
    else:
        st.title("👤 Cadastrar Novo Administrador")
        nome_novo = st.text_input("Nome completo", key="nome_admin")
        login_novo = st.text_input("Login", key="login_admin")
        senha_nova = st.text_input("Senha", type="password", key="senha_admin")
        if st.button("Cadastrar", key="btn_cadastrar"):
            if nome_novo and login_novo and senha_nova:
                if os.path.exists(caminho_usuarios):
                    df_usuarios = pd.read_csv(caminho_usuarios)
                else:
                    df_usuarios = pd.DataFrame(columns=["nome", "login", "senha"])
                if login_novo in df_usuarios["login"].values:
                    st.warning("⚠️ Este login já está em uso.")
                else:
                    novo = {"nome": nome_novo, "login": login_novo, "senha": senha_nova}
                    df_usuarios = pd.concat([df_usuarios, pd.DataFrame([novo])], ignore_index=True)
                    df_usuarios.to_csv(caminho_usuarios, index=False)
                    st.success("✅ Usuário cadastrado com sucesso!")
            else:
                st.warning("Preencha todos os campos para cadastrar o usuário.")

# ==== ADMINISTRAÇÃO ====
elif menu == "👨‍🍳 Administração":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para acessar esta tela.")
    else:
        st.title("👨‍🍳 Administração de Marmitas")
        st.subheader("📦 Pedidos Recebidos - Gestão de Status (Massa)")

        status_opcoes = ["Recebido pela Cozinha", "Em preparo", "Enviado", "Entregue", "Cancelado"]
        if os.path.exists(caminho_csv):
            df_pedidos = pd.read_csv(caminho_csv, dtype={"Matrícula": str})
            if "Status" not in df_pedidos.columns:
                df_pedidos["Status"] = "Recebido pela Cozinha"
            df_pendentes = df_pedidos[df_pedidos["Status"].isin(["Recebido pela Cozinha", "Em preparo", "Enviado"])]

            df_pendentes["Desc"] = df_pendentes.apply(
                lambda row: f"{row['ID Pedido']} | {row['Nome']} | {row['Marmita']}", axis=1)
            opcoes_multiselect = df_pendentes["Desc"].tolist()

            if "pedidos_selecionados" not in st.session_state:
                st.session_state["pedidos_selecionados"] = []

            st.write("Ou clique para selecionar todos:")

            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Selecionar todos", key="btn_select_all"):
                    st.session_state["pedidos_selecionados"] = opcoes_multiselect
                    st.rerun()
            with col2:
                if st.button("Limpar seleção", key="btn_limpar_select_all"):
                    st.session_state["pedidos_selecionados"] = []
                    st.rerun()

            valores_validos = [v for v in st.session_state["pedidos_selecionados"] if v in opcoes_multiselect]
            pedidos_selecionados = st.multiselect(
                "Selecione os pedidos para atualizar (busca por ID ou Nome)",
                opcoes_multiselect,
                default=valores_validos,
                key="multiselect_pedidos"
            )
            st.session_state["pedidos_selecionados"] = pedidos_selecionados

            novo_status_massa = st.selectbox("Novo status", status_opcoes, key="novo_status_massa")
            if st.button("Atualizar status", key="btn_atualizar_status_massa"):
                if pedidos_selecionados:
                    alterados = []
                    for desc in pedidos_selecionados:
                        id_pedido = desc.split("|")[0].strip()
                        idx = df_pedidos[df_pedidos["ID Pedido"] == id_pedido].index
                        if len(idx) > 0:
                            idx = idx[0]
                            atual = df_pedidos.at[idx, "Status"]
                            qnt = int(df_pedidos.at[idx, "Quantidade"])
                            id_marmita = df_pedidos.at[idx, "ID Marmita"]
                            if atual != "Cancelado" and novo_status_massa == "Cancelado":
                                df_marmitas = pd.read_csv(caminho_marmitas)
                                df_marmitas.loc[df_marmitas["ID Marmita"] == int(id_marmita), "Saldo Atual"] += qnt
                                df_marmitas.to_csv(caminho_marmitas, index=False)
                            registrar_historico(
                                id_pedido=id_pedido,
                                status_antigo=atual,
                                status_novo=novo_status_massa,
                                usuario=st.session_state.usuario if "usuario" in st.session_state else ""
                            )
                            df_pedidos.at[idx, "Status"] = novo_status_massa
                            alterados.append(id_pedido)
                    df_pedidos.to_csv(caminho_csv, index=False)
                    st.success(f"Status de {len(alterados)} pedido(s) atualizado para '{novo_status_massa}'!")
                    st.rerun()

            # Inclui as novas colunas nas tabelas
            colunas_exibir = ["ID Pedido", "Nome", "Marmita", "Quantidade", "Líder", "Centro de Custo", "Status", "Matrícula"]
            colunas_exibir = [c for c in colunas_exibir if c in df_pendentes.columns]
            df_pendentes_visu = df_pendentes[colunas_exibir].copy()
            df_pendentes_visu["Status"] = df_pendentes_visu["Status"].apply(lambda s: cor_status(s))
            st.write(df_pendentes_visu.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.subheader("📋 Marmitas em Estoque com Saldo Atual")
        if not os.path.exists(caminho_marmitas):
            pd.DataFrame(
                columns=["ID Marmita", "Marmita", "Estoque", "Saldo Atual", "Data de Cadastro", "Imagem"]
            ).to_csv(caminho_marmitas, index=False)
        df_marmitas = pd.read_csv(caminho_marmitas)
        if df_marmitas.empty:
            st.info("Nenhuma marmita cadastrada ainda.")
        else:
            st.dataframe(df_marmitas, use_container_width=True)

        st.subheader("➕ Novo Cadastro ou Atualização de Estoque")
        nova_marmita = st.text_input("Nome da marmita", key="nome_marmita")
        novo_estoque = st.number_input("Quantidade em estoque", min_value=0, step=1, key="quantidade_marmita")
        foto_file = st.file_uploader("Foto do prato (obrigatório para novo cadastro)", type=["jpg", "jpeg", "png"], key="foto_marmita")
        imagem_path = ""

        if st.button("Salvar marmita", key="btn_salvar_marmita"):
            if not nova_marmita:
                st.warning("Informe o nome da marmita.")
            else:
                ja_existe = False
                if "Marmita" in df_marmitas.columns and nova_marmita in df_marmitas["Marmita"].values:
                    ja_existe = True

                if not ja_existe and not foto_file:
                    st.warning("Para cadastrar uma nova marmita, é obrigatório enviar uma foto do prato!")
                else:
                    data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if foto_file:
                        ext = os.path.splitext(foto_file.name)[1].lower()
                        unique_img = f"imagens/{uuid.uuid4().hex}{ext}"
                        imagem_path = unique_img
                        with open(imagem_path, "wb") as f:
                            f.write(foto_file.getbuffer())
                    if ja_existe:
                        idx = df_marmitas[df_marmitas["Marmita"] == nova_marmita].index[0]
                        df_marmitas.at[idx, "Estoque"] = novo_estoque
                        df_marmitas.at[idx, "Saldo Atual"] = novo_estoque
                        df_marmitas.at[idx, "Data de Cadastro"] = data_cadastro
                        if imagem_path:
                            df_marmitas.at[idx, "Imagem"] = imagem_path
                        st.success(f"Estoque da marmita '{nova_marmita}' atualizado para {novo_estoque}.")
                    else:
                        novo_id = gerar_id_marmita(df_marmitas)
                        nova_row = {
                            "ID Marmita": novo_id,
                            "Marmita": nova_marmita,
                            "Estoque": novo_estoque,
                            "Saldo Atual": novo_estoque,
                            "Data de Cadastro": data_cadastro,
                            "Imagem": imagem_path
                        }
                        df_marmitas = pd.concat([df_marmitas, pd.DataFrame([nova_row])], ignore_index=True)
                        st.success(f"Marmita '{nova_marmita}' cadastrada com estoque {novo_estoque} e ID {novo_id}.")
                    df_marmitas.to_csv(caminho_marmitas, index=False)
                    st.rerun()

        if st.button("Zerar todos os saldos", key="btn_zerar_saldos"):
            df_marmitas["Saldo Atual"] = 0
            df_marmitas.to_csv(caminho_marmitas, index=False)
            st.success("Todos os saldos foram zerados.")
            st.rerun()

# ==== HISTÓRICO DE PEDIDOS ====
elif menu == "📑 Histórico de Pedidos":
    st.title("📑 Histórico de Pedidos")
    if os.path.exists(caminho_csv):
        try:
            df = pd.read_csv(caminho_csv, dtype={"Matrícula": str})
            df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
            if "Status" not in df.columns:
                df["Status"] = "Recebido pela Cozinha"
            if df.empty:
                st.info("Nenhum pedido registrado ainda.")
            else:
                busca_matricula = st.text_input("Filtrar por matrícula (deixe em branco para mostrar tudo):")
                data_min = df["Data"].min().date()
                data_max = df["Data"].max().date()
                data_inicio = st.date_input("De:", value=data_min, key="data_inicio")
                data_fim = st.date_input("Até:", value=data_max, key="data_fim")
                filtro = (
                    (df["Data"] >= pd.to_datetime(data_inicio)) &
                    (df["Data"] <= pd.to_datetime(data_fim) + pd.Timedelta(days=1))
                )
                df_filtrado = df.loc[filtro]
                if busca_matricula:
                    df_filtrado = df_filtrado[
                        df_filtrado["Matrícula"].astype(str).str.contains(busca_matricula, case=False, na=False)
                    ]
                def cor_status_table(s):
                    if s == "Entregue":
                        return "background-color: #3cb371; color: white;"
                    if s == "Cancelado":
                        return "background-color: #d9534f; color: white;"
                    if s in ("Recebido pela Cozinha", "Em preparo", "Enviado"):
                        return "background-color: #ffcc00; color: black;"
                    return ""
                colunas_exibir = ["ID Pedido", "Data", "Nome", "Matrícula", "Unidade", "Destino da Entrega", "Líder", "Centro de Custo", "Marmita", "Quantidade", "Status"]
                colunas_exibir = [c for c in colunas_exibir if c in df_filtrado.columns]
                st.dataframe(df_filtrado[colunas_exibir].style.applymap(cor_status_table, subset=["Status"]), use_container_width=True)
                st.success(f"{len(df_filtrado)} pedidos exibidos.")
                csv_export = df_filtrado[colunas_exibir].to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Exportar como CSV",
                    data=csv_export,
                    file_name="historico_pedidos.csv",
                    mime="text/csv",
                    key="btn_exportar_csv"
                )
        except pd.errors.EmptyDataError:
            st.warning("O arquivo de pedidos existe, mas está vazio ou mal formatado.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
    else:
        st.info("Nenhum pedido registrado ainda.")

# ==== HISTÓRICO DE ALTERAÇÕES ====
elif menu == "📝 Histórico de Alterações":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para acessar esta tela.")
    else:
        st.title("📝 Histórico de Alterações de Status")
        if os.path.exists(caminho_historico):
            df_hist = pd.read_csv(caminho_historico)
            if df_hist.empty:
                st.info("Nenhuma alteração registrada ainda.")
            else:
                busca_id = st.text_input("Filtrar por ID do Pedido (opcional):")
                busca_usuario = st.text_input("Filtrar por usuário (opcional):")
                data_min = pd.to_datetime(df_hist["DataHora"]).min().date()
                data_max = pd.to_datetime(df_hist["DataHora"]).max().date()
                data_inicio = st.date_input("De:", value=data_min, key="data_inicio_hist")
                data_fim = st.date_input("Até:", value=data_max, key="data_fim_hist")
                df_hist["DataHora"] = pd.to_datetime(df_hist["DataHora"])
                filtro = (
                    (df_hist["DataHora"] >= pd.to_datetime(data_inicio)) &
                    (df_hist["DataHora"] <= pd.to_datetime(data_fim) + pd.Timedelta(days=1))
                )
                df_filtrado = df_hist.loc[filtro]
                if busca_id:
                    df_filtrado = df_filtrado[df_filtrado["ID Pedido"].astype(str).str.contains(busca_id, case=False, na=False)]
                if busca_usuario:
                    df_filtrado = df_filtrado[df_filtrado["Usuario"].astype(str).str.contains(busca_usuario, case=False, na=False)]
                st.dataframe(df_filtrado.sort_values("DataHora", ascending=False), use_container_width=True)
                st.success(f"{len(df_filtrado)} alterações exibidas.")
                csv_export = df_filtrado.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Exportar log como CSV",
                    data=csv_export,
                    file_name="historico_alteracoes.csv",
                    mime="text/csv",
                    key="btn_exportar_hist_csv"
                )
        else:
            st.info("Nenhuma alteração registrada ainda.")
