const API_URL = `${window.location.protocol}//${window.location.hostname}:8000`;

const AppState = {
  tipoCartao: null,
  nomeCartao: null,
  loja: null,
  dados: null,
  solicitacao: null
};

async function apiRequest(caminho, opcoes = {}) {
  const resposta = await fetch(`${API_URL}${caminho}`, opcoes);
  const dados = await resposta.json().catch(() => ({}));

  if (!resposta.ok) {
    throw new Error(dados.detail || "Não foi possível concluir a operação.");
  }

  return dados;
}

function apenasNumeros(valor) {
  return String(valor || "").replace(/\D/g, "");
}

function formatarStatus(status) {
  return String(status || "").replaceAll("_", " ").toLowerCase().replace(/(^|\s)\S/g, (letra) => letra.toUpperCase());
}

function mostrarMensagem(mensagem) {
  const elemento = document.getElementById("mensagem-global");
  if (!elemento) return;
  elemento.textContent = mensagem;
  elemento.hidden = false;
}

function esconderMensagem() {
  const elemento = document.getElementById("mensagem-global");
  if (elemento) elemento.hidden = true;
}

function irParaPasso(numero) {
  document.querySelectorAll(".passo").forEach((elemento) => {
    elemento.hidden = elemento.dataset.passo !== String(numero);
  });
  Stepper.atualizar(numero);
  esconderMensagem();
  document.getElementById("formulario")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

document.addEventListener("DOMContentLoaded", () => {
  Stepper.init();
  PassoUm.init();
  PassoTres.init();

  ["btn-solicitar-cartao", "btn-hero-solicitar"].forEach((id) => {
    document.getElementById(id)?.addEventListener("click", () => {
      document.getElementById("formulario")?.scrollIntoView({ behavior: "smooth" });
    });
  });
});
