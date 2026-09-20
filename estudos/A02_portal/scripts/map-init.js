/**
 * Inicialização do mapa e da interface do painel lateral.
 *
 * Namespace global `App`, compartilhado com layers.js — o geoportal é
 * estático e sem build step, então os scripts conversam por este objeto
 * único em vez de módulos ES.
 */
window.App = {
  map: null,
  layers: {},
};

(function () {
  // Centro aproximado de Bagé/RS. É só o enquadramento inicial: a vista real
  // é ajustada por fitBounds assim que o limite municipal carrega em
  // layers.js — nenhuma coordenada do município fica "valendo" no código.
  const CENTRO_INICIAL = [-31.3314, -54.1069];
  const ZOOM_INICIAL = 10;

  const mapa = L.map("mapa", {
    center: CENTRO_INICIAL,
    zoom: ZOOM_INICIAL,
    zoomControl: true,
  });

  const camadaMapa = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa);

  // satélite alternativo (Esri World Imagery — gratuito, sem API key)
  const camadaSatelite = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      attribution:
        "Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
      maxZoom: 19,
    }
  );

  L.control.scale({ imperial: false }).addTo(mapa);

  window.App.map = mapa;
  window.App.baseLayers = { Mapa: camadaMapa, Satélite: camadaSatelite };

  // ---------- grupo "Mapa base" (rádios Mapa / Satélite) ----------

  document.getElementById("radio-base-mapa").addEventListener("change", (evento) => {
    if (!evento.target.checked) return;
    mapa.removeLayer(camadaSatelite);
    mapa.addLayer(camadaMapa);
  });

  document.getElementById("radio-base-satelite").addEventListener("change", (evento) => {
    if (!evento.target.checked) return;
    mapa.removeLayer(camadaMapa);
    mapa.addLayer(camadaSatelite);
  });

  // ---------- painel / gaveta mobile ----------

  const painel = document.getElementById("painel");
  const botaoAbrir = document.getElementById("botao-abrir-painel");
  const botaoFechar = document.getElementById("botao-fechar-painel");

  botaoAbrir.addEventListener("click", () => {
    painel.classList.add("aberto");
    botaoAbrir.setAttribute("aria-expanded", "true");
  });

  botaoFechar.addEventListener("click", () => {
    painel.classList.remove("aberto");
    botaoAbrir.setAttribute("aria-expanded", "false");
  });

  // ---------- grupos colapsáveis ----------

  document.querySelectorAll(".grupo-titulo").forEach((botao) => {
    botao.addEventListener("click", () => {
      const grupo = botao.closest(".grupo");
      const fechado = grupo.classList.toggle("fechada");
      botao.setAttribute("aria-expanded", String(!fechado));
    });
  });
})();
