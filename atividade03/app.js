const $ = seletor => document.querySelector(seletor);
const numeros = valor => String(valor || "").replace(/\D/g, "");
const cartas = { DM: "Cartão DM", LOJA_FISICA: "Cartão Loja Física", LOJA_DIGITAL: "Cartão Loja Digital" };

function aba(nome) {
  document.querySelectorAll("[data-aba]").forEach(botao => {
    const ativa = botao.dataset.aba === nome;
    botao.classList.toggle("ativa", ativa);
    botao.setAttribute("aria-selected", String(ativa));
    botao.tabIndex = ativa ? 0 : -1;
  });
  document.querySelectorAll("[role=tabpanel]").forEach(painel => {
    painel.hidden = painel.id !== `painel-${nome}`;
  });
}

document.querySelectorAll("[data-aba]").forEach(botao => {
  botao.addEventListener("click", () => aba(botao.dataset.aba));
});

function resposta(elemento, texto, estado = "") {
  elemento.textContent = texto;
  elemento.dataset.estado = estado;
}

async function requisicao(caminho, opcoes = {}) {
  let retorno;
  try {
    retorno = await fetch(caminho, opcoes);
  } catch {
    throw new Error("Não foi possível conectar à aplicação.");
  }
  const dados = await retorno.json().catch(() => ({}));
  if (!retorno.ok) throw new Error(dados.erro || "Não foi possível concluir a operação.");
  return dados;
}

function formatarCep(valor) {
  return numeros(valor).slice(0, 8).replace(/^(\d{5})(\d)/, "$1-$2");
}

function formatarCpf(valor) {
  return numeros(valor).slice(0, 11).replace(/^(\d{3})(\d)/, "$1.$2").replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3").replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
}

["#cep-busca", "#cep-pedido"].forEach(seletor => {
  $(seletor).addEventListener("input", evento => {
    evento.target.value = formatarCep(evento.target.value);
    if (seletor === "#cep-pedido") atualizarLojasPedido();
  });
});

["#cpf", "#cpf-busca"].forEach(seletor => {
  $(seletor).addEventListener("input", evento => {
    evento.target.value = formatarCpf(evento.target.value);
  });
});

$("#telefone").addEventListener("input", evento => {
  const valor = numeros(evento.target.value).slice(0, 11);
  evento.target.value = valor.length > 10
    ? valor.replace(/^(\d{2})(\d{5})(\d{4})$/, "($1) $2-$3")
    : valor.replace(/^(\d{2})(\d{4})(\d{1,4})$/, "($1) $2-$3");
});

function criarElemento(tag, classe, texto) {
  const elemento = document.createElement(tag);
  if (classe) elemento.className = classe;
  if (texto !== undefined) elemento.textContent = String(texto);
  return elemento;
}

function montarLoja(loja, cep) {
  const item = criarElemento("article", "item");
  const topo = criarElemento("div", "item__topo");
  topo.append(criarElemento("h4", "", loja.nome), criarElemento("span", "item__local", loja.uf));
  item.append(topo, criarElemento("p", "", `${loja.endereco} · ${loja.cidade}`));
  const botao = criarElemento("button", "item__acao", "Escolher esta loja");
  botao.type = "button";
  botao.addEventListener("click", async () => {
    aba("solicitar");
    $("#cep-pedido").value = formatarCep(cep);
    $("#cartao").value = "LOJA_FISICA";
    atualizarLojasPedido();
    await carregarLojasPedido(loja.id);
  });
  item.append(botao);
  return item;
}

$("#form-lojas").addEventListener("submit", async evento => {
  evento.preventDefault();
  const cep = numeros($("#cep-busca").value);
  const aviso = $("#retorno-lojas");
  const lista = $("#lista-lojas");
  lista.replaceChildren();
  if (cep.length !== 8) return resposta(aviso, "Informe um CEP com 8 números.", "erro");
  const botao = evento.currentTarget.querySelector("button");
  botao.disabled = true;
  resposta(aviso, "Buscando lojas...");
  try {
    const dados = await requisicao(`/api/lojas?cep=${encodeURIComponent(cep)}`);
    resposta(aviso, dados.total ? `${dados.total} loja(s) encontrada(s) em ${dados.uf}.` : `Nenhuma loja cadastrada em ${dados.uf}.`, "ok");
    dados.lojas.forEach(loja => lista.append(montarLoja(loja, cep)));
  } catch (erro) {
    resposta(aviso, erro.message, "erro");
  } finally {
    botao.disabled = false;
  }
});

function atualizarLojasPedido() {
  const fisico = $("#cartao").value === "LOJA_FISICA";
  $("#campo-loja").hidden = !fisico;
  $("#loja").required = fisico;
  $("#loja").replaceChildren(new Option("Consulte as lojas pelo CEP", ""));
  $("#ajuda-loja").textContent = "Escolha uma loja do mesmo estado do CEP.";
}

$("#cartao").addEventListener("change", atualizarLojasPedido);

async function carregarLojasPedido(selecionar = null) {
  const cep = numeros($("#cep-pedido").value);
  if (cep.length !== 8) {
    resposta($("#retorno-pedido"), "Informe um CEP com 8 números antes de buscar lojas.", "erro");
    return;
  }
  const botao = $("#buscar-lojas-pedido");
  botao.disabled = true;
  resposta($("#retorno-pedido"), "Buscando lojas...");
  try {
    const dados = await requisicao(`/api/lojas?cep=${encodeURIComponent(cep)}`);
    const seletor = $("#loja");
    seletor.replaceChildren(new Option("Selecione uma loja", ""));
    dados.lojas.forEach(loja => seletor.add(new Option(`${loja.nome} · ${loja.cidade}`, String(loja.id))));
    if (selecionar !== null) seletor.value = String(selecionar);
    $("#ajuda-loja").textContent = `${dados.total} loja(s) disponível(is) em ${dados.uf}.`;
    resposta($("#retorno-pedido"), dados.total ? "Lojas carregadas. Escolha uma para continuar." : "Nenhuma loja parceira disponível nesse estado.", dados.total ? "ok" : "erro");
  } catch (erro) {
    resposta($("#retorno-pedido"), erro.message, "erro");
  } finally {
    botao.disabled = false;
  }
}

$("#buscar-lojas-pedido").addEventListener("click", () => carregarLojasPedido());

$("#form-pedido").addEventListener("submit", async evento => {
  evento.preventDefault();
  const formulario = evento.currentTarget;
  if (!formulario.reportValidity()) return;
  const valores = new FormData(formulario);
  const payload = {
    nome: String(valores.get("nome") || "").trim(),
    cpf: numeros(valores.get("cpf")),
    email: String(valores.get("email") || "").trim(),
    telefone: numeros(valores.get("telefone")),
    cep: numeros(valores.get("cep")),
    cartao: String(valores.get("cartao") || ""),
    loja_id: valores.get("cartao") === "LOJA_FISICA" ? Number(valores.get("loja_id")) || null : null
  };
  const botao = $("#enviar-pedido");
  botao.disabled = true;
  $("#comprovante").hidden = true;
  resposta($("#retorno-pedido"), "Registrando solicitação...");
  try {
    const pedido = await requisicao("/api/pedidos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    resposta($("#retorno-pedido"), "Solicitação registrada com sucesso.", "ok");
    const comprovante = $("#comprovante");
    comprovante.replaceChildren(
      criarElemento("h4", "", `Pedido #${pedido.id} registrado`),
      criarElemento("p", "", `${pedido.cartao} · Status: Em análise`),
      criarElemento("p", "", "Sua solicitação foi recebida e está aguardando avaliação.")
    );
    const acompanhar = criarElemento("button", "botao", "Acompanhar pedido →");
    acompanhar.type = "button";
    acompanhar.addEventListener("click", () => {
      $("#cpf-busca").value = formatarCpf(payload.cpf);
      aba("acompanhar");
      $("#form-acompanhar").requestSubmit();
    });
    comprovante.append(acompanhar);
    comprovante.hidden = false;
  } catch (erro) {
    resposta($("#retorno-pedido"), erro.message, "erro");
  } finally {
    botao.disabled = false;
  }
});

$("#form-acompanhar").addEventListener("submit", async evento => {
  evento.preventDefault();
  const cpf = numeros($("#cpf-busca").value);
  const botao = evento.currentTarget.querySelector("button");
  const lista = $("#lista-pedidos");
  const aviso = $("#retorno-consulta");
  lista.replaceChildren();
  botao.disabled = true;
  resposta(aviso, "Consultando pedidos...");
  try {
    const pedidos = await requisicao(`/api/pedidos?cpf=${encodeURIComponent(cpf)}`);
    resposta(aviso, pedidos.length ? `${pedidos.length} solicitação(ões) encontrada(s).` : "Nenhuma solicitação encontrada para este CPF.", "ok");
    pedidos.forEach(pedido => {
      const item = criarElemento("article", "item");
      const topo = criarElemento("div", "item__topo");
      topo.append(criarElemento("h4", "", `Pedido #${pedido.id}`), criarElemento("span", "status", "Em análise"));
      item.append(topo, criarElemento("p", "", pedido.cartao));
      if (pedido.loja) item.append(criarElemento("p", "", `Loja: ${pedido.loja}`));
      item.append(criarElemento("span", "item__data", new Date(pedido.criado_em).toLocaleString("pt-BR")));
      lista.append(item);
    });
  } catch (erro) {
    resposta(aviso, erro.message, "erro");
  } finally {
    botao.disabled = false;
  }
});
