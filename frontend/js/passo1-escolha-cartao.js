const PassoUm = {
  cartoesFallback: [
    { tipo: "DM", nome: "Cartão DM", descricao: "Inicie sua solicitação do Cartão DM." },
    { tipo: "LOJA_FISICA", nome: "Cartão Loja Física", descricao: "Escolha uma loja parceira disponível no seu estado." },
    { tipo: "LOJA_DIGITAL", nome: "Cartão Loja Digital", descricao: "Registre sua solicitação para a opção digital." }
  ],

  async init() {
    let cartoes = this.cartoesFallback;

    try {
      const resposta = await apiRequest("/cartoes/");
      if (Array.isArray(resposta) && resposta.length) cartoes = resposta;
    } catch (_) {
      mostrarMensagem("Não foi possível carregar os cartões da API. As opções locais foram exibidas para continuar a demonstração.");
    }

    this.render(cartoes);
  },

  render(cartoes) {
    const passo = document.getElementById("passo-1");
    if (!passo) return;

    passo.innerHTML = `
      <h3 class="passo__titulo">Qual cartão você procura?</h3>
      <p class="passo__descricao">Escolha uma opção para continuar.</p>
      <div class="cartoes-grid">
        ${cartoes.map((cartao) => `
          <button type="button" class="cartao-opcao" data-tipo-cartao="${cartao.tipo}">
            <span class="cartao-opcao__icone">DM</span>
            <h3>${cartao.nome}</h3>
            <p>${cartao.descricao || "Selecione para continuar."}</p>
          </button>
        `).join("")}
      </div>
      <div class="acoes-passo">
        <span></span>
        <button type="button" class="btn-primario" id="continuar-passo-1" disabled>Continuar</button>
      </div>
    `;

    const botaoContinuar = document.getElementById("continuar-passo-1");

    passo.querySelectorAll("[data-tipo-cartao]").forEach((botao) => {
      botao.addEventListener("click", () => {
        passo.querySelectorAll("[data-tipo-cartao]").forEach((item) => item.classList.remove("selecionado"));
        botao.classList.add("selecionado");
        AppState.tipoCartao = botao.dataset.tipoCartao;
        AppState.nomeCartao = botao.querySelector("h3").textContent;
        botaoContinuar.disabled = false;
        esconderMensagem();
      });
    });

    botaoContinuar.addEventListener("click", () => {
      PassoDois.render();
      irParaPasso(2);
    });
  }
};
