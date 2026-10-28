function iniciarConsultaStatus() {
  const formulario = document.getElementById("consulta-status-form");
  const resultado = document.getElementById("consulta-status-resultado");
  const campoCpf = document.getElementById("cpf-consulta");
  if (!formulario || !resultado || !campoCpf) return;

  const botao = formulario.querySelector('button[type="submit"]');
  let cpfAtual = "";
  let pagina = 1;
  let carregados = 0;
  let carregando = false;

  function elemento(tag, classe, texto) {
    const item = document.createElement(tag);
    if (classe) item.className = classe;
    if (texto !== undefined) item.textContent = texto;
    return item;
  }

  function dataFormatada(data) {
    const partes = String(data || "").slice(0, 10).split("-");
    if (partes.length !== 3) return "";
    return [partes[2], partes[1], partes[0]].join("/");
  }

  function criarCartao(solicitacao) {
    const nomes = {
      DM: "Cartão DM",
      LOJA_FISICA: "Cartão Loja Física",
      LOJA_DIGITAL: "Cartão Loja Digital"
    };
    const cartao = elemento("article", "consulta-status__item");
    const topo = elemento("div", "consulta-status__item-topo");
    const nome = elemento("strong", "consulta-status__cartao", nomes[solicitacao.tipo_cartao] || "Cartão");
    const status = elemento("span", "consulta-status__status", formatarStatus(solicitacao.status));
    status.dataset.status = ["APROVADO", "REPROVADO", "EM_ANALISE"].includes(solicitacao.status)
      ? solicitacao.status
      : "EM_ANALISE";
    topo.append(nome, status);

    const detalhes = elemento("div", "consulta-status__detalhes");
    detalhes.append(elemento("span", "", `Pedido #${solicitacao.id}`));
    const data = dataFormatada(solicitacao.criado_em);
    if (data) detalhes.append(elemento("span", "", data));
    cartao.append(topo, detalhes);
    return cartao;
  }

  function mensagem(texto) {
    resultado.hidden = false;
    resultado.replaceChildren(elemento("p", "consulta-status__vazio", texto));
  }

  async function buscar(proxima = false) {
    if (carregando) return;

    const cpf = apenasNumeros(campoCpf.value);
    if (cpf.length !== 11) {
      mensagem("Informe um CPF com 11 números.");
      return;
    }

    if (!proxima || cpf !== cpfAtual) {
      pagina = 1;
      carregados = 0;
      resultado.replaceChildren();
    }

    cpfAtual = cpf;
    carregando = true;
    resultado.hidden = false;
    botao.disabled = true;
    botao.textContent = "Buscando...";

    try {
      const resposta = await apiRequest(`/solicitacoes/consultar?pagina=${pagina}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf })
      });

      if (cpf !== apenasNumeros(campoCpf.value)) return;

      const solicitacoes = Array.isArray(resposta.solicitacoes) ? resposta.solicitacoes : [];
      const total = Number(resposta.total) || 0;
      let lista = resultado.querySelector(".consulta-status__lista");

      if (pagina === 1) {
        resultado.replaceChildren();
        if (!total) {
          mensagem("Nenhuma solicitação encontrada para este CPF.");
          return;
        }

        resultado.append(elemento("p", "consulta-status__resumo", `${total} ${total === 1 ? "solicitação encontrada" : "solicitações encontradas"}`));
        lista = elemento("div", "consulta-status__lista");
        resultado.append(lista);
      }

      if (!lista) return;

      resultado.querySelector(".consulta-status__carregar")?.remove();
      solicitacoes.forEach(solicitacao => lista.append(criarCartao(solicitacao)));
      carregados += solicitacoes.length;
      pagina += 1;

      if (carregados < total && solicitacoes.length > 0) {
        const mais = elemento("button", "btn-secundario consulta-status__carregar", "Mostrar mais solicitações");
        mais.type = "button";
        mais.addEventListener("click", () => buscar(true));
        resultado.append(mais);
      }
    } catch (erro) {
      if (pagina === 1) {
        mensagem(erro.message);
      } else {
        resultado.querySelector(".consulta-status__carregar")?.remove();
        const tentar = elemento("button", "btn-secundario consulta-status__carregar", "Tentar novamente");
        tentar.type = "button";
        tentar.addEventListener("click", () => buscar(true));
        resultado.append(elemento("p", "consulta-status__vazio", erro.message), tentar);
      }
    } finally {
      carregando = false;
      botao.disabled = false;
      botao.textContent = "Buscar solicitações";
    }
  }

  campoCpf.addEventListener("input", () => {
    const numeros = apenasNumeros(campoCpf.value).slice(0, 11);
    campoCpf.value = numeros
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    if (numeros !== cpfAtual) {
      resultado.hidden = true;
      resultado.replaceChildren();
    }
  });

  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    buscar();
  });
}

document.addEventListener("DOMContentLoaded", iniciarConsultaStatus);
