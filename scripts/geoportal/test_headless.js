// Teste headless (Playwright) do geoportal do Acervo Bagé.
// Mesmo esquema do repositório ClimaPampa (uruguaiana-clima-saude): sobe um
// servidor HTTP local — fetch() de GeoJSON não funciona em file:// — abre
// index.html em Chromium headless e valida:
//   - mapa Leaflet inicializado;
//   - os 7 grupos temáticos presentes no painel;
//   - a camada do limite municipal carregada a partir do catálogo e ativa
//     no mapa, com o enquadramento caindo sobre Bagé;
//   - os grupos ainda sem camada marcados como vazios (e não quebrados);
//   - rodapé de fontes/licenças preenchido a partir do catálogo;
//   - ausência de erros de JS/console.
//
// Uso: npm run test:geoportal
// Requer Chromium do Playwright (npx playwright install chromium).

const path = require("path");
const http = require("http");
const fs = require("fs");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..", "..");
const SCREENSHOT_PATH = path.join(ROOT, "scripts", "geoportal", "geoportal-headless.png");

const MIME = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".geojson": "application/json",
};

// bounding box aproximado do município de Bagé/RS — só para confirmar que o
// fitBounds caiu no lugar certo (tolerância larga de propósito: é teste de
// sanidade do enquadramento, não de precisão geométrica)
const BBOX_BAGE = { oeste: -55.2, leste: -53.3, sul: -31.9, norte: -30.7 };

function serve() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const urlPath = decodeURIComponent(req.url.split("?")[0]);
      const filePath = path.join(ROOT, urlPath === "/" ? "index.html" : urlPath);
      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.writeHead(404);
          res.end(`not found: ${filePath}`);
          return;
        }
        const ext = path.extname(filePath);
        res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
        res.end(data);
      });
    });
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

async function main() {
  const server = await serve();
  const { port } = server.address();
  const baseUrl = `http://127.0.0.1:${port}/`;

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const consoleErrors = [];
  const pageErrors = [];

  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => pageErrors.push(String(err)));

  console.log(`Abrindo ${baseUrl}`);
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);

  const checks = {
    tituloOk: (await page.title()) === "Acervo Bagé — Geoportal Bagé/RS",

    mapaLeafletPresente: await page.evaluate(() => {
      const el = document.getElementById("mapa");
      return !!(el && el.classList.contains("leaflet-container"));
    }),

    gruposTematicosPresentes: await page.evaluate(() => {
      const esperados = ["territorio", "urbano", "mobilidade", "saude",
                         "educacao", "ambiente", "nao-espacial"];
      return esperados.every((chave) => !!document.querySelector(`.grupo[data-grupo="${chave}"]`));
    }),

    alternanciaMapaSatelitePresente: await page.evaluate(
      () => !!document.getElementById("radio-base-mapa") && !!document.getElementById("radio-base-satelite")
    ),

    limiteMunicipalNoCatalogo: await page.evaluate(
      () => !!(window.App && window.App.layers && window.App.layers.limite_municipal)
    ),

    limiteMunicipalAtivoNoMapa: await page.evaluate(
      () => window.App.map.hasLayer(window.App.layers.limite_municipal)
    ),

    limiteMunicipalComGeometria: await page.evaluate(() => {
      let feicoes = 0;
      window.App.layers.limite_municipal.eachLayer(() => {
        feicoes += 1;
      });
      return feicoes === 1;
    }),

    checkboxTerritorioMontado: await page.evaluate(
      () => document.querySelectorAll("#camadas-territorio input[type=checkbox]").length === 1
    ),

    gruposVaziosMarcados: await page.evaluate(() => {
      const vazios = ["urbano", "mobilidade", "saude", "educacao", "ambiente", "nao-espacial"];
      return vazios.every((tema) => {
        const el = document.getElementById(`camadas-${tema}`);
        return !!el && !!el.querySelector(".grupo-vazio");
      });
    }),

    rodapeFontesPreenchido: await page.evaluate(() => {
      const el = document.getElementById("rodape-fontes");
      if (!el) return false;
      const blocos = el.querySelectorAll(".fonte-bloco");
      const temLicenca = el.textContent.includes("Licença:");
      return blocos.length === 1 && temLicenca;
    }),
  };

  // o fitBounds usa a geometria real da camada: se caiu sobre Bagé, o GeoJSON
  // certo foi carregado e reprojetado corretamente para 4326
  const centro = await page.evaluate(() => {
    const c = window.App.map.getCenter();
    return { lat: c.lat, lng: c.lng };
  });
  checks.enquadramentoSobreBage =
    centro.lng > BBOX_BAGE.oeste && centro.lng < BBOX_BAGE.leste &&
    centro.lat > BBOX_BAGE.sul && centro.lat < BBOX_BAGE.norte;

  // alternância mapa/satélite muda mesmo a camada base
  await page.click("#radio-base-satelite");
  await page.waitForTimeout(400);
  checks.satelitesAtivaAoClicar = await page.evaluate(
    () => window.App.map.hasLayer(window.App.baseLayers["Satélite"]) &&
          !window.App.map.hasLayer(window.App.baseLayers.Mapa)
  );
  await page.click("#radio-base-mapa");
  await page.waitForTimeout(400);
  checks.mapaVoltaAoClicar = await page.evaluate(
    () => window.App.map.hasLayer(window.App.baseLayers.Mapa)
  );

  // desligar/ligar a camada pelo checkbox
  await page.click("#camadas-territorio input[type=checkbox]");
  await page.waitForTimeout(300);
  checks.checkboxDesligaCamada = await page.evaluate(
    () => !window.App.map.hasLayer(window.App.layers.limite_municipal)
  );
  await page.click("#camadas-territorio input[type=checkbox]");
  await page.waitForTimeout(300);
  checks.checkboxReligaCamada = await page.evaluate(
    () => window.App.map.hasLayer(window.App.layers.limite_municipal)
  );

  await page.screenshot({ path: SCREENSHOT_PATH, fullPage: false });

  await browser.close();
  server.close();

  console.log("\n=== Checagens funcionais ===");
  console.log(JSON.stringify(checks, null, 2));
  console.log(`\ncentro do mapa após fitBounds: ${centro.lat.toFixed(4)}, ${centro.lng.toFixed(4)}`);

  console.log("\n=== Erros de console ===");
  console.log(consoleErrors.length ? consoleErrors.join("\n") : "(nenhum)");

  console.log("\n=== Exceções JS de página ===");
  console.log(pageErrors.length ? pageErrors.join("\n") : "(nenhuma)");

  console.log(`\nScreenshot: ${SCREENSHOT_PATH}`);

  const reprovadas = Object.entries(checks).filter(([, ok]) => !ok).map(([nome]) => nome);
  const ok = reprovadas.length === 0 && consoleErrors.length === 0 && pageErrors.length === 0;
  if (!ok) {
    if (reprovadas.length) console.error(`\nChecagens reprovadas: ${reprovadas.join(", ")}`);
    console.error("FALHOU");
    process.exitCode = 1;
    return;
  }
  console.log("\nOK");
}

main();
