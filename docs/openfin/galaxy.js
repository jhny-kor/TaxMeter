// Finance ontology "universe" — dependency-free canvas galaxy for the OpenFin hero.
// Each export domain orbits the manifest core; node size ∝ sqrt(item_count).
// IIFE-scoped: classic scripts share one global lexical scope, so an unwrapped
// top-level `const` here would collide with the same name in app.js (e.g. numberFormat).
(() => {
const MANIFEST_URL = "../opentax/finance-ontology-manifest.json";
const GOLDEN = 2.399963229728653;

const DOMAINS = {
  tax: { label: "세금·공제", color: "#7fe36d" },
  "local-government-supports": { label: "지자체 지원금", color: "#42d8e8" },
  "card-products": { label: "카드 상품", color: "#a782ff" },
  "deposit-products": { label: "정기예금", color: "#38a7ff" },
  "saving-products": { label: "적금", color: "#59c2ff" },
  "loan-products": { label: "대출", color: "#f7b733" },
  "insurance-products": { label: "보험", color: "#ff746b" },
  "finance-reference": { label: "금융 기준정보", color: "#b9c6d8" },
};

const numberFormat = new Intl.NumberFormat("ko-KR");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const stage = document.querySelector("[data-galaxy]");
if (stage) initGalaxy(stage).catch((error) => console.error("galaxy", error));

async function initGalaxy(root) {
  const canvas = root.querySelector("canvas");
  const tooltip = root.querySelector("[data-galaxy-tooltip]");
  const legend = document.querySelector("[data-galaxy-legend]");
  const ctx = canvas.getContext("2d");

  const manifest = await fetchManifest();
  const exports = (manifest.exports || []).filter((entry) => DOMAINS[entry.domain]);
  const maxCount = Math.max(1, ...exports.map((entry) => Number(entry.item_count || 0)));

  const nodes = exports.map((entry, index) => {
    const meta = DOMAINS[entry.domain];
    const count = Number(entry.item_count || 0);
    return {
      domain: entry.domain,
      label: meta.label,
      color: meta.color,
      count,
      products: Number(entry.product_count || 0),
      weight: Math.sqrt(count / maxCount),
      ringT: exports.length > 1 ? index / (exports.length - 1) : 0.5,
      angle: index * GOLDEN,
      speed: 0,
      satellites: buildSatellites(entry),
      x: 0,
      y: 0,
      r: 0,
    };
  });

  renderLegend(legend, nodes);

  let stars = [];
  let view = { w: 0, h: 0, cx: 0, cy: 0, min: 0, coreR: 0 };
  let hovered = null;
  let t = 0;

  function resize() {
    const rect = root.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    view.w = rect.width;
    view.h = rect.height;
    view.cx = rect.width / 2;
    view.cy = rect.height / 2;
    view.min = Math.min(rect.width, rect.height);
    view.coreR = Math.max(18, view.min * 0.06);
    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const starCount = Math.round((rect.width * rect.height) / 5200);
    stars = Array.from({ length: starCount }, () => ({
      x: Math.random() * rect.width,
      y: Math.random() * rect.height,
      z: 0.3 + Math.random() * 0.7,
      phase: Math.random() * Math.PI * 2,
    }));

    for (const node of nodes) {
      const orbit = view.min * (0.17 + 0.28 * node.ringT);
      node.orbit = orbit;
      node.r = 6 + 22 * node.weight;
      node.speed = (reduceMotion.matches ? 0 : 1) * (0.045 / (0.6 + node.ringT)) / 60;
    }
    if (reduceMotion.matches) draw();
  }

  function positionNodes() {
    for (const node of nodes) {
      node.angle += node.speed;
      node.x = view.cx + Math.cos(node.angle) * node.orbit;
      node.y = view.cy + Math.sin(node.angle) * node.orbit * 0.62; // slight tilt → disc
    }
  }

  function draw() {
    ctx.clearRect(0, 0, view.w, view.h);
    drawStars();
    drawOrbits();
    for (const node of nodes) drawFilament(node);
    drawCore();
    for (const node of nodes) drawNode(node);
  }

  function drawStars() {
    for (const star of stars) {
      const tw = reduceMotion.matches ? 0.7 : 0.5 + 0.5 * Math.sin(t * 0.002 + star.phase);
      ctx.globalAlpha = 0.25 + 0.55 * star.z * tw;
      ctx.fillStyle = "#cfe4ff";
      ctx.fillRect(star.x, star.y, star.z * 1.6, star.z * 1.6);
    }
    ctx.globalAlpha = 1;
  }

  function drawOrbits() {
    for (const node of nodes) {
      ctx.beginPath();
      ctx.ellipse(view.cx, view.cy, node.orbit, node.orbit * 0.62, 0, 0, Math.PI * 2);
      ctx.strokeStyle = node === hovered ? withAlpha(node.color, 0.45) : "rgba(140,170,210,0.08)";
      ctx.lineWidth = node === hovered ? 1.4 : 1;
      ctx.stroke();
    }
  }

  function drawFilament(node) {
    const grad = ctx.createLinearGradient(view.cx, view.cy, node.x, node.y);
    grad.addColorStop(0, withAlpha(node.color, 0.02));
    grad.addColorStop(1, withAlpha(node.color, node === hovered ? 0.55 : 0.22));
    ctx.beginPath();
    ctx.moveTo(view.cx, view.cy);
    ctx.lineTo(node.x, node.y);
    ctx.strokeStyle = grad;
    ctx.lineWidth = node === hovered ? 1.8 : 1;
    ctx.stroke();
  }

  function drawCore() {
    const pulse = reduceMotion.matches ? 1 : 1 + 0.06 * Math.sin(t * 0.003);
    const r = view.coreR * pulse;
    const halo = ctx.createRadialGradient(view.cx, view.cy, 0, view.cx, view.cy, r * 3.4);
    halo.addColorStop(0, "rgba(120,220,255,0.42)");
    halo.addColorStop(0.4, "rgba(80,150,255,0.14)");
    halo.addColorStop(1, "rgba(80,150,255,0)");
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(view.cx, view.cy, r * 3.4, 0, Math.PI * 2);
    ctx.fill();

    const body = ctx.createRadialGradient(view.cx - r * 0.3, view.cy - r * 0.3, r * 0.1, view.cx, view.cy, r);
    body.addColorStop(0, "#eaf6ff");
    body.addColorStop(0.5, "#68c8ff");
    body.addColorStop(1, "#1f6fd6");
    ctx.fillStyle = body;
    ctx.beginPath();
    ctx.arc(view.cx, view.cy, r, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawNode(node) {
    const active = node === hovered;
    for (const sat of node.satellites) {
      const a = reduceMotion.matches ? sat.a0 : sat.a0 + t * 0.0006 * sat.dir;
      const sx = node.x + Math.cos(a) * sat.dist;
      const sy = node.y + Math.sin(a) * sat.dist;
      ctx.globalAlpha = 0.65;
      ctx.fillStyle = node.color;
      ctx.beginPath();
      ctx.arc(sx, sy, sat.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    const glow = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.r * (active ? 3.4 : 2.6));
    glow.addColorStop(0, withAlpha(node.color, active ? 0.85 : 0.6));
    glow.addColorStop(1, withAlpha(node.color, 0));
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.r * (active ? 3.4 : 2.6), 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = node.color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.beginPath();
    ctx.arc(node.x - node.r * 0.28, node.y - node.r * 0.28, node.r * 0.32, 0, Math.PI * 2);
    ctx.fill();

    if (view.min > 520 || active) {
      ctx.font = `${active ? 600 : 500} ${active ? 15 : 13}px Inter, system-ui, sans-serif`;
      ctx.fillStyle = active ? "#ffffff" : "rgba(226,236,248,0.82)";
      ctx.textAlign = "center";
      ctx.fillText(node.label, node.x, node.y + node.r + 16);
    }
  }

  function loop(now) {
    t = now;
    if (!reduceMotion.matches) {
      positionNodes();
      draw();
    }
    requestAnimationFrame(loop);
  }

  function pickNode(px, py) {
    let best = null;
    let bestDist = Infinity;
    for (const node of nodes) {
      const d = Math.hypot(px - node.x, py - node.y);
      if (d < node.r + 14 && d < bestDist) {
        best = node;
        bestDist = d;
      }
    }
    return best;
  }

  function onMove(event) {
    const rect = canvas.getBoundingClientRect();
    const px = event.clientX - rect.left;
    const py = event.clientY - rect.top;
    const node = pickNode(px, py);
    hovered = node;
    canvas.style.cursor = node ? "pointer" : "default";
    if (node) {
      tooltip.hidden = false;
      tooltip.style.left = `${px}px`;
      tooltip.style.top = `${py}px`;
      tooltip.innerHTML =
        `<strong style="color:${node.color}">${node.label}</strong>` +
        `<span>${numberFormat.format(node.count)} items` +
        (node.products ? ` · ${numberFormat.format(node.products)} 상품` : "") +
        `</span><em>직접 조회 →</em>`;
    } else {
      tooltip.hidden = true;
    }
    if (reduceMotion.matches) draw();
  }

  canvas.addEventListener("mousemove", onMove);
  canvas.addEventListener("mouseleave", () => {
    hovered = null;
    tooltip.hidden = true;
    if (reduceMotion.matches) draw();
  });
  canvas.addEventListener("click", (event) => {
    const rect = canvas.getBoundingClientRect();
    const node = pickNode(event.clientX - rect.left, event.clientY - rect.top);
    if (node) window.location.href = `explorer.html?domain=${encodeURIComponent(node.domain)}`;
  });

  const ro = new ResizeObserver(resize);
  ro.observe(root);
  reduceMotion.addEventListener?.("change", resize);
  resize();
  requestAnimationFrame(loop);
}

function buildSatellites(entry) {
  const count = Math.min(6, Math.round(Number(entry.product_count || entry.item_count || 0) / 260));
  return Array.from({ length: count }, (_, i) => ({
    a0: (i / Math.max(1, count)) * Math.PI * 2,
    dist: 16 + i * 5,
    r: 1.4 + Math.random() * 1.6,
    dir: Math.random() > 0.5 ? 1 : -1,
  }));
}

function renderLegend(legend, nodes) {
  if (!legend) return;
  legend.innerHTML = nodes
    .map(
      (node) => `
      <a class="galaxy-chip" href="explorer.html?domain=${encodeURIComponent(node.domain)}">
        <span class="galaxy-dot" style="background:${node.color};box-shadow:0 0 10px ${node.color}"></span>
        <span class="galaxy-chip-label">${node.label}</span>
        <span class="galaxy-chip-count">${numberFormat.format(node.count)}</span>
      </a>`
    )
    .join("");
}

async function fetchManifest() {
  const res = await fetch(MANIFEST_URL, { cache: "no-store", headers: { accept: "application/json" } });
  if (!res.ok) throw new Error(`manifest ${res.status}`);
  return res.json();
}

function withAlpha(hex, alpha) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}
})();
