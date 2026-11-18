const API_URL = `${window.location.protocol}//${window.location.hostname}:8000`;
let tokenParceiro = sessionStorage.getItem("token-parceiro");

const elementos = {
  login: document.getElementById("login"),
  painel: document.getElementById("painel"),
  loginForm: document.getElementById("login-form"),
  contribuidorForm: document.getElementById("contribuidor-form"),
  lista: document.getElementById("lista-contribuidores"),
  dadosLoja: document.getElementById("dados-loja"),
  mensagem: document.getElementById("mensagem"),
  sair: document.getElementById("sair")
};

function mostrarMensagem(texto, sucesso = false) {
  elementos.mensagem.textContent = texto;
  elementos.mensagem.classList.toggle("sucesso", sucesso);
}

function limparMensagem() {
  elementos.mensagem.textContent = "";
  elementos.mensagem.classList.remove("sucesso");
}

async function requisicao(caminho, opcoes = {}) {
  const headers = {
    Accept: "application/json",
    ...(opcoes.body ? { "Content-Type": "application/json" } : {}),
    ...(tokenParceiro ? { Authorization: `Bearer ${tokenParceiro}` } : {}),
    ...opcoes.headers
  };

  const resposta = await fetch(`${API_URL}${caminho}`, {
    ...opcoes,
    headers
  });

  if (resposta.status === 204) {
    if (!resposta.ok) {
      throw new Error("Não foi possível concluir a operação.");
    }
    return null;
  }

  const dados = await resposta.json().catch(() => ({}));

  if (!resposta.ok) {
    throw new Error(dados.detail || "Não foi possível concluir a operação.");
  }

  return dados;
}

function encerrarSessao() {
  tokenParceiro = null;
  sessionStorage.removeItem("token-parceiro");
  elementos.login.hidden = false;
  elementos.painel.hidden = true;
  elementos.lista.replaceChildren();
  elementos.dadosLoja.textContent = "";
  limparMensagem();
}

async function carregarPainel() {
  try {
    const conta = await requisicao("/parceiros/eu");

    elementos.dadosLoja.textContent = `Loja #${conta.loja_id} • ${conta.email}`;
    elementos.login.hidden = true;
    elementos.painel.hidden = false;

    await listarContribuidores();
  } catch (erro) {
    if (erro.message === "Sessão inválida ou expirada." ||
        erro.message === "Autenticação necessária.") {
      encerrarSessao();
    }
    mostrarMensagem(erro.message);
  }
}

async function listarContribuidores() {
  elementos.lista.textContent = "Carregando contribuidores...";

  try {
    const contribuidores = await requisicao("/parceiros/eu/contribuidores");
    elementos.lista.replaceChildren();

    if (!contribuidores.length) {
      elementos.lista.textContent = "Nenhum contribuidor cadastrado.";
      return;
    }

    contribuidores.forEach(contribuidor => {
      const item = document.createElement("div");
      item.className = "contribuidor";

      const informacoes = document.createElement("div");
      const nome = document.createElement("strong");
      const status = document.createElement("p");

      nome.textContent = contribuidor.nome;
      status.textContent = contribuidor.ativo ? "Ativo" : "Inativo";
      informacoes.append(nome, status);

      const botao = document.createElement("button");
      botao.type = "button";

      if (contribuidor.ativo) {
        botao.textContent = "Desativar";
        botao.className = "desativar";
        botao.addEventListener("click", () => desativarContribuidor(contribuidor.id));
      } else {
        botao.textContent = "Reativar";
        botao.className = "reativar";
        botao.addEventListener("click", () => reativarContribuidor(contribuidor.nome));
      }

      item.append(informacoes, botao);
      elementos.lista.appendChild(item);
    });
  } catch (erro) {
    elementos.lista.textContent = "Não foi possível carregar os contribuidores.";
    mostrarMensagem(erro.message);
  }
}

async function desativarContribuidor(id) {
  limparMensagem();

  try {
    await requisicao(`/parceiros/eu/contribuidores/${id}`, {
      method: "DELETE"
    });

    mostrarMensagem("Contribuidor desativado com sucesso.", true);
    await listarContribuidores();
  } catch (erro) {
    mostrarMensagem(erro.message);
  }
}

async function reativarContribuidor(nome) {
  limparMensagem();

  try {
    await requisicao("/parceiros/eu/contribuidores", {
      method: "POST",
      body: JSON.stringify({ nome })
    });

    mostrarMensagem("Contribuidor reativado com sucesso.", true);
    await listarContribuidores();
  } catch (erro) {
    mostrarMensagem(erro.message);
  }
}

elementos.loginForm.addEventListener("submit", async evento => {
  evento.preventDefault();
  limparMensagem();

  const botao = elementos.loginForm.querySelector("button");
  const email = document.getElementById("email").value.trim();
  const senha = document.getElementById("senha").value;

  botao.disabled = true;
  botao.textContent = "Entrando...";

  try {
    const dados = await requisicao("/parceiros/autenticar", {
      method: "POST",
      body: JSON.stringify({ email, senha })
    });

    tokenParceiro = dados.access_token;
    sessionStorage.setItem("token-parceiro", tokenParceiro);
    await carregarPainel();
  } catch (erro) {
    mostrarMensagem(erro.message);
  } finally {
    botao.disabled = false;
    botao.textContent = "Entrar";
  }
});

elementos.contribuidorForm.addEventListener("submit", async evento => {
  evento.preventDefault();
  limparMensagem();

  const campoNome = document.getElementById("nome-contribuidor");
  const nome = campoNome.value.trim();
  const botao = elementos.contribuidorForm.querySelector("button");

  if (nome.length < 3) {
    mostrarMensagem("Informe um nome com pelo menos 3 caracteres.");
    return;
  }

  botao.disabled = true;
  botao.textContent = "Cadastrando...";

  try {
    await requisicao("/parceiros/eu/contribuidores", {
      method: "POST",
      body: JSON.stringify({ nome })
    });

    campoNome.value = "";
    mostrarMensagem("Contribuidor cadastrado com sucesso.", true);
    await listarContribuidores();
  } catch (erro) {
    mostrarMensagem(erro.message);
  } finally {
    botao.disabled = false;
    botao.textContent = "Cadastrar contribuidor";
  }
});

elementos.sair.addEventListener("click", encerrarSessao);

if (tokenParceiro) {
  carregarPainel();
}
