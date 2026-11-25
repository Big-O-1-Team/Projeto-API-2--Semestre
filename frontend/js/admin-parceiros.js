const API_URL = window.location.protocol + "//" + window.location.hostname + ":8000";
const formularioLoja = document.getElementById("loja-form");
const formularioConta = document.getElementById("conta-form");
const aviso = document.getElementById("admin-mensagem");
const registro = document.getElementById("loja-criada");
let lojaCriadaId = null;

function apresentarMensagem(texto, sucesso = false) {
  aviso.textContent = texto;
  aviso.classList.toggle("sucesso", sucesso);
}

async function requisitarAdmin(caminho, corpo) {
  const token = document.getElementById("token-admin").value.trim();
  if (!token) throw new Error("Informe a chave de acesso administrativo.");

  const resposta = await fetch(API_URL + caminho, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "x-admin-token": token
    },
    body: JSON.stringify(corpo)
  });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    const detalhe = dados.detail;
    throw new Error(typeof detalhe === "string" ? detalhe : "Não foi possível concluir o cadastro.");
  }
  return dados;
}

document.getElementById("loja-cep").addEventListener("input", (evento) => {
  const numeros = evento.target.value.replace(/\D/g, "").slice(0, 8);
  evento.target.value = numeros.replace(/(\d{5})(\d)/, "$1-$2");
});

formularioLoja.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  apresentarMensagem("");
  const dados = new FormData(formularioLoja);
  const botao = document.getElementById("cadastrar-loja");
  const cep = String(dados.get("cep") || "").replace(/\D/g, "");

  if (!document.getElementById("token-admin").value.trim()) {
    apresentarMensagem("Informe a chave de acesso administrativo.");
    document.getElementById("token-admin").focus();
    return;
  }
  if (cep.length !== 8) {
    apresentarMensagem("Informe um CEP com 8 números.");
    document.getElementById("loja-cep").focus();
    return;
  }

  botao.disabled = true;
  botao.textContent = "Cadastrando loja...";
  try {
    const loja = await requisitarAdmin("/lojas/parceiras", {
      nome: String(dados.get("nome") || "").trim(),
      estado: String(dados.get("estado") || "").trim(),
      cidade: String(dados.get("cidade") || "").trim(),
      endereco: String(dados.get("endereco") || "").trim(),
      cep,
      programa_id: dados.get("programa_id") ? Number(dados.get("programa_id")) : null,
      latitude: dados.get("latitude") ? Number(dados.get("latitude")) : null,
      longitude: dados.get("longitude") ? Number(dados.get("longitude")) : null,
      emite_cartao_credito: dados.has("emite_cartao_credito")
    });
    lojaCriadaId = loja.id;
    registro.textContent = "Loja " + loja.nome + " cadastrada com sucesso. Código #" + loja.id + ".";
    registro.hidden = false;
    formularioLoja.querySelectorAll("input, select").forEach(campo => campo.disabled = true);
    formularioLoja.querySelector("button[type=submit]").hidden = true;
    const acesso = document.getElementById("acesso-parceiro");
    acesso.hidden = false;
    acesso.scrollIntoView({ behavior: "smooth", block: "start" });
    apresentarMensagem("Agora você pode criar o acesso do responsável pela loja.", true);
  } catch (erro) {
    apresentarMensagem(erro.message);
  } finally {
    botao.disabled = false;
    botao.textContent = "Cadastrar loja";
  }
});

formularioConta.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  apresentarMensagem("");
  if (!lojaCriadaId) {
    apresentarMensagem("Cadastre primeiro a loja.");
    return;
  }
  const botao = document.getElementById("cadastrar-conta");
  botao.disabled = true;
  botao.textContent = "Criando acesso...";
  try {
    const conta = await requisitarAdmin("/parceiros/contas", {
      loja_id: lojaCriadaId,
      email: document.getElementById("conta-email").value.trim(),
      senha: document.getElementById("conta-senha").value
    });
    document.getElementById("conta-senha").value = "";
    document.getElementById("token-admin").value = "";
    formularioConta.hidden = true;
    apresentarMensagem("Acesso criado para " + conta.email + ". O parceiro já pode entrar no portal.", true);
  } catch (erro) {
    apresentarMensagem(erro.message);
  } finally {
    botao.disabled = false;
    botao.textContent = "Criar acesso";
  }
});

async function carregarProgramas() {
  const resposta = await fetch(API_URL + "/lojas/programas");
  if (!resposta.ok) throw new Error("Não foi possível consultar os programas.");
  const programas = await resposta.json();
  const seletor = document.getElementById("loja-programa");
  seletor.replaceChildren(new Option("Loja independente", ""));
  programas.forEach(p => seletor.append(new Option(p.rede + " — " + p.nome + " (#" + p.id + ")", p.id)));
}
document.getElementById("carregar-programas").addEventListener("click", () => carregarProgramas().catch(e => apresentarMensagem(e.message)));
document.getElementById("programa-form").addEventListener("submit", async evento => {
  evento.preventDefault();
  const botao = evento.currentTarget.querySelector("button");
  botao.disabled = true;
  try {
    let id = Number(document.getElementById("rede-id").value);
    if (!id) {
      const rede = await requisitarAdmin("/lojas/redes", { nome: document.getElementById("rede-nome").value.trim() });
      id = rede.id;
      document.getElementById("rede-id").value = id;
    }
    const p = await requisitarAdmin("/lojas/programas", { rede_id: id, nome: document.getElementById("programa-nome").value.trim(), modalidade: document.getElementById("programa-modalidade").value });
    await carregarProgramas();
    document.getElementById("loja-programa").value = p.id;
    apresentarMensagem("Programa cadastrado. Rede #" + id + ".", true);
  } catch (erro) {
    apresentarMensagem(erro.message);
  } finally {
    botao.disabled = false;
  }
});
carregarProgramas().catch(() => {});
