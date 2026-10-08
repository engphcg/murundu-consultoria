#!/usr/bin/env node
/* Mede os títulos (h1, h2, h3) do index.html em várias larguras e nos dois
 * temas, e FALHA (exit 1) se achar qualquer um destes defeitos:
 *
 *   1. palavra PARTIDA entre linhas (hifenização ou quebra forçada) — detectada
 *      por Range.getClientRects: uma palavra que ocupa mais de um retângulo foi
 *      partida. É o defeito de "empreendi-/mento" e "con-/sultoria";
 *   2. título com `hyphens: auto` (a causa daquele defeito);
 *   3. título mais largo que a própria caixa (palavra que não coube e acionou a
 *      rede `overflow-wrap`);
 *   4. rolagem horizontal da página.
 *
 * ⚠️ O que esta medição NÃO enxerga: o Chromium headless não traz o dicionário
 * de hifenização do português, então `hyphens: auto` não faz nada aqui e o item
 * 1 sozinho não o pegaria. É por isso que o item 2 existe: ele confere a CAUSA.
 *
 * Uso (precisa do pacote `playwright` e de um Chromium):
 *     npm install playwright
 *     node scripts/medir_titulos.js
 * Variáveis opcionais: CHROMIUM_PATH (executável do Chromium).
 */
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const PAGINA = pathToFileURL(path.resolve(__dirname, '..', 'index.html')).href;
const LARGURAS = [320, 360, 390, 414, 600, 768, 1024, 1280, 1440, 1920];
const TEMAS = ['light', 'dark'];

function medirNaPagina() {
  const achados = [];
  const titulos = [...document.querySelectorAll('h1, h2, h3')];
  for (const h of titulos) {
    const nome = `${h.tagName} "${h.textContent.trim().replace(/\s+/g, ' ').slice(0, 40)}"`;
    if (getComputedStyle(h).hyphens === 'auto') achados.push(`${nome}: hyphens: auto`);
    if (h.scrollWidth > h.clientWidth + 1) achados.push(`${nome}: mais largo que a caixa (${h.scrollWidth} > ${h.clientWidth})`);
    const caminho = document.createTreeWalker(h, NodeFilter.SHOW_TEXT);
    let no;
    while ((no = caminho.nextNode())) {
      const re = /\S+/g;
      let m;
      while ((m = re.exec(no.nodeValue))) {
        const r = document.createRange();
        r.setStart(no, m.index);
        r.setEnd(no, m.index + m[0].length);
        const linhas = new Set([...r.getClientRects()].map((x) => Math.round(x.top)));
        if (linhas.size > 1) achados.push(`${nome}: palavra partida "${m[0]}"`);
      }
    }
  }
  if (document.documentElement.scrollWidth > innerWidth) achados.push('página com rolagem horizontal');
  return achados;
}

(async () => {
  const navegador = await chromium.launch(
    process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}
  );
  let falhas = 0;
  for (const tema of TEMAS) {
    for (const largura of LARGURAS) {
      const pagina = await navegador.newPage({ viewport: { width: largura, height: 900 }, colorScheme: tema });
      await pagina.goto(PAGINA);
      await pagina.evaluate(() => document.fonts.ready);
      const achados = await pagina.evaluate(medirNaPagina);
      falhas += achados.length;
      console.log(`${tema.padEnd(5)} ${String(largura).padStart(4)} px  ${achados.length ? 'FALHA' : 'ok'}`);
      achados.forEach((a) => console.log(`        ${a}`));
      await pagina.close();
    }
  }
  await navegador.close();
  console.log(falhas ? `\nREPROVADO: ${falhas} achado(s).` : '\nAPROVADO: nenhum título partido, hifenizado ou estourado.');
  process.exit(falhas ? 1 : 0);
})();
