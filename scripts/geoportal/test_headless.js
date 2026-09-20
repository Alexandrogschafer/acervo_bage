// Teste headless (Playwright) do esqueleto do geoportal do ACERVO_BAGE.
//
// Sobe um servidor HTTP local (fetch() de GeoJSON não funciona em file://),
// abre index.html em Chromium headless e valida:
//   - mapa Leaflet inicializado e enquadrado sobre Bagé;
//   - painel presente, com o aviso de que ainda não há camadas;
//   - NENHUMA camada carregada — o esqueleto não publica nada, e um teste que
//     não checa isso deixaria passar uma camada entrando sem catálogo;
//   - evento `acervobage:mapa-pronto` disparado;
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

// bounding box aproximado de Bagé/RS — sanidade do enquadramento, não precisão
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
        res.writeHead(200, {
          "Content-Type": MIME[path.extname(filePath)] || "application/octet-stream",
        });
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

  // registra o evento antes do carregamento, senão ele dispara antes do listener
  await page.addInitScript(() => {
    window.__mapaPronto = false;
    window.addEventListener("acervobage:mapa-pronto", () => {
      window.__mapaPronto = true;
    });
  });

  console.log(`Abrindo ${baseUrl}`);
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);

  const centro = await page.evaluate(() => {
    const c = window.App.map.getCenter();
    return { lat: c.lat, lng: c.lng };
  });

  const checks = {
    tituloOk: (await page.title()) === "ACERVO_BAGE — Geoportal",

    mapaLeafletPresente: await page.evaluate(() => {
      const el = document.getElementById("mapa");
      return !!(el && el.classList.contains("leaflet-container"));
    }),

    eventoMapaProntoDisparado: await page.evaluate(() => window.__mapaPronto === true),

    painelPresente: await page.evaluate(
      () => !!document.getElementById("painel") && !!document.getElementById("camadas")
    ),

    avisoSemCamadasVisivel: await page.evaluate(() => {
      const el = document.querySelector(".aviso");
      return !!el && el.textContent.includes("ainda sem camadas");
    }),

    // o esqueleto NÃO publica camada: App.layers tem que estar vazio
    nenhumaCamadaCarregada: await page.evaluate(
      () => window.App && Object.keys(window.App.layers).length === 0
    ),

    enquadramentoSobreBage:
      centro.lng > BBOX_BAGE.oeste && centro.lng < BBOX_BAGE.leste &&
      centro.lat > BBOX_BAGE.sul && centro.lat < BBOX_BAGE.norte,
  };

  await page.screenshot({ path: SCREENSHOT_PATH, fullPage: false });
  await browser.close();
  server.close();

  console.log("\n=== Checagens funcionais ===");
  console.log(JSON.stringify(checks, null, 2));
  console.log(`\ncentro do mapa: ${centro.lat.toFixed(4)}, ${centro.lng.toFixed(4)}`);
  console.log("\n=== Erros de console ===");
  console.log(consoleErrors.length ? consoleErrors.join("\n") : "(nenhum)");
  console.log("\n=== Exceções JS de página ===");
  console.log(pageErrors.length ? pageErrors.join("\n") : "(nenhuma)");
  console.log(`\nScreenshot: ${SCREENSHOT_PATH}`);

  const reprovadas = Object.entries(checks).filter(([, ok]) => !ok).map(([n]) => n);
  if (reprovadas.length || consoleErrors.length || pageErrors.length) {
    if (reprovadas.length) console.error(`\nChecagens reprovadas: ${reprovadas.join(", ")}`);
    console.error("FALHOU");
    process.exitCode = 1;
    return;
  }
  console.log("\nOK");
}

main();
