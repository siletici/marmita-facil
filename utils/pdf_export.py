def mostrar_comprovante_pedido(pedido):
    st.markdown(f"""
        <div style="background:#23272B; padding:32px; border-radius:20px; max-width:480px; margin:auto; color:#fff; box-shadow:0 6px 24px #0002;">
            <div style="text-align:center; margin-bottom:18px;">
                <img src="https://marmita-facil-dados.s3.us-east-2.amazonaws.com/imagens/logo-marmitafacil.png" alt="Logo" style="max-width:180px; border-radius:10px;"/>
            </div>
            <h2 style="text-align:center; color:#FFC300; margin-bottom:18px;">Comprovante de Pedido</h2>
            <hr style="border:1px solid #ED212B;">
            <p><strong>Nome:</strong> {pedido["nome"]}</p>
            <p><strong>Matrícula:</strong> {pedido["matricula"]}</p>
            <p><strong>Unidade:</strong> {pedido["unidade"]}</p>
            <p><strong>Destino da Entrega:</strong> {pedido["destino"]}</p>
            <p><strong>Líder:</strong> {pedido["lider"]}</p>
            <p><strong>Centro de Custo:</strong> {pedido["centro_custo"]}</p>
            <p><strong>Marmita:</strong> {pedido["marmita_nome"]}</p>
            <p><strong>Quantidade:</strong> {pedido["quantidade"]}</p>
            <p><strong>Data/Hora:</strong> {pedido["data"]}</p>
            {"<p><strong>Observações:</strong> " + pedido['observacoes'] + "</p>" if pedido["observacoes"] else ""}
            <hr style="border:1px solid #ED212B; margin-top:18px;">
            <p style="color:#FFF; margin-top:18px; text-align:center;">
                <b>Para gerar o comprovante em PDF:</b><br>
                Pressione <b>Ctrl+P</b> (ou <b>Comando+P</b> no Mac) e escolha <b>Salvar como PDF</b>.<br>
                <b>Depois, envie este comprovante no WhatsApp do seu líder ou responsável administrativo.</b>
            </p>
        </div>
    """, unsafe_allow_html=True)






