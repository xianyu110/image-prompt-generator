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
  if (item.model.includes("GPT")) els.modelSelect.value = "GPT Image 2";
  generatePrompt();
  copyText(item.prompt);
  document.querySelector("#generator").scrollIntoView({ behavior: "smooth", block: "start" });
}

function generatePrompt() {
  const subject = els.subjectInput.value.trim() || "一张高质量 AI 图片";
  const style = els.styleSelect.value;
  const model = els.modelSelect.value;
  const ratio = els.ratioSelect.value;
  const modelHint = model === "Seedream 5 Pro"
    ? "强调可控编辑、文字可读性、多轮改图和商业设计落地。"
    : model === "Nano Banana Pro"
      ? "强调创意发散、复杂画面、多图融合和风格化视觉。"
      : "强调真实世界知识、文本渲染、精确构图和高质量细节。";
  els.builderOutput.textContent = [
    `请生成：${subject}`,
    `模型方向：${model}。${modelHint}`,
    `视觉风格：${style}。`,
    `画面比例：${ratio}。`,
    "构图要求：主体明确，层次清晰，保留足够留白，画面有完整的光影和材质细节。",
    "质量要求：文字清晰可读，无水印，无多余畸变，不要破损手指、错误透视或脏乱背景。",
  ].join("\n");
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
