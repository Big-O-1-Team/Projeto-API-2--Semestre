const Stepper = {
  etapas: ["Escolha", "Seus dados", "Resultado"],

  init() {
    const elemento = document.getElementById("stepper");
    if (!elemento) return;

    elemento.innerHTML = this.etapas.map((etapa, indice) => `
      <div class="stepper__item" data-stepper="${indice + 1}">
        <span class="stepper__numero">${indice + 1}</span>
        <span>${etapa}</span>
      </div>
    `).join("");

    this.atualizar(1);
  },

  atualizar(passoAtual) {
    document.querySelectorAll("[data-stepper]").forEach((item) => {
      const numero = Number(item.dataset.stepper);
      item.classList.toggle("ativo", numero === passoAtual);
      item.classList.toggle("concluido", numero < passoAtual);
      const circulo = item.querySelector(".stepper__numero");
      if (circulo) circulo.textContent = numero < passoAtual ? "✓" : String(numero);
    });
  }
};
