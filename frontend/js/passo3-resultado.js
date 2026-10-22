const PassoTres = {
  init() {},

  exibirResultado() {
    const passo = document.getElementById("passo-3");
    const solicitacao = AppState.solicitacao;
    if (!passo || !solicitacao) return;

    const estados = {
      APROVADO: { icone: "✓", titulo: "Solicitação aprovada", descricao: "Sua solicitação foi aprovada na pré-qualificação inicial." },
      REPROVADO: { icone: "!", titulo: "Solicitação reprovada", descricao: "Essa opção de cartão não está disponível para o perfil informado." },
      EM_ANALISE: { icone: "⌛", titulo: "Solicitação em análise", descricao: "Recebemos seus dados. Sua solicitação precisa de análise antes de uma decisão." }
    };
    const estado = estados[solicitacao.status] || estados.EM_ANALISE;

    passo.innerHTML = `
      <div class="status-box" data-status="${solicitacao.status}">
        <div class="status-box__icone">${estado.icone}</div>
        <h3>${estado.titulo}</h3>
        <p>${estado.descricao}</p>
        <div class="resumo-solicitacao">
          <div><span>Número</span><strong>#${solicitacao.id}</strong></div>
          <div><span>Cartão</span><strong>${AppState.nomeCartao || solicitacao.tipo_cartao}</strong></div>
          <div><span>Status</span><strong>${formatarStatus(solicitacao.status)}</strong></div>
          ${AppState.loja ? `<div><span>Loja</span><strong>${AppState.loja.nome}</strong></div>` : ""}
        </div>
        <div class="acoes-passo acoes-passo--centro">
          <button type="button" class="btn-secundario" id="consultar-solicitacao">Acompanhar solicitação</button>
          <button type="button" class="btn-primario" id="nova-solicitacao">Fazer nova solicitação</button>
        </div>
      </div>
    `;

    document.getElementById("consultar-solicitacao").addEventListener("click", () => {
      document.getElementById("numero-solicitacao").value = solicitacao.id;
      document.getElementById("cpf-consulta").value = AppState.dados.cpf;
      document.getElementById("consultar-status").scrollIntoView({ behavior: "smooth", block: "start" });
    });

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
