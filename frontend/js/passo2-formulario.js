const PassoDois = {
  render() {
    const passo = document.getElementById("passo-2");
    if (!passo) return;

    const precisaLoja = AppState.tipoCartao === "LOJA_FISICA";

    passo.innerHTML = `
      <h3 class="passo__titulo">Agora, conte um pouco sobre você</h3>
      <p class="passo__descricao">Cartão selecionado: <strong>${AppState.nomeCartao || AppState.tipoCartao}</strong></p>
      <form id="form-dados" novalidate>
        <div class="form-grid">
          <div class="campo campo--completo">
            <label for="nome">Nome completo</label>
            <input id="nome" name="nome" autocomplete="name" required minlength="3" placeholder="Digite seu nome completo">
          </div>
          <div class="campo">
            <label for="cpf">CPF</label>
            <input id="cpf" name="cpf" inputmode="numeric" required maxlength="14" placeholder="000.000.000-00">
          </div>
          <div class="campo">
            <label for="telefone">Telefone</label>
            <input id="telefone" name="telefone" inputmode="tel" required maxlength="15" placeholder="(12) 99999-9999">
          </div>
          <div class="campo campo--completo">
            <label for="email">E-mail</label>
            <input id="email" name="email" type="email" autocomplete="email" required placeholder="voce@email.com">
          </div>
          <div class="campo campo--completo">
            <label for="cep">CEP</label>
            <div class="cep-linha">
              <input id="cep" name="cep" inputmode="numeric" required maxlength="9" placeholder="00000-000">
              ${precisaLoja ? '<button type="button" class="btn-secundario" id="buscar-lojas">Buscar lojas</button>' : ""}
            </div>
          </div>
          ${precisaLoja ? `
            <div class="lojas-box" id="lojas-box">
              <strong>Lojas parceiras</strong>
              <p>Informe seu CEP e clique em “Buscar lojas”.</p>
            </div>
          ` : ""}
        </div>
        <div class="acoes-passo">
          <button type="button" class="btn-secundario" id="voltar-passo-1">Voltar</button>
          <button type="submit" class="btn-primario" id="enviar-solicitacao">Enviar solicitação</button>
        </div>
      </form>
    `;

    this.configurarMascaras();

    document.getElementById("voltar-passo-1").addEventListener("click", () => irParaPasso(1));

    if (precisaLoja) {
      document.getElementById("buscar-lojas").addEventListener("click", () => this.buscarLojas());
    }

    document.getElementById("form-dados").addEventListener("submit", (evento) => this.enviar(evento));
  },

  configurarMascaras() {
    const cpf = document.getElementById("cpf");
    const telefone = document.getElementById("telefone");
    const cep = document.getElementById("cep");

    cpf.addEventListener("input", () => {
      const valor = apenasNumeros(cpf.value).slice(0, 11);
      cpf.value = valor.replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    });

    telefone.addEventListener("input", () => {
      const valor = apenasNumeros(telefone.value).slice(0, 11);
      telefone.value = valor.length > 10
        ? valor.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3")
        : valor.replace(/(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3");
    });

    cep.addEventListener("input", () => {
      const valor = apenasNumeros(cep.value).slice(0, 8);
      cep.value = valor.replace(/(\d{5})(\d{1,3})/, "$1-$2");
      AppState.loja = null;
    });
  },

  async buscarLojas() {
    const cep = apenasNumeros(document.getElementById("cep").value);
    const box = document.getElementById("lojas-box");

    if (cep.length !== 8) {
      mostrarMensagem("Informe um CEP com 8 números antes de buscar as lojas.");
      return;
    }

    esconderMensagem();
    box.innerHTML = "<strong>Lojas parceiras</strong><p>Buscando lojas...</p>";

    try {
      const resposta = await apiRequest(`/lojas/parceiras?cep=${cep}`);

      if (!resposta.lojas.length) {
        box.innerHTML = `<strong>Lojas parceiras em ${resposta.uf}</strong><p>Nenhuma loja cadastrada para este estado no ambiente de demonstração.</p>`;
        AppState.loja = null;
        return;
      }

      box.innerHTML = `
        <strong>Lojas parceiras em ${resposta.uf}</strong>
        <p>${resposta.total} opção(ões) encontrada(s). Escolha uma para continuar.</p>
        <select id="loja-id" aria-label="Escolha uma loja parceira">
          <option value="">Selecione uma loja</option>
          ${resposta.lojas.map((loja) => `<option value="${loja.id}">${loja.nome} — ${loja.cidade}</option>`).join("")}
        </select>
      `;

      document.getElementById("loja-id").addEventListener("change", (evento) => {
        const loja = resposta.lojas.find((item) => String(item.id) === evento.target.value);
        AppState.loja = loja || null;
      });
    } catch (erro) {
      box.innerHTML = "<strong>Lojas parceiras</strong><p>Não foi possível consultar as lojas.</p>";
      mostrarMensagem(erro.message);
    }
  },

  async enviar(evento) {
    evento.preventDefault();
    esconderMensagem();

    const form = evento.currentTarget;
    if (!form.reportValidity()) return;

    const dadosForm = new FormData(form);
    const payload = {
      nome: String(dadosForm.get("nome") || "").trim(),
      cpf: apenasNumeros(dadosForm.get("cpf")),
      email: String(dadosForm.get("email") || "").trim(),
      telefone: apenasNumeros(dadosForm.get("telefone")),
      cep: apenasNumeros(dadosForm.get("cep")),
      tipo_cartao: AppState.tipoCartao,
      loja_id: AppState.loja ? AppState.loja.id : null
    };

    if (AppState.tipoCartao === "LOJA_FISICA" && !AppState.loja) {
      mostrarMensagem("Busque o CEP e escolha uma loja parceira antes de enviar.");
      return;
    }

    const botao = document.getElementById("enviar-solicitacao");
    botao.disabled = true;
    botao.textContent = "Enviando...";
    form.classList.add("loading");

    try {
      const resposta = await apiRequest("/solicitacoes/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      AppState.dados = payload;
      AppState.solicitacao = resposta;
      PassoTres.exibirResultado();
      irParaPasso(3);
    } catch (erro) {
      mostrarMensagem(erro.message);
    } finally {
      botao.disabled = false;
      botao.textContent = "Enviar solicitação";
      form.classList.remove("loading");
    }
  }
};
