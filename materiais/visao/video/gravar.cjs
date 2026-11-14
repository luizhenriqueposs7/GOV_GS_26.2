const {chromium} = require(process.env.CV_PLAYWRIGHT);
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {performance} = require("node:perf_hooks");

(async () => {
  const root = process.env.CV_PROJETO;
  const pasta = path.join(root, "video");
  const plano = JSON.parse(fs.readFileSync(path.join(pasta, "roteiro_visual.json"), "utf8"));
  const browser = await chromium.launch({executablePath: process.env.CV_CHROME});
  const context = await browser.newContext({
    viewport: {width: plano.canvas[0], height: plano.canvas[1]},
    locale: "pt-BR",
    recordVideo: {dir: pasta, size: {width: plano.canvas[0], height: plano.canvas[1]}},
  });
  const page = await context.newPage();
  page.setDefaultTimeout(30000);
  await page.addInitScript(() => {
    window.contagemDuranteExecucao = [];
    new MutationObserver(() => {
      const texto = document.querySelector("#progresso")?.textContent || "";
      if (texto.startsWith("Total processado ") && window.contagemDuranteExecucao.at(-1) !== texto) {
        window.contagemDuranteExecucao.push(texto);
      }
    }).observe(document, {subtree: true, childList: true, characterData: true});
  });
  const erros = [];
  page.on("pageerror", erro => erros.push(String(erro)));
  const inicio = performance.now();
  const registros = [];
  async function ate(segundo) {
    const falta = segundo * 1000 - (performance.now() - inicio);
    if (falta > 0) await page.waitForTimeout(falta);
  }
  function registrar(nome, previsto) {
    const real = (performance.now() - inicio) / 1000;
    registros.push({nome, previsto, real});
    console.log(nome, real.toFixed(2));
  }
  async function concluirImagem(arquivo, esperado) {
    await page.locator('input[name="imagens"]').setInputFiles(path.join(root, "data", arquivo));
    const respostaPendente = page.waitForResponse(r => r.request().method() === "POST");
    await page.getByRole("button", {name: "Analisar", exact: true}).click();
    const resposta = await respostaPendente;
    assert.equal(resposta.status(), 200);
    await page.waitForFunction(() => document.querySelectorAll("tbody tr").length === 1 &&
      document.querySelector("#acompanhamento").hidden);
    assert.match(await page.locator("tbody").textContent(), new RegExp(esperado));
    assert.equal(await page.getByText("FPS observado", {exact: true}).count(), 0);
  }
  try {
    await page.goto("http://127.0.0.1:8766/", {waitUntil: "load"});
    for (const evento of plano.eventos.slice(1)) {
      await ate(evento.inicio);
      if (evento.tela === "ao_vivo") {
        await page.goto("http://127.0.0.1:8765/", {waitUntil: "load"});
        registrar("inicio_execucao", evento.inicio);
        await ate(306.0);
        await page.getByRole("link", {name: "Inspeção visual"}).click();
        await ate(311.3);
        await concluirImagem("recortes/117_227_1362.jpg", "Possível fissura");
        registrar("imagem_com_fissura", 311.3);
        await ate(326.2);
        await page.evaluate(() => window.scrollTo(0, 0));
        await concluirImagem("recortes/223_2951_454.jpg", "Sem fissura sinalizada");
        registrar("imagem_sem_fissura", 326.2);
        await ate(335.0);
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.locator('input[name="video"]').setInputFiles(
          path.join(root, "demo", "monitoramento_ao_vivo.mp4"));
        await ate(345.5);
        await page.getByRole("button", {name: "Analisar", exact: true}).click();
        registrar("video_enviado", 345.5);
        await page.waitForFunction(() => {
          const n = parseInt((document.querySelector("#progresso")?.textContent || "")
            .replace("Total processado ", ""), 10);
          return n >= 25 && n < 170;
        });
        await page.locator("#acompanhamento").evaluate(el => el.scrollIntoView({block: "start"}));
        assert.equal(await page.locator("#resultado").isVisible(), false);
        await page.screenshot({path: path.join(pasta, "execucao_em_andamento.png")});
        await page.waitForFunction(() => document.querySelectorAll("tbody tr").length === 180 &&
          document.querySelector("#acompanhamento").hidden);
        const contagens = await page.evaluate(() => window.contagemDuranteExecucao);
        assert(contagens.length >= 100);
        registros.push({nome: "atualizacoes_ao_vivo", quantidade: contagens.length,
          fim: (performance.now() - inicio) / 1000});
        await ate(361.5);
        await page.locator("#resultado").evaluate(el => el.scrollIntoView({block: "start"}));
        assert.equal(await page.getByText("FPS observado", {exact: true}).count(), 1);
        await page.screenshot({path: path.join(pasta, "execucao_concluida.png")});
        await ate(369.0);
        await page.getByRole("heading", {name: "Classificação por quadro"})
          .evaluate(el => el.scrollIntoView({block: "start"}));
      } else {
        if (evento.tela === "sutis") {
          await page.goto("http://127.0.0.1:8766/?tela=sutis", {waitUntil: "load"});
        } else {
          await page.evaluate(async tela => {
            const imagem = document.querySelector("#tela");
            imagem.src = "assets/" + tela + ".png";
            await imagem.decode();
          }, evento.tela);
        }
        registrar(evento.tela, evento.inicio);
      }
    }
    await ate(plano.duracao_audio);
    assert.deepEqual(erros, []);
    const video = page.video();
    await context.close();
    await video.saveAs(path.join(pasta, "captura_completa.webm"));
    fs.writeFileSync(path.join(pasta, "verificacao_gravacao.json"),
      JSON.stringify({eventos: registros, erros}, null, 2));
    console.log("Captura contínua concluída.");
  } catch (erro) {
    await page.screenshot({path: path.join(pasta, "falha_gravacao.png")}).catch(() => {});
    throw erro;
  } finally {
    await browser.close();
  }
})().catch(erro => {console.error(erro); process.exitCode = 1;});
