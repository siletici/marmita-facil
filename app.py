# app.py com controle de saldo atualizado ao pedir
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# PDF
from utils.pdf_export import gerar_pdf

# Configuração da página
st.set_page_config(page_title="Marmita Fácil", layout="centered")

# Caminhos
caminho_csv = "data/pedidos.csv"
caminho_marmitas = "data/marmitas.csv"
caminho_usuarios = "data/usuarios.csv"

# Sessão de autenticação
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# =======================
# MENU LATERAL
# =======================
menu = st.sidebar.selectbox("Navegar", [
    "📋 Fazer Pedido",
    "📑 Histórico de Pedidos",
    "🔐 Login Admin",
    "👨‍🍳 Administração",
    "👤 Cadastrar Usuário"])

# =======================
# 📋 FAZER PEDIDO
# =======================
if menu == "📋 Fazer Pedido":
    st.title("🍱 Marmita Fácil")
    st.subheader("Faça seu pedido de forma rápida e prática!")

    nome = st.text_input("Seu nome")
    matricula = st.text_input("Sua matrícula")
    unidade = st.text_input("Unidade de atuação")
    destino = st.text_input("Local de destino da entrega")
    lider = st.text_input("Nome do seu líder imediato")

    marmitas_disponiveis = []
    if os.path.exists(caminho_marmitas):
        df_marmitas = pd.read_csv(caminho_marmitas)
        marmitas_disponiveis = df_marmitas[df_marmitas["Saldo Atual"] > 0]["Marmita"].tolist()

    if marmitas_disponiveis:
        opcao = st.selectbox("Escolha sua marmita do dia:", ["---"] + marmitas_disponiveis)
    else:
        opcao = "---"
        st.warning("⚠️ Nenhuma marmita disponível com saldo.")

    observacoes = st.text_area("Alguma observação? (opcional)")

    if st.button("Fazer pedido"):
        if nome and opcao != "---":
            pedido = {
                "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nome": nome,
                "Matrícula": matricula,
                "Unidade": unidade,
                "Destino da Entrega": destino,
                "Líder Imediato": lider,
                "Marmita": opcao,
                "Observações": observacoes
            }

            nome_arquivo = f"{nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            caminho_pdf = gerar_pdf(pedido, nome_arquivo)
            st.success(f"📄 PDF gerado: {caminho_pdf}")

            with open(caminho_pdf, "rb") as file:
                st.download_button(
                    label="📥 Baixar comprovante em PDF",
                    data=file,
                    file_name=nome_arquivo,
                    mime="application/pdf")

            if not os.path.exists(caminho_csv):
                pd.DataFrame(columns=pedido.keys()).to_csv(caminho_csv, index=False)

            df = pd.read_csv(caminho_csv)
            df = pd.concat([df, pd.DataFrame([pedido])], ignore_index=True)
            df.to_csv(caminho_csv, index=False)

            # Abater saldo da marmita
            df_marmitas.loc[df_marmitas["Marmita"] == opcao, "Saldo Atual"] -= 1
            df_marmitas.to_csv(caminho_marmitas, index=False)

            st.success(f"✅ Pedido feito com sucesso, {nome}!")
            st.info(f"Você escolheu: {opcao}")
            if observacoes:
                st.write(f"Obs: {observacoes}")
        else:
            st.warning("⚠️ Preencha seu nome e escolha uma marmita.")


# =======================
# 🔐 LOGIN ADMIN
# =======================
if menu == "🔐 Login Admin":
    st.title("🔐 Login do Administrador")

    login = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if os.path.exists(caminho_usuarios):
            df_usuarios = pd.read_csv(caminho_usuarios)
            usuario = df_usuarios[(df_usuarios["login"] == login) & (df_usuarios["senha"] == senha)]
            if not usuario.empty:
                st.success(f"Bem-vindo(a), {usuario.iloc[0]['nome']}!")
                st.session_state.autenticado = True
                st.session_state.usuario = usuario.iloc[0]['nome']
            else:
                st.error("Usuário ou senha inválidos.")
        else:
            st.warning("Nenhum usuário cadastrado. Cadastre usuários manualmente no CSV.")

# =======================
# 👤 CADASTRO DE USUÁRIO
# =======================
elif menu == "👤 Cadastrar Usuário":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para cadastrar novos usuários.")
    else:
        st.title("👤 Cadastrar Novo Administrador")

        nome_novo = st.text_input("Nome completo")
        login_novo = st.text_input("Login")
        senha_nova = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
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

# =======================
# 👨‍🍳 ADMINISTRAÇÃO
# =======================
elif menu == "👨‍🍳 Administração":
    if not st.session_state.autenticado:
        st.error("🔒 Acesso restrito. Faça login como administrador para acessar esta tela.")
    else:
        st.title("👨‍🍳 Administração de Marmitas")

        if not os.path.exists(caminho_marmitas):
            pd.DataFrame(columns=["Marmita", "Estoque", "Saldo Atual", "Data de Cadastro"]).to_csv(caminho_marmitas, index=False)

        df_marmitas = pd.read_csv(caminho_marmitas)

        st.subheader("📋 Marmitas em Estoque com Saldo Atual")
        if df_marmitas.empty:
            st.info("Nenhuma marmita cadastrada ainda.")
        else:
            st.dataframe(df_marmitas, use_container_width=True)

        st.subheader("➕ Novo Cadastro ou Atualização de Estoque")

        nova_marmita = st.text_input("Nome da marmita")
        novo_estoque = st.number_input("Quantidade em estoque", min_value=0, step=1)

        if st.button("Salvar marmita"):
            if nova_marmita:
                data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if nova_marmita in df_marmitas["Marmita"].values:
                    df_marmitas.loc[df_marmitas["Marmita"] == nova_marmita, ["Estoque", "Saldo Atual"]] = novo_estoque
                    st.success(f"Estoque da marmita '{nova_marmita}' atualizado para {novo_estoque}.")
                else:
                    df_marmitas = pd.concat([
                        df_marmitas,
                        pd.DataFrame([{
                            "Marmita": nova_marmita,
                            "Estoque": novo_estoque,
                            "Saldo Atual": novo_estoque,
                            "Data de Cadastro": data_cadastro
                        }])
                    ], ignore_index=True)
                    st.success(f"Marmita '{nova_marmita}' cadastrada com estoque {novo_estoque}.")
                df_marmitas.to_csv(caminho_marmitas, index=False)
            else:
                st.warning("Informe o nome da marmita.")

        if st.button("Zerar todos os saldos"):
            df_marmitas["Saldo Atual"] = 0
            df_marmitas.to_csv(caminho_marmitas, index=False)
            st.success("Todos os saldos foram zerados.")

# =======================
# 📑 HISTÓRICO DE PEDIDOS COM FILTRO
# =======================
elif menu == "📑 Histórico de Pedidos":
    st.title("📑 Histórico de Pedidos")

    if os.path.exists(caminho_csv):
        try:
            df = pd.read_csv(caminho_csv)
            if df.empty:
                st.info("Nenhum pedido registrado ainda.")
            else:
                df["Data"] = pd.to_datetime(df["Data"])

                data_inicio = st.date_input("De:", value=df["Data"].min().date())
                data_fim = st.date_input("Até:", value=df["Data"].max().date())

                df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicio)) & (df["Data"] <= pd.to_datetime(data_fim))]

                st.dataframe(df_filtrado, use_container_width=True)
                st.success(f"{len(df_filtrado)} pedidos exibidos.")

                csv_export = df_filtrado.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exportar como CSV", data=csv_export, file_name="historico_pedidos.csv", mime="text/csv")

        except pd.errors.EmptyDataError:
            st.warning("O arquivo de pedidos existe, mas está vazio ou mal formatado.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
    else:
        st.info("Nenhum pedido registrado ainda.")

# =======================
# 📋 FAZER PEDIDO
# =======================
if menu == "📋 Fazer Pedido":
    st.title("🍱 Marmita Fácil")
    st.subheader("Faça seu pedido de forma rápida e prática!")

    nome = st.text_input("Seu nome")
    matricula = st.text_input("Sua matrícula")
    unidade = st.text_input("Unidade de atuação")
    destino = st.text_input("Local de destino da entrega")
    lider = st.text_input("Nome do seu líder imediato")

    # Carregar marmitas disponíveis do estoque
    marmitas_disponiveis = []
    if os.path.exists(caminho_marmitas):
        df_marmitas = pd.read_csv(caminho_marmitas)
        marmitas_disponiveis = df_marmitas[df_marmitas["Saldo Atual"] > 0]["Marmita"].tolist()

    if marmitas_disponiveis:
        opcao = st.selectbox("Escolha sua marmita do dia:", ["---"] + marmitas_disponiveis)
    else:
        opcao = "---"
        st.warning("⚠️ Nenhuma marmita disponível no estoque.")

    observacoes = st.text_area("Alguma observação? (opcional)")

    if st.button("Fazer pedido"):
        if nome and opcao != "---":
            pedido = {
                "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nome": nome,
                "Matrícula": matricula,
                "Unidade": unidade,
                "Destino da Entrega": destino,
                "Líder Imediato": lider,
                "Marmita": opcao,
                "Observações": observacoes
            }

            nome_arquivo = f"{nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            caminho_pdf = gerar_pdf(pedido, nome_arquivo)
            st.success(f"📄 PDF gerado: {caminho_pdf}")

            with open(caminho_pdf, "rb") as file:
                st.download_button(
                    label="📥 Baixar comprovante em PDF",
                    data=file,
                    file_name=nome_arquivo,
                    mime="application/pdf"
                )

            # Salvar pedido
            if not os.path.exists(caminho_csv):
                pd.DataFrame(columns=pedido.keys()).to_csv(caminho_csv, index=False)

            df = pd.read_csv(caminho_csv)
            df = pd.concat([df, pd.DataFrame([pedido])], ignore_index=True)
            df.to_csv(caminho_csv, index=False)

            # Atualizar saldo
            df_marmitas.loc[df_marmitas["Marmita"] == opcao, "Saldo Atual"] -= 1
            df_marmitas.to_csv(caminho_marmitas, index=False)

            st.success(f"✅ Pedido feito com sucesso, {nome}!")
            st.info(f"Você escolheu: {opcao}")
            if observacoes:
                st.write(f"Obs: {observacoes}")
        else:
            st.warning("⚠️ Preencha seu nome e escolha uma marmita.")

# =======================
# 📑 HISTÓRICO
# =======================
elif menu == "📑 Histórico de Pedidos":
    st.title("📑 Histórico de Pedidos")

    if os.path.exists(caminho_csv):
        try:
            df = pd.read_csv(caminho_csv, parse_dates=["Data"])

            if df.empty:
                st.info("Nenhum pedido registrado ainda.")
            else:
                df["Data"] = pd.to_datetime(df["Data"])
                data_inicio = st.date_input("De:", value=df["Data"].min().date())
                data_fim = st.date_input("Até:", value=df["Data"].max().date())

                filtro = (df["Data"] >= pd.to_datetime(data_inicio)) & (df["Data"] <= pd.to_datetime(data_fim))
                df_filtrado = df.loc[filtro]

                st.dataframe(df_filtrado, use_container_width=True)
                st.success(f"{len(df_filtrado)} pedidos encontrados no período.")

                csv_export = df_filtrado.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="🗃️ Exportar pedidos em CSV",
                    data=csv_export,
                    file_name=f"pedidos_{data_inicio}_a_{data_fim}.csv",
                    mime="text/csv"
                )

        except pd.errors.EmptyDataError:
            st.warning("O arquivo de pedidos existe, mas está vazio ou mal formatado.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
    else:
        st.info("Nenhum pedido registrado ainda.")

# =======================
# 👨‍🍳 ADMIN
# =======================
elif menu == "👨‍🍳 Administração":
    if not st.session_state.autenticado:
        st.warning("🔒 Faça login para acessar a administração.")
        st.stop()

    st.title("👨‍🍳 Administração de Marmitas")

    if not os.path.exists(caminho_marmitas):
        pd.DataFrame(columns=["Marmita", "Estoque Inicial", "Saldo Atual"]).to_csv(caminho_marmitas, index=False)

    df_marmitas = pd.read_csv(caminho_marmitas)

    st.subheader("📋 Marmitas em estoque")
    if df_marmitas.empty:
        st.info("Nenhuma marmita cadastrada ainda.")
    else:
        st.dataframe(df_marmitas, use_container_width=True)

    st.subheader("➕ Cadastrar nova marmita ou atualizar estoque")
    nova_marmita = st.text_input("Nome da marmita")
    novo_estoque = st.number_input("Quantidade em estoque", min_value=0, step=1)

    if st.button("Salvar marmita"):
        if nova_marmita:
            if nova_marmita in df_marmitas["Marmita"].values:
                df_marmitas.loc[df_marmitas["Marmita"] == nova_marmita, "Estoque Inicial"] = novo_estoque
                df_marmitas.loc[df_marmitas["Marmita"] == nova_marmita, "Saldo Atual"] = novo_estoque
                st.success(f"Estoque da marmita '{nova_marmita}' atualizado.")
            else:
                novo = {"Marmita": nova_marmita, "Estoque Inicial": novo_estoque, "Saldo Atual": novo_estoque}
                df_marmitas = pd.concat([df_marmitas, pd.DataFrame([novo])], ignore_index=True)
                st.success(f"Marmita '{nova_marmita}' cadastrada com estoque {novo_estoque}.")
            df_marmitas.to_csv(caminho_marmitas, index=False)
        else:
            st.warning("Informe o nome da marmita.")

    if st.button("🔁 Zerar e reiniciar saldos"):
        df_marmitas["Saldo Atual"] = df_marmitas["Estoque Inicial"]
        df_marmitas.to_csv(caminho_marmitas, index=False)
        st.success("Saldos reiniciados com sucesso!")

