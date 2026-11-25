const PassoDois = {
  render() {
    const passo = document.getElementById("passo-2");
    if (!passo) return;

    const precisaLoja = AppState.tipoCartao !== "DM";
    this.localizacao = null;
    this.buscaAtual = 0;

    AppState.loja = null;
    AppState.contribuidorId = null;
    AppState.contribuidoresCarregados = false;
    AppState.contribuidoresDisponiveis = false;

    passo.innerHTML = `
      <h3 class="passo__titulo">Agora, conte um pouco sobre você</h3>
      <p class="passo__descricao">Cartão selecionado: <strong>${escaparHtml(AppState.nomeCartao || AppState.tipoCartao)}</strong></p>
      ${AppState.tipoCartao === "LOJA_DIGITAL" ? '<p class="aviso-digital">O Cartão Loja Digital não possui emissão de via física e pode ser solicitado de qualquer estado.</p>' : ""}
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
            <div class="campo campo--completo">
              <label for="filtro-parceiros">Loja, rede ou cidade</label>
              <input id="filtro-parceiros" type="search" placeholder="Buscar por nome">
              <button type="button" class="btn-secundario" id="filtrar-parceiros">Pesquisar</button>
              ${AppState.tipoCartao === "LOJA_FISICA" ? '<button type="button" class="btn-secundario" id="usar-localizacao">Usar minha localização</button><small>A localização é opcional e usada apenas para ordenar as lojas elegíveis pelo CEP.</small>' : ""}
            </div>
            <div class="lojas-box" id="lojas-box">
              <p>Escolha uma unidade ou parceiro digital.</p>
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
      document.getElementById("filtrar-parceiros").addEventListener("click", () => this.buscarLojas());
      document.getElementById("usar-localizacao")?.addEventListener("click", () => this.usarLocalizacao());
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

      this.buscaAtual++;
      this.localizacao = null;
      AppState.loja = null;
      AppState.contribuidorId = null;
      AppState.contribuidoresCarregados = false;
      AppState.contribuidoresDisponiveis = false;

      const box = document.getElementById("lojas-box");

      if (box) {
        box.innerHTML = `
          <strong>Lojas parceiras</strong>
          <p>CEP alterado. Busque as lojas novamente.</p>
        `;
      }
    });
  },

  usarLocalizacao() {
    if (!navigator.geolocation) {
      mostrarMensagem("Localização indisponível. Busque pelo CEP.");
      return;
    }
    if (apenasNumeros(document.getElementById("cep").value).length !== 8) {
      mostrarMensagem("Informe primeiro o CEP.");
      return;
    }
    const cep = document.getElementById("cep").value;
    const botao = document.getElementById("usar-localizacao");
    botao.disabled = true;
    navigator.geolocation.getCurrentPosition(posicao => {
      botao.disabled = false;
      if (!botao.isConnected || document.getElementById("cep").value !== cep) return;
      this.localizacao = { latitude: posicao.coords.latitude, longitude: posicao.coords.longitude };
      this.buscarLojas();
    }, () => {
      botao.disabled = false;
      this.localizacao = null;
      mostrarMensagem("Não foi possível acessar sua localização. Use o CEP.");
    }, { timeout: 10000, maximumAge: 0 });
  },

  async buscarLojas(pagina = 1) {
    const cep = apenasNumeros(document.getElementById("cep").value);
    const box = document.getElementById("lojas-box");
    const modalidade = AppState.tipoCartao;
    if (cep.length !== 8) {
      mostrarMensagem("Informe um CEP com 8 números.");
      return;
    }
    const pedido = ++this.buscaAtual;
    esconderMensagem();
    AppState.loja = null;
    AppState.contribuidorId = null;
    AppState.contribuidoresCarregados = false;
    box.textContent = "Buscando lojas...";
    try {
      const params = { cep, modalidade, pagina, limite: 50, busca: document.getElementById("filtro-parceiros").value };
      let resposta;
      if (this.localizacao && modalidade === "LOJA_FISICA") {
        resposta = await apiRequest("/lojas/buscar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...params, ...this.localizacao })
        });
      } else {
        resposta = await apiRequest("/lojas/parceiras?" + new URLSearchParams(params));
      }
      if (pedido !== this.buscaAtual || !box.isConnected || apenasNumeros(document.getElementById("cep").value) !== cep || modalidade !== AppState.tipoCartao) return;
      box.replaceChildren();
      const resumo = document.createElement("p");
      resumo.textContent = resposta.total + " opção(ões) disponível(is)." + (this.localizacao ? " Distância aproximada em linha reta." : "");
      box.append(resumo);
      if (!resposta.lojas.length) return;
      const seletor = document.createElement("select");
      seletor.id = "loja-id";
      seletor.required = true;
      seletor.setAttribute("aria-label", "Escolha a unidade");
      seletor.append(new Option("Selecione uma unidade", ""));
      const grupos = new Map();
      for (const loja of resposta.lojas) {
        const nome = loja.rede_nome ? loja.rede_nome + " — " + loja.programa_nome : "Lojas independentes";
        if (!grupos.has(nome)) {
          const grupo = document.createElement("optgroup");
          grupo.label = nome;
          seletor.append(grupo);
          grupos.set(nome, grupo);
        }
        const distancia = loja.distancia_km == null ? "" : " — " + loja.distancia_km.toLocaleString("pt-BR") + " km";
        const local = modalidade === "LOJA_DIGITAL" ? "" : " — " + loja.cidade + ", " + loja.endereco;
        const opcao = new Option(loja.nome + local + distancia, String(loja.id) + ":" + (loja.programa_id || ""));
        if (this.localizacao) {
          opcao.textContent = (loja.rede_nome ? loja.rede_nome + " — " + loja.programa_nome + " — " : "") + opcao.textContent;
          seletor.append(opcao);
        } else grupos.get(nome).append(opcao);
      }
      if (this.localizacao) seletor.querySelectorAll("optgroup").forEach(g => { if (!g.children.length) g.remove(); });
      box.append(seletor);
      const navegacao = document.createElement("div");
      navegacao.className = "acoes-passo";
      for (const [texto, destino, desabilitado] of [["Anterior", pagina - 1, pagina === 1], ["Próxima", pagina + 1, pagina * resposta.limite >= resposta.total]]) {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "btn-secundario";
        b.textContent = texto;
        b.disabled = desabilitado;
        b.addEventListener("click", () => this.buscarLojas(destino));
        navegacao.append(b);
      }
      box.append(navegacao);
      const detalhe = document.createElement("p");
      detalhe.setAttribute("aria-live", "polite");
      box.append(detalhe);
      seletor.addEventListener("change", async () => {
        const loja = resposta.lojas.find(item => String(item.id) + ":" + (item.programa_id || "") === seletor.value);
        AppState.loja = loja || null;
        AppState.contribuidorId = null;
        AppState.contribuidoresCarregados = false;
        document.getElementById("contribuidores-box")?.remove();
        detalhe.textContent = loja?.programa_nome ? "Cartão: " + loja.programa_nome + ". Uma solicitação por programa compartilhado." : "";
        if (loja) await this.buscarContribuidores(loja.id);
      });
    } catch (erro) {
      if (pedido !== this.buscaAtual || !box.isConnected) return;
      box.textContent = "Não foi possível consultar as lojas.";
      mostrarMensagem(erro.message);
    }
  },

  async buscarContribuidores(lojaId) {
    const box = document.getElementById("lojas-box");
    const container = document.createElement("div");

    container.id = "contribuidores-box";
    container.textContent = "Buscando contribuidores...";
    box.appendChild(container);

    try {
      const contribuidores = await apiRequest(`/lojas/parceiras/${lojaId}/contribuidores`);

      if (AppState.loja?.id !== lojaId) return;

      AppState.contribuidoresCarregados = true;
      AppState.contribuidoresDisponiveis = contribuidores.length > 0;

      if (!contribuidores.length) {
        container.textContent = "Esta loja ainda não possui contribuidores cadastrados. A solicitação poderá continuar sem atribuição.";
        return;
      }

      container.innerHTML = `
        <div class="campo">
          <label for="contribuidor-id">Atendente responsável (opcional)</label>
          <select id="contribuidor-id">
            <option value="">Não sei informar</option>
            ${contribuidores.map(contribuidor => `<option value="${contribuidor.id}">${escaparHtml(contribuidor.nome)}</option>`).join("")}
          </select>
        </div>
      `;

      document.getElementById("contribuidor-id").addEventListener("change", (evento) => {
        AppState.contribuidorId = evento.target.value ? Number(evento.target.value) : null;
      });
    } catch (erro) {
      if (AppState.loja?.id !== lojaId) return;

      AppState.contribuidoresCarregados = true;
      AppState.contribuidorId = null;
      container.textContent = "Atendente indisponível. Você pode continuar sem atribuição.";
    }
  },

  async enviar(evento) {
    evento.preventDefault();
    esconderMensagem();

    const form = evento.currentTarget;

    if (!form.reportValidity()) return;

    if (AppState.tipoCartao !== "DM" && !AppState.loja) {
      mostrarMensagem("Busque o CEP e escolha uma loja parceira antes de enviar.");
      return;
    }

    if (AppState.tipoCartao !== "DM" && !AppState.contribuidoresCarregados) {
      mostrarMensagem("Não foi possível carregar os contribuidores. Selecione a loja novamente.");
      return;
    }

    const dadosForm = new FormData(form);
    const payload = {
      nome: String(dadosForm.get("nome") || "").trim(),
      cpf: apenasNumeros(dadosForm.get("cpf")),
      email: String(dadosForm.get("email") || "").trim(),
      telefone: apenasNumeros(dadosForm.get("telefone")),
      cep: apenasNumeros(dadosForm.get("cep")),
      tipo_cartao: AppState.tipoCartao,
      loja_id: AppState.loja ? AppState.loja.id : null,
      programa_id: AppState.loja?.programa_id || null,
      contribuidor_id: AppState.contribuidorId
    };

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
