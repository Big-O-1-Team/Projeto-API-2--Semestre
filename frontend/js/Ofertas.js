const OFERTAS_DM = [
  {
    id: "EP",
    sigla: "EP",
    nome: "EP",
    descricao: "Uma alternativa de crédito da DM para você conhecer.",
    url: ""
  },
  {
    id: "DMCRED",
    sigla: "DC",
    nome: "DMCred",
    descricao: "Mais uma opção de crédito da DM, além do cartão.",
    url: ""
  }
];

const PassoTres = {
  init() {},

  montarOfertas(status) {
    if (!OFERTAS_DM.length) return "";

    const reprovado = status === "REPROVADO";
    const titulo = reprovado ? "Outras opções para você" : "Conheça outros produtos DM";
    const descricao = reprovado
      ? "O cartão solicitado não está disponível agora, mas a DM tem outras opções que você pode conhecer."
      : "Enquanto sua solicitação segue, veja outros produtos que a DM oferece.";

    const cards = OFERTAS_DM.map((oferta) => `
      <article class="oferta-card" data-oferta="${oferta.id}">
        <span class="oferta-card__icone" aria-hidden="true">${oferta.sigla}</span>
        <div class="oferta-card__texto">
          <h5>${oferta.nome}</h5>
          <p>${oferta.descricao}</p>
        </div>
        ${oferta.url ? `<a class="btn-secundario oferta-card__acao" href="${oferta.url}" target="_blank" rel="noopener noreferrer">Saber mais</a>` : ""}
      </article>
    `).join("");

    return `
      <section class="ofertas" id="ofertas-dm" aria-labelledby="ofertas-dm-titulo">
        <h4 class="ofertas__titulo" id="ofertas-dm-titulo">${titulo}</h4>
        <p class="ofertas__descricao">${descricao}</p>
        <div class="ofertas__lista">${cards}</div>
      </section>
    `;
  },

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
      ${this.montarOfertas(solicitacao.status)}
    `;

    document.getElementById("consultar-solicitacao").addEventListener("click", () => {
      document.getElementById("cpf-consulta").value = AppState.dados.cpf;
      document.getElementById("consultar-status").scrollIntoView({ behavior: "smooth", block: "start" });
      document.getElementById("consulta-status-form").requestSubmit();
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
