import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const ler = (caminho) => readFileSync(new URL(caminho, import.meta.url), "utf8");
const html = ler("../index.html");
const css = ler("../css/formulario.css");
const backend = ler("../../backend/app/controllers/application_controller.py");
const colaboradores = ler("../../backend/app/services/collaborator_service.py");
const consulta = ler("../js/status-consulta.js");
const passo1 = ler("../js/passo1-escolha-cartao.js");
const catalogo = ler("../../backend/app/seed.py");
const passo2 = ler("../js/passo2-formulario.js");
const passo3 = ler("../js/passo3-resultado.js");

test("navegação e botões do novo design permanecem conectados", () => {
  for (const id of ["btn-solicitar-cartao", "btn-hero-solicitar", "stepper", "passo-1", "passo-2", "passo-3", "mensagem-global"]) {
    assert.ok(html.includes(`id="${id}"`), id);
  }
  for (const script of ["stepper.js", "passo1-escolha-cartao.js", "passo2-formulario.js", "passo3-resultado.js", "main.js", "status-consulta.js"]) {
    assert.ok(html.includes(`src="js/${script}"`), script);
  }
});

test("consulta exige CPF e código privado", () => {
  assert.ok(html.includes('id="cpf-consulta"'));
  assert.ok(html.includes('id="consulta-status-form"'));
  assert.ok(html.includes('id="consulta-status-resultado"'));
  assert.ok(html.includes('id="codigo-consulta"'));
  assert.ok(consulta.includes("JSON.stringify({ cpf, codigo })"));
  assert.ok(consulta.includes("/solicitacoes/consultar"));
  assert.ok(consulta.includes('method: "POST"'));
});

test("a listagem de solicitações mantém cores, cartões e paginação", () => {
  for (const classe of ["consulta-status__lista", "consulta-status__item", "consulta-status__status", "consulta-status__resumo", "consulta-status__carregar", "consulta-status__vazio"]) {
    assert.ok(css.includes(`.${classe}`), classe);
  }
  assert.ok(css.includes('data-status="APROVADO"'));
  assert.ok(css.includes('data-status="REPROVADO"'));
  assert.ok(consulta.includes("Mostrar mais solicitações"));
});

test("os três cartões, o CEP e o envio continuam disponíveis", () => {
  assert.ok(catalogo.includes('"LOJA_FISICA"'));
  assert.ok(catalogo.includes('"LOJA_DIGITAL"'));
  assert.ok(catalogo.includes('"DM"'));
  assert.ok(passo2.includes("/lojas/parceiras?"));
  assert.ok(passo2.includes("navigator.geolocation.getCurrentPosition"));
  assert.ok(passo2.includes("programa_nome"));
  assert.ok(passo2.includes('apiRequest("/solicitacoes/"'));
  assert.ok(passo3.includes('id="consultar-solicitacao"'));
  assert.ok(passo3.includes('"consulta-status-form").requestSubmit()'));
});

test("backend mantém consulta por CPF e aprovação por modalidade", () => {
  assert.ok(backend.includes('@router.post("/consultar"'));
  assert.ok(backend.includes("modalidade_autorizada(cpf, db)"));
  assert.ok(backend.includes('tipo_cartao == "DM"'));
  assert.ok(colaboradores.includes("from app.models.collaborator import Collaborator"));
});


test("página sem frases redundantes e catálogo sem opções locais", () => {
  for (const frase of ["✦ Toda história merece crédito. · Protótipo acadêmico","Uma experiência mais fácil para você01 / 03","POR QUE ESCOLHER NOSSO FLUXO","Do primeiro clique ao acompanhamento, uma jornada pensada para você saber exatamente o que fazer.","COMO FUNCIONA","Uma jornada direta, sem complicação e com todas as informações em um só lugar.","VAMOS COMEÇAR?","Escolha sua opção, informe seus dados e acompanhe o andamento da solicitação.","✦Um passo de cada vez.Simples assim.","A aprovação está sujeita à análise. Este formulário faz parte de um projeto acadêmico.","ACOMPANHE DE PERTO","Já fez sua solicitação? Informe seu CPF e o código privado recebido ao solicitar.","↗É rápido, fácil e você não precisa preencher tudo de novo.","DÚVIDAS FREQUENTES","Toda história merece crédito.","Encontre respostas rápidas para seguir com mais tranquilidade.","Uma experiência mais fácil para você","01 / 03","Toda história merece crédito.","Protótipo acadêmico Uma experiência"]) {
    assert.ok(!html.includes(frase), frase);
  }
  assert.ok(!passo1.includes("cartoesFallback"));
  assert.ok(passo1.includes('apiRequest("/cartoes/")'));
  assert.ok(passo1.includes("Tentar novamente"));
  assert.ok(html.includes('src="js/api-config.js"'));
});


test("mapa interativo está ligado ao formulário", () => {
  const mapa = ler("../js/mapa-lojas.js");
  assert.ok(html.includes('src="vendor/leaflet/leaflet.js"'));
  assert.ok(html.includes('src="js/mapa-lojas.js"'));
  assert.ok(passo2.includes("MapaLojas.exibir"));
  assert.ok(mapa.includes("L.marker"));
  assert.ok(mapa.includes('new Event("change"'));
  assert.ok(mapa.includes("OpenStreetMap"));
});
