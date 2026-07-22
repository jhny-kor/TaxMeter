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
      planet: buildPlanet(entry.domain, index),
      index,
      spinLon: Math.random() * Math.PI * 2,
      tex: null,
      sprite: null,
      x: 0,
      y: 0,
      r: 0,
    };
  });

  renderLegend(legend, nodes);
  for (const node of nodes) node.tex = buildTexture(node);

  let stars = [];
  let nebula = [];
  let comets = [];
  let view = { w: 0, h: 0, cx: 0, cy: 0, min: 0, coreR: 0 };
  let hovered = null;
  let t = 0;
  let frameCount = 0;

  const STAR_TINTS = ["#ffffff", "#cfe4ff", "#bcd0ff", "#ffe6c4", "#ffd3e0", "#d7ffe9"];
  const NEBULA_TINTS = ["#4326a3", "#0f5f74", "#22307f", "#6a1e63", "#0e4a5c", "#7a2b1e"];

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

    const starCount = Math.round((rect.width * rect.height) / 2600);
    stars = Array.from({ length: starCount }, () => {
      const z = 0.3 + Math.random() * 0.7;
      return {
        x: Math.random() * rect.width,
        y: Math.random() * rect.height,
        z,
        size: z * (0.6 + Math.random() * 1.1),
        color: STAR_TINTS[(Math.random() * STAR_TINTS.length) | 0],
        phase: Math.random() * Math.PI * 2,
        twSpeed: 0.0012 + Math.random() * 0.0022,
        glint: Math.random() < 0.06,
      };
    });

    nebula = Array.from({ length: 6 }, () => ({
      x: Math.random() * rect.width,
      y: Math.random() * rect.height,
      r: view.min * (0.35 + Math.random() * 0.55),
      color: NEBULA_TINTS[(Math.random() * NEBULA_TINTS.length) | 0],
      alpha: 0.1 + Math.random() * 0.12,
      vx: (Math.random() - 0.5) * 0.04,
      vy: (Math.random() - 0.5) * 0.04,
    }));

    for (const node of nodes) {
      const orbit = view.min * (0.17 + 0.28 * node.ringT);
      node.orbit = orbit;
      node.r = 6 + 22 * node.weight;
      node.speed = (reduceMotion.matches ? 0 : 1) * (0.045 / (0.6 + node.ringT)) / 60;
      renderSprite(node);
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
    drawNebula();
    drawStars();
    drawOrbits();
    for (const node of nodes) drawFilament(node);
    drawCore();
    for (const node of nodes) drawNode(node);
    drawComets();
  }

  function drawNebula() {
    ctx.globalCompositeOperation = "screen";
    for (const cloud of nebula) {
      if (!reduceMotion.matches) {
        cloud.x = wrap(cloud.x + cloud.vx, view.w);
        cloud.y = wrap(cloud.y + cloud.vy, view.h);
      }
      const g = ctx.createRadialGradient(cloud.x, cloud.y, 0, cloud.x, cloud.y, cloud.r);
      g.addColorStop(0, withAlpha(cloud.color, cloud.alpha));
      g.addColorStop(0.6, withAlpha(cloud.color, cloud.alpha * 0.35));
      g.addColorStop(1, withAlpha(cloud.color, 0));
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, view.w, view.h);
    }
    ctx.globalCompositeOperation = "source-over";
  }

  function drawStars() {
    for (const star of stars) {
      const tw = reduceMotion.matches ? 0.75 : 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t * star.twSpeed + star.phase));
      const alpha = (0.2 + 0.6 * star.z) * tw;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = star.color;
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
      ctx.fill();
      if (star.glint) {
        ctx.globalAlpha = alpha * 0.7;
        const g = star.size * 4;
        ctx.fillRect(star.x - g, star.y - 0.35, g * 2, 0.7);
        ctx.fillRect(star.x - 0.35, star.y - g, 0.7, g * 2);
      }
    }
    ctx.globalAlpha = 1;
  }

  function drawComets() {
    if (!reduceMotion.matches && comets.length < 2 && Math.random() < 0.006) {
      const fromLeft = Math.random() < 0.5;
      comets.push({
        x: fromLeft ? -30 : view.w + 30,
        y: Math.random() * view.h * 0.5,
        vx: (fromLeft ? 1 : -1) * (2.4 + Math.random() * 2),
        vy: 1.6 + Math.random() * 2,
        life: 1,
      });
    }
    for (let i = comets.length - 1; i >= 0; i--) {
      const c = comets[i];
      c.x += c.vx * 3.4;
      c.y += c.vy * 3.4;
      c.life -= 0.012;
      if (c.life <= 0 || c.y > view.h + 40 || c.x < -60 || c.x > view.w + 60) {
        comets.splice(i, 1);
        continue;
      }
      const tx = c.x - c.vx * 16;
      const ty = c.y - c.vy * 16;
      const g = ctx.createLinearGradient(c.x, c.y, tx, ty);
      g.addColorStop(0, `rgba(255,255,255,${0.9 * c.life})`);
      g.addColorStop(1, "rgba(180,220,255,0)");
      ctx.strokeStyle = g;
      ctx.lineWidth = 2;
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(c.x, c.y);
      ctx.lineTo(tx, ty);
      ctx.stroke();
      ctx.fillStyle = `rgba(255,255,255,${c.life})`;
      ctx.beginPath();
      ctx.arc(c.x, c.y, 1.7, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function wrap(value, max) {
    if (value < 0) return value + max;
    if (value > max) return value - max;
    return value;
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
    const halo = ctx.createRadialGradient(view.cx, view.cy, 0, view.cx, view.cy, r * 4.2);
    halo.addColorStop(0, "rgba(150,230,255,0.5)");
    halo.addColorStop(0.35, "rgba(90,160,255,0.16)");
    halo.addColorStop(1, "rgba(80,150,255,0)");
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(view.cx, view.cy, r * 4.2, 0, Math.PI * 2);
    ctx.fill();

    if (!reduceMotion.matches) {
      ctx.save();
      ctx.translate(view.cx, view.cy);
      ctx.rotate(t * 0.00018);
      ctx.globalCompositeOperation = "screen";
      const rays = 18;
      for (let k = 0; k < rays; k++) {
        ctx.rotate((Math.PI * 2) / rays);
        const len = r * (2.4 + 0.7 * Math.sin(t * 0.004 + k * 1.7));
        const g = ctx.createLinearGradient(0, 0, 0, -len);
        g.addColorStop(0, "rgba(150,225,255,0.22)");
        g.addColorStop(1, "rgba(150,225,255,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.moveTo(-1.4, 0);
        ctx.lineTo(1.4, 0);
        ctx.lineTo(0, -len);
        ctx.closePath();
        ctx.fill();
      }
      ctx.restore();
      ctx.globalCompositeOperation = "source-over";
    }

    const body = ctx.createRadialGradient(view.cx - r * 0.3, view.cy - r * 0.3, r * 0.1, view.cx, view.cy, r);
    body.addColorStop(0, "#ffffff");
    body.addColorStop(0.45, "#8ad6ff");
    body.addColorStop(1, "#1f6fd6");
    ctx.fillStyle = body;
    ctx.beginPath();
    ctx.arc(view.cx, view.cy, r, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawNode(node) {
    const active = node === hovered;

    if (!reduceMotion.matches) {
      const steps = 12;
      for (let s = steps; s >= 1; s--) {
        const aa = node.angle - s * 0.05;
        const tx = view.cx + Math.cos(aa) * node.orbit;
        const ty = view.cy + Math.sin(aa) * node.orbit * 0.62;
        const f = 1 - s / steps;
        ctx.globalAlpha = f * (active ? 0.5 : 0.28);
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(tx, ty, node.r * f * 0.55, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

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

    drawPlanet(node, active);

    if (view.min > 520 || active) {
      ctx.font = `${active ? 600 : 500} ${active ? 15 : 13}px Inter, system-ui, sans-serif`;
      ctx.fillStyle = active ? "#ffffff" : "rgba(226,236,248,0.82)";
      ctx.textAlign = "center";
      ctx.fillText(node.label, node.x, node.y + node.r + 16);
    }
  }

  function drawPlanet(node, active) {
    const { x, y, r, color } = node;
    const p = node.planet;
    // Light comes from the core (the sun): the lit hemisphere always faces it,
    // so the textured sphere shows real phases as it orbits.
    const dx = view.cx - x;
    const dy = view.cy - y;
    const dist = Math.hypot(dx, dy) || 1;
    const nlx = dx / dist;
    const nly = dy / dist;
    const lx = x + nlx * r * 0.55;
    const ly = y + nly * r * 0.55;

    const glowR = r * (active ? 2.6 : 2.0);
    const glow = ctx.createRadialGradient(x, y, r * 0.7, x, y, glowR);
    glow.addColorStop(0, withAlpha(color, active ? 0.42 : 0.26));
    glow.addColorStop(1, withAlpha(color, 0));
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(x, y, glowR, 0, Math.PI * 2);
    ctx.fill();

    if (p.ring) drawRing(node, "back");

    if (node.sprite) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(node.sprite, x - r, y - r, r * 2, r * 2);

      // Night-side shadow, cast from the point opposite the sun.
      const sx = x - nlx * r;
      const sy = y - nly * r;
      const shadow = ctx.createRadialGradient(lx, ly, r * 0.1, sx, sy, r * 2);
      shadow.addColorStop(0, "rgba(2,3,10,0)");
      shadow.addColorStop(0.55, "rgba(2,3,10,0.12)");
      shadow.addColorStop(0.82, "rgba(1,2,8,0.62)");
      shadow.addColorStop(1, "rgba(0,1,6,0.92)");
      ctx.fillStyle = shadow;
      ctx.fillRect(x - r, y - r, r * 2, r * 2);

      // Warm day-side illumination near the sub-solar point.
      ctx.globalCompositeOperation = "soft-light";
      const day = ctx.createRadialGradient(lx, ly, 0, lx, ly, r * 1.5);
      day.addColorStop(0, "rgba(255,248,232,0.6)");
      day.addColorStop(1, "rgba(255,248,232,0)");
      ctx.fillStyle = day;
      ctx.fillRect(x - r, y - r, r * 2, r * 2);
      ctx.globalCompositeOperation = "source-over";
      ctx.restore();
    }

    // Atmospheric limb (Fresnel rim) glowing on the lit edge.
    ctx.save();
    ctx.globalCompositeOperation = "screen";
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.lineWidth = Math.max(1.2, r * 0.12);
    const rim = ctx.createLinearGradient(lx, ly, x - nlx * r, y - nly * r);
    rim.addColorStop(0, tint(color, 0.85, 0.85));
    rim.addColorStop(0.45, tint(color, 0.25, 0.16));
    rim.addColorStop(1, tint(color, 0, 0));
    ctx.strokeStyle = rim;
    ctx.stroke();
    ctx.restore();

    // Specular glint.
    ctx.save();
    ctx.globalCompositeOperation = "screen";
    ctx.fillStyle = "rgba(255,255,255,0.45)";
    ctx.beginPath();
    ctx.arc(lx, ly, r * 0.13, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    if (p.ring) drawRing(node, "front");
  }

  function drawRing(node, part) {
    const { x, y, r, color } = node;
    const rx = r * 2.1;
    const ry = r * 0.44;
    const back = part === "back";
    ctx.save();
    ctx.beginPath();
    ctx.ellipse(x, y, rx, ry, 0, back ? Math.PI : 0, back ? Math.PI * 2 : Math.PI);
    ctx.lineWidth = r * 0.42;
    const rg = ctx.createLinearGradient(x - rx, y, x + rx, y);
    rg.addColorStop(0, tint(color, 0.2, 0));
    rg.addColorStop(0.16, tint(color, 0.35, 0.5));
    rg.addColorStop(0.5, tint(color, 0.55, 0.8));
    rg.addColorStop(0.84, tint(color, 0.35, 0.5));
    rg.addColorStop(1, tint(color, 0.2, 0));
    ctx.strokeStyle = rg;
    ctx.stroke();
    ctx.restore();
  }

  function loop(now) {
    t = now;
    if (!reduceMotion.matches) {
      positionNodes();
      // Re-render one planet's sphere per frame (round-robin) to animate axial spin cheaply.
      if (nodes.length) {
        const spinner = nodes[frameCount % nodes.length];
        spinner.spinLon += 0.09;
        renderSprite(spinner);
      }
      draw();
    }
    frameCount++;
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

  const fsBtn = root.querySelector("[data-galaxy-fullscreen]");
  if (fsBtn) {
    const syncFsLabel = () => {
      const on = document.fullscreenElement === root || root.classList.contains("galaxy-fs-fallback");
      fsBtn.textContent = on ? "⤢ 나가기" : "⤢ 전체화면";
    };
    fsBtn.addEventListener("click", () => {
      if (document.fullscreenElement) {
        document.exitFullscreen?.();
      } else if (root.classList.contains("galaxy-fs-fallback")) {
        root.classList.remove("galaxy-fs-fallback");
      } else if (root.requestFullscreen) {
        root.requestFullscreen().catch(() => {
          root.classList.add("galaxy-fs-fallback");
          syncFsLabel();
          resize();
        });
      } else {
        root.classList.add("galaxy-fs-fallback");
      }
      syncFsLabel();
      resize();
    });
    document.addEventListener("fullscreenchange", () => {
      syncFsLabel();
      resize();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && root.classList.contains("galaxy-fs-fallback")) {
        root.classList.remove("galaxy-fs-fallback");
        syncFsLabel();
        resize();
      }
    });
  }

  const ro = new ResizeObserver(resize);
  ro.observe(root);
  reduceMotion.addEventListener?.("change", resize);
  resize();
  requestAnimationFrame(loop);
}

const TEX_W = 200;
const TEX_H = 100;

function buildPlanet(domain, index) {
  const kind = ["gas", "rocky", "ice"][index % 3];
  const spotCount = kind === "gas" ? 2 + (index % 2) : kind === "rocky" ? 6 : 3;
  const spots = [];
  for (let i = 0; i < spotCount; i++) {
    spots.push({
      u: Math.random(),
      v: kind === "gas" ? 0.28 + Math.random() * 0.44 : Math.random(),
      rx: (kind === "gas" ? 0.05 + Math.random() * 0.08 : 0.03 + Math.random() * 0.06),
      ry: (kind === "gas" ? 0.03 + Math.random() * 0.04 : 0.03 + Math.random() * 0.06),
      strength: 0.4 + Math.random() * 0.45,
      light: Math.random() > 0.5,
    });
  }
  return {
    kind,
    bandCount: 3 + (index % 4),
    seed: (index * 131 + 17) % 997 / 6.1,
    spots,
    ring: domain === "finance-reference" || domain === "local-government-supports",
  };
}

// ── Procedural planet surface: equirectangular texture (value-noise fBm),
//    projected onto a sphere per-pixel with sun-tracking lighting. No deps. ──
function hexRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function lerpN(a, b, tt) {
  return a + (b - a) * tt;
}
function mixc(a, b, tt) {
  return [lerpN(a[0], b[0], tt), lerpN(a[1], b[1], tt), lerpN(a[2], b[2], tt)];
}
function lightenc(c, amt) {
  return [lerpN(c[0], 255, amt), lerpN(c[1], 255, amt), lerpN(c[2], 255, amt)];
}
function darkenc(c, amt) {
  return [c[0] * (1 - amt), c[1] * (1 - amt), c[2] * (1 - amt)];
}
function hash2(x, y) {
  let n = (x | 0) * 374761393 + (y | 0) * 668265263;
  n = (n ^ (n >> 13)) * 1274126177;
  return ((n ^ (n >> 16)) >>> 0) / 4294967295;
}
function vnoise(x, y) {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const xf = x - xi;
  const yf = y - yi;
  const u = xf * xf * (3 - 2 * xf);
  const v = yf * yf * (3 - 2 * yf);
  const a = hash2(xi, yi);
  const b = hash2(xi + 1, yi);
  const c = hash2(xi, yi + 1);
  const d = hash2(xi + 1, yi + 1);
  return a * (1 - u) * (1 - v) + b * u * (1 - v) + c * (1 - u) * v + d * u * v;
}
function fbm(x, y, oct) {
  let s = 0;
  let amp = 0.5;
  let f = 1;
  let tot = 0;
  for (let i = 0; i < oct; i++) {
    s += amp * vnoise(x * f, y * f);
    tot += amp;
    f *= 2;
    amp *= 0.5;
  }
  return s / tot;
}
function buildTexture(node) {
  const w = TEX_W;
  const h = TEX_H;
  const data = new Uint8ClampedArray(w * h * 3);
  const base = hexRgb(node.color);
  const p = node.planet;
  const s = p.seed;
  for (let j = 0; j < h; j++) {
    const v = j / (h - 1);
    for (let i = 0; i < w; i++) {
      const u = i / w;
      let col;
      if (p.kind === "gas") {
        const turb = fbm(u * 5 + s, v * 8 + s, 4);
        const bands = Math.sin(v * p.bandCount * Math.PI * 2 + turb * 5);
        col = mixc(darkenc(base, 0.34), lightenc(base, 0.4), 0.5 + 0.5 * bands);
      } else if (p.kind === "ice") {
        const n = fbm(u * 7 + s, v * 7 + s, 4);
        col = mixc(mixc(base, [210, 230, 255], 0.4), [245, 250, 255], n);
        if (v < 0.13 || v > 0.87) col = mixc(col, [255, 255, 255], 0.78);
      } else {
        const n = fbm(u * 8 + s, v * 8 + s, 5);
        const land = lightenc(base, 0.22);
        const low = darkenc(base, 0.5);
        col = n > 0.5 ? mixc(low, land, (n - 0.5) * 2) : mixc(darkenc(base, 0.62), low, n * 2);
      }
      const idx = (j * w + i) * 3;
      data[idx] = col[0];
      data[idx + 1] = col[1];
      data[idx + 2] = col[2];
    }
  }
  for (const spot of p.spots) stampSpot(data, w, h, spot, base);
  return { data, w, h };
}
function stampSpot(data, w, h, s, base) {
  const cx = s.u * w;
  const cy = s.v * h;
  const rx = Math.max(1, s.rx * w);
  const ry = Math.max(1, s.ry * h);
  const col = s.light ? lightenc(base, 0.55) : darkenc(base, 0.55);
  const j0 = Math.max(0, (cy - ry) | 0);
  const j1 = Math.min(h, (cy + ry + 1) | 0);
  const i0 = Math.max(0, (cx - rx) | 0);
  const i1 = Math.min(w, (cx + rx + 1) | 0);
  for (let j = j0; j < j1; j++) {
    for (let i = i0; i < i1; i++) {
      const dx = (i - cx) / rx;
      const dy = (j - cy) / ry;
      const d = dx * dx + dy * dy;
      if (d < 1) {
        const tt = (1 - d) * s.strength;
        const idx = (j * w + i) * 3;
        data[idx] = lerpN(data[idx], col[0], tt);
        data[idx + 1] = lerpN(data[idx + 1], col[1], tt);
        data[idx + 2] = lerpN(data[idx + 2], col[2], tt);
      }
    }
  }
}
function renderSprite(node) {
  if (!node.tex) return;
  const R = Math.max(2, Math.round(node.r));
  const D = R * 2;
  if (!node.sprite) node.sprite = document.createElement("canvas");
  if (node.sprite.width !== D) {
    node.sprite.width = D;
    node.sprite.height = D;
  }
  const sctx = node.sprite.getContext("2d");
  const img = sctx.createImageData(D, D);
  const out = img.data;
  const td = node.tex.data;
  const tw = node.tex.w;
  const th = node.tex.h;
  const spin = node.spinLon || 0;
  for (let py = 0; py < D; py++) {
    const y = (py - R + 0.5) / R;
    for (let px = 0; px < D; px++) {
      const x = (px - R + 0.5) / R;
      const d2 = x * x + y * y;
      const o = (py * D + px) * 4;
      if (d2 > 1) {
        out[o + 3] = 0;
        continue;
      }
      const nz = Math.sqrt(1 - d2);
      const lon = Math.atan2(x, nz) + spin;
      const lat = Math.asin(y < -1 ? -1 : y > 1 ? 1 : y);
      let u = (lon / (2 * Math.PI)) % 1;
      if (u < 0) u += 1;
      const vv = lat / Math.PI + 0.5;
      let ti = (u * tw) | 0;
      let tj = (vv * th) | 0;
      if (ti >= tw) ti = tw - 1;
      if (tj >= th) tj = th - 1;
      const k = (tj * tw + ti) * 3;
      const limb = 0.76 + 0.24 * nz;
      out[o] = td[k] * limb;
      out[o + 1] = td[k + 1] * limb;
      out[o + 2] = td[k + 2] * limb;
      out[o + 3] = 255;
    }
  }
  sctx.putImageData(img, 0, 0);
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

// Lighten (amt>0) or darken (amt<0) a hex color; optional alpha → rgba string.
function tint(hex, amt, alpha) {
  const n = parseInt(hex.slice(1), 16);
  let r = (n >> 16) & 255;
  let g = (n >> 8) & 255;
  let b = n & 255;
  if (amt >= 0) {
    r += (255 - r) * amt;
    g += (255 - g) * amt;
    b += (255 - b) * amt;
  } else {
    const k = 1 + amt;
    r *= k;
    g *= k;
    b *= k;
  }
  return `rgba(${r | 0}, ${g | 0}, ${b | 0}, ${alpha == null ? 1 : alpha})`;
}
})();
