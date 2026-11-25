import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";
import { chromium } from "playwright";

await mkdir("demonstracao", { recursive: true });
const api = "http://127.0.0.1:8000";
const web = "http://127.0.0.1:5173";
const browser = await chromium.launch({ headless: true });
const contexto = await browser.newContext({
  viewport: { width: 1280, height: 850 },
  permissions: ["geolocation"],
  geolocation: { latitude: -23.222, longitude: -45.913 },
  recordVideo: { dir: "demonstracao", size: { width: 1280, height: 850 } }
});
const pagina = await contexto.newPage();
const erros = [];
pagina.on("pageerror", erro => erros.push(erro.message));
pagina.on("response", async resposta => {
  if (resposta.url().startsWith(api) && resposta.status() >= 400) console.log(resposta.status(), resposta.url(), await resposta.text().catch(() => ""));
});

async function formulario(tipo, cpf, email) {
  await pagina.locator('[data-tipo-cartao="' + tipo + '"]').click();
  await pagina.locator("#continuar-passo-1").click();
  await pagina.locator("#nome").fill("Pessoa de Demonstração");
  await pagina.locator("#cpf").fill(cpf);
  await pagina.locator("#telefone").fill("12999998888");
  await pagina.locator("#email").fill(email);
  await pagina.locator("#cep").fill("12210000");
}

try {
  await pagina.goto(web);
  await formulario("DM", "32376226643", "teste-dm@example.com");
  await pagina.locator("#enviar-solicitacao").click();
  await pagina.locator('[data-status="APROVADO"]').first().waitFor();
  await pagina.screenshot({ path: "demonstracao/01-aprovacao.png" });
  await pagina.locator("#consultar-solicitacao").click();
  await pagina.locator(".consulta-status__item").first().waitFor();
  assert.match(await pagina.locator(".consulta-status__item").first().innerText(), /Aprovado/);
  await pagina.locator("#nova-solicitacao").click();
  await formulario("LOJA_FISICA", "98765432100", "teste-rede@example.com");
  await pagina.locator("#usar-localizacao").click();
  await pagina.locator("#loja-id option").nth(1).waitFor({ state: "attached" });
  const opcoes = await pagina.locator("#loja-id option").allTextContents();
  assert.match(opcoes[1], /Aquarius/);
  await pagina.screenshot({ path: "demonstracao/02-localizacao.png" });
  const lojas = await (await fetch(api + "/lojas/parceiras?cep=12210000")).json();
  const unidade = lojas.lojas.find(l => l.nome.includes("Aquarius"));
  const outra = lojas.lojas.find(l => l.id !== unidade.id && l.programa_id === unidade.programa_id);
  assert.ok(outra);
  await pagina.locator("#loja-id").selectOption(String(unidade.id) + ':' + unidade.programa_id);
  await pagina.locator("#contribuidores-box").getByText("sem atribuição", { exact: false }).waitFor();
  await pagina.locator("#enviar-solicitacao").click();
  await pagina.locator('#passo-3 [data-status="EM_ANALISE"]').waitFor();
  await pagina.screenshot({ path: "demonstracao/03-solicitacao.png" });

  const pedido = { nome: "Pessoa de Demonstração", cpf: "98765432100", email: "teste-rede@example.com", telefone: "12999998888", cep: "12210000", tipo_cartao: "LOJA_FISICA", loja_id: outra.id };
  const duplicada = await fetch(api + "/solicitacoes/", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(pedido) });
  assert.equal(duplicada.status, 409);
  const fora = await fetch(api + "/solicitacoes/", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({...pedido, cep: "20040020"}) });
  assert.equal(fora.status, 400);
  const concorrente = {...pedido, cpf: "52998224725", email: "concorrente@example.com"};
  const simultaneas = await Promise.all([unidade.id, outra.id].map(loja_id => fetch(api + "/solicitacoes/", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({...concorrente, loja_id})})));
  assert.deepEqual(simultaneas.map(r => r.status).sort(), [201, 409]);
  await pagina.locator("#nova-solicitacao").click();
  await formulario("LOJA_DIGITAL", "32376226643", "teste-dm@example.com");
  await pagina.locator("#buscar-lojas").click();
  await pagina.locator("#loja-id option").nth(1).waitFor({ state: "attached" });
  await pagina.locator("#loja-id").selectOption({ index: 1 });
  await pagina.locator("#contribuidores-box").getByText("sem atribuição", { exact: false }).waitFor();
  await pagina.locator("#enviar-solicitacao").click();
  await pagina.locator('#passo-3 [data-status="REPROVADO"]').waitFor();
  await pagina.screenshot({ path: "demonstracao/04-ofertas.png" });
  await pagina.locator("#aceitar-ofertas").check();
  await pagina.locator("#enviar-interesse-ofertas").click();
  await pagina.locator('#resultado-interesse-ofertas[data-situacao="PENDENTE_ENVIO"]').waitFor();
  assert.equal((await fetch(api + "/usuarios/")).status, 403);
  assert.deepEqual(erros, []);
  const celular = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await celular.goto(web);
  await celular.locator('[data-tipo-cartao="DM"]').waitFor();
  assert.ok(await celular.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1));
  await celular.screenshot({ path: "demonstracao/05-mobile.png", fullPage: true });
  await celular.close();
  console.log("Jornada MySQL + navegador aprovada (CEP simulado; SMTP não configurado).");
} catch (erro) {
  console.log("Mensagem da interface:", await pagina.locator("#mensagem-global").textContent().catch(() => ""));
  console.log("Erros JS:", erros);
  await pagina.screenshot({ path: "demonstracao/falha.png" }).catch(() => {});
  throw erro;
} finally {
  await contexto.close();
  await browser.close();
}
