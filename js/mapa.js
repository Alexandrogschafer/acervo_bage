/**
 * Geoportal do ACERVO_BAGE — inicialização do mapa.
 *
 * ESQUELETO: inicializa o Leaflet e nada mais. Nenhuma camada é carregada
 * ainda, de propósito.
 *
 * Quando houver camada publicada, ela virá de `data/geoportal/` — GeoJSON em
 * EPSG:4326, produzido pelos scripts de `scripts/geoportal/` a partir da
 * cópia principal do acervo (`data/acervo/`). O portal deve montar a lista a
 * partir do catálogo, não de uma lista escrita aqui: fonte e licença de cada
 * camada saem de `data/catalogo_camadas.csv` + `data/catalogo_fontes.csv`, e
 * duas fontes de verdade divergiriam com o tempo.
 *
 * Namespace global `App`, sem build step — os scripts conversam por ele.
 */
window.App = {
  map: null,
  layers: {},
};

(function () {
  // Enquadramento inicial de Bagé/RS. É provisório: assim que o limite
  // municipal estiver em data/geoportal/, a vista passa a ser definida por
  // fitBounds sobre a geometria real, e estas coordenadas deixam de importar.
  const CENTRO_INICIAL = [-31.3314, -54.1069];
  const ZOOM_INICIAL = 10;

  const mapa = L.map("mapa", {
    center: CENTRO_INICIAL,
    zoom: ZOOM_INICIAL,
    zoomControl: true,
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa);

  L.control.scale({ imperial: false }).addTo(mapa);

  window.App.map = mapa;

  // sinaliza que o mapa está pronto — o carregador de camadas, quando existir,
  // deve pendurar-se aqui em vez de adivinhar o momento certo
  window.dispatchEvent(new CustomEvent("acervobage:mapa-pronto"));
})();
