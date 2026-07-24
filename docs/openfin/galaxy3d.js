// OpenFin finance-ontology universe — Three.js WebGL renderer.
// Realistic planets: procedural PBR textures (albedo/bump/roughness/clouds),
// Fresnel atmosphere shaders, Saturn rings, point-light sun with real phases.
// Textures are generated in-browser (CanvasTexture) — no external assets.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

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
  "pension-products": { label: "연금저축", color: "#2dd4bf" },
  "tax-advantaged-accounts": { label: "세제혜택 계좌", color: "#f472b6" },
  "finance-reference": { label: "금융 기준정보", color: "#b9c6d8" },
};

const numberFormat = new Intl.NumberFormat("ko-KR");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const stage = document.querySelector("[data-galaxy]");
if (stage) initGalaxy(stage).catch((error) => console.error("galaxy3d", error));

/* ── procedural noise ─────────────────────────────────────── */
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
function hexRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function lerpN(a, b, t) {
  return a + (b - a) * t;
}
function mixc(a, b, t) {
  return [lerpN(a[0], b[0], t), lerpN(a[1], b[1], t), lerpN(a[2], b[2], t)];
}
function lightenc(c, amt) {
  return [lerpN(c[0], 255, amt), lerpN(c[1], 255, amt), lerpN(c[2], 255, amt)];
}
function darkenc(c, amt) {
  return [c[0] * (1 - amt), c[1] * (1 - amt), c[2] * (1 - amt)];
}

/* ── procedural planet texture maps ───────────────────────── */
function makeCanvas(w, h) {
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  return canvas;
}

// Height field shared by albedo/bump so shading matches the surface.
function heightAt(u, v, kind, seed) {
  if (kind === "gas") {
    return fbm(u * 4 + seed, v * 9 + seed, 4);
  }
  // wrap longitude so the seam at u=0/1 is invisible
  const wrapU = Math.sin(u * Math.PI * 2) * 0.5 + 0.5;
  const wrapU2 = Math.cos(u * Math.PI * 2) * 0.5 + 0.5;
  return fbm(wrapU * 4 + wrapU2 * 4 + seed, v * 7 + seed, 5);
}

function buildMaps(node) {
  const W = 512;
  const H = 256;
  const p = node.planet;
  const base = hexRgb(node.color);
  const albedo = makeCanvas(W, H);
  const bump = makeCanvas(W, H);
  const actx = albedo.getContext("2d");
  const bctx = bump.getContext("2d");
  const aimg = actx.createImageData(W, H);
  const bimg = bctx.createImageData(W, H);
  const seed = p.seed;

  for (let j = 0; j < H; j++) {
    const v = j / (H - 1);
    for (let i = 0; i < W; i++) {
      const u = i / W;
      let col;
      let height;
      if (p.kind === "gas") {
        const turb = fbm(u * 5 + seed, v * 8 + seed, 4);
        const swirl = Math.sin(v * p.bandCount * Math.PI * 2 + turb * 5.2);
        const tt = 0.5 + 0.5 * swirl;
        col = mixc(darkenc(base, 0.38), lightenc(base, 0.44), tt);
        // fine streaks along bands
        const streak = fbm(u * 24 + seed, v * 60, 3);
        col = mixc(col, lightenc(base, 0.2), streak * 0.25);
        height = 0.5 + 0.08 * swirl;
      } else if (p.kind === "ice") {
        const n = heightAt(u, v, p.kind, seed);
        col = mixc(mixc(base, [208, 228, 255], 0.45), [246, 251, 255], n);
        const crack = fbm(u * 30 + seed, v * 30 + seed, 3);
        if (crack > 0.62) col = mixc(col, darkenc(base, 0.25), (crack - 0.62) * 1.6);
        if (v < 0.13 || v > 0.87) col = mixc(col, [255, 255, 255], 0.8);
        height = 0.4 + n * 0.35;
      } else {
        const n = heightAt(u, v, p.kind, seed);
        const land = lightenc(base, 0.24);
        const low = darkenc(base, 0.52);
        col = n > 0.5 ? mixc(low, land, (n - 0.5) * 2) : mixc(darkenc(base, 0.66), low, n * 2);
        height = n;
      }
      const k = (j * W + i) * 4;
      aimg.data[k] = col[0];
      aimg.data[k + 1] = col[1];
      aimg.data[k + 2] = col[2];
      aimg.data[k + 3] = 255;
      const hv = Math.max(0, Math.min(255, height * 255));
      bimg.data[k] = hv;
      bimg.data[k + 1] = hv;
      bimg.data[k + 2] = hv;
      bimg.data[k + 3] = 255;
    }
  }

  // storm spots / craters
  for (const s of p.spots) {
    const cx = s.u * W;
    const cy = s.v * H;
    const rx = Math.max(2, s.rx * W);
    const ry = Math.max(2, s.ry * H);
    const col = s.light ? lightenc(base, 0.55) : darkenc(base, 0.55);
    for (let j = Math.max(0, (cy - ry) | 0); j < Math.min(H, (cy + ry + 1) | 0); j++) {
      for (let i = Math.max(0, (cx - rx) | 0); i < Math.min(W, (cx + rx + 1) | 0); i++) {
        const dx = (i - cx) / rx;
        const dy = (j - cy) / ry;
        const d = dx * dx + dy * dy;
        if (d < 1) {
          const t = (1 - d) * s.strength;
          const k = (j * W + i) * 4;
          aimg.data[k] = lerpN(aimg.data[k], col[0], t);
          aimg.data[k + 1] = lerpN(aimg.data[k + 1], col[1], t);
          aimg.data[k + 2] = lerpN(aimg.data[k + 2], col[2], t);
          if (p.kind === "rocky") {
            // crater rim: depress center, raise edge
            const rim = d > 0.55 ? 40 : -50;
            bimg.data[k] = Math.max(0, Math.min(255, bimg.data[k] + rim * s.strength));
          }
        }
      }
    }
  }

  actx.putImageData(aimg, 0, 0);
  bctx.putImageData(bimg, 0, 0);
  return { albedo, bump };
}

function buildCloudMap(seed) {
  const W = 256;
  const H = 128;
  const canvas = makeCanvas(W, H);
  const ctx2 = canvas.getContext("2d");
  const img = ctx2.createImageData(W, H);
  for (let j = 0; j < H; j++) {
    const v = j / (H - 1);
    for (let i = 0; i < W; i++) {
      const u = i / W;
      const n = fbm(u * 6 + seed, v * 6 + seed, 5);
      const c = Math.max(0, (n - 0.52) * 3.2);
      const a = Math.min(1, c) * 235;
      const k = (j * W + i) * 4;
      img.data[k] = 255;
      img.data[k + 1] = 255;
      img.data[k + 2] = 255;
      img.data[k + 3] = a;
    }
  }
  ctx2.putImageData(img, 0, 0);
  return canvas;
}

function buildRingMap(color) {
  // 1D radial stripes; ring geometry UVs are remapped so u = radial fraction.
  const W = 256;
  const canvas = makeCanvas(W, 4);
  const ctx2 = canvas.getContext("2d");
  const base = hexRgb(color);
  for (let i = 0; i < W; i++) {
    const t = i / (W - 1);
    const stripes = fbm(t * 22, 0.5, 3);
    const gap = t > 0.42 && t < 0.5 ? 0.15 : 1; // Cassini-like division
    const alpha = Math.max(0, Math.sin(t * Math.PI)) * (0.35 + stripes * 0.65) * gap;
    const col = mixc(lightenc(base, 0.45), darkenc(base, 0.1), stripes);
    ctx2.fillStyle = `rgba(${col[0] | 0}, ${col[1] | 0}, ${col[2] | 0}, ${alpha})`;
    ctx2.fillRect(i, 0, 1, 4);
  }
  return canvas;
}

function glowTexture(inner, outer) {
  const size = 256;
  const canvas = makeCanvas(size, size);
  const ctx2 = canvas.getContext("2d");
  const g = ctx2.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, inner);
  g.addColorStop(0.35, outer);
  g.addColorStop(1, "rgba(0,0,0,0)");
  ctx2.fillStyle = g;
  ctx2.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(canvas);
}

function labelSprite(text, count) {
  const pad = 8;
  const canvas = makeCanvas(4, 4);
  const ctx2 = canvas.getContext("2d");
  ctx2.font = "600 26px Inter, system-ui, sans-serif";
  const w1 = ctx2.measureText(text).width;
  ctx2.font = "400 19px Inter, system-ui, sans-serif";
  const w2 = ctx2.measureText(count).width;
  const w = Math.ceil(Math.max(w1, w2)) + pad * 2;
  canvas.width = w;
  canvas.height = 62;
  const c = canvas.getContext("2d");
  c.textAlign = "center";
  c.shadowColor = "rgba(0,0,0,0.9)";
  c.shadowBlur = 6;
  c.font = "600 26px Inter, system-ui, sans-serif";
  c.fillStyle = "rgba(235,243,252,0.95)";
  c.fillText(text, w / 2, 26);
  c.font = "400 19px Inter, system-ui, sans-serif";
  c.fillStyle = "rgba(170,190,214,0.9)";
  c.fillText(count, w / 2, 52);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: tex,
      transparent: true,
      depthTest: false,
      opacity: 0.95,
      sizeAttenuation: false, // constant on-screen size regardless of camera distance
    })
  );
  sprite.scale.set(w / 900, 62 / 900, 1);
  return sprite;
}

/* ── atmosphere shader (fresnel, sun at origin) ───────────── */
const ATMO_VERT = `
  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  void main() {
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPosition.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    gl_Position = projectionMatrix * viewMatrix * worldPosition;
  }
`;
const ATMO_FRAG = `
  uniform vec3 atmosphereColor;
  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  void main() {
    vec3 normalDirection = normalize(vWorldNormal);
    vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
    // sun sits at the world origin
    vec3 sunDirection = normalize(-vWorldPosition);
    float fresnel = pow(1.0 - max(dot(normalDirection, viewDirection), 0.0), 3.0);
    float sunFactor = smoothstep(-0.35, 0.45, dot(normalDirection, sunDirection));
    float alpha = fresnel * mix(0.05, 0.65, sunFactor);
    vec3 finalColor = atmosphereColor * mix(0.35, 1.3, sunFactor);
    gl_FragColor = vec4(finalColor, alpha);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }
`;

function buildPlanetSpec(domain, index) {
  const kind = ["gas", "rocky", "ice"][index % 3];
  const spotCount = kind === "gas" ? 2 + (index % 2) : kind === "rocky" ? 7 : 3;
  const spots = [];
  for (let i = 0; i < spotCount; i++) {
    spots.push({
      u: Math.random(),
      v: kind === "gas" ? 0.28 + Math.random() * 0.44 : Math.random(),
      rx: kind === "gas" ? 0.04 + Math.random() * 0.06 : 0.015 + Math.random() * 0.035,
      ry: kind === "gas" ? 0.025 + Math.random() * 0.035 : 0.015 + Math.random() * 0.035,
      strength: 0.4 + Math.random() * 0.45,
      light: Math.random() > 0.5,
    });
  }
  return {
    kind,
    bandCount: 3 + (index % 4),
    seed: ((index * 131 + 17) % 997) / 6.1,
    spots,
    ring: domain === "finance-reference" || domain === "local-government-supports",
  };
}

/* ── main ─────────────────────────────────────────────────── */
async function initGalaxy(root) {
  const canvas = root.querySelector("canvas");
  const tooltip = root.querySelector("[data-galaxy-tooltip]");
  const legend = document.querySelector("[data-galaxy-legend]");

  const manifest = await fetchManifest();
  const exportsList = (manifest.exports || []).filter((entry) => DOMAINS[entry.domain]);
  const maxCount = Math.max(1, ...exportsList.map((entry) => Number(entry.item_count || 0)));

  const nodes = exportsList.map((entry, index) => {
    const meta = DOMAINS[entry.domain];
    const count = Number(entry.item_count || 0);
    return {
      domain: entry.domain,
      label: meta.label,
      color: meta.color,
      count,
      products: Number(entry.product_count || 0),
      weight: Math.sqrt(count / maxCount),
      ringT: exportsList.length > 1 ? index / (exportsList.length - 1) : 0.5,
      angle: index * GOLDEN,
      planet: buildPlanetSpec(entry.domain, index),
    };
  });

  renderLegend(legend, nodes);

  /* renderer */
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 600);
  camera.position.set(0, 13, 27);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.enablePan = false;
  controls.minDistance = 7;
  controls.maxDistance = 90;
  controls.maxPolarAngle = 1.48;
  controls.autoRotate = !reduceMotion.matches;
  controls.autoRotateSpeed = 0.25;

  /* lights */
  scene.add(new THREE.AmbientLight(0x9fb3d8, 0.65));
  const sunLight = new THREE.PointLight(0xfff2dd, 3.2, 0, 0); // decay 0: even brightness across orbits
  scene.add(sunLight);

  /* sun */
  const sun = new THREE.Mesh(
    new THREE.SphereGeometry(2, 48, 24),
    new THREE.MeshBasicMaterial({ color: 0xeaf6ff })
  );
  scene.add(sun);
  const sunGlow = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture("rgba(190,235,255,0.95)", "rgba(90,160,255,0.28)"),
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
  );
  sunGlow.scale.set(11, 11, 1);
  scene.add(sunGlow);

  /* stars */
  scene.add(buildStars());

  /* orbit lines + planets */
  const maxAniso = renderer.capabilities.getMaxAnisotropy();
  const pickMeshes = [];
  for (const node of nodes) {
    node.orbitRadius = 6.5 + node.ringT * 13;
    node.orbitSpeed = 0.10 / (0.6 + node.ringT);
    node.radius = 0.55 + 1.35 * node.weight;

    const orbitLine = buildOrbitLine(node.orbitRadius);
    node.orbitLine = orbitLine;
    scene.add(orbitLine);

    const group = new THREE.Group();
    node.group = group;
    scene.add(group);

    const maps = buildMaps(node);
    const albedoTex = new THREE.CanvasTexture(maps.albedo);
    albedoTex.colorSpace = THREE.SRGBColorSpace;
    albedoTex.anisotropy = maxAniso;
    albedoTex.wrapS = THREE.RepeatWrapping;
    const bumpTex = new THREE.CanvasTexture(maps.bump);
    bumpTex.wrapS = THREE.RepeatWrapping;

    const material = new THREE.MeshStandardMaterial({
      map: albedoTex,
      bumpMap: bumpTex,
      bumpScale: node.planet.kind === "gas" ? 0.4 : 1.6,
      metalness: 0,
      roughness: node.planet.kind === "ice" ? 0.55 : 0.95,
    });
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(node.radius, 64, 32), material);
    mesh.userData.node = node;
    node.mesh = mesh;
    group.add(mesh);
    pickMeshes.push(mesh);

    // atmosphere
    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(node.radius * 1.09, 48, 24),
      new THREE.ShaderMaterial({
        uniforms: { atmosphereColor: { value: new THREE.Color(node.color) } },
        vertexShader: ATMO_VERT,
        fragmentShader: ATMO_FRAG,
        side: THREE.BackSide,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      })
    );
    node.atmosphere = atmosphere;
    group.add(atmosphere);

    // clouds on ice worlds, drifting at their own speed
    if (node.planet.kind === "ice") {
      const cloudTex = new THREE.CanvasTexture(buildCloudMap(node.planet.seed + 3.7));
      cloudTex.colorSpace = THREE.SRGBColorSpace;
      cloudTex.wrapS = THREE.RepeatWrapping;
      const clouds = new THREE.Mesh(
        new THREE.SphereGeometry(node.radius * 1.02, 48, 24),
        new THREE.MeshStandardMaterial({
          map: cloudTex,
          transparent: true,
          opacity: 0.85,
          depthWrite: false,
          metalness: 0,
          roughness: 1,
        })
      );
      node.clouds = clouds;
      group.add(clouds);
    }

    // Saturn-style ring
    if (node.planet.ring) {
      const ringGeo = new THREE.RingGeometry(node.radius * 1.55, node.radius * 2.6, 128, 1);
      remapRingUv(ringGeo, node.radius * 1.55, node.radius * 2.6);
      const ringTex = new THREE.CanvasTexture(buildRingMap(node.color));
      ringTex.colorSpace = THREE.SRGBColorSpace;
      const ring = new THREE.Mesh(
        ringGeo,
        new THREE.MeshBasicMaterial({
          map: ringTex,
          side: THREE.DoubleSide,
          transparent: true,
          depthWrite: false,
        })
      );
      ring.rotation.x = Math.PI / 2 - 0.22;
      group.add(ring);
    }

    // floating label
    const label = labelSprite(node.label, `${numberFormat.format(node.count)} items`);
    label.position.y = node.radius * 1.6 + 1.1;
    group.add(label);

    // planets tilt slightly, like the real thing
    mesh.rotation.z = (Math.random() - 0.5) * 0.4;
  }

  /* resize */
  function resize() {
    const rect = root.getBoundingClientRect();
    const w = Math.max(1, rect.width);
    const h = Math.max(1, rect.height);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  const ro = new ResizeObserver(resize);
  ro.observe(root);
  resize();

  /* fullscreen */
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

  /* picking: hover tooltip + click-through to the explorer */
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let hovered = null;
  let downAt = null;

  function pick(event) {
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(pickMeshes, false)[0];
    return hit ? hit.object.userData.node : null;
  }

  canvas.addEventListener("pointermove", (event) => {
    const node = pick(event);
    if (node !== hovered) {
      if (hovered) setHighlight(hovered, false);
      hovered = node;
      if (hovered) setHighlight(hovered, true);
    }
    canvas.style.cursor = node ? "pointer" : "grab";
    if (node && tooltip) {
      const rect = canvas.getBoundingClientRect();
      tooltip.hidden = false;
      tooltip.style.left = `${event.clientX - rect.left}px`;
      tooltip.style.top = `${event.clientY - rect.top}px`;
      tooltip.innerHTML =
        `<strong style="color:${node.color}">${node.label}</strong>` +
        `<span>${numberFormat.format(node.count)} items` +
        (node.products ? ` · ${numberFormat.format(node.products)} 상품` : "") +
        `</span><em>클릭하여 직접 조회 →</em>`;
    } else if (tooltip) {
      tooltip.hidden = true;
    }
  });
  canvas.addEventListener("pointerleave", () => {
    if (hovered) setHighlight(hovered, false);
    hovered = null;
    if (tooltip) tooltip.hidden = true;
  });
  canvas.addEventListener("pointerdown", (event) => {
    downAt = [event.clientX, event.clientY];
  });
  canvas.addEventListener("pointerup", (event) => {
    if (!downAt) return;
    const moved = Math.hypot(event.clientX - downAt[0], event.clientY - downAt[1]);
    downAt = null;
    if (moved < 6) {
      const node = pick(event);
      if (node) window.location.href = `explorer.html?domain=${encodeURIComponent(node.domain)}`;
    }
  });

  function setHighlight(node, on) {
    node.orbitLine.material.opacity = on ? 0.4 : 0.1;
    node.orbitLine.material.color.set(on ? node.color : "#8aa5c8");
    node.atmosphere.scale.setScalar(on ? 1.12 : 1);
  }

  /* animation */
  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const delta = Math.min(clock.getDelta(), 0.05);
    if (!reduceMotion.matches) {
      for (const node of nodes) {
        node.angle += node.orbitSpeed * delta;
        node.group.position.set(
          Math.cos(node.angle) * node.orbitRadius,
          0,
          Math.sin(node.angle) * node.orbitRadius
        );
        node.mesh.rotation.y += delta * 0.25;
        if (node.clouds) node.clouds.rotation.y += delta * 0.32;
      }
      const pulse = 11 + Math.sin(clock.elapsedTime * 1.8) * 0.5;
      sunGlow.scale.set(pulse, pulse, 1);
    } else {
      for (const node of nodes) {
        node.group.position.set(
          Math.cos(node.angle) * node.orbitRadius,
          0,
          Math.sin(node.angle) * node.orbitRadius
        );
      }
    }
    controls.update();
    renderer.render(scene, camera);
  });
}

function buildOrbitLine(radius) {
  const points = [];
  for (let i = 0; i <= 128; i++) {
    const a = (i / 128) * Math.PI * 2;
    points.push(new THREE.Vector3(Math.cos(a) * radius, 0, Math.sin(a) * radius));
  }
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  return new THREE.Line(
    geometry,
    new THREE.LineBasicMaterial({ color: 0x8aa5c8, transparent: true, opacity: 0.1 })
  );
}

function buildStars() {
  const count = 2600;
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const tints = [
    [1, 1, 1],
    [0.8, 0.89, 1],
    [1, 0.9, 0.78],
    [1, 0.83, 0.88],
  ];
  for (let i = 0; i < count; i++) {
    const radius = 90 + Math.random() * 160;
    const z = Math.random() * 2 - 1;
    const a = Math.random() * Math.PI * 2;
    const xy = Math.sqrt(1 - z * z);
    positions[i * 3] = radius * xy * Math.cos(a);
    positions[i * 3 + 1] = radius * z;
    positions[i * 3 + 2] = radius * xy * Math.sin(a);
    const tint = tints[(Math.random() * tints.length) | 0];
    const dim = 0.4 + Math.random() * 0.6;
    colors[i * 3] = tint[0] * dim;
    colors[i * 3 + 1] = tint[1] * dim;
    colors[i * 3 + 2] = tint[2] * dim;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  return new THREE.Points(
    geometry,
    new THREE.PointsMaterial({
      size: 0.7,
      sizeAttenuation: true,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      depthWrite: false,
    })
  );
}

// RingGeometry UVs are planar by default; remap u to the radial fraction so a
// 1D stripe texture reads as concentric ring bands.
function remapRingUv(geometry, inner, outer) {
  const pos = geometry.attributes.position;
  const uv = geometry.attributes.uv;
  const span = outer - inner;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const r = Math.sqrt(x * x + y * y);
    uv.setXY(i, (r - inner) / span, 0.5);
  }
  uv.needsUpdate = true;
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
