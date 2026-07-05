const state = {
  prompts: [],
  filtered: [],
  featuredOffset: 0,
  query: "",
  model: "全部模型",
  category: "全部分类",
  activePrompt: null,
};

const els = {
  search: document.querySelector("#searchInput"),
  promptGrid: document.querySelector("#promptGrid"),
  featuredGrid: document.querySelector("#featuredGrid"),
  resultCount: document.querySelector("#resultCount"),
  modelFilters: document.querySelector("#modelFilters"),
  categoryFilters: document.querySelector("#categoryFilters"),
  emptyState: document.querySelector("#emptyState"),
  shuffleButton: document.querySelector("#shuffleButton"),
  builderForm: document.querySelector("#builderForm"),
  subjectInput: document.querySelector("#subjectInput"),
  styleSelect: document.querySelector("#styleSelect"),
  modelSelect: document.querySelector("#modelSelect"),
  ratioSelect: document.querySelector("#ratioSelect"),
  generatedOutput: document.querySelector("#generatedOutput"),
  builderOutput: document.querySelector("#builderOutput"),
  copyGeneratedButton: document.querySelector("#copyGeneratedButton"),
  promptModal: document.querySelector("#promptModal"),
  modalClose: document.querySelector("#modalClose"),
  modalImage: document.querySelector("#modalImage"),
  modalAuthor: document.querySelector("#modalAuthor"),
  modalTitle: document.querySelector("#modalTitle"),
  modalPrompt: document.querySelector("#modalPrompt"),
  modalSource: document.querySelector("#modalSource"),
  copyModalButton: document.querySelector("#copyModalButton"),
  toast: document.querySelector("#toast"),
  menuButton: document.querySelector("#menuButton"),
};

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalize(value) {
  return String(value || "").toLowerCase();
}

function truncate(value, max = 230) {
  if (!value || value.length <= max) return value;
  return `${value.slice(0, max).trim()}...`;
}

function authorLabel(item) {
  const source = item.source || "unknown";
  if (source.includes("@")) return source;
  return source.startsWith("@") ? source : `@${source}`;
}

function timeLabel(item) {
  if (item.id.startsWith("gpt-")) return "X 来源";
  if (item.id.startsWith("seedream-")) return "原创";
  return "精选";
}

function imageBlock(item) {
  if (item.image) {
    return `<div class="card-image"><img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.title)}" loading="lazy"></div>`;
  }
  return `<div class="card-image"><div class="image-fallback">${escapeHtml(item.model)}<br>${escapeHtml(item.category)}</div></div>`;
}

function cardTemplate(item) {
  return `
    <article class="prompt-card" data-id="${escapeHtml(item.id)}" tabindex="0">
      <div class="card-top">
        <span class="author">作者 ${escapeHtml(authorLabel(item))}</span>
        <span class="date">${escapeHtml(timeLabel(item))}</span>
      </div>
      ${imageBlock(item)}
      <div class="prompt-preview">
        <div class="preview-bar">查看完整提示词 →</div>
        <p>${escapeHtml(truncate(item.prompt))}</p>
      </div>
      <div class="tag-row">
        <span class="tag model">${escapeHtml(item.model)}</span>
        <span class="tag">${escapeHtml(item.category)}</span>
      </div>
      <div class="card-actions">
        <button class="try-button" type="button" data-try-id="${escapeHtml(item.id)}">立即尝试</button>
        <a class="share-button" href="${escapeHtml(item.sourceUrl || "#")}" target="_blank" rel="noreferrer" aria-label="查看来源">↗</a>
      </div>
    </article>
  `;
}

function renderFeatured() {
  const gpt = state.prompts.filter((item) => item.model === "GPT Image 2" && item.image);
  const withImages = state.prompts.filter((item) => item.image && item.model !== "GPT Image 2");
  const pool = gpt.concat(withImages, state.prompts.filter((item) => !item.image));
  const start = state.featuredOffset % Math.max(pool.length, 1);
  const items = [...pool.slice(start, start + 6), ...pool.slice(0, Math.max(0, start + 6 - pool.length))].slice(0, 6);
  els.featuredGrid.innerHTML = items.map(cardTemplate).join("");
}

function renderGrid() {
  els.promptGrid.innerHTML = state.filtered.map(cardTemplate).join("");
  els.emptyState.hidden = state.filtered.length > 0;
  els.resultCount.textContent = `${state.filtered.length} 条提示词 · 共 ${state.prompts.length} 条`;
}

function buildFilter(container, values, active, allLabel, key) {
  container.innerHTML = [allLabel, ...values].map((value) => {
    const isActive = value === active ? " active" : "";
    return `<button class="filter-chip${isActive}" type="button" data-filter="${key}" data-value="${escapeHtml(value)}">${escapeHtml(value)}</button>`;
  }).join("");
}

function renderFilters() {
  buildFilter(els.modelFilters, unique(state.prompts.map((item) => item.model)), state.model, "全部模型", "model");
  buildFilter(els.categoryFilters, unique(state.prompts.map((item) => item.category)), state.category, "全部分类", "category");
}

function applyFilters() {
  const q = normalize(state.query);
  state.filtered = state.prompts.filter((item) => {
    const modelMatch = state.model === "全部模型" || item.model === state.model;
    const categoryMatch = state.category === "全部分类" || item.category === state.category;
    const haystack = normalize([
      item.title,
      item.model,
      item.category,
      item.source,
      item.prompt,
    ].join(" "));
    return modelMatch && categoryMatch && (!q || haystack.includes(q));
  });
  renderFilters();
  renderGrid();
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }
  showToast("已复制提示词");
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => els.toast.classList.remove("show"), 1600);
}

function openModal(item) {
  state.activePrompt = item;
  els.modalImage.innerHTML = item.image
    ? `<img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.title)}">`
    : `<div class="image-fallback">${escapeHtml(item.model)}<br>${escapeHtml(item.category)}</div>`;
  els.modalAuthor.textContent = `作者 ${authorLabel(item)} · ${item.model} · ${item.category}`;
  els.modalTitle.textContent = item.title;
  els.modalPrompt.textContent = item.prompt;
  els.modalSource.href = item.sourceUrl || "#";
  els.promptModal.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeModal() {
  els.promptModal.hidden = true;
  document.body.style.overflow = "";
}

function tryPrompt(item) {
  els.subjectInput.value = item.prompt;
  if (item.model.includes("Nano")) els.modelSelect.value = "Nano Banana Pro";
  if (item.model.includes("Seedream")) els.modelSelect.value = "Seedream 5 Pro";
  if (item.model.includes("GPT Image 1.5")) els.modelSelect.value = "GPT Image 1.5";
  if (item.model.includes("GPT Image 2")) els.modelSelect.value = "GPT Image 2";
  if (item.model.includes("Seedance")) els.modelSelect.value = "Seedance 2.0";
  if (item.model.includes("Grok")) els.modelSelect.value = "Grok Imagine";
  if (item.model.includes("Gemini")) els.modelSelect.value = "Gemini 3 Pro";
  generatePrompt();
  copyText(item.prompt);
  document.querySelector("#generator").scrollIntoView({ behavior: "smooth", block: "start" });
}

function generatePrompt() {
  const subject = els.subjectInput.value.trim() || "一张高质量 AI 图片";
  const style = els.styleSelect.value;
  const model = els.modelSelect.value;
  const ratio = els.ratioSelect.value;
  const modelHints = {
    "Seedream 5 Pro": "强调可控编辑、中文文字可读性、多轮改图、局部修改和商业设计落地。",
    "Nano Banana Pro": "强调创意发散、复杂画面、多图融合、风格化视觉和强烈视觉记忆点。",
    "GPT Image 2": "强调真实世界知识、文字渲染、精确构图、细节一致性和高质量成片。",
    "GPT Image 1.5": "强调稳定照片质感、自然光影、清晰主体和较少复杂文字的安全构图。",
    "Seedance 2.0": "可用于图片和视频；强调画面连续性、动作感、镜头语言、主体一致性和动态构图。",
    "Grok Imagine": "强调热点语境、社交传播感、强反差创意和可快速理解的画面钩子。",
    "Gemini 3 Pro": "强调复杂指令理解、多模态推理、信息结构和长上下文一致性。",
  };
  const shared = [
    `主题：${subject}`,
    `目标模型：${model}`,
    `模型策略：${modelHints[model] || "根据模型能力生成高质量视觉结果。"}`,
    `风格：${style}`,
    `比例：${ratio}`,
  ];
  const isVideoStoryboard = model === "Seedance 2.0" && style === "视频分镜";
  const output = isVideoStoryboard
    ? [
        ...shared,
        "视频结构：用 3-5 个镜头描述起承转合，每个镜头包含景别、主体动作、镜头运动、时长和转场。",
        "运动要求：动作连续、主体一致、避免突兀变形，镜头移动自然。",
        "质量要求：无水印，无错乱文字，无多余肢体，画面节奏适合短视频传播。",
      ]
    : [
        ...shared,
        "画面结构：主体明确，前景/中景/背景层次清晰，保留足够留白，光影和材质细节完整。",
        model === "Seedance 2.0" ? "Seedance 图片建议：即使生成单张图，也写清动作瞬间、运动方向、镜头焦段和动态张力。" : "",
        "文本要求：如画面包含文字，必须短、清楚、可读，并与版式自然融合。",
        "质量要求：无水印，无多余畸变，不要破损手指、错误透视、脏乱背景或低质贴图感。",
        "可替换变量：把 [主体]、[品牌/人物]、[场景]、[文字] 替换成你的具体需求。",
      ].filter(Boolean);
  els.builderOutput.textContent = output.join("\n");
  els.generatedOutput.hidden = false;
}

function findPrompt(id) {
  return state.prompts.find((item) => item.id === id);
}

function handleCardClick(event) {
  const tryButton = event.target.closest("[data-try-id]");
  if (tryButton) {
    event.preventDefault();
    event.stopPropagation();
    const item = findPrompt(tryButton.dataset.tryId);
    if (item) tryPrompt(item);
    return;
  }

  if (event.target.closest(".share-button")) {
    event.stopPropagation();
    return;
  }

  const card = event.target.closest(".prompt-card");
  if (card) {
    const item = findPrompt(card.dataset.id);
    if (item) openModal(item);
  }
}

function attachEvents() {
  document.addEventListener("click", handleCardClick);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !els.promptModal.hidden) closeModal();
    if ((event.key === "Enter" || event.key === " ") && event.target.closest(".prompt-card")) {
      event.preventDefault();
      const item = findPrompt(event.target.closest(".prompt-card").dataset.id);
      if (item) openModal(item);
    }
  });

  els.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    applyFilters();
  });

  document.addEventListener("click", (event) => {
    const filter = event.target.closest("[data-filter]");
    if (!filter) return;
    if (filter.dataset.filter === "model") state.model = filter.dataset.value;
    if (filter.dataset.filter === "category") state.category = filter.dataset.value;
    applyFilters();
  });

  els.shuffleButton.addEventListener("click", () => {
    state.featuredOffset += 6;
    renderFeatured();
  });

  els.builderForm.addEventListener("submit", (event) => {
    event.preventDefault();
    generatePrompt();
  });

  els.copyGeneratedButton.addEventListener("click", () => {
    if (els.builderOutput.textContent) copyText(els.builderOutput.textContent);
  });

  els.copyModalButton.addEventListener("click", () => {
    if (state.activePrompt) {
      copyText(state.activePrompt.prompt);
      tryPrompt(state.activePrompt);
      closeModal();
    }
  });

  els.modalClose.addEventListener("click", closeModal);
  els.promptModal.addEventListener("click", (event) => {
    if (event.target === els.promptModal) closeModal();
  });

  els.menuButton.addEventListener("click", () => {
    document.body.classList.toggle("menu-open");
  });

  document.querySelectorAll(".nav-links a").forEach((link) => {
    link.addEventListener("click", () => document.body.classList.remove("menu-open"));
  });
}

async function init() {
  const params = new URLSearchParams(window.location.search);
  state.query = params.get("q") || "";
  els.search.value = state.query;

  const response = await fetch("data/prompts.json");
  const data = await response.json();
  state.prompts = data.prompts || [];
  state.filtered = state.prompts;

  renderFeatured();
  applyFilters();
  attachEvents();
}

init().catch((error) => {
  console.error(error);
  els.emptyState.hidden = false;
  els.emptyState.textContent = "提示词数据加载失败。";
});
