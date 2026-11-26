const PassoUm = {
  async init() {
    const passo = document.getElementById("passo-1");
    if (!passo) return;
    passo.textContent = "Carregando cartões...";
    esconderMensagem();
    try {
      const cartoes = await apiRequest("/cartoes/");
      if (!Array.isArray(cartoes) || !cartoes.length) {
        throw new Error("Nenhum cartão disponível.");
      }
      this.render(cartoes);
    } catch (_) {
      passo.replaceChildren();
      const mensagem = document.createElement("p");
      mensagem.textContent = "Não foi possível carregar os cartões.";
      const botao = document.createElement("button");
      botao.type = "button";
      botao.className = "btn-secundario";
      botao.textContent = "Tentar novamente";
      botao.addEventListener("click", () => this.init());
      passo.append(mensagem, botao);
    }
  },

  render(cartoes) {
    const passo = document.getElementById("passo-1");
    if (!passo) return;

    passo.innerHTML = `
      <h3 class="passo__titulo">Qual cartão você procura?</h3>
      
      <div class="cartoes-grid">
        ${cartoes.map((cartao) => `
          <button type="button" class="cartao-opcao" data-tipo-cartao="${escaparHtml(cartao.tipo)}">
            <span class="cartao-opcao__icone">DM</span>
            <h3>${escaparHtml(cartao.nome)}</h3>
            <p>${escaparHtml(cartao.descricao || "Selecione para continuar.")}</p>
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
