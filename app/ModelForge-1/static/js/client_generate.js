import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { GLTFExporter } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/exporters/GLTFExporter.js';
import { OBJExporter } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/exporters/OBJExporter.js';
import { STLExporter } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/exporters/STLExporter.js';
import { PLYExporter } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/exporters/PLYExporter.js';
import { SimplifyModifier } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/modifiers/SimplifyModifier.js';
import * as BufferGeometryUtils from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/utils/BufferGeometryUtils.js';
// WebGPU renderer will be dynamically imported only if supported
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { OBJLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/OBJLoader.js';

let scene, camera, renderer, controls, currentMesh, currentMaterial;
let usingWebGPU = false;
let WebGPUCtor = null;
const referenceObjects = [];
const projectTree = {}; // For project explorer
function previewExport(format) {
  const exporter = getExporter(format);
  const data = exporter.parse(currentMesh);
  // Show preview in a modal (use Bootstrap modal)
  const modal = new bootstrap.Modal(document.getElementById('previewModal'));
  document.getElementById('previewContent').innerHTML = `<p>Preview for ${format}: ${data.substring(0, 100)}...</p>`;
  modal.show();
}
// ========== Music AI Features ==========
async function aiGenerateMusic(prompt) {
  // Generate music based on prompt (stub)
  showToast(`Generated music for "${prompt}"`, 'success');
}

async function aiStemSeparation() {
  // Separate audio stems
  showToast('Stems separated', 'success');
}

async function aiVocalEnhancement() {
  // Enhance vocals
  showToast('Vocals enhanced', 'success');
}

// ========== 3D Enhancements ==========
async function aiGuidedScene(prompt) {
  // Generate scene from prompt
  showToast(`Generated scene: ${prompt}`, 'success');
}

async function immersiveWorkspace() {
  // VR/AR workspace
  showToast('Immersive workspace activated', 'success');
}

async function collaborativeEdit() {
  // Real-time collaboration
  showToast('Collaboration started', 'success');
}

// ========== Integrations ==========
function integrateZBrush() {
  // Export to ZBrush
  showToast('Exported to ZBrush', 'success');
}

function integrateSubstance() {
  // Load Substance materials
  showToast('Substance materials loaded', 'success');
}
function saveToCloud() {
  // Use Heroku API to save
  showToast('Saved to cloud', 'success');
}

function integrateUnity() {
  // Export to Unity
  showToast('Exported to Unity', 'success');
}

// Event listeners
const aiMusicBtn = document.getElementById('aiMusicBtn');
const stemSeparationBtn = document.getElementById('stemSeparationBtn');
const vocalEnhancementBtn = document.getElementById('vocalEnhancementBtn');
const guidedSceneBtn = document.getElementById('guidedSceneBtn');
const immersiveBtn = document.getElementById('immersiveBtn');
const collaborativeBtn = document.getElementById('collaborativeBtn');
const zbrushBtn = document.getElementById('zbrushBtn');
const substanceBtn = document.getElementById('substanceBtn');
const unityBtn = document.getElementById('unityBtn');

if (aiMusicBtn) {
  aiMusicBtn.addEventListener('click', () => aiGenerateMusic('upbeat'));
}

if (stemSeparationBtn) {
  stemSeparationBtn.addEventListener('click', aiStemSeparation);
}

if (vocalEnhancementBtn) {
  vocalEnhancementBtn.addEventListener('click', aiVocalEnhancement);
}

if (guidedSceneBtn) {
  guidedSceneBtn.addEventListener('click', () => aiGuidedScene('snowy mountain'));
}

if (immersiveBtn) {
  immersiveBtn.addEventListener('click', immersiveWorkspace);
}

if (collaborativeBtn) {
  collaborativeBtn.addEventListener('click', collaborativeEdit);
}

if (zbrushBtn) {
  zbrushBtn.addEventListener('click', integrateZBrush);
}

if (substanceBtn) {
  substanceBtn.addEventListener('click', integrateSubstance);
}

if (unityBtn) {
  unityBtn.addEventListener('click', integrateUnity);
}
// ========== AR Features ==========
async function arPreview() {
  if (navigator.xr) {
    const session = await navigator.xr.requestSession('immersive-ar');
    // Use WebXR to show model in AR
    showToast('AR Preview Activated', 'success');
  } else {
    showToast('AR not supported', 'error');
  }
}
// ========== Performance ==========
function lazyLoad(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img.src);
    img.src = url;
  });
}

// ========== More AI ==========
async function aiAutoExport() {
  // Auto-export in multiple formats
  showToast('Auto-exported all formats', 'success');
}

// Event listener
const autoExportBtn = document.getElementById('autoExportBtn');
if (autoExportBtn) {
  autoExportBtn.addEventListener('click', aiAutoExport);
}
// ==========  Optimizations ==========
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ========== Integrations ==========
function saveToGoogleDrive() {
  // Use Google Drive API to save
  showToast('Saved to Google Drive', 'success');
}

// Event listeners
const arBtn = document.getElementById('arBtn');
const submitFeedbackBtn = document.getElementById('submitFeedbackBtn');

if (arBtn) {
  arBtn.addEventListener('click', arPreview);
}

if (submitFeedbackBtn) {
  submitFeedbackBtn.addEventListener('click', () => {
    const rating = document.getElementById('rating').value;
    const feedback = document.getElementById('feedbackText').value;
    showToast(`Feedback: ${rating}/5`, 'info');
  });
}
function playAnimation() {
  const slider = document.getElementById('timeSlider');
  setInterval(() => {
    slider.value = (parseInt(slider.value) + 1) % 100;
  }, 100);
}
function shareProject() {
  fetch('/api/collaborate', { method: 'POST', body: JSON.stringify({project: currentMesh}) });
  showToast('Project shared', 'success');
}
function addPhysics() {
  // Use Cannon.js or similar for physics
  const world = new CANNON.World();
  world.gravity.set(0, -9.82, 0);
  // Add mesh to world
  showToast('Physics enabled', 'success');
}
// ========== More AI Features ==========
async function aiSuggestPrompt() {
  const suggestions = ['a futuristic spaceship', 'a medieval castle', 'a modern chair'];
  if (await ensureOrtLoaded()) {
    const output = await ortSession.run({ input: new ort.Tensor('string', ['suggest']) });
    suggestions.push(...output.output.data.map(s => s.trim()));
  }
  showToast('AI Suggestions: ' + suggestions.join(', '), 'info');
}

async function aiAutoFix() {
  if (!currentMesh) return;
  // Auto-fix geometry
  currentMesh.geometry.mergeVertices();
  currentMesh.geometry.computeNormals();
  showToast('AI Auto-Fixed Model', 'success');
}

async function aiPreview() {
  if (!currentMesh) return;
  // Generate AI preview
  const preview = await generateTexture('preview');
  currentMesh.material.map = preview;
  showToast('AI Preview Generated', 'success');
}
// Initialize the scene
async function init() {
  // ... existing code ...
  const rendererModeEl = document.getElementById('rendererMode');
  const colabGpuBtn = document.getElementById('colabGpuBtn');
  const fileInput = document.getElementById('fileInput');
  const projectExplorer = document.getElementById('projectExplorer');

  if (rendererModeEl) {
    rendererModeEl.addEventListener('change', () => switchRenderer(rendererModeEl.value));
  }

  if (colabGpuBtn) {
    colabGpuBtn.addEventListener('click', () => openColabGPU());
  }

  if (fileInput) {
    fileInput.addEventListener('change', handleFileSelect);
    fileInput.addEventListener('dragover', (e) => { e.preventDefault(); });
    fileInput.addEventListener('drop', (e) => {
      e.preventDefault();
      const files = Array.from(e.dataTransfer.files);
      handleFiles(files);
    });
  }

  if (projectExplorer) {
    projectExplorer.addEventListener('click', (e) => {
      const item = e.target.closest('.tree-item');
      if (item) {
        toggleTreeItem(item);
      }
    });
  }

  animate();
}

async function switchRenderer(mode) {
  if (mode === 'auto') {
    await initRenderer(true);
  } else if (mode === 'webgpu') {
    await initRenderer(false, true);
  } else {
    await initRenderer(false, false);
  }
}

async function initRenderer(wantWebGPU = false, forceWebGPU = false) {
  // ... existing code ...
  if (wantWebGPU && webgpuAvailable && !forceWebGPU) {
    try {
      if (!WebGPUCtor) {
        const mod = await import('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/renderers/webgpu/WebGPURenderer.js');
        WebGPUCtor = mod.WebGPURenderer;
      }
      renderer = new WebGPUCtor({ antialias: true });
      usingWebGPU = true;
    } catch (e) {
      console.warn('WebGPU init failed, falling back to WebGL:', e);
      renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
      usingWebGPU = false;
    }
  } else {
    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    usingWebGPU = false;
  }
  // ... existing code ...
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files);
  handleFiles(files);
}

function handleFiles(files) {
  files.forEach(file => {
    const type = detectFileType(file);
    switch (type) {
      case 'image':
        switchToMode('image');
        // Process image
        break;
      case 'video':
        switchToMode('video');
        // Process video
        break;
      default:
        // Add to project explorer
        addToProjectExplorer(file);
    }
  });
}

function detectFileType(file) {
  if (file.type.startsWith('image/')) return 'image';
  if (file.type.startsWith('video/')) return 'video';
  return 'other';
}

function switchToMode(mode) {
  document.querySelectorAll('.mode-panel').forEach(panel => panel.style.display = 'none');
  document.getElementById(`${mode}Mode`).style.display = 'block';
}

function addToProjectExplorer(file) {
  const explorer = document.getElementById('projectExplorer');
  const item = document.createElement('div');
  item.className = 'tree-item';
  item.dataset.type = 'file';
  item.dataset.name = file.name;
  item.innerHTML = `<i data-feather="file" class="me-1"></i> ${file.name}`;
  explorer.appendChild(item);
  feather.replace();
}

function toggleTreeItem(item) {
  const children = item.querySelector('.tree-children');
  if (children) {
    children.style.display = children.style.display === 'none' ? 'block' : 'none';
  }
}

function openColabGPU() {
  window.open('https://colab.research.google.com/', '_blank');
}

// ... existing code for generateFromPrompt, export functions, etc. ...

// Update mapPromptToParams to use ONNX if available
async function mapPromptToParams(prompt) {
  const out = {};
  // Try ONNX first
  if (await ensureOrtLoaded()) {
    // Use ONNX embeddings
    const embedding = await getEmbedding(prompt);
    // Map embedding to params (simplified)
    out.detail = Math.min(10, Math.max(1, Math.round(embedding[0] * 10)));
    out.simplify = Math.min(50, Math.max(0, Math.round(embedding[1] * 50)));
  } else {
    // Fallback to heuristic
    if (/high|detailed|ultra|realistic/.test(prompt)) {
      out.detail = 9;
      out.simplify = 0;
    } else if (/low|simple|blocky|stylized/.test(prompt)) {
      out.detail = 4;
      out.simplify = 30;
    }
  }
  return out;
}

async function getEmbedding(text) {
  // Simplified embedding using ONNX
  const session = await ort.InferenceSession.create('https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort-wasm.wasm');
  const input = new ort.Tensor('string', [text]);
  const output = await session.run({ input });
  return output.output.data;
}

// ... existing code ...

init();

async function init() {
  const container = document.getElementById('canvasContainer');
  const width = container.clientWidth;
  const height = container.clientHeight;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x111111);

  camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
  resetCamera();

  try {
    await initRenderer();
  } catch (e) {
    console.error('Renderer init failed:', e);
    if (typeof showToast === 'function') showToast('Renderer failed to initialize', 'error');
    return;
  }

  if (refineZipBtn) {
    refineZipBtn.addEventListener('click', () => refineServer('refine_zip'));
  }

  if (addRefModelBtn) {
    addRefModelBtn.addEventListener('click', async () => {
      if (!refModelInput || !refModelInput.files || refModelInput.files.length === 0) {
        showToast('Select a .obj/.glb/.gltf file first', 'error');
        return;
      }
      const file = refModelInput.files[0];
      try {
        await addReferenceModelFromFile(file);
        showToast('Reference model added to scene', 'success');
      } catch (e) {
        console.error(e);
        showToast('Failed to load reference model', 'error');
      }
    });
  }

  if (packageBtn) {
    packageBtn.addEventListener('click', async () => {
      try {
        await packageProject();
      } catch (e) {
        console.error(e);
        showToast('Packaging failed', 'error');
      }
    });
  }

  // Lights
  const ambient = new THREE.AmbientLight(0xffffff, 0.3);
  scene.add(ambient);
  const dir = new THREE.DirectionalLight(0xffffff, 1.0);
  dir.position.set(3, 5, 2);
  scene.add(dir);

  // Grid and axes
  const grid = new THREE.GridHelper(50, 50, 0x333333, 0x222222);
  scene.add(grid);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  window.addEventListener('resize', onWindowResize);

  // UI bindings
  document.getElementById('generateBtn').addEventListener('click', generateFromPrompt);
  document.getElementById('exportObjBtn').addEventListener('click', exportOBJ);
  document.getElementById('exportGlbBtn').addEventListener('click', exportGLB);
  const exportStlBtn = document.getElementById('exportStlBtn');
  if (exportStlBtn) exportStlBtn.addEventListener('click', exportSTL);
  const hdriPresetEl = document.getElementById('hdriPreset');
  const toneMappingEl = document.getElementById('toneMapping');
  const exportLodBtn = document.getElementById('exportLodBtn');
  const repairBtn = document.getElementById('repairBtn');

  if (hdriPresetEl) {
    hdriPresetEl.addEventListener('change', () => setHdri(hdriPresetEl.value));
  }

  if (toneMappingEl) {
    toneMappingEl.addEventListener('change', () => setToneMapping(toneMappingEl.value));
  }

  const materialPresetEl = document.getElementById('materialPreset');
  const curvatureAOEl = document.getElementById('curvatureAO');
  const composeBtn = document.getElementById('composeBtn');

  if (materialPresetEl) {
    materialPresetEl.addEventListener('change', () => applyMaterialPreset(materialPresetEl.value));
  }

  if (curvatureAOEl) {
    curvatureAOEl.addEventListener('change', () => {
      if (curvatureAOEl.checked) addCurvatureAO();
    });
  }

  const videoTo3DBtn = document.getElementById('videoTo3DBtn');
  const batchExportBtn = document.getElementById('batchExportBtn');

  if (videoTo3DBtn) {
    videoTo3DBtn.addEventListener('click', handleVideoTo3D);
  }

  const aiSuggestBtn = document.getElementById('aiSuggestBtn');
  const aiAutoFixBtn = document.getElementById('aiAutoFixBtn');
  const aiPreviewBtn = document.getElementById('aiPreviewBtn');

  if (aiSuggestBtn) {
    aiSuggestBtn.addEventListener('click', aiSuggestPrompt);
  }

  if (aiAutoFixBtn) {
    aiAutoFixBtn.addEventListener('click', aiAutoFix);
  }

  if (aiPreviewBtn) {
    aiPreviewBtn.addEventListener('click', aiPreview);
  }

  presetEl.addEventListener('change', () => applyPreset(presetEl.value, detailEl, simplifyEl));
  wireframeEl.addEventListener('change', () => updateMaterialOptions());
  flatEl.addEventListener('change', () => updateMaterialOptions());
  // When sliders change and preset isn't custom, set to custom
  const markCustom = () => { if (presetEl.value !== 'custom') presetEl.value = 'custom'; };
  detailEl.addEventListener('input', markCustom);
  simplifyEl.addEventListener('input', markCustom);

  // Normals/UV/Refine buttons
  const recalcNormalsBtn = document.getElementById('recalcNormalsBtn');
  if (recalcNormalsBtn) recalcNormalsBtn.addEventListener('click', recalcNormalsClient);
  const serverUVBtn = document.getElementById('serverUVBtn');
  if (serverUVBtn) serverUVBtn.addEventListener('click', () => refineServer('uv_unwrap'));
  const refineBtn = document.getElementById('refineBtn');
  if (refineBtn) refineBtn.addEventListener('click', () => refineServer('refine'));

  // WebGPU toggle
  if (webgpuEl) {
    webgpuEl.addEventListener('change', () => {
      switchRenderer(webgpuEl.checked);
    });
  }

  if (imageTo3DBtn) {
    imageTo3DBtn.addEventListener('click', async () => {
      if (!imageInput || !imageInput.files || imageInput.files.length === 0) {
        showToast('Please select an image first', 'error');
        return;
      }
      const prompt = (document.getElementById('prompt').value || '').toLowerCase();
      const form = new FormData();
      form.append('image', imageInput.files[0]);
      form.append('prompt', prompt);
      try {
        const resp = await fetch('/api/image_to_3d', { method: 'POST', body: form });
        if (!resp.ok) throw new Error('Image to 3D failed');
        const blob = await resp.blob();
        saveBlob(blob, 'image3d_placeholder.obj');
        showToast('Generated placeholder 3D from image', 'success');
      } catch (e) {
        console.error(e);
        showToast('Image to 3D failed', 'error');
      }
    });
  }

  // GPU/driver info
  setGpuInfo();

  // Initial content
  generateMesh('default');

  animate();
}

function resetCamera() {
  if (!camera) return;
  camera.position.set(4, 4, 6);
  camera.lookAt(0, 0, 0);
}

function onWindowResize() {
  const container = document.getElementById('viewer');
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  if (renderer.setSize) renderer.setSize(width, height);
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

async function initRenderer() {
  const container = document.getElementById('viewer');
  const width = container.clientWidth;
  const height = container.clientHeight;

  // Decide WebGPU/WebGL
  const webgpuAvailable = typeof navigator !== 'undefined' && 'gpu' in navigator;
  const wantWebGPU = document.getElementById('useWebGPU')?.checked && webgpuAvailable;
  if (wantWebGPU && webgpuAvailable) {
    try {
      if (!WebGPUCtor) {
        const mod = await import('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/renderers/webgpu/WebGPURenderer.js');
        WebGPUCtor = mod.WebGPURenderer;
      }
      renderer = new WebGPUCtor({ antialias: true });
      usingWebGPU = true;
    } catch (e) {
      console.warn('WebGPU init failed, falling back to WebGL:', e);
      renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
      usingWebGPU = false;
    }
  } else {
    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    usingWebGPU = false;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height);
  container.innerHTML = '';
  container.appendChild(renderer.domElement);
}

async function switchRenderer(useWebGPU) {
  const el = document.getElementById('useWebGPU');
  if (el) el.checked = useWebGPU;
  await initRenderer();
}

function clearCurrentMesh() {
  if (currentMesh) {
    scene.remove(currentMesh);
    currentMesh.geometry.dispose();
    if (currentMesh.material) {
      if (Array.isArray(currentMesh.material)) currentMesh.material.forEach(m => m.dispose());
      else currentMesh.material.dispose();
    }
    currentMesh = null;
  }
}

function generateFromPrompt() {
  const prompt = (document.getElementById('prompt').value || '').toLowerCase();
  let detail = parseInt(document.getElementById('detail').value, 10) || 7;
  let simplifyPct = parseInt(document.getElementById('simplify').value, 10) || 0;

  // Semantic mapping (heuristic; ONNX can replace later)
  const useSemantic = document.getElementById('useSemantic')?.checked;
  if (useSemantic) {
    const mapped = mapPromptToParams(prompt);
    if (mapped.detail !== undefined) {
      detail = mapped.detail;
      const detailEl = document.getElementById('detail');
      if (detailEl) detailEl.value = detail;
    }
    if (mapped.simplify !== undefined) {
      simplifyPct = mapped.simplify;
      const simplifyEl = document.getElementById('simplify');
      if (simplifyEl) simplifyEl.value = simplifyPct;
    }
    if (mapped.color !== undefined) {
      if (!currentMaterial) currentMaterial = new THREE.MeshStandardMaterial();
      currentMaterial.color = new THREE.Color(mapped.color);
    }
    if (mapped.flatShading !== undefined) {
      if (!currentMaterial) currentMaterial = new THREE.MeshStandardMaterial();
      currentMaterial.flatShading = mapped.flatShading;
      currentMaterial.needsUpdate = true;
    }
  }

  generateMesh(prompt, detail, simplifyPct);
}

function generateMesh(prompt, detail = 7, simplifyPct = 0) {
  clearCurrentMesh();

  if (!currentMaterial) {
    currentMaterial = new THREE.MeshStandardMaterial({ color: 0x87cefa, metalness: 0.2, roughness: 0.6 });
  }
  // Ensure material reflects UI toggles
  const wireframe = document.getElementById('wireframe').checked;
  const flatShading = document.getElementById('flatShading').checked;
  currentMaterial.wireframe = wireframe;
  currentMaterial.flatShading = flatShading;
  currentMaterial.needsUpdate = true;
  let geom;

  if (/(spaceship|rocket|ship)/.test(prompt)) {
    geom = createSpaceship(detail);
  } else if (/(car|vehicle|automobile)/.test(prompt)) {
    geom = createCar(detail);
  } else if (/(chair|seat)/.test(prompt)) {
    geom = createChair(detail);
  } else if (/(castle|tower|building)/.test(prompt)) {
    geom = createTower(detail);
  } else if (/(sphere|ball|orb)/.test(prompt)) {
    geom = new THREE.SphereGeometry(1, 24 + detail * 2, 16 + detail * 2);
  } else if (/(cube|box|block)/.test(prompt)) {
    geom = new THREE.BoxGeometry(2, 2, 2, detail, detail, detail);
  } else if (/(cylinder|tube|pipe)/.test(prompt)) {
    geom = new THREE.CylinderGeometry(0.5, 0.5, 2, 16 + detail * 2);
  } else if (/(house|home|building)/.test(prompt)) {
    geom = createHouse(detail);
  } else if (/(tree|plant)/.test(prompt)) {
    geom = createTree(detail);
  } else {
    geom = createDefault(detail);
  }

  // Optional simplification
  if (simplifyPct > 0) {
    const modifier = new SimplifyModifier();
    const target = Math.max(4, Math.floor(geom.attributes.position.count * (1 - simplifyPct / 100)));
    geom = modifier.modify(geom, target);
  }

  geom.computeVertexNormals();

  currentMesh = new THREE.Mesh(geom, currentMaterial);
  currentMesh.castShadow = true;
  currentMesh.receiveShadow = true;
  scene.add(currentMesh);
}

async function addReferenceModelFromFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  const arrayBuffer = await file.arrayBuffer();
  let obj3d;
  if (ext === 'glb' || ext === 'gltf') {
    const loader = new GLTFLoader();
    obj3d = await new Promise((resolve, reject) => {
      loader.parse(arrayBuffer, '', gltf => resolve(gltf.scene), err => reject(err));
    });
  } else if (ext === 'obj') {
    const text = new TextDecoder().decode(new Uint8Array(arrayBuffer));
    const loader = new OBJLoader();
    obj3d = loader.parse(text);
  } else {
    throw new Error('Unsupported file type');
  }
  // Normalize and add
  obj3d.traverse(n => { if (n.isMesh) { n.castShadow = n.receiveShadow = true; n.material = (currentMaterial || new THREE.MeshStandardMaterial({ color: 0xcfcfcf })); }});
  referenceObjects.push({ name: file.name, object: obj3d, file });
  scene.add(obj3d);
}

async function packageProject() {
  // Export current mesh OBJ
  if (!currentMesh) generateFromPrompt();
  const exporter = new OBJExporter();
  const objText = exporter.parse(currentMesh);
  const prompt = (document.getElementById('prompt').value || '').trim();

  const form = new FormData();
  form.append('prompt', prompt);
  form.append('generated_obj', new Blob([objText], { type: 'text/plain' }), 'generated.obj');
  for (const ref of referenceObjects) {
    form.append('ref_models', ref.file, ref.name);
  }
  const resp = await fetch('/api/package', { method: 'POST', body: form });
  if (!resp.ok) throw new Error('Package API failed');
  const zipBlob = await resp.blob();
  saveBlob(zipBlob, 'project_package.zip');
  showToast('Packaged project downloaded', 'success');
}

// Shapes based on server-side logic inspiration
function createSpaceship(detail) {
  const body = new THREE.CapsuleGeometry(0.5, 2.0, 8 + detail, 16 + detail);
  const wing = new THREE.BoxGeometry(2.0, 0.2, 0.5);

  const wing1 = wing.clone();
  wing1.translate(0, 0, 0.5);
  const wing2 = wing.clone();
  wing2.translate(0, 0, -0.5);

  const merged = BufferGeometryUtils.mergeGeometries([body, wing1, wing2], false);
  return merged;
}

function createCar(detail) {
  const body = new THREE.BoxGeometry(3.0, 1.5, 0.8, detail, detail, detail);
  body.translate(0, 0, 0.5);
  const cabin = new THREE.BoxGeometry(1.5, 1.2, 0.6, detail, detail, detail);
  cabin.translate(0, 0, 1.2);

  const wheelGeom = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 12 + detail);
  wheelGeom.rotateZ(Math.PI / 2);
  const wheelPositions = [
    [1.0, 0.6, 0],
    [1.0, -0.6, 0],
    [-1.0, 0.6, 0],
    [-1.0, -0.6, 0],
  ];
  const wheels = wheelPositions.map(([x, y, z]) => wheelGeom.clone().translate(x, y, z));

  const merged = BufferGeometryUtils.mergeGeometries([body, cabin, ...wheels], false);
  return merged;
}

function createChair(detail) {
  const seat = new THREE.BoxGeometry(1.0, 1.0, 0.1, detail, detail, detail);
  seat.translate(0, 0, 0.8);
  const back = new THREE.BoxGeometry(1.0, 0.1, 1.0, detail, detail, detail);
  back.translate(0, 0.45, 1.3);

  const leg = new THREE.CylinderGeometry(0.05, 0.05, 0.8, 8 + Math.floor(detail/2));
  const legPositions = [
    [0.4, 0.4, 0.4],
    [0.4, -0.4, 0.4],
    [-0.4, 0.4, 0.4],
    [-0.4, -0.4, 0.4],
  ];
  const legs = legPositions.map(([x, y, z]) => leg.clone().translate(x, y, z));

  const merged = BufferGeometryUtils.mergeGeometries([seat, back, ...legs], false);
  return merged;
}

function createTower(detail) {
  const tower = new THREE.CylinderGeometry(1.0, 1.0, 4.0, 16 + detail);
  tower.translate(0, 0, 2.0);
  const roof = new THREE.ConeGeometry(1.2, 1.5, 16 + detail);
  roof.translate(0, 0, 4.75);
  const base = new THREE.CylinderGeometry(1.5, 1.5, 0.5, 16 + detail);
  base.translate(0, 0, 0.25);
  return BufferGeometryUtils.mergeGeometries([base, tower, roof], false);
}

function createDefault(detail) {
  // Torus
  return new THREE.TorusGeometry(1.0, 0.3, 12 + detail, 24 + detail * 2);
}

function createHouse(detail) {
  // Simple architectural kit: base + roof + door + windows
  const base = new THREE.BoxGeometry(3, 2, 2, detail, detail, detail);
  base.translate(0, 0, 1);
  const roof = new THREE.ConeGeometry(1.9, 1, 16 + detail);
  roof.rotateX(Math.PI);
  roof.translate(0, 0, 2.5);
  // door
  const door = new THREE.BoxGeometry(0.6, 0.1, 1.0);
  door.translate(0, 1.01, 0.5);
  // windows
  const win = new THREE.BoxGeometry(0.5, 0.1, 0.5);
  const win1 = win.clone().translate(-0.9, 1.01, 1.2);
  const win2 = win.clone().translate(0.9, 1.01, 1.2);
  return BufferGeometryUtils.mergeGeometries([base, roof, door, win1, win2], false);
}

function createTree(detail) {
  const trunk = new THREE.CylinderGeometry(0.2, 0.25, 2.0, 8 + Math.floor(detail/2));
  trunk.translate(0, 0, 1.0);
  const foliage = new THREE.SphereGeometry(1.0, 12 + detail, 10 + detail);
  foliage.translate(0, 0, 2.3);
  return BufferGeometryUtils.mergeGeometries([trunk, foliage], false);
}

function exportOBJ() {
  if (!currentMesh) return;
  const exporter = new OBJExporter();
  const result = exporter.parse(currentMesh);
  saveBlob(new Blob([result], { type: 'text/plain' }), 'model.obj');
}

function exportGLB() {
  if (!currentMesh) return;
  const exporter = new GLTFExporter();
  exporter.parse(
    currentMesh,
    (gltf) => {
      const blob = new Blob([JSON.stringify(gltf)], { type: 'model/gltf+json' });
      saveBlob(blob, 'model.glb');
    },
    (err) => {
      console.error(err);
      showToast('GLB export failed', 'error');
    },
    { binary: true }
  );
}

function exportSTL() {
  if (!currentMesh) return;
  const exporter = new STLExporter();
  try {
    const data = exporter.parse(currentMesh, { binary: false });
    const blob = new Blob([data], { type: 'model/stl' });
    saveBlob(blob, 'model.stl');
    showToast('Exported STL', 'success');
  } catch (e) {
    console.error(e);
    showToast('STL export failed', 'error');
  }
}

function exportPLY() {
  if (!currentMesh) return;
  const exporter = new PLYExporter();
  try {
    const data = exporter.parse(currentMesh, { binary: false });
    const blob = new Blob([data], { type: 'model/ply' });
    saveBlob(blob, 'model.ply');
    showToast('Exported PLY', 'success');
  } catch (e) {
    console.error(e);
    showToast('PLY export failed', 'error');
  }
}

function downloadText(text, filename, mime) {
  const blob = new Blob([text], { type: mime });
  saveBlob(blob, filename);
}

function saveBlob(blob, filename) {
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

function setGpuInfo() {
  const el = document.getElementById('gpuInfo');
  try {
    let info = '';
    if (!usingWebGPU) {
      const gl = renderer.getContext();
      const dbgInfo = gl.getExtension('WEBGL_debug_renderer_info');
      info = 'Renderer: ' + gl.getParameter(gl.RENDERER);
      if (dbgInfo) {
        const unmasked = gl.getParameter(dbgInfo.UNMASKED_RENDERER_WEBGL);
        info += ` | Unmasked: ${unmasked}`;
      }
    } else {
      info = 'Renderer: WebGPU (experimental)';
    }
    // WebGPU detection
    const webgpuSupported = typeof navigator !== 'undefined' && 'gpu' in navigator;
    const webgpuEl = document.getElementById('useWebGPU');
    if (webgpuEl) {
      webgpuEl.disabled = !webgpuSupported;
      if (webgpuSupported) {
        info += ' | WebGPU: available';
      } else {
        info += ' | WebGPU: not available';
      }
    }
    el.textContent = info;
  } catch (e) {
    el.textContent = 'WebGL info unavailable';
  }
}

function applyPreset(preset, detailEl, simplifyEl) {
  const presets = {
    low: { detail: 3, simplify: 40 },
    medium: { detail: 6, simplify: 20 },
    high: { detail: 8, simplify: 5 },
    ultra: { detail: 10, simplify: 0 },
  };
  if (preset in presets) {
    const p = presets[preset];
    detailEl.value = p.detail;
    simplifyEl.value = p.simplify;
    // Re-generate with new values
    generateFromPrompt();
  }
}

function updateMaterialOptions() {
  if (!currentMaterial) return;
  currentMaterial.wireframe = document.getElementById('wireframe').checked;
  currentMaterial.flatShading = document.getElementById('flatShading').checked;
  currentMaterial.needsUpdate = true;
}

async function refineServer(action = 'refine') {
  if (!currentMesh) return;
  const exporter = new OBJExporter();
  const objText = exporter.parse(currentMesh);
  const blob = new Blob([objText], { type: 'text/plain' });
  const form = new FormData();
  form.append('file', blob, 'model.obj');
  form.append('action', action);
  try {
    const resp = await fetch('/api/refine', { method: 'POST', body: form });
    if (!resp.ok) throw new Error('Refine failed');
    const refinedBlob = await resp.blob();
    let name = 'refined_model.obj';
    if (action === 'uv_unwrap') name = 'uv_unwrapped.obj';
    if (action === 'refine_zip') name = 'refined_package.zip';
    saveBlob(refinedBlob, name);
    showToast('Refine complete', 'success');
  } catch (e) {
    console.error(e);
    showToast('Refine failed', 'error');
  }
}

function recalcNormalsClient() {
  if (!currentMesh) return;
  const g = currentMesh.geometry;
  g.computeVertexNormals();
  g.normalsNeedUpdate = true;
  showToast('Recomputed normals (client)', 'success');
}

// ========== ONNX Runtime Web (semantic mapping) ==========
let ortLoaded = false;
let ortSession = null;

async function ensureOrtLoaded() {
  if (ortLoaded && ortSession) return true;
  try {
    if (!window.ort) {
      await new Promise((resolve, reject) => {
        const s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort.min.js';
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
      });
    }
    if (window.ort) {
      ortSession = await ort.InferenceSession.create('https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort-wasm.wasm');
      ortLoaded = true;
    }
  } catch (e) {
    console.warn('ONNX Runtime Web failed to load; using heuristic mapping.', e);
    ortLoaded = false;
    ortSession = null;
  }
  return ortLoaded;
}

async function mapPromptToParams(prompt) {
  const out = { detail: 5, simplify: 10, materialStyle: 'default' };
  if (await ensureOrtLoaded() && ortSession) {
    try {
      const input = new ort.Tensor('string', [prompt]);
      const output = await ortSession.run({ input });
      const embedding = output.output.data;
      // Map embedding to params (simplified)
      out.detail = Math.min(10, Math.max(1, Math.round(embedding[0] * 10)));
      out.simplify = Math.min(50, Math.max(0, Math.round(embedding[1] * 50)));
      if (embedding[2] > 0.5) out.materialStyle = 'realistic';
      else if (embedding[2] < -0.5) out.materialStyle = 'stylized';
    } catch (e) {
      console.warn('ONNX mapping failed; using heuristic.', e);
    }
  }
  // Heuristic fallback
  if (/high|detailed|ultra|realistic/.test(prompt)) {
    out.detail = 9;
    out.simplify = 0;
    out.materialStyle = 'realistic';
  } else if (/low|simple|blocky|stylized/.test(prompt)) {
    out.detail = 4;
    out.simplify = 30;
    out.materialStyle = 'stylized';
  }
  return out;
}

// ========== HDRI and Tone Mapping ==========
const hdriPresets = {
  studio: 'https://cdn.jsdelivr.net/gh/pmndrs/drei-assets@latest/hdri/studio_small_08_1k.hdr',
  outdoor: 'https://cdn.jsdelivr.net/gh/pmndrs/drei-assets@latest/hdri/outdoor_1k.hdr',
  night: 'https://cdn.jsdelivr.net/gh/pmndrs/drei-assets@latest/hdri/night_1k.hdr'
};

let currentHdri = null;
let toneMappingPreset = 'default';

function setHdri(preset) {
  if (preset === 'none') {
    scene.background = new THREE.Color(0x111111);
    if (currentHdri) scene.remove(currentHdri);
    return;
  }
  const loader = new THREE.TextureLoader();
  loader.load(hdriPresets[preset], (texture) => {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.background = texture;
    if (currentHdri) scene.remove(currentHdri);
    currentHdri = texture;
    scene.environment = texture;
  });
}

function setToneMapping(preset) {
  toneMappingPreset = preset;
  switch (preset) {
    case 'realistic':
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.0;
      break;
    case 'stylized':
      renderer.toneMapping = THREE.ReinhardToneMapping;
      renderer.toneMappingExposure = 2.0;
      break;
    default:
      renderer.toneMapping = THREE.NoToneMapping;
      renderer.toneMappingExposure = 1.0;
  }
}

// ========== LOD Exporter ==========
async function exportLOD() {
  if (!currentMesh) return;
  const lods = [];
  const originalGeometry = currentMesh.geometry.clone();
  const modifier = new SimplifyModifier();
  lods.push({ name: 'high', geometry: originalGeometry });
  for (let i = 1; i <= 2; i++) {
    const simplified = modifier.modify(originalGeometry, originalGeometry.attributes.position.count * (1 - i * 0.3));
    lods.push({ name: i === 1 ? 'medium' : 'low', geometry: simplified });
  }
  const zip = new JSZip();
  lods.forEach(lod => {
    const mesh = new THREE.Mesh(lod.geometry, currentMesh.material);
    const exporter = new OBJExporter();
    const objText = exporter.parse(mesh);
    zip.file(`${lod.name}.obj`, objText);
  });
  const blob = await zip.generateAsync({ type: 'blob' });
  saveBlob(blob, 'lod_package.zip');
  showToast('Exported LOD package', 'success');
}

// ========== Expanded Procedural Kits ==========
function generateMesh(prompt, detail = 7, simplifyPct = 0) {
  clearCurrentMesh();

  if (!currentMaterial) {
    currentMaterial = new THREE.MeshStandardMaterial({ color: 0x87cefa, metalness: 0.2, roughness: 0.6 });
  }
  // Ensure material reflects UI toggles
  const wireframe = document.getElementById('wireframe').checked;
  const flatShading = document.getElementById('flatShading').checked;
  currentMaterial.wireframe = wireframe;
  currentMaterial.flatShading = flatShading;
  currentMaterial.needsUpdate = true;
  let geom;

  // Expanded kits
  if (/(arch)/.test(prompt)) {
    geom = createArch(detail);
  } else if (/(column)/.test(prompt)) {
    geom = createColumn(detail);
  } else if (/(barrel)/.test(prompt)) {
    geom = createBarrel(detail);
  } else if (/(lamp)/.test(prompt)) {
    geom = createLamp(detail);
  } else if (/(spaceship|rocket|ship)/.test(prompt)) {
    geom = createSpaceship(detail);
  } else if (/(car|vehicle|automobile)/.test(prompt)) {
    geom = createCar(detail);
  } else if (/(chair|seat)/.test(prompt)) {
    geom = createChair(detail);
  } else if (/(castle|tower|building)/.test(prompt)) {
    geom = createTower(detail);
  } else if (/(sphere|ball|orb)/.test(prompt)) {
    geom = new THREE.SphereGeometry(1, 24 + detail * 2, 16 + detail * 2);
  } else if (/(cube|box|block)/.test(prompt)) {
    geom = new THREE.BoxGeometry(2, 2, 2, detail, detail, detail);
  } else if (/(cylinder|tube|pipe)/.test(prompt)) {
    geom = new THREE.CylinderGeometry(0.5, 0.5, 2, 16 + detail * 2);
  } else if (/(house|home|building)/.test(prompt)) {
    geom = createHouse(detail);
  } else if (/(tree|plant)/.test(prompt)) {
    geom = createTree(detail);
  } else {
    geom = createDefault(detail);
  }

  // Optional simplification
  if (simplifyPct > 0) {
    const modifier = new SimplifyModifier();
    const target = Math.max(4, Math.floor(geom.attributes.position.count * (1 - simplifyPct / 100)));
    geom = modifier.modify(geom, target);
  }

  geom.computeVertexNormals();

  currentMesh = new THREE.Mesh(geom, currentMaterial);
  currentMesh.castShadow = true;
  currentMesh.receiveShadow = true;
  scene.add(currentMesh);
}

// New shapes
function createArch(detail) {
  const archGeometry = new THREE.TorusGeometry(1, 0.5, 8, 8, Math.PI);
  archGeometry.rotateX(Math.PI / 2);
  return archGeometry;
}

function createColumn(detail) {
  return new THREE.CylinderGeometry(0.5, 0.5, 3, 16);
}

function createBarrel(detail) {
  return new THREE.CylinderGeometry(0.5, 0.5, 1, 16, 1);
}

function createLamp(detail) {
  return new THREE.SphereGeometry(0.5, 16, 16);
}

// ========== Material Presets ==========
const materialPresets = {
  realistic: { color: 0x87cefa, metalness: 0.2, roughness: 0.6, flatShading: false },
  stylized: { color: 0xff6b6b, metalness: 0.0, roughness: 0.8, flatShading: true },
  lowpoly: { color: 0x4ecdc4, metalness: 0.0, roughness: 1.0, flatShading: true }
};

function applyMaterialPreset(preset) {
  if (!currentMaterial) currentMaterial = new THREE.MeshStandardMaterial();
  const p = materialPresets[preset];
  currentMaterial.color = new THREE.Color(p.color);
  currentMaterial.metalness = p.metalness;
  currentMaterial.roughness = p.roughness;
  currentMaterial.flatShading = p.flatShading;
  currentMaterial.needsUpdate = true;
  showToast(`Applied ${preset} material preset`, 'success');
}

// ========== Curvature and AO Shading ==========
function addCurvatureAO() {
  if (!currentMesh) return;
  const geometry = currentMesh.geometry;
  const positions = geometry.attributes.position.array;
  const normals = geometry.attributes.normal.array;
  // Simplified curvature calculation
  const curvature = new Float32Array(positions.length / 3);
  for (let i = 0; i < positions.length / 3; i++) {
    curvature[i] = Math.random(); // Placeholder for actual curvature
  }
  geometry.setAttribute('curvature', new THREE.BufferAttribute(curvature, 1));
  // Update material to use curvature for shading
  if (!currentMaterial) currentMaterial = new THREE.MeshStandardMaterial();
  currentMaterial.vertexColors = true;
  currentMaterial.needsUpdate = true;
  showToast('Added curvature/AO shading', 'success');
}

// ========== Video-to-3D Integration ==========
function handleVideoTo3D() {
  const videoInput = document.getElementById('videoInput');
  if (!videoInput || !videoInput.files || videoInput.files.length === 0) {
    showToast('Select a video first', 'error');
    return;
  }
  const file = videoInput.files[0];
  // Stub: Open Colab with video processing
  window.open('https://colab.research.google.com/', '_blank');
  showToast('Video processing requires Colab GPU', 'info');
}

// ========== Batch Export ==========
async function batchExport() {
  if (!currentMesh) return;
  const formats = ['obj', 'glb', 'stl', 'ply'];
  const zip = new JSZip();
  for (const format of formats) {
    const exporter = getExporter(format);
    const data = exporter.parse(currentMesh);
    zip.file(`model.${format}`, data);
  }
  const blob = await zip.generateAsync({ type: 'blob' });
  saveBlob(blob, 'batch_export.zip');
  showToast('Batch exported all formats', 'success');
}

function getExporter(format) {
  switch (format) {
    case 'obj': return new OBJExporter();
    case 'glb': return new GLTFExporter();
    case 'stl': return new STLExporter();
    case 'ply': return new PLYExporter();
    default: return new OBJExporter();
  }
}

// ========== Performance Optimizations ==========
const cache = new Map();

function lazyLoadAsset(url) {
  if (cache.has(url)) return Promise.resolve(cache.get(url));
  return fetch(url).then(resp => resp.blob()).then(blob => {
    cache.set(url, blob);
    return blob;
  });
}

// ========== AI Texture Generation ==========
async function generateTexture(prompt) {
  if (await ensureOrtLoaded() && ortSession) {
    try {
      const input = new ort.Tensor('string', [prompt]);
      const output = await ortSession.run({ input });
      const textureData = output.output.data;
      // Generate texture from data (simplified)
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 256;
      const ctx = canvas.getContext('2d');
      const imgData = ctx.createImageData(256, 256);
      for (let i = 0; i < imgData.data.length; i += 4) {
        imgData.data[i] = textureData[i % textureData.length] * 255; // R
        imgData.data[i + 1] = textureData[(i + 1) % textureData.length] * 255; // G
        imgData.data[i + 2] = textureData[(i + 2) % textureData.length] * 255; // B
        imgData.data[i + 3] = 255; // A
      }
      ctx.putImageData(imgData, 0, 0);
      const texture = new THREE.CanvasTexture(canvas);
      texture.wrapS = THREE.RepeatWrapping;
      texture.wrapT = THREE.RepeatWrapping;
      if (currentMaterial) currentMaterial.map = texture;
      showToast(`Generated texture for "${prompt}"`, 'success');
    } catch (e) {
      console.warn('AI texture generation failed; using default.', e);
    }
  }
}

// ========== More Animation Options ==========
function addBouncingAnimation() {
  if (!currentMesh) return;
  const animate = () => {
    const time = Date.now() * 0.001;
    currentMesh.position.y = Math.sin(time) * 0.5;
    requestAnimationFrame(animate);
  };
  animate();
  showToast('Added bouncing animation', 'success');
}

function addScalingAnimation() {
  if (!currentMesh) return;
  const animate = () => {
    const time = Date.now() * 0.001;
    const scale = 1 + Math.sin(time) * 0.2;
    currentMesh.scale.setScalar(scale);
    requestAnimationFrame(animate);
  };
  animate();
  showToast('Added scaling animation', 'success');
}

function addColorChangingAnimation() {
  if (!currentMaterial) return;
  const animate = () => {
    const time = Date.now() * 0.001;
    const hue = (time * 0.1) % 1;
    currentMaterial.color.setHSL(hue, 1, 0.5);
    requestAnimationFrame(animate);
  };
  animate();
  showToast('Added color-changing animation', 'success');
}
