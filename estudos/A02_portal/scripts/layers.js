/**
 * Monta as camadas do geoportal a partir do catálogo.
 *
 * O portal NÃO tem lista de camadas escrita no código: ele lê
 * data/geoportal/catalogo.json (projeção de data/catalogo_camadas.csv +
 * data/catalogo_fontes.csv, gerada por scripts/geoportal/exportar_catalogo.py)
 * e, para cada camada, busca o GeoJSON correspondente em data/geoportal/,
 * insere o checkbox no grupo do tema e escreve fonte + licença no rodapé.
 *
 * Consequência prática: publicar camada nova é mexer em CSV e rodar dois
 * scripts — nunca editar index.html nem este arquivo. Enquanto um grupo não
 * tem camada no catálogo, ele mostra "nenhuma camada publicada ainda".
 */

const DIR_DADOS = "data/geoportal";

// tema do catálogo -> id do container no index.html.
// Mudar aqui exige mudar o `data-grupo`/`id` correspondente no HTML.
const CONTAINER_POR_TEMA = {
  territorio: "camadas-territorio",
  urbano: "camadas-urbano",
  mobilidade: "camadas-mobilidade",
  saude: "camadas-saude",
  educacao: "camadas-educacao",
  ambiente: "camadas-ambiente",
  nao_espacial: "camadas-nao-espacial",
};

// Estilos por id de camada. Fallback deliberado para camadas ainda sem
// estilo próprio: melhor um polígono cinza visível do que uma camada que
// carrega e não aparece.
const ESTILOS = {
  limite_municipal: {
    style: { color: "#123c26", weight: 2.5, dashArray: "4 4", fill: false },
    interactive: false,
    ligadoPorPadrao: true,
    enquadrar: true, // usa esta camada para o fitBounds inicial
  },
};

const ESTILO_PADRAO = {
  style: { color: "#5a6472", weight: 1.5, fillColor: "#5a6472", fillOpacity: 0.2 },
  ligadoPorPadrao: false,
};

async function buscarJSON(nomeArquivo) {
  const resposta = await fetch(`${DIR_DADOS}/${nomeArquivo}`);
  if (!resposta.ok) {
    throw new Error(`falha ao carregar ${nomeArquivo}: HTTP ${resposta.status}`);
  }
  return resposta.json();
}

function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto == null ? "" : String(texto);
  return div.innerHTML;
}

/** Marca como vazios os grupos temáticos que não receberam camada nenhuma. */
function marcarGruposVazios() {
  Object.values(CONTAINER_POR_TEMA).forEach((idContainer) => {
    const container = document.getElementById(idContainer);
    if (container && container.children.length === 0) {
      container.innerHTML =
        '<p class="secao-ajuda grupo-vazio">Nenhuma camada publicada ainda.</p>';
    }
  });
}

/** Rodapé: fonte, instituição e licença de cada camada publicada. */
function montarRodapeFontes(camadas) {
  const container = document.getElementById("rodape-fontes");
  if (!container) return;

  if (!camadas.length) {
    container.innerHTML = '<p class="secao-ajuda">Nenhuma camada publicada ainda.</p>';
    return;
  }

  container.innerHTML = camadas
    .map((camada) => {
      const fontes = camada.fontes.length
        ? camada.fontes
            .map(
              (fonte) => `
              <div class="fonte-linha">
                <a href="${escapar(fonte.url)}" target="_blank" rel="noopener noreferrer"
                   >${escapar(fonte.instituicao)}</a> — ${escapar(fonte.nome)}
                <span class="fonte-licenca">Licença: ${escapar(fonte.licenca)}</span>
              </div>`
            )
            .join("")
        : '<div class="fonte-linha fonte-sem-fonte">⚠ sem fonte declarada no catálogo</div>';

      const preliminar =
        camada.situacao !== "publicada"
          ? `<span class="marca-preliminar">${escapar(camada.situacao)}</span>`
          : "";

      return `
        <div class="fonte-bloco">
          <strong>${escapar(camada.nome)}</strong> ${preliminar}
          <span class="fonte-versao">v${escapar(camada.versao)} · ${escapar(camada.data)}</span>
          ${fontes}
        </div>`;
    })
    .join("");
}

/** Insere o checkbox da camada no grupo do tema e liga/desliga no mapa. */
function montarToggle(camada, layerLeaflet, ligado) {
  const mapa = window.App.map;
  const idContainer = CONTAINER_POR_TEMA[camada.tema];
  const container = idContainer ? document.getElementById(idContainer) : null;

  if (!container) {
    // tema do catálogo sem grupo correspondente no HTML: erro de catálogo, não
    // do portal — a camada é carregada mesmo assim, mas o problema fica visível
    console.warn(
      `camada '${camada.id}': tema '${camada.tema}' não tem grupo no painel ` +
        `(temas válidos: ${Object.keys(CONTAINER_POR_TEMA).join(", ")})`
    );
    return;
  }

  const rotulo = document.createElement("label");
  rotulo.className = "checkbox-linha";
  rotulo.innerHTML = `<input type="checkbox" ${ligado ? "checked" : ""} /> ${escapar(camada.nome)}`;
  container.appendChild(rotulo);

  const checkbox = rotulo.querySelector("input");
  checkbox.addEventListener("change", (evento) => {
    if (evento.target.checked) mapa.addLayer(layerLeaflet);
    else mapa.removeLayer(layerLeaflet);
  });
}

async function iniciarCamadas() {
  const mapa = window.App.map;

  try {
    const catalogo = await buscarJSON("catalogo.json");
    const camadas = catalogo.camadas || [];

    // busca todos os GeoJSON em paralelo; uma camada quebrada não derruba as
    // outras (Promise.allSettled), mas aparece no console e no painel
    const resultados = await Promise.allSettled(
      camadas.map((camada) => buscarJSON(camada.arquivo))
    );

    let camadaParaEnquadrar = null;

    camadas.forEach((camada, indice) => {
      const resultado = resultados[indice];
      if (resultado.status !== "fulfilled") {
        console.error(`camada '${camada.id}' não carregou:`, resultado.reason);
        return;
      }

      const config = ESTILOS[camada.id] || ESTILO_PADRAO;
      const layerLeaflet = L.geoJSON(resultado.value, {
        style: config.style,
        interactive: config.interactive !== false,
      });

      window.App.layers[camada.id] = layerLeaflet;

      const ligado = Boolean(config.ligadoPorPadrao);
      if (ligado) layerLeaflet.addTo(mapa);
      montarToggle(camada, layerLeaflet, ligado);

      if (config.enquadrar) camadaParaEnquadrar = layerLeaflet;
    });

    if (camadaParaEnquadrar) {
      mapa.fitBounds(camadaParaEnquadrar.getBounds(), { padding: [16, 16] });
    }

    marcarGruposVazios();
    montarRodapeFontes(camadas);

    window.dispatchEvent(new CustomEvent("acervobage:camadas-prontas"));
  } catch (erro) {
    console.error("Erro ao carregar o catálogo do geoportal:", erro);
    marcarGruposVazios();
    const rodape = document.getElementById("rodape-fontes");
    if (rodape) {
      rodape.innerHTML =
        '<p class="secao-ajuda">Não foi possível carregar o catálogo. Veja o console.</p>';
    }
  }
}

iniciarCamadas();
