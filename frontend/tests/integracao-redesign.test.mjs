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

test("consulta solicita apenas CPF", () => {
  assert.ok(html.includes('id="cpf-consulta"'));
  assert.ok(html.includes('id="consulta-status-form"'));
  assert.ok(html.includes('id="consulta-status-resultado"'));
  assert.ok(!html.includes('id="numero-solicitacao"'));
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
  assert.ok(passo1.includes('"LOJA_FISICA"'));
  assert.ok(passo1.includes('"LOJA_DIGITAL"'));
  assert.ok(passo1.includes('"DM"'));
  assert.ok(passo2.includes("/lojas/parceiras?cep="));
  assert.ok(passo2.includes('apiRequest("/solicitacoes/"'));
  assert.ok(passo3.includes('id="consultar-solicitacao"'));
  assert.ok(passo3.includes('"consulta-status-form").requestSubmit()'));
});

test("backend mantém consulta por CPF e aprovação por modalidade", () => {
  assert.ok(backend.includes('@router.post("/consultar"'));
  assert.ok(backend.includes("modalidade_autorizada(cpf, db)"));
  assert.ok(backend.includes("tipo_cartao == modalidade_permitida"));
  assert.ok(colaboradores.includes("from app.models.collaborator import Collaborator"));
});
