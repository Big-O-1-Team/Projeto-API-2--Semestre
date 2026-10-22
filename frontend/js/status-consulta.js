function iniciarConsultaStatus() {
  const formulario = document.getElementById("consulta-status-form");
  const resultado = document.getElementById("consulta-status-resultado");
  if (!formulario || !resultado) return;

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const numero = document.getElementById("numero-solicitacao").value.trim();
    const cpf = apenasNumeros(document.getElementById("cpf-consulta").value);
    const botao = formulario.querySelector('button[type="submit"]');
    resultado.hidden = false;
    resultado.textContent = "";

    if (!/^\d+$/.test(numero) || cpf.length !== 11) {
      resultado.textContent = "Informe o número da solicitação e um CPF com 11 números.";
      return;
    }

    botao.disabled = true;
    botao.textContent = "Consultando...";

    try {
      const solicitacao = await apiRequest(`/solicitacoes/${numero}?cpf=${cpf}`);
      const titulo = document.createElement("strong");
      titulo.textContent = `Solicitação #${solicitacao.id}`;
      const status = document.createElement("p");
      status.textContent = `Status: ${formatarStatus(solicitacao.status)}`;
      const cartao = document.createElement("p");
      cartao.textContent = `Cartão: ${solicitacao.tipo_cartao.replaceAll("_", " ")}`;
      resultado.replaceChildren(titulo, status, cartao);
    } catch (erro) {
      resultado.textContent = erro.message;
    } finally {
      botao.disabled = false;
      botao.textContent = "Consultar status";
    }
  });
}

document.addEventListener("DOMContentLoaded", iniciarConsultaStatus);
