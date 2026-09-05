/**
 * AI Learning Platform — Frontend Controller
 */

// Application State
const state = {
  currentView: 'upload',
  lessonPlan: null,
  activeSectionIndex: 0,
  currentCheckpointQuestion: null,
  selectedCheckpointOption: null,
  finalQuizAnswers: {},
  user: JSON.parse(localStorage.getItem('ai_teacher_user') || 'null'),
  explanationMode: 'detailed',
  selectedQuizDifficulty: 'all',
  simulation: {
    voltage: 12,
    resistance: 4,
    current: 3.00,
    animFrameId: null,
    particleOffset: 0
  },
  speech: {
    synth: window.speechSynthesis || null,
    utterance: null,
    isSpeaking: false,
    speed: 1.0,
    progressInterval: null,
    currentTime: 0,
    totalDuration: 30
  },
  flashcards: [],
  currentFlashcardIndex: 0,
  isFlashcardFlipped: false,
  taxonomyTree: null,
  mindmapMode: 'tree',
  pipelineFlow: [],
  lastReport: null,
  lastQuizResults: null
};

// Clean legacy electricity concepts if present in state.user
if (state.user) {
  const legacy = ["Electric Current", "Ohm's Law Basics", "Circuit Calculations", "Ohm's Law & Circuit Math"];
  if (Array.isArray(state.user.mastered_concepts)) {
    state.user.mastered_concepts = state.user.mastered_concepts.filter(c => !legacy.includes(c));
  }
  if (Array.isArray(state.user.needs_review_concepts)) {
    state.user.needs_review_concepts = state.user.needs_review_concepts.filter(c => !legacy.includes(c));
  }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  refreshIcons();
  initDragAndDrop();
  syncUserProfileUI();
  loadCurrentLessonFromBackend();
});

function refreshIcons() {
  setTimeout(() => {
    if (window.lucide && typeof lucide.createIcons === 'function') {
      lucide.createIcons();
    }
  }, 50);
}

// --- View Router ---
function switchView(viewName) {
  state.currentView = viewName;

  // Update Nav Buttons
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.className = 'nav-btn px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-2 text-slate-600 hover:text-slate-900';
  });

  const activeBtn = document.getElementById(`nav-${viewName}`);
  if (activeBtn) {
    activeBtn.className = 'nav-btn px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center gap-2 bg-white text-slate-900 shadow-sm border border-slate-200';
  }

  // Toggle View Panels
  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.add('hidden');
  });

  const targetPanel = document.getElementById(`view-${viewName}`);
  if (targetPanel) {
    targetPanel.classList.remove('hidden');
  }

  if (viewName === 'player') {
    renderPlayerSection(state.activeSectionIndex);
  } else if (viewName === 'quiz') {
    renderFinalQuiz();
  } else if (viewName === 'bonus') {
    loadBonusFeatures();
  } else if (viewName === 'profile') {
    syncUserProfileUI();
  } else if (viewName === 'report') {
    if (state.lastReport && state.lastQuizResults) {
      renderReport(state.lastReport, state.lastQuizResults);
    } else {
      renderEmptyReport();
    }
  }

  refreshIcons();
}

// --- Drag and Drop File Ingest ---
function initDragAndDrop() {
  const dropZone = document.getElementById('drop-zone');
  if (!dropZone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.add('border-sky-500', 'bg-sky-100/60');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-sky-500', 'bg-sky-100/60');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleUploadedFile(files[0]);
    }
  });
}

function handleFileSelected(event) {
  const file = event.target.files[0];
  if (file) {
    handleUploadedFile(file);
  }
}

function handleUploadedFile(file) {
  const badge = document.getElementById('file-badge');
  badge.classList.remove('hidden');
  badge.textContent = `Extracting text from ${file.name} (${(file.size / 1024).toFixed(1)} KB)...`;

  const formData = new FormData();
  formData.append('file', file);

  fetch('/api/upload', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      badge.textContent = `Attached: ${data.filename} (${data.char_count} chars extracted)`;
      document.getElementById('raw-text-input').value = data.text;

      // Auto-update Topic parameter to match uploaded document title
      if (data.suggested_topic) {
        const topicInput = document.getElementById('param-topic');
        topicInput.value = data.suggested_topic;
        topicInput.classList.add('ring-2', 'ring-sky-500');
        setTimeout(() => topicInput.classList.remove('ring-2', 'ring-sky-500'), 2000);
      }

      // Automatically generate & open Lesson Studio for seamless workflow
      startLessonGeneration();
    } else {
      badge.textContent = `Attached: ${file.name}`;
    }
  })
  .catch(err => {
    console.error('Upload error:', err);
    badge.textContent = `Attached: ${file.name} (Ready)`;
  });
}

// --- Load Lesson Plan Data ---
async function loadCurrentLessonFromBackend() {
  try {
    const res = await fetch('/api/current-lesson');
    const data = await res.json();
    state.lessonPlan = data;
  } catch (err) {
    console.error('Failed to load lesson plan:', err);
  }
}

async function loadSampleLesson() {
  document.getElementById('param-topic').value = "Chapter 4: Electricity & Magnetism";
  document.getElementById('param-level').value = "beginner";
  document.getElementById('param-lang').value = "en";
  document.getElementById('param-time').value = "20";
  document.getElementById('raw-text-input').value = 
`I. Electric Current & Charge Flow: Electric current (I) is the rate of flow of electric charges measured in Amperes through a conductive medium.
II. Electrical Potential & Voltage: Voltage (V) represents electrical potential difference and energy pressure driving electron migration across a circuit.
III. Ohm's Law & Resistance: Electrical resistance (R) opposes current flow, establishing the foundational relationship V = I * R.
IV. Circuit Topology & Power: Series and parallel network configurations determine equivalent resistance and branch current distribution.`;

  await startLessonGeneration();
}

async function startLessonGeneration() {
  const btn = document.getElementById('btn-generate-plan');
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating Lesson Plan...`;
  refreshIcons();

  const payload = {
    text: document.getElementById('raw-text-input').value,
    topic: document.getElementById('param-topic').value,
    level: document.getElementById('param-level').value,
    language: document.getElementById('param-lang').value,
    time_minutes: parseInt(document.getElementById('param-time').value, 10),
  };

  try {
    const res = await fetch('/api/generate-lesson-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    state.lessonPlan = await res.json();
    state.activeSectionIndex = 0;
    switchView('player');
  } catch (err) {
    console.error('Error generating lesson:', err);
    alert('Error connecting to backend API. Please check server status.');
  } finally {
    btn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i> Generate & Open Studio`;
    refreshIcons();
  }
}

// --- Lesson Player Controller ---
function renderPlayerSection(index) {
  if (!state.lessonPlan || !state.lessonPlan.sections || state.lessonPlan.sections.length === 0) return;

  state.activeSectionIndex = index;
  const plan = state.lessonPlan;
  const section = plan.sections[index];

  // Header badges & metadata
  document.getElementById('player-lesson-title').textContent = plan.title || "Interactive Lesson";
  document.getElementById('player-lesson-topic').textContent = plan.topic_or_chapter || section.concept;
  document.getElementById('player-badge-lang').textContent = (plan.language || "en").toUpperCase();
  document.getElementById('player-badge-level').textContent = (plan.level || "beginner").toUpperCase();
  document.getElementById('player-badge-time').textContent = `${plan.time_minutes || 20} Mins`;

  // Render Section Navigation Pills
  const pillsContainer = document.getElementById('section-nav-pills');
  pillsContainer.innerHTML = '';
  plan.sections.forEach((sec, idx) => {
    const pill = document.createElement('button');
    pill.className = `px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
      idx === index 
        ? 'bg-sky-600 text-white shadow-sm' 
        : 'bg-sky-50 text-sky-900 hover:bg-sky-100 border border-sky-200'
    }`;
    const cleanLabel = sec.concept.length > 26 ? sec.concept.slice(0, 24) + '...' : sec.concept;
    pill.textContent = `Sec ${idx + 1}: ${cleanLabel}`;
    pill.onclick = () => renderPlayerSection(idx);
    pillsContainer.appendChild(pill);
  });

  // Stage Concept Info
  document.getElementById('current-concept-heading').textContent = section.concept;
  const visualBadge = document.getElementById('visual-type-badge');
  const visualType = section.visual_type || 'diagram';
  visualBadge.innerHTML = `<i data-lucide="layout" class="w-3.5 h-3.5"></i> ${visualType.toUpperCase()} MODE`;

  // Narration and Explanation texts
  document.getElementById('section-narration-text').textContent = `"${section.narration_script || section.explanation}"`;
  renderExplanationText();
  document.getElementById('section-example-text').textContent = section.example || `Practical real-world application of ${section.concept}`;

  // Prepare Interactive Canvas Simulation
  startVisualSimulation(visualType, section);
  refreshIcons();
}

function renderExplanationText() {
  if (!state.lessonPlan || !state.lessonPlan.sections) return;
  const section = state.lessonPlan.sections[state.activeSectionIndex];
  const el = document.getElementById('section-explanation-text');
  if (!el) return;

  if (state.explanationMode === 'concise') {
    el.textContent = section.concise_explanation || `• ${section.concept}: Core principle and functional scope.\n• Action Point: Direct execution framework and key takeaways.`;
  } else {
    el.textContent = section.detailed_explanation || section.explanation;
  }
}

function setExplanationMode(mode) {
  state.explanationMode = mode;
  const btnConcise = document.getElementById('btn-exp-concise');
  const btnDetailed = document.getElementById('btn-exp-detailed');
  if (btnConcise) btnConcise.className = mode === 'concise' ? 'px-2.5 py-0.5 rounded text-[11px] font-semibold transition-all bg-white text-slate-900 shadow-xs' : 'px-2.5 py-0.5 rounded text-[11px] font-semibold transition-all text-slate-600 hover:text-slate-900';
  if (btnDetailed) btnDetailed.className = mode === 'detailed' ? 'px-2.5 py-0.5 rounded text-[11px] font-semibold transition-all bg-white text-slate-900 shadow-xs' : 'px-2.5 py-0.5 rounded text-[11px] font-semibold transition-all text-slate-600 hover:text-slate-900';
  renderExplanationText();
}

// --- Visual Canvas Simulation Engine ---
function startVisualSimulation(visualType, section) {
  const canvas = document.getElementById('visual-canvas');
  const imgEl = document.getElementById('visual-extracted-img');
  const svgEl = document.getElementById('visual-svg-container');
  const modeLabel = document.getElementById('visual-mode-label');

  if (state.simulation.animFrameId) {
    cancelAnimationFrame(state.simulation.animFrameId);
  }

  const conceptLower = (section.concept || '').toLowerCase();
  const topicLower = (state.lessonPlan?.topic_or_chapter || '').toLowerCase();
  const isCircuitTopic = conceptLower.includes('circuit') || conceptLower.includes('ohm') || conceptLower.includes('voltage') || topicLower.includes('circuit') || topicLower.includes('ohm');

  const controlsBar = document.getElementById('interactive-controls-bar');
  if (controlsBar) {
    if (!isCircuitTopic) {
      controlsBar.classList.add('hidden');
    } else {
      controlsBar.classList.remove('hidden');
    }
  }

  // 1. If an extracted document image is attached to this section
  if (section.image_url || section.extracted_image_url) {
    const url = section.image_url || section.extracted_image_url;
    if (imgEl) {
      imgEl.onerror = () => {
        imgEl.classList.add('hidden');
        if (canvas) canvas.classList.remove('hidden');
        if (modeLabel) modeLabel.textContent = 'LLM Dynamic Diagram';
        drawDynamicConceptDiagram(canvas.getContext('2d'), canvas.width, canvas.height, section);
      };
      imgEl.src = url;
      imgEl.classList.remove('hidden');
    }
    if (canvas) canvas.classList.add('hidden');
    if (svgEl) svgEl.classList.add('hidden');
    if (modeLabel) modeLabel.textContent = 'Extracted Document Figure';
    return;
  }

  // Hide image viewer, show dynamic canvas
  if (imgEl) imgEl.classList.add('hidden');
  if (svgEl) svgEl.classList.add('hidden');
  if (canvas) canvas.classList.remove('hidden');

  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function loop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (isCircuitTopic) {
      if (visualType === 'graph') {
        if (modeLabel) modeLabel.textContent = "Ohm's Law V-I Graph";
        drawOhmsLawGraph(ctx, canvas.width, canvas.height);
      } else if (visualType === 'equation' || visualType === 'formula') {
        if (modeLabel) modeLabel.textContent = "Ohm's Law Formula";
        drawFormulaVisual(ctx, canvas.width, canvas.height, section);
      } else {
        if (modeLabel) modeLabel.textContent = 'Circuit Concept Diagram';
        drawDynamicConceptDiagram(ctx, canvas.width, canvas.height, section);
      }
    } else {
      if (visualType === 'graph') {
        if (modeLabel) modeLabel.textContent = 'Concept Data Graph';
        drawDynamicConceptGraph(ctx, canvas.width, canvas.height, section);
      } else if (visualType === 'equation' || visualType === 'formula') {
        if (modeLabel) modeLabel.textContent = 'Concept Spec & Formula';
        drawDynamicFormulaVisual(ctx, canvas.width, canvas.height, section);
      } else {
        if (modeLabel) modeLabel.textContent = 'LLM Dynamic Diagram';
        drawDynamicConceptDiagram(ctx, canvas.width, canvas.height, section);
      }
    }

    state.simulation.particleOffset += 1.5;
    state.simulation.animFrameId = requestAnimationFrame(loop);
  }

  loop();
}

function updateCircuitSimulation() {
  const v = parseFloat(document.getElementById('slider-voltage')?.value || 12);
  const r = parseFloat(document.getElementById('slider-resistance')?.value || 4);
  const i = v / r;

  state.simulation.voltage = v;
  state.simulation.resistance = r;
  state.simulation.current = i;

  const valV = document.getElementById('val-voltage');
  const valR = document.getElementById('val-resistance');
  const valI = document.getElementById('val-current');

  if (valV) valV.textContent = `${v}V`;
  if (valR) valR.textContent = `${r}Ω`;
  if (valI) valI.textContent = i.toFixed(2);
}

// Draw dynamic concept diagram on canvas based on section concepts & LLM nodes
function drawDynamicConceptDiagram(ctx, w, h, section) {
  // Dark glassmorphic background
  ctx.fillStyle = '#0b0f19';
  ctx.fillRect(0, 0, w, h);

  // Subtle grid
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  for (let x = 0; x < w; x += 40) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
  }
  for (let y = 0; y < h; y += 40) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  // Header Title
  ctx.fillStyle = '#f8fafc';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.fillText(`CONCEPT FLOW: ${section.concept.toUpperCase()}`, 20, 28);

  const details = section.visual_details || {};
  let rawNodes = details.nodes;
  if (!rawNodes || !Array.isArray(rawNodes) || rawNodes.length === 0) {
    const conceptWords = section.concept.split(' ');
    rawNodes = [
      { label: `${conceptWords[0] || 'Input'} Component`, category: 'input', description: 'Initial state / driver' },
      { label: `${conceptWords[1] || 'Process'} Mechanism`, category: 'process', description: 'Core functional interaction' },
      { label: `${conceptWords[2] || 'Output'} Result`, category: 'output', description: 'Observed outcome / yield' }
    ];
  }

  const numNodes = Math.min(rawNodes.length, 4);
  const boxW = numNodes <= 3 ? 150 : 120;
  const boxH = 90;
  const gap = numNodes <= 3 ? 45 : 25;
  const totalW = numNodes * boxW + (numNodes - 1) * gap;
  const startX = (w - totalW) / 2;
  const cy = h / 2 - 10;

  const nodeColors = {
    input: { bg: 'rgba(56, 189, 248, 0.15)', border: '#38bdf8', text: '#38bdf8' },
    process: { bg: 'rgba(168, 85, 247, 0.15)', border: '#a855f7', text: '#a855f7' },
    output: { bg: 'rgba(52, 211, 153, 0.15)', border: '#34d399', text: '#34d399' },
    primary: { bg: 'rgba(99, 102, 241, 0.15)', border: '#6366f1', text: '#818cf8' }
  };

  const nodePositions = [];

  // Render Connections & Animated Flow Particles
  for (let i = 0; i < numNodes; i++) {
    const nx = startX + i * (boxW + gap);
    const ny = cy - boxH / 2;
    nodePositions.push({ x: nx, y: ny, w: boxW, h: boxH });

    if (i < numNodes - 1) {
      const nextX = startX + (i + 1) * (boxW + gap);
      const startPointX = nx + boxW;
      const endPointX = nextX;

      // Connection Line
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(startPointX, cy);
      ctx.lineTo(endPointX, cy);
      ctx.stroke();

      // Arrowhead
      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.moveTo(endPointX, cy);
      ctx.lineTo(endPointX - 8, cy - 5);
      ctx.lineTo(endPointX - 8, cy + 5);
      ctx.closePath();
      ctx.fill();

      // Animated Particle
      const lineLen = endPointX - startPointX;
      const particleDist = (state.simulation.particleOffset * 2.0) % lineLen;
      ctx.fillStyle = '#f43f5e';
      ctx.beginPath();
      ctx.arc(startPointX + particleDist, cy, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Render Node Cards
  for (let i = 0; i < numNodes; i++) {
    const pos = nodePositions[i];
    const nData = rawNodes[i];
    const cat = (nData.category || (i === 0 ? 'input' : (i === numNodes - 1 ? 'output' : 'process'))).toLowerCase();
    const style = nodeColors[cat] || nodeColors.primary;

    // Card Box
    ctx.fillStyle = style.bg;
    ctx.strokeStyle = style.border;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(pos.x, pos.y, pos.w, pos.h, 10);
    ctx.fill();
    ctx.stroke();

    // Node Badge
    ctx.fillStyle = style.border;
    ctx.font = 'bold 9px Inter, sans-serif';
    ctx.fillText(cat.toUpperCase(), pos.x + 10, pos.y + 18);

    // Node Label
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 11px Inter, sans-serif';
    const labelText = nData.label || nData.title || `Step ${i+1}`;
    ctx.fillText(labelText.length > 18 ? labelText.slice(0, 16) + '..' : labelText, pos.x + 10, pos.y + 42);

    // Node Description
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px Inter, sans-serif';
    const descText = nData.description || nData.desc || section.concept;
    ctx.fillText(descText.length > 20 ? descText.slice(0, 18) + '..' : descText, pos.x + 10, pos.y + 66);
  }

  // Key Formula / Takeaway Bar
  const formula = details.key_formula || section.example || `Key Principle: ${section.concept}`;
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.strokeStyle = '#34d399';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(20, h - 45, w - 40, 32, 8);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = '#34d399';
  ctx.font = 'bold 11px monospace';
  ctx.fillText(`⚡ ${formula.slice(0, 70)}`, 32, h - 25);
}

function drawOhmsLawGraph(ctx, w, h) {
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, w, h);

  const pad = 60;
  const originX = pad;
  const originY = h - pad;
  const graphW = w - pad * 2;
  const graphH = h - pad * 2;

  ctx.strokeStyle = '#475569';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(originX, pad);
  ctx.lineTo(originX, originY);
  ctx.lineTo(originX + graphW, originY);
  ctx.stroke();

  ctx.fillStyle = '#94a3b8';
  ctx.font = '12px Inter, sans-serif';
  ctx.fillText('Current I (Amperes) →', originX + graphW / 2 - 50, originY + 35);

  ctx.save();
  ctx.translate(originX - 35, originY - graphH / 2 + 50);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText('Voltage V (Volts) →', 0, 0);
  ctx.restore();

  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  for (let step = 1; step <= 5; step++) {
    const x = originX + (graphW / 5) * step;
    const y = originY - (graphH / 5) * step;
    ctx.beginPath(); ctx.moveTo(x, originY); ctx.lineTo(x, pad); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(originX, y); ctx.lineTo(originX + graphW, y); ctx.stroke();
  }

  const maxI = 6;
  const maxV = 24;
  const currentI = state.simulation.current;
  const currentV = state.simulation.voltage;

  const targetX = originX + (currentI / maxI) * graphW;
  const targetY = originY - (currentV / maxV) * graphH;

  ctx.strokeStyle = '#6366f1';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(originX, originY);
  ctx.lineTo(originX + graphW, originY - ((maxI * state.simulation.resistance) / maxV) * graphH);
  ctx.stroke();

  ctx.fillStyle = '#ec4899';
  ctx.beginPath();
  ctx.arc(targetX, targetY, 6, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#f472b6';
  ctx.font = 'bold 12px monospace';
  ctx.fillText(`(${currentI.toFixed(2)}A, ${currentV}V) | Slope = R = ${state.simulation.resistance}Ω`, targetX + 10, targetY - 10);
}

function drawDynamicConceptGraph(ctx, w, h, section) {
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, w, h);

  const pad = 60;
  const originX = pad;
  const originY = h - pad;
  const graphW = w - pad * 2;
  const graphH = h - pad * 2;

  // Grid Lines
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  for (let step = 1; step <= 5; step++) {
    const x = originX + (graphW / 5) * step;
    const y = originY - (graphH / 5) * step;
    ctx.beginPath(); ctx.moveTo(x, originY); ctx.lineTo(x, pad); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(originX, y); ctx.lineTo(originX + graphW, y); ctx.stroke();
  }

  // Axes
  ctx.strokeStyle = '#475569';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(originX, pad);
  ctx.lineTo(originX, originY);
  ctx.lineTo(originX + graphW, originY);
  ctx.stroke();

  // Axis Labels
  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px Inter, sans-serif';
  ctx.fillText('Execution Metric / Phase →', originX + graphW / 2 - 60, originY + 35);

  ctx.save();
  ctx.translate(originX - 35, originY - graphH / 2 + 40);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText('Performance Level →', 0, 0);
  ctx.restore();

  // Concept Title Header
  ctx.fillStyle = '#38bdf8';
  ctx.font = 'bold 13px Inter, sans-serif';
  ctx.fillText(`DATA TREND: ${section.concept.toUpperCase()}`, originX, pad - 20);

  // Animated Trend Curve
  ctx.strokeStyle = '#6366f1';
  ctx.lineWidth = 3;
  ctx.beginPath();
  const points = [];
  for (let i = 0; i <= 50; i++) {
    const px = originX + (graphW / 50) * i;
    const normX = i / 50;
    const normY = 1 / (1 + Math.exp(-6 * (normX - 0.5)));
    const py = originY - normY * graphH * 0.8 - 15;
    points.push({ x: px, y: py });
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.stroke();

  // Animated Glow Dot along curve
  const animIndex = Math.floor((state.simulation.particleOffset * 0.8) % points.length);
  const activePt = points[animIndex] || points[points.length - 1];

  ctx.fillStyle = '#ec4899';
  ctx.beginPath();
  ctx.arc(activePt.x, activePt.y, 6, 0, Math.PI * 2);
  ctx.fill();

  // Tooltip Callout
  const details = section.visual_details || {};
  const formulaText = details.key_formula || section.example || section.concept;
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.strokeStyle = '#34d399';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(Math.min(activePt.x, w - 240), Math.max(pad + 10, activePt.y - 45), 220, 32, 6);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = '#34d399';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(`📊 ${formulaText.slice(0, 32)}`, Math.min(activePt.x + 8, w - 232), Math.max(pad + 30, activePt.y - 25));
}

function drawDynamicFormulaVisual(ctx, w, h, section) {
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, w, h);

  const cx = w / 2;
  const cy = h / 2;

  // Header Title
  ctx.fillStyle = '#818cf8';
  ctx.font = 'bold 16px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(section.concept.toUpperCase(), cx, cy - 60);

  const details = section.visual_details || {};
  const formulaText = details.key_formula || section.example || `Core Principle: ${section.concept}`;

  // Formula Card Box
  ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(cx - (w * 0.4), cy - 25, w * 0.8, 65, 12);
  ctx.fill();
  ctx.stroke();

  // Big Formula text
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 18px monospace';
  ctx.fillText(formulaText.slice(0, 50), cx, cy + 12);

  // Subtext / Description
  ctx.font = '12px Inter, sans-serif';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText(section.explanation.slice(0, 80) + '...', cx, cy + 65);

  ctx.textAlign = 'left';
}

function drawFormulaVisual(ctx, w, h, section) {
  drawDynamicFormulaVisual(ctx, w, h, section);
}

// --- Audio & Narration (Web Speech API) ---
// --- Audio & Narration (Web Speech API) ---
function toggleSpeech() {
  if (!state.lessonPlan) return;
  const section = state.lessonPlan.sections[state.activeSectionIndex];
  const textToSpeak = section.narration_script || section.explanation;

  if (state.speech.isSpeaking) {
    if ('speechSynthesis' in window && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      updateAudioPlayerUI(true);
      return;
    } else {
      stopSpeech();
      return;
    }
  }

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    state.speech.utterance = new SpeechSynthesisUtterance(textToSpeak);
    const lang = state.lessonPlan.language || 'en';
    state.speech.utterance.lang = lang === 'hi' ? 'hi-IN' : (lang === 'es' ? 'es-ES' : 'en-US');
    state.speech.utterance.rate = state.speech.speed || 1.0;

    // Estimate duration based on word count (~150 words per minute)
    const words = textToSpeak.split(' ').length;
    state.speech.totalDuration = Math.max(10, Math.ceil(words / 2.5));
    state.speech.currentTime = 0;

    state.speech.utterance.onstart = () => {
      state.speech.isSpeaking = true;
      updateAudioPlayerUI(true);
      startAudioTicker();
    };

    state.speech.utterance.onend = () => {
      stopSpeech();
    };

    window.speechSynthesis.speak(state.speech.utterance);
  } else {
    alert('Web Speech API is not supported in this browser.');
  }
}

function stopSpeech() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  state.speech.isSpeaking = false;
  state.speech.currentTime = 0;
  if (state.speech.progressInterval) {
    clearInterval(state.speech.progressInterval);
  }
  updateAudioPlayerUI(false);
}

function skipSpeech(seconds) {
  if (!state.speech.isSpeaking) {
    toggleSpeech();
    return;
  }
  state.speech.currentTime = Math.max(0, Math.min(state.speech.totalDuration, state.speech.currentTime + seconds));
  const percent = state.speech.totalDuration > 0 ? (state.speech.currentTime / state.speech.totalDuration) : 0;
  const fill = document.getElementById('audio-progress-fill');
  if (fill) fill.style.width = `${percent * 100}%`;
  const curTime = document.getElementById('audio-time-current');
  if (curTime) curTime.textContent = formatAudioTime(state.speech.currentTime);

  if ('speechSynthesis' in window && state.lessonPlan && state.lessonPlan.sections) {
    window.speechSynthesis.cancel();
    const section = state.lessonPlan.sections[state.activeSectionIndex];
    const textToSpeak = section.narration_script || section.explanation;
    const charIndex = Math.floor(percent * textToSpeak.length);
    const slicedText = textToSpeak.slice(charIndex);

    if (slicedText.trim().length > 0) {
      state.speech.utterance = new SpeechSynthesisUtterance(slicedText);
      const lang = state.lessonPlan.language || 'en';
      state.speech.utterance.lang = lang === 'hi' ? 'hi-IN' : (lang === 'es' ? 'es-ES' : 'en-US');
      state.speech.utterance.rate = state.speech.speed || 1.0;
      state.speech.utterance.onend = () => stopSpeech();
      window.speechSynthesis.speak(state.speech.utterance);
    } else {
      stopSpeech();
    }
  }
}

function changeSpeechSpeed(speedStr) {
  state.speech.speed = parseFloat(speedStr) || 1.0;
  if (state.speech.isSpeaking) {
    toggleSpeech();
    toggleSpeech();
  }
}

function seekAudioProgress(event) {
  const bar = event.currentTarget;
  const rect = bar.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const percent = Math.max(0, Math.min(1, clickX / rect.width));
  state.speech.currentTime = Math.floor(percent * state.speech.totalDuration);
  const fill = document.getElementById('audio-progress-fill');
  if (fill) fill.style.width = `${percent * 100}%`;
  const curTime = document.getElementById('audio-time-current');
  if (curTime) curTime.textContent = formatAudioTime(state.speech.currentTime);

  if (state.speech.isSpeaking && 'speechSynthesis' in window && state.lessonPlan && state.lessonPlan.sections) {
    window.speechSynthesis.cancel();
    const section = state.lessonPlan.sections[state.activeSectionIndex];
    const textToSpeak = section.narration_script || section.explanation;
    const charIndex = Math.floor(percent * textToSpeak.length);
    const slicedText = textToSpeak.slice(charIndex);

    if (slicedText.trim().length > 0) {
      state.speech.utterance = new SpeechSynthesisUtterance(slicedText);
      const lang = state.lessonPlan.language || 'en';
      state.speech.utterance.lang = lang === 'hi' ? 'hi-IN' : (lang === 'es' ? 'es-ES' : 'en-US');
      state.speech.utterance.rate = state.speech.speed || 1.0;
      state.speech.utterance.onend = () => stopSpeech();
      window.speechSynthesis.speak(state.speech.utterance);
    } else {
      stopSpeech();
    }
  }
}

function startAudioTicker() {
  if (state.speech.progressInterval) clearInterval(state.speech.progressInterval);
  state.speech.progressInterval = setInterval(() => {
    if (!state.speech.isSpeaking) {
      clearInterval(state.speech.progressInterval);
      return;
    }
    state.speech.currentTime += 1;
    if (state.speech.currentTime > state.speech.totalDuration) {
      state.speech.currentTime = state.speech.totalDuration;
    }
    const percent = (state.speech.currentTime / state.speech.totalDuration) * 100;
    const fill = document.getElementById('audio-progress-fill');
    if (fill) fill.style.width = `${percent}%`;
    const curTime = document.getElementById('audio-time-current');
    if (curTime) curTime.textContent = formatAudioTime(state.speech.currentTime);
    const totTime = document.getElementById('audio-time-total');
    if (totTime) totTime.textContent = formatAudioTime(state.speech.totalDuration);
  }, 1000 / state.speech.speed);
}

function formatAudioTime(secs) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
}

function updateAudioPlayerUI(isPlaying) {
  const stateText = document.getElementById('speech-state-text');
  if (stateText) stateText.textContent = isPlaying ? 'Audio playing...' : 'Ready for narration';

  const playIcon = document.getElementById('speech-icon');
  if (playIcon) playIcon.setAttribute('data-lucide', isPlaying ? 'pause' : 'volume-2');

  const barPlayIcon = document.getElementById('audio-bar-play-icon');
  if (barPlayIcon) barPlayIcon.setAttribute('data-lucide', isPlaying ? 'pause' : 'play');

  refreshIcons();
}

// --- Checkpoint Modal & Evaluation Interaction ---
function openCheckpointModal() {
  if (!state.lessonPlan) return;
  const section = state.lessonPlan.sections[state.activeSectionIndex];
  const qObj = section.checkpoint_question;

  state.currentCheckpointQuestion = qObj;
  state.selectedCheckpointOption = null;

  document.getElementById('checkpoint-topic-name').textContent = section.concept;
  document.getElementById('checkpoint-question-text').textContent = qObj.question;

  const container = document.getElementById('checkpoint-options-container');
  container.innerHTML = '';

  qObj.options.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.className = 'w-full p-3 rounded-lg border border-slate-200 bg-slate-50 hover:border-indigo-500 text-left text-xs font-medium text-slate-800 flex items-center gap-3 transition-all option-btn';
    btn.innerHTML = `
      <span class="w-6 h-6 rounded bg-white border border-slate-300 flex items-center justify-center font-bold text-[11px] text-slate-700">
        ${String.fromCharCode(65 + idx)}
      </span>
      <span>${opt}</span>
    `;
    btn.onclick = () => {
      document.querySelectorAll('.option-btn').forEach(b => {
        b.classList.remove('border-indigo-600', 'bg-indigo-50', 'text-indigo-900');
        b.classList.add('bg-slate-50', 'border-slate-200');
      });
      btn.classList.remove('bg-slate-50', 'border-slate-200');
      btn.classList.add('border-indigo-600', 'bg-indigo-50', 'text-indigo-900');
      state.selectedCheckpointOption = opt;
    };
    container.appendChild(btn);
  });

  const feedback = document.getElementById('checkpoint-feedback');
  feedback.className = 'hidden rounded-lg p-4 transition-all';
  feedback.innerHTML = '';

  document.getElementById('modal-checkpoint').classList.remove('hidden');
  refreshIcons();
}

function closeCheckpointModal() {
  document.getElementById('modal-checkpoint').classList.add('hidden');
}

async function submitCheckpointAnswer() {
  if (!state.selectedCheckpointOption) {
    alert('Please select an option first.');
    return;
  }

  const qObj = state.currentCheckpointQuestion;
  const submitBtn = document.getElementById('btn-submit-answer');
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Evaluating...`;
  refreshIcons();

  try {
    const res = await fetch('/api/interact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: qObj.question,
        correct_answer: qObj.correct,
        student_answer: state.selectedCheckpointOption
      })
    });

    const result = await res.json();
    displayCheckpointFeedback(result);
  } catch (err) {
    console.error('Evaluation error:', err);
    alert('Error during answer evaluation.');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i> Submit Response`;
    refreshIcons();
  }
}

function displayCheckpointFeedback(res) {
  const feedback = document.getElementById('checkpoint-feedback');
  feedback.classList.remove('hidden');

  if (res.correct) {
    feedback.className = 'rounded-lg p-4 bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs space-y-2';
    feedback.innerHTML = `
      <div class="flex items-center gap-2 font-bold text-emerald-800">
        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-600"></i> Correct!
      </div>
      <p class="leading-relaxed">${res.new_explanation}</p>
      <div class="pt-2 flex justify-end">
        <button onclick="advanceToNextSection()" class="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-md text-xs font-semibold flex items-center gap-1">
          Next Section →
        </button>
      </div>
    `;
  } else {
    feedback.className = 'rounded-lg p-4 bg-rose-50 border border-rose-200 text-rose-900 text-xs space-y-3';
    feedback.innerHTML = `
      <div class="flex items-center gap-2 font-bold text-rose-800">
        <i data-lucide="alert-circle" class="w-4 h-4 text-rose-600"></i> Identified Concept Gap:
      </div>
      <p class="font-medium text-rose-950 bg-white p-2.5 rounded-md border border-rose-200">
        "${res.misconception}"
      </p>
      <div class="space-y-1">
        <span class="font-bold text-slate-700 text-[11px] uppercase tracking-wider">Clarification:</span>
        <p class="text-slate-800 leading-relaxed">${res.new_explanation}</p>
      </div>
      <div class="pt-2 flex justify-end gap-2">
        <button onclick="openCheckpointModal()" class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-md text-xs font-medium">
          Try Again
        </button>
      </div>
    `;
  }
  refreshIcons();
}

function advanceToNextSection() {
  closeCheckpointModal();
  if (state.activeSectionIndex < state.lessonPlan.sections.length - 1) {
    renderPlayerSection(state.activeSectionIndex + 1);
  } else {
    switchView('quiz');
  }
}

// --- Final Quiz & Learning Report ---
function filterQuizDifficulty(diff) {
  state.selectedQuizDifficulty = diff;
  ['all', 'easy', 'medium', 'hard'].forEach(d => {
    const btn = document.getElementById(`btn-diff-${d}`);
    if (!btn) return;
    if (d === diff) {
      btn.className = 'px-3 py-1 rounded-md text-xs font-semibold bg-white text-slate-900 shadow-xs';
    } else {
      const color = d === 'easy' ? 'text-emerald-700 hover:bg-emerald-50' : (d === 'medium' ? 'text-amber-700 hover:bg-amber-50' : (d === 'hard' ? 'text-rose-700 hover:bg-rose-50' : 'text-slate-600 hover:text-slate-900'));
      btn.className = `px-3 py-1 rounded-md text-xs font-semibold ${color}`;
    }
  });
  renderFinalQuiz();
}

function renderFinalQuiz() {
  if (!state.lessonPlan || !state.lessonPlan.final_quiz) return;
  const container = document.getElementById('final-quiz-container');
  container.innerHTML = '';

  const allQuiz = state.lessonPlan.final_quiz;
  const filteredQuiz = allQuiz.filter(q => {
    if (state.selectedQuizDifficulty === 'all') return true;
    return (q.difficulty || 'medium').toLowerCase() === state.selectedQuizDifficulty;
  });

  if (filteredQuiz.length === 0) {
    container.innerHTML = `
      <div class="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center text-xs text-slate-500">
        No questions found for the selected difficulty level '${state.selectedQuizDifficulty}'. Showing all questions.
      </div>
    `;
  }

  const listToRender = filteredQuiz.length > 0 ? filteredQuiz : allQuiz;

  listToRender.forEach((q, renderIdx) => {
    const qId = q.id || `q_${renderIdx}`;
    const diff = (q.difficulty || 'medium').toLowerCase();
    const badgeColor = diff === 'easy' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : (diff === 'medium' ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-rose-100 text-rose-800 border-rose-200');

    const card = document.createElement('div');
    card.className = 'bg-slate-50 p-5 rounded-xl border border-slate-200 space-y-3';
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold text-indigo-700 uppercase tracking-wider">Question ${renderIdx + 1}</span>
        <span class="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase border ${badgeColor}">${diff.toUpperCase()} LEVEL</span>
      </div>
      <h4 class="text-xs font-semibold text-slate-900">${q.question}</h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1" id="quiz-opt-group-${qId}">
        ${q.options.map((opt, optIdx) => {
          const isSelected = state.finalQuizAnswers[qId] === opt;
          const btnClass = isSelected
            ? `p-3 rounded-lg border-2 border-indigo-600 bg-indigo-50 text-indigo-950 font-medium text-left text-xs flex items-center gap-2 transition-all quiz-opt-btn-${qId}`
            : `p-3 rounded-lg border border-slate-200 bg-white hover:border-indigo-500 text-left text-xs text-slate-800 flex items-center gap-2 transition-all quiz-opt-btn-${qId}`;

          return `
            <button type="button" onclick="selectQuizAnswer('${qId}', '${opt.replace(/'/g, "\\'")}', this)" class="${btnClass}">
              <span class="w-5 h-5 rounded bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-[10px] text-slate-600">
                ${String.fromCharCode(65 + optIdx)}
              </span>
              <span>${opt}</span>
            </button>
          `;
        }).join('')}
      </div>
    `;
    container.appendChild(card);
  });
}

function selectQuizAnswer(qId, optValue, elem) {
  state.finalQuizAnswers[qId] = optValue;
  document.querySelectorAll(`.quiz-opt-btn-${qId}`).forEach(btn => {
    btn.className = `p-3 rounded-lg border border-slate-200 bg-white hover:border-indigo-500 text-left text-xs text-slate-800 flex items-center gap-2 transition-all quiz-opt-btn-${qId}`;
  });
  elem.className = `p-3 rounded-lg border-2 border-indigo-600 bg-indigo-50 text-indigo-950 font-medium text-left text-xs flex items-center gap-2 transition-all quiz-opt-btn-${qId}`;
}

async function submitFinalQuiz() {
  const finalQuiz = state.lessonPlan ? (state.lessonPlan.final_quiz || []) : [];
  if (Object.keys(state.finalQuizAnswers).length < finalQuiz.length && finalQuiz.length > 0) {
    if (!confirm('You have unanswered quiz questions. Submit anyway?')) {
      return;
    }
  }

  const quizResultsPayload = finalQuiz.map((q, idx) => {
    const qId = q.id || `q_${idx}`;
    const selected = state.finalQuizAnswers[qId] || "";
    const sel = selected.trim().toLowerCase();
    const corr = (q.correct || "").trim().toLowerCase();
    
    let isCorrect = false;
    if (sel && corr) {
      if (sel === corr) {
        isCorrect = true;
      } else if (sel.length === 1 && corr.startsWith(sel)) {
        isCorrect = true;
      } else if (corr.length === 1 && sel.startsWith(corr)) {
        isCorrect = true;
      } else if (sel.length > 3 && corr.length > 3 && (sel.includes(corr) || corr.includes(sel))) {
        isCorrect = true;
      }
    }

    return {
      question: q.question,
      selected: selected,
      correct: q.correct,
      is_correct: isCorrect,
      topic: q.concept_category || state.lessonPlan?.topic_or_chapter || "Module Assessment"
    };
  });

  const submitBtn = document.getElementById('btn-submit-quiz');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Processing Assessment...`;
  }
  refreshIcons();

  try {
    const res = await fetch('/api/assessment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quiz_results: quizResultsPayload })
    });

    const report = await res.json();
    state.lastReport = report;
    state.lastQuizResults = quizResultsPayload;
    renderReport(report, quizResultsPayload);
    
    // Live sync to Learner Profile & Performance Analytics
    syncLearnerProfileFromReport(report, quizResultsPayload);

    switchView('report');
  } catch (err) {
    console.error('Report submission error:', err);
    alert('Error generating report.');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i data-lucide="send" class="w-4 h-4"></i> Submit Quiz & View Performance Report`;
    }
    refreshIcons();
  }
}

function syncLearnerProfileFromReport(report, quizResults) {
  if (!state.user) {
    state.user = {
      name: "Student",
      email: "student@aiplatform.org",
      username: "student_user",
      learning_streak_days: 4,
      completed_lessons: 3,
      mastered_concepts: [],
      needs_review_concepts: []
    };
  }

  state.user.completed_lessons = (state.user.completed_lessons || 0) + 1;
  state.user.learning_streak_days = (state.user.learning_streak_days || 1) + 1;
  
  if (report.strong_areas) {
    state.user.mastered_concepts = Array.from(new Set([...(state.user.mastered_concepts || []), ...report.strong_areas]));
  }
  if (report.weak_areas) {
    state.user.needs_review_concepts = Array.from(new Set([...(state.user.needs_review_concepts || []), ...report.weak_areas]));
  }

  localStorage.setItem('ai_teacher_user', JSON.stringify(state.user));
  syncUserProfileUI();
}

function renderEmptyReport() {
  const scoreNum = document.getElementById('report-score-num');
  if (scoreNum) scoreNum.textContent = '0%';

  const tierBadge = document.getElementById('report-tier-badge');
  if (tierBadge) {
    tierBadge.textContent = 'Pending Assessment';
    tierBadge.className = 'mt-3 px-3 py-0.5 bg-slate-100 text-slate-700 border border-slate-300 rounded-full text-xs font-semibold';
  }

  const strongList = document.getElementById('report-strong-list');
  if (strongList) strongList.innerHTML = `<span class="text-xs text-slate-500 italic">No quiz submitted yet for this session.</span>`;

  const weakList = document.getElementById('report-weak-list');
  if (weakList) weakList.innerHTML = `<span class="text-xs text-slate-500 italic">No quiz submitted yet for this session.</span>`;

  const totalEl = document.getElementById('report-stat-total');
  if (totalEl) totalEl.textContent = '0';

  const correctEl = document.getElementById('report-stat-correct');
  if (correctEl) correctEl.textContent = '0';

  const recText = document.getElementById('report-recommendation-text');
  if (recText) recText.textContent = 'Complete the Module Evaluation Quiz in the Assessment tab to evaluate your knowledge and generate custom pedagogical recommendations.';
}

function renderReport(report, rawResults) {
  document.getElementById('report-score-num').textContent = `${report.score}%`;

  const tierBadge = document.getElementById('report-tier-badge');
  if (report.score >= 80) {
    tierBadge.textContent = 'Mastery Tier';
    tierBadge.className = 'mt-3 px-3 py-0.5 bg-emerald-100 text-emerald-800 border border-emerald-300 rounded-full text-xs font-semibold';
  } else if (report.score >= 50) {
    tierBadge.textContent = 'Proficient Tier';
    tierBadge.className = 'mt-3 px-3 py-0.5 bg-amber-100 text-amber-800 border border-amber-300 rounded-full text-xs font-semibold';
  } else {
    tierBadge.textContent = 'Foundational Tier';
    tierBadge.className = 'mt-3 px-3 py-0.5 bg-rose-100 text-rose-800 border border-rose-300 rounded-full text-xs font-semibold';
  }

  const strongList = document.getElementById('report-strong-list');
  strongList.innerHTML = '';
  if (report.strong_areas && report.strong_areas.length > 0) {
    report.strong_areas.forEach(area => {
      const tag = document.createElement('span');
      tag.className = 'px-2.5 py-1 bg-white text-slate-700 border border-slate-200 rounded text-xs font-medium';
      tag.textContent = area;
      strongList.appendChild(tag);
    });
  } else {
    strongList.innerHTML = `<span class="text-xs text-slate-500 italic">None identified in this attempt.</span>`;
  }

  const weakList = document.getElementById('report-weak-list');
  weakList.innerHTML = '';
  if (report.weak_areas && report.weak_areas.length > 0) {
    report.weak_areas.forEach(area => {
      const tag = document.createElement('span');
      tag.className = 'px-2.5 py-1 bg-rose-50 text-rose-800 border border-rose-200 rounded text-xs font-medium';
      tag.textContent = area;
      weakList.appendChild(tag);
    });
  } else {
    weakList.innerHTML = `<span class="text-xs text-slate-500 italic">None! All concepts passed.</span>`;
  }

  const total = rawResults.length;
  const correct = rawResults.filter(r => r.is_correct).length;
  document.getElementById('report-stat-total').textContent = total;
  document.getElementById('report-stat-correct').textContent = correct;
  document.getElementById('report-recommendation-text').textContent = report.recommendation;
}

// --- Bonus Hub: Dynamic Flashcards, Concept Mind Map & Study Notes ---
async function loadBonusFeatures() {
  switchBonusTab('flashcards');
  try {
    const res = await fetch('/api/study-tools');
    const data = await res.json();

    state.flashcards = data.flashcards || [];
    state.currentFlashcardIndex = 0;
    renderCurrentFlashcard();

    document.getElementById('notes-content-box').textContent = data.study_notes || "";
    state.taxonomyTree = data.taxonomy_tree;
    state.pipelineFlow = data.pipeline_flow || [];

    drawMindMapCanvas();
  } catch (err) {
    console.error('Bonus features loading error:', err);
  }
}

function switchBonusTab(tab) {
  ['flashcards', 'mindmap', 'notes'].forEach(t => {
    document.getElementById(`bonus-tab-${t}`).classList.add('hidden');
    const btn = document.getElementById(`tab-btn-${t}`);
    if (btn) btn.className = 'px-4 py-2 rounded-md text-xs font-semibold text-slate-600 hover:text-slate-900';
  });

  document.getElementById(`bonus-tab-${tab}`).classList.remove('hidden');
  const activeBtn = document.getElementById(`tab-btn-${tab}`);
  if (activeBtn) activeBtn.className = 'px-4 py-2 rounded-md text-xs font-semibold bg-sky-600 text-white';

  if (tab === 'mindmap') {
    drawMindMapCanvas();
  }
}

function renderCurrentFlashcard() {
  if (state.flashcards.length === 0) return;
  const card = state.flashcards[state.currentFlashcardIndex];
  state.isFlashcardFlipped = false;
  document.getElementById('flashcard-inner').classList.remove('flipped');

  document.getElementById('flashcard-counter').textContent = `${state.currentFlashcardIndex + 1} / ${state.flashcards.length}`;
  document.getElementById('fc-front-text').textContent = card.front;
  document.getElementById('fc-back-text').textContent = card.back;
  document.getElementById('fc-example-text').textContent = card.example ? `Example: ${card.example}` : '';
}

function flipCurrentFlashcard() {
  state.isFlashcardFlipped = !state.isFlashcardFlipped;
  const inner = document.getElementById('flashcard-inner');
  if (state.isFlashcardFlipped) {
    inner.classList.add('flipped');
  } else {
    inner.classList.remove('flipped');
  }
}

function prevFlashcard() {
  if (state.currentFlashcardIndex > 0) {
    state.currentFlashcardIndex--;
    renderCurrentFlashcard();
  }
}

function nextFlashcard() {
  if (state.currentFlashcardIndex < state.flashcards.length - 1) {
    state.currentFlashcardIndex++;
    renderCurrentFlashcard();
  }
}

function copyStudyNotes() {
  const notes = document.getElementById('notes-content-box').textContent;
  navigator.clipboard.writeText(notes).then(() => {
    alert('Study notes copied to clipboard!');
  });
}

function setMindmapMode(mode) {
  state.mindmapMode = mode;
  const btnTree = document.getElementById('btn-mm-tree');
  const btnPipe = document.getElementById('btn-mm-pipeline');
  if (btnTree && btnPipe) {
    if (mode === 'tree') {
      btnTree.className = 'px-3 py-1 rounded-md text-xs font-semibold transition-all bg-sky-600 text-white shadow-xs flex items-center gap-1';
      btnPipe.className = 'px-3 py-1 rounded-md text-xs font-semibold transition-all text-slate-600 hover:text-slate-900 flex items-center gap-1';
    } else {
      btnTree.className = 'px-3 py-1 rounded-md text-xs font-semibold transition-all text-slate-600 hover:text-slate-900 flex items-center gap-1';
      btnPipe.className = 'px-3 py-1 rounded-md text-xs font-semibold transition-all bg-sky-600 text-white shadow-xs flex items-center gap-1';
    }
  }
  drawMindMapCanvas();
}

function wrapCanvasText(ctx, text, x, y, maxWidth, lineHeight, maxLines = 2, align = 'center') {
  if (!text) return 0;
  ctx.textAlign = align;
  const words = text.split(' ');
  let line = '';
  let lines = [];

  for (let n = 0; n < words.length; n++) {
    const testLine = line + words[n] + ' ';
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth && n > 0) {
      lines.push(line.trim());
      line = words[n] + ' ';
      if (lines.length >= maxLines - 1) break;
    } else {
      line = testLine;
    }
  }
  lines.push(line.trim());

  const totalBlockH = (lines.length - 1) * lineHeight;
  const startY = y - totalBlockH / 2;

  lines.forEach((l, i) => {
    ctx.fillText(l, x, startY + i * lineHeight);
  });
  return lines.length;
}

function drawMindMapCanvas() {
  const canvas = document.getElementById('mindmap-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  const tree = state.taxonomyTree || {
    name: state.lessonPlan?.topic_or_chapter || "Study Module",
    children: [
      { name: "Pillar 1: System Scope", children: [{ name: "Architecture Specs" }, { name: "Input Baseline" }] },
      { name: "Pillar 2: Execution", children: [{ name: "Processing Pipeline" }, { name: "Operational Engine" }] }
    ]
  };

  if (state.mindmapMode === 'pipeline') {
    drawPipelineFlowchart(ctx, w, h, tree);
  } else {
    drawTreeMindMap(ctx, w, h, tree);
  }
}

function drawTreeMindMap(ctx, w, h, tree) {
  // Background
  ctx.fillStyle = '#090d16';
  ctx.fillRect(0, 0, w, h);

  // Subtle radial glow
  const radGrad = ctx.createRadialGradient(w / 2, 60, 10, w / 2, 60, 380);
  radGrad.addColorStop(0, 'rgba(56, 189, 248, 0.1)');
  radGrad.addColorStop(1, 'rgba(9, 13, 22, 0)');
  ctx.fillStyle = radGrad;
  ctx.fillRect(0, 0, w, h);

  const rootX = w * 0.5;
  const rootY = 48;
  const rootW = Math.min(340, w * 0.45);
  const rootH = 50;

  // Root Node
  ctx.fillStyle = '#0f172a';
  ctx.strokeStyle = '#6366f1';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.roundRect(rootX - rootW / 2, rootY - rootH / 2, rootW, rootH, 12);
  ctx.fill();
  ctx.stroke();

  // Root Badge
  ctx.fillStyle = '#818cf8';
  ctx.font = 'bold 9px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('DOCUMENT KNOWLEDGE TAXONOMY', rootX, rootY - 10);

  // Root Title with word-wrapping
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 12px Inter, sans-serif';
  wrapCanvasText(ctx, (tree.name || "Study Module").toUpperCase(), rootX, rootY + 9, rootW - 24, 14, 2, 'center');

  const children = tree.children || [];
  const numChildren = children.length;
  if (numChildren === 0) return;

  const colW = w / numChildren;
  const childY = 155;
  const palette = ['#38bdf8', '#a855f7', '#34d399', '#f59e0b', '#ec4899'];

  children.forEach((c, idx) => {
    const cx = colW * idx + colW / 2;
    const col = palette[idx % palette.length];

    // Smooth Bezier line to root
    ctx.strokeStyle = col + '77';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(rootX, rootY + rootH / 2);
    ctx.bezierCurveTo(rootX, (rootY + childY) / 2, cx, (rootY + childY) / 2, cx, childY - 26);
    ctx.stroke();

    // Pillar Card
    const cardW = Math.min(colW - 20, 200);
    const cardH = 52;

    ctx.fillStyle = 'rgba(15, 23, 42, 0.96)';
    ctx.strokeStyle = col;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(cx - cardW / 2, childY - cardH / 2, cardW, cardH, 10);
    ctx.fill();
    ctx.stroke();

    // Pillar Badge
    ctx.fillStyle = col;
    ctx.font = 'bold 9px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`PILLAR 0${idx + 1}`, cx, childY - 12);

    // Pillar Title
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 11px Inter, sans-serif';
    wrapCanvasText(ctx, c.name, cx, childY + 7, cardW - 16, 13, 2, 'center');

    // Sub-children: Stack vertically within this column's lane so they never overlap neighbors
    const subChildren = c.children || [];
    const subStartY = childY + 44;
    const subCardW = Math.min(colW - 24, 190);
    const subCardH = 32;

    subChildren.forEach((sc, sIdx) => {
      const sy = subStartY + sIdx * 46;

      // Connecting line from pillar to sub-node
      ctx.strokeStyle = col + '55';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(cx, childY + cardH / 2);
      ctx.lineTo(cx, sy - subCardH / 2);
      ctx.stroke();

      // Sub-node card
      ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
      ctx.strokeStyle = col + '88';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(cx - subCardW / 2, sy - subCardH / 2, subCardW, subCardH, 6);
      ctx.fill();
      ctx.stroke();

      // Accent dot
      ctx.fillStyle = col;
      ctx.beginPath();
      ctx.arc(cx - subCardW / 2 + 12, sy, 3.5, 0, Math.PI * 2);
      ctx.fill();

      // Sub-node full readable text
      ctx.fillStyle = '#e2e8f0';
      ctx.font = '10px Inter, sans-serif';
      wrapCanvasText(ctx, sc.name, cx + 8, sy, subCardW - 32, 12, 2, 'center');
    });
  });
}

function drawPipelineFlowchart(ctx, w, h, tree) {
  // Background
  ctx.fillStyle = '#070b14';
  ctx.fillRect(0, 0, w, h);

  // Flowchart title
  ctx.fillStyle = '#38bdf8';
  ctx.font = 'bold 10px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('⚡ DOCUMENT EXECUTION PIPELINE & PROCESS FLOW', 30, 32);

  const steps = (state.pipelineFlow && state.pipelineFlow.length > 0)
    ? state.pipelineFlow
    : (tree.children || []).map((c, i) => ({
        step: i + 1,
        title: c.name,
        visual_type: 'diagram',
        sub_steps: (c.children || []).map(sc => sc.name),
        summary: `Core execution phase ${i + 1} for ${c.name}`
      }));

  const numSteps = Math.min(steps.length, 5);
  if (numSteps === 0) return;

  const padX = 30;
  const colW = (w - padX * 2) / numSteps;
  const cardW = Math.min(colW - 28, 195);
  const cardH = 340;
  const cardY = 55;
  const palette = ['#38bdf8', '#a855f7', '#34d399', '#f59e0b', '#ec4899'];

  steps.slice(0, numSteps).forEach((st, idx) => {
    const cx = padX + colW * idx + colW / 2;
    const cardX = cx - cardW / 2;
    const col = palette[idx % palette.length];

    // Pipeline Step Card
    ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
    ctx.strokeStyle = col;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(cardX, cardY, cardW, cardH, 12);
    ctx.fill();
    ctx.stroke();

    // Header Badge
    ctx.fillStyle = col + '25';
    ctx.beginPath();
    ctx.roundRect(cardX + 10, cardY + 12, cardW - 20, 24, 6);
    ctx.fill();

    ctx.fillStyle = col;
    ctx.font = 'bold 10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`PHASE 0${idx + 1} • ${(st.visual_type || 'PROCESS').toUpperCase()}`, cx, cardY + 28);

    // Step Title
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px Inter, sans-serif';
    wrapCanvasText(ctx, st.title, cx, cardY + 62, cardW - 24, 15, 2, 'center');

    // Divider Line
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cardX + 12, cardY + 84);
    ctx.lineTo(cardX + cardW - 12, cardY + 84);
    ctx.stroke();

    // Sub-components / Operational Modules
    ctx.fillStyle = '#94a3b8';
    ctx.font = 'bold 9px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('CORE MECHANISMS & DATA:', cardX + 14, cardY + 102);

    const subSteps = st.sub_steps || [];
    subSteps.slice(0, 3).forEach((sub, sIdx) => {
      const capsuleY = cardY + 115 + sIdx * 44;

      ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
      ctx.strokeStyle = col + '55';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(cardX + 10, capsuleY, cardW - 20, 36, 6);
      ctx.fill();
      ctx.stroke();

      // Check bullet
      ctx.fillStyle = col;
      ctx.beginPath();
      ctx.arc(cardX + 22, capsuleY + 18, 4, 0, Math.PI * 2);
      ctx.fill();

      // Substep label
      ctx.fillStyle = '#f1f5f9';
      ctx.font = '10px Inter, sans-serif';
      wrapCanvasText(ctx, sub, cardX + 32, capsuleY + 18, cardW - 48, 12, 2, 'left');
    });

    // Deliverable / Metric footer
    const formulaText = st.key_formula || st.summary || `${st.title} Specification`;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
    ctx.strokeStyle = '#34d399';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(cardX + 8, cardY + cardH - 50, cardW - 16, 38, 6);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#34d399';
    ctx.font = '9px monospace';
    wrapCanvasText(ctx, `✓ ${formulaText}`, cx, cardY + cardH - 31, cardW - 24, 11, 2, 'center');

    // Connecting Arrow to Next Step
    if (idx < numSteps - 1) {
      const nextCardX = padX + colW * (idx + 1) + colW / 2 - cardW / 2;
      const startAx = cardX + cardW;
      const endAx = nextCardX;
      const midAy = cardY + 60;

      // Pipe Line
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(startAx, midAy);
      ctx.lineTo(endAx, midAy);
      ctx.stroke();

      // Directional Arrowhead
      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.moveTo(endAx, midAy);
      ctx.lineTo(endAx - 7, midAy - 5);
      ctx.lineTo(endAx - 7, midAy + 5);
      ctx.closePath();
      ctx.fill();
    }
  });
}

// --- USER AUTHENTICATION CONTROLLER ---
function openAuthModal() {
  document.getElementById('modal-auth').classList.remove('hidden');
  refreshIcons();
}

function closeAuthModal() {
  document.getElementById('modal-auth').classList.add('hidden');
}

function switchAuthTab(tab) {
  if (tab === 'login') {
    document.getElementById('form-auth-login').classList.remove('hidden');
    document.getElementById('form-auth-register').classList.add('hidden');
    document.getElementById('auth-tab-login').className = 'flex-1 py-1.5 rounded-md text-xs font-semibold bg-white text-slate-900 shadow-xs transition-all';
    document.getElementById('auth-tab-register').className = 'flex-1 py-1.5 rounded-md text-xs font-semibold text-slate-600 hover:text-slate-900 transition-all';
  } else {
    document.getElementById('form-auth-login').classList.add('hidden');
    document.getElementById('form-auth-register').classList.remove('hidden');
    document.getElementById('auth-tab-register').className = 'flex-1 py-1.5 rounded-md text-xs font-semibold bg-white text-slate-900 shadow-xs transition-all';
    document.getElementById('auth-tab-login').className = 'flex-1 py-1.5 rounded-md text-xs font-semibold text-slate-600 hover:text-slate-900 transition-all';
  }
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username_or_email: username, password: password })
    });
    const data = await res.json();
    state.user = data.profile;
    localStorage.setItem('ai_teacher_user', JSON.stringify(state.user));
    syncUserProfileUI();
    closeAuthModal();
    alert(`Welcome back, ${state.user.name || username}!`);
  } catch (err) {
    console.error('Login error:', err);
    alert('Error logging in.');
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('reg-name').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;
  const level = document.getElementById('reg-level').value;
  const language = document.getElementById('reg-lang').value;

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        email: email,
        username: username,
        password: password,
        level: level,
        language: language
      })
    });
    const data = await res.json();
    state.user = data.profile;
    localStorage.setItem('ai_teacher_user', JSON.stringify(state.user));
    syncUserProfileUI();
    closeAuthModal();
    alert(`Account created successfully! Welcome ${name}.`);
  } catch (err) {
    console.error('Register error:', err);
    alert('Error registering user.');
  }
}

function syncUserProfileUI() {
  const uNameSpan = document.getElementById('header-user-name');
  const user = state.user;

  if (uNameSpan) {
    uNameSpan.textContent = user ? (user.name || user.username) : 'Login / Register';
  }

  // Sync Learner Profile View elements
  const avatarEl = document.getElementById('profile-avatar-circle');
  if (avatarEl) {
    const displayName = user ? (user.name || user.username || 'Student') : 'Student';
    const parts = displayName.trim().split(' ');
    const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : displayName.slice(0, 2).toUpperCase();
    avatarEl.textContent = initials;
  }

  const nameEl = document.getElementById('profile-display-name');
  if (nameEl) nameEl.textContent = user ? (user.name || user.username || 'Student Learner') : 'Student Learner';

  const emailEl = document.getElementById('profile-display-email');
  if (emailEl) emailEl.textContent = user ? (user.email || 'student@aiplatform.org') : 'student@aiplatform.org';

  const idEl = document.getElementById('profile-display-id');
  if (idEl) idEl.textContent = `ID: ${user ? (user.username || 'student_001') : 'student_001'}`;

  const streakEl = document.getElementById('profile-streak-count');
  if (streakEl) streakEl.textContent = `${user ? (user.learning_streak_days || 1) : 1} Days`;

  const completedEl = document.getElementById('profile-completed-count');
  if (completedEl) completedEl.textContent = `${user ? (user.completed_lessons || 0) : 0} Modules`;

  const topicSummaryEl = document.getElementById('profile-topic-summary');
  if (topicSummaryEl) {
    topicSummaryEl.textContent = state.lessonPlan ? (state.lessonPlan.topic_or_chapter || 'Active Curriculum Progress') : 'Active Curriculum Progress';
  }

  const levelEl = document.getElementById('profile-level-display');
  if (levelEl) {
    const lvl = user ? (user.preferred_level || user.level || 'beginner') : 'beginner';
    levelEl.textContent = lvl.charAt(0).toUpperCase() + lvl.slice(1);
  }

  // Mastered concepts ledger
  const masteredLedger = document.getElementById('profile-mastered-ledger');
  if (masteredLedger) {
    const masteredList = user && user.mastered_concepts ? user.mastered_concepts : [];
    if (masteredList.length === 0) {
      masteredLedger.innerHTML = `<span class="text-xs text-slate-500 italic">Complete assessments to record mastered concepts.</span>`;
    } else {
      masteredLedger.innerHTML = masteredList.map(c => `
        <span class="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded text-xs font-semibold flex items-center gap-1.5 shadow-xs">
          <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> ${c}
        </span>
      `).join('');
    }
  }

  // Review concepts ledger
  const reviewLedger = document.getElementById('profile-review-ledger');
  if (reviewLedger) {
    const reviewList = user && user.needs_review_concepts ? user.needs_review_concepts : [];
    if (reviewList.length === 0) {
      reviewLedger.innerHTML = `<span class="text-xs text-slate-500 italic">No concept gaps identified.</span>`;
    } else {
      reviewLedger.innerHTML = reviewList.map(c => `
        <span class="px-2.5 py-1 bg-rose-50 text-rose-800 border border-rose-200 rounded text-xs font-semibold flex items-center gap-1.5 shadow-xs">
          <i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-rose-600"></i> ${c}
        </span>
      `).join('');
    }
  }

  refreshIcons();
}
