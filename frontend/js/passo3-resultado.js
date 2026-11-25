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
    const reprovado = solicitacao.status === "REPROVADO";

    passo.innerHTML = [
      '<div class="status-box" data-status="', escaparHtml(solicitacao.status), '">',
      '<div class="status-box__icone" aria-hidden="true">', estado.icone, '</div>',
      '<h3>', estado.titulo, '</h3><p>', estado.descricao, '</p>',
      '<div class="resumo-solicitacao">',
      '<div><span>Número</span><strong>#', escaparHtml(solicitacao.id), '</strong></div>',
      '<div><span>Cartão</span><strong>', escaparHtml(AppState.nomeCartao || solicitacao.tipo_cartao), '</strong></div>',
      '<div><span>Status</span><strong>', escaparHtml(formatarStatus(solicitacao.status)), '</strong></div>',
      AppState.loja ? '<div><span>Loja</span><strong>' + escaparHtml(AppState.loja.nome) + '</strong></div>' : '',
      '</div>',
      '<div class="acoes-passo acoes-passo--centro">',
      '<button type="button" class="btn-secundario" id="consultar-solicitacao">Acompanhar solicitação</button>',
      '<button type="button" class="btn-primario" id="nova-solicitacao">Fazer nova solicitação</button>',
      '</div></div>',
      '<section class="ofertas" aria-labelledby="ofertas-titulo">',
      '<p class="ofertas__eyebrow">OUTRAS POSSIBILIDADES</p>',
      '<h3 id="ofertas-titulo">Conheça outras opções da DM</h3>',
      '<p class="ofertas__intro">Além dos cartões, existem outras modalidades que podem ser avaliadas conforme seu perfil. Nenhuma oferta é uma aprovação automática.</p>',
      '<div class="ofertas__grade">',
      '<article class="ofertas__card"><span class="ofertas__icone" aria-hidden="true">✦</span><h4>Empréstimo pessoal</h4><p>Uma alternativa de crédito para conhecer e avaliar conforme as condições disponíveis.</p><span>Disponibilidade sujeita à análise</span></article>',
      '<article class="ofertas__card"><span class="ofertas__icone" aria-hidden="true">↗</span><h4>DMCred</h4><p>Outras soluções de crédito que podem atender necessidades diferentes.</p><span>Disponibilidade sujeita à análise</span></article>',
      '</div></section>',
      reprovado
        ? '<form id="interesse-ofertas-form" class="ofertas__consentimento"><h3>Quer saber mais sobre outras opções?</h3><p>Se desejar receber informações por e-mail, marque a opção abaixo. O cadastro só será confirmado depois que você acessar o link enviado para seu e-mail.</p><label class="ofertas__check"><input id="aceitar-ofertas" type="checkbox" required><span>Quero receber por e-mail informações sobre outras opções e ofertas da DM.</span></label><button class="btn-primario" id="enviar-interesse-ofertas" type="submit">Quero receber informações</button><p class="ofertas__retorno" id="resultado-interesse-ofertas" role="status" aria-live="polite"></p></form>'
        : ''
    ].join("");

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

    document.getElementById("interesse-ofertas-form")?.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      const formulario = evento.currentTarget;
      if (!formulario.reportValidity()) return;
      const botao = document.getElementById("enviar-interesse-ofertas");
      const retorno = document.getElementById("resultado-interesse-ofertas");
      botao.disabled = true;
      botao.textContent = "Registrando interesse...";
      retorno.textContent = "";
      try {
        const resposta = await apiRequest("/ofertas/interesse", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            solicitacao_id: solicitacao.id,
            cpf: AppState.dados.cpf,
            email: AppState.dados.email,
            aceitar: true
          })
        });
        retorno.textContent = resposta.mensagem;
        retorno.dataset.situacao = resposta.situacao;
        if (["AGUARDANDO_CONFIRMACAO", "CONFIRMADO"].includes(resposta.situacao)) {
          botao.hidden = true;
          document.getElementById("aceitar-ofertas").disabled = true;
        }
      } catch (erro) {
        retorno.textContent = erro.message || "Não foi possível registrar seu interesse.";
        retorno.dataset.situacao = "ERRO";
      } finally {
        botao.disabled = false;
        botao.textContent = "Quero receber informações";
      }
    });
  }
};
