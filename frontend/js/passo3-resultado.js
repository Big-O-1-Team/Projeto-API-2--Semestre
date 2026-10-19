const PassoTres = {
  init() {},

  exibirResultado() {
    const passo = document.getElementById("passo-3");
    const solicitacao = AppState.solicitacao;
    if (!passo || !solicitacao) return;

    passo.innerHTML = `
      <div class="status-box">
        <div class="status-box__icone">⌛</div>
        <h3>Solicitação em análise</h3>
        <p>Recebemos seus dados. Nesta primeira entrega, solicitações de clientes ainda não identificados como colaboradores seguem com o status inicial “Em análise”.</p>
        <div class="resumo-solicitacao">
          <div><span>Número</span><strong>#${solicitacao.id}</strong></div>
          <div><span>Cartão</span><strong>${AppState.nomeCartao || solicitacao.tipo_cartao}</strong></div>
          <div><span>Status</span><strong>${formatarStatus(solicitacao.status)}</strong></div>
          ${AppState.loja ? `<div><span>Loja</span><strong>${AppState.loja.nome}</strong></div>` : ""}
        </div>
        <div class="acoes-passo" style="justify-content:center">
          <button type="button" class="btn-primario" id="nova-solicitacao">Fazer nova solicitação</button>
        </div>
      </div>
    `;

    document.getElementById("nova-solicitacao").addEventListener("click", () => {
      AppState.tipoCartao = null;
      AppState.nomeCartao = null;
      AppState.loja = null;
      AppState.dados = null;
      AppState.solicitacao = null;
      PassoUm.init();
      irParaPasso(1);
    });
  }
};
