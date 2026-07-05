const ALL_MODELS = "__all_models__";
const ALL_CATEGORIES = "__all_categories__";

const state = {
  prompts: [],
  filtered: [],
  featuredOffset: 0,
  query: "",
  model: ALL_MODELS,
  category: ALL_CATEGORIES,
  sort: "featured",
  language: "en",
  theme: "light",
  background: "green",
  activePrompt: null,
};

const copy = {
  en: {
    navGenerator: "Generator",
    navHot: "Trending Prompts",
    navLibrary: "Prompt Library",
    titleSticker: "Prompt Generator",
    heroSubtitle: "Fresh AI image prompts updated daily",
    generateLabel: "Generate",
    generatedTitle: "Generated Prompt",
    copy: "Copy",
    statPill: "30,000+ free image and video prompts",
    hotTitle: "Trending Prompts",
    shuffle: "Shuffle",
    libraryTitle: "Prompt Library",
    loading: "Loading...",
    searchLabel: "Search",
    searchPlaceholder: "Search author, model, style, prompt...",
    modelFilterLabel: "Model",
    categoryFilterLabel: "Category",
    sortLabel: "Sort",
    sortFeatured: "Featured",
    sortNewest: "Newest",
    sortModel: "Model A-Z",
    sortCategory: "Category A-Z",
    sortAuthor: "Author A-Z",
    emptyState: "No matching prompts found. Try another keyword or model.",
    allModels: "All models",
    allCategories: "All categories",
    resultCount: (shown, total) => `${shown} prompts · ${total} total`,
    author: "Author",
    selected: "Selected",
    original: "Original",
    curated: "Curated",
    sourceX: "X source",
    viewPrompt: "View full prompt →",
    tryIt: "Try it",
    copied: "Prompt copied",
    modalSource: "View source",
    faqTitle: "What is Image Prompt Generator?",
    faqOneTitle: "How is this different from a normal prompt list?",
    faqOneBody: "The page combines a model-aware prompt generator with a browsable prompt gallery. Each card keeps the author, source, image preview, model, and copy action.",
    faqTwoTitle: "Can I filter prompts by image model?",
    faqTwoBody: "Yes. Pick a model in the generator dropdown and the prompt gallery below switches to examples and templates for that model.",
    faqThreeTitle: "Why include Seedance 2.0?",
    faqThreeBody: "Seedance 2.0 is best known for multimodal video generation, while some third-party creator tools expose image workflows. This generator supports both image keyframe prompts and video storyboard prompts.",
    languageToggle: "中文",
    themeDark: "Dark",
    themeLight: "Light",
    backgroundLabel: "Background",
    backToTop: "Back to top",
    subjectFallback: "a high-quality AI image",
    loadError: "Prompt data failed to load.",
    metaTitle: "Image Prompt Generator | Free AI Image Prompt Generator",
    metaDescription: "Image Prompt Generator helps you create and explore AI image prompts for GPT Image, Seedream, Seedance, Grok Imagine, Gemini, and Nano Banana Pro, with images, authors, model filters, and one-click copy.",
  },
  zh: {
    navGenerator: "提示词生成",
    navHot: "热门提示词",
    navLibrary: "全部案例",
    titleSticker: "提示词生成器",
    heroSubtitle: "每日持续更新中",
    generateLabel: "生成",
    generatedTitle: "生成结果",
    copy: "复制",
    statPill: "30,000+ 免费图像、视频提示词",
    hotTitle: "热门提示词",
    shuffle: "换一批",
    libraryTitle: "全部提示词",
    loading: "正在加载...",
    searchLabel: "搜索",
    searchPlaceholder: "搜索作者、模型、风格、提示词...",
    modelFilterLabel: "模型",
    categoryFilterLabel: "分类",
    sortLabel: "排序",
    sortFeatured: "默认精选",
    sortNewest: "最新",
    sortModel: "模型 A-Z",
    sortCategory: "分类 A-Z",
    sortAuthor: "作者 A-Z",
    emptyState: "没有找到匹配的提示词，换个关键词或模型试试。",
    allModels: "全部模型",
    allCategories: "全部分类",
    resultCount: (shown, total) => `${shown} 条提示词 · 共 ${total} 条`,
    author: "作者",
    selected: "已选择",
    original: "原创",
    curated: "精选",
    sourceX: "X 来源",
    viewPrompt: "查看完整提示词 →",
    tryIt: "立即尝试",
    copied: "已复制提示词",
    modalSource: "查看来源",
    faqTitle: "Image Prompt Generator 是什么？",
    faqOneTitle: "这个网站和普通提示词列表有什么不同？",
    faqOneBody: "页面把模型感知的提示词生成器和可浏览案例库结合起来，每张卡片保留作者、来源、图片预览、模型和复制操作。",
    faqTwoTitle: "能按图片模型切换提示词吗？",
    faqTwoBody: "可以。在顶部生成器选择一个模型后，下方提示词案例会切换到对应模型的案例和模板。",
    faqThreeTitle: "为什么加入 Seedance 2.0？",
    faqThreeBody: "Seedance 2.0 更常见的官方定位是多模态视频生成，也有第三方创作工具提供图片工作流。这里同时支持静帧图像提示词和视频分镜提示词。",
    languageToggle: "English",
    themeDark: "深色",
    themeLight: "浅色",
    backgroundLabel: "背景",
    backToTop: "回到顶部",
    subjectFallback: "一张高质量 AI 图片",
    loadError: "提示词数据加载失败。",
    metaTitle: "Image Prompt Generator | AI 图片与视频提示词生成器",
    metaDescription: "Image Prompt Generator 收集 GPT Image、Seedream、Seedance、Grok、Gemini 等模型可用的 AI image prompt 案例，带图片、作者信息和一键复制。",
  },
};

const modelAliases = {
  "GPT Image 2": ["GPT Image 2"],
  "GPT Image 1.5": ["GPT Image 1.5"],
  "Nano Banana Pro": ["Nano Banana Pro"],
  "Seedream 5 Pro": ["Seedream 5 Pro", "Seedream"],
  "Seedance 2.0": ["Seedance 2.0"],
  "Grok Imagine": ["Grok Imagine"],
  "Gemini 3 Pro": ["Gemini 3 Pro"],
};

const builtInPrompts = [
  {
    id: "model-template-seedance-keyframe",
    title: "Seedance image keyframe prompt",
    model: "Seedance 2.0",
    category: "Video / Keyframe",
    source: "Image Prompt Generator",
    sourceUrl: "https://github.com/xianyu110/image-prompt-generator",
    image: "",
    prompt: "Create a cinematic keyframe as if it were the strongest still from a short video: [subject] moving through [scene], clear motion direction, consistent character identity, dynamic lens perspective, natural motion blur, realistic lighting, high-resolution details, no watermark.",
  },
  {
    id: "model-template-grok-social",
    title: "Grok Imagine social hook prompt",
    model: "Grok Imagine",
    category: "Social Creative",
    source: "Image Prompt Generator",
    sourceUrl: "https://github.com/xianyu110/image-prompt-generator",
    image: "",
    prompt: "Generate a bold social-first image about [topic]: instantly readable visual metaphor, strong contrast, expressive subject, sharp meme-like composition without text clutter, cinematic lighting, high detail, designed to be understood in one second.",
  },
  {
    id: "model-template-gemini-structured",
    title: "Gemini structured visual prompt",
    model: "Gemini 3 Pro",
    category: "Structured Prompt",
    source: "Image Prompt Generator",
    sourceUrl: "https://github.com/xianyu110/image-prompt-generator",
    image: "",
    prompt: "Create a highly structured image following these constraints: subject [subject], scene [scene], composition [layout], visual hierarchy [priority], style [style], color palette [palette], readable text only if necessary, consistent details across all objects, no extra limbs, no watermark.",
  },
];

const els = {
  search: document.querySelector("#searchInput"),
  searchLabel: document.querySelector("#searchLabel"),
  libraryModelSelect: document.querySelector("#libraryModelSelect"),
  libraryCategorySelect: document.querySelector("#libraryCategorySelect"),
  modelFilterLabel: document.querySelector("#modelFilterLabel"),
  categoryFilterLabel: document.querySelector("#categoryFilterLabel"),
  sortSelect: document.querySelector("#sortSelect"),
  sortLabel: document.querySelector("#sortLabel"),
  promptGrid: document.querySelector("#promptGrid"),
  featuredGrid: document.querySelector("#featuredGrid"),
  resultCount: document.querySelector("#resultCount"),
  modelFilters: document.querySelector("#modelFilters"),
  categoryFilters: document.querySelector("#categoryFilters"),
  emptyState: document.querySelector("#emptyState"),
  shuffleButton: document.querySelector("#shuffleButton"),
  builderForm: document.querySelector("#builderForm"),
  subjectInput: document.querySelector("#subjectInput"),
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
  languageToggle: document.querySelector("#languageToggle"),
  themeToggle: document.querySelector("#themeToggle"),
  backgroundSelect: document.querySelector("#backgroundSelect"),
  backgroundPickerLabel: document.querySelector(".background-picker span"),
  backToTopButton: document.querySelector("#backToTopButton"),
};

function t(key, ...args) {
  const value = copy[state.language][key] ?? copy.en[key] ?? key;
  return typeof value === "function" ? value(...args) : value;
}

function modelMatches(item, selectedModel) {
  if (selectedModel === ALL_MODELS) return true;
  const aliases = modelAliases[selectedModel] || [selectedModel];
  return aliases.includes(item.model);
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function compareText(a, b) {
  return String(a || "").localeCompare(String(b || ""), state.language === "zh" ? "zh-CN" : "en", {
    sensitivity: "base",
    numeric: true,
  });
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
  if (source === "Image Prompt Generator") return source;
  if (source.includes("@")) return source;
  return source.startsWith("@") ? source : `@${source}`;
}

function timeLabel(item) {
  if (item.id.startsWith("gpt-")) return t("sourceX");
  if (item.id.startsWith("seedream-") || item.id.startsWith("model-template-")) return t("original");
  return t("curated");
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
        <span class="author">${escapeHtml(t("author"))} ${escapeHtml(authorLabel(item))}</span>
        <span class="date">${escapeHtml(timeLabel(item))}</span>
      </div>
      ${imageBlock(item)}
      <div class="prompt-preview">
        <div class="preview-bar">${escapeHtml(t("viewPrompt"))}</div>
        <p>${escapeHtml(truncate(item.prompt))}</p>
      </div>
      <div class="tag-row">
        <span class="tag model">${escapeHtml(item.model)}</span>
        <span class="tag">${escapeHtml(item.category)}</span>
      </div>
      <div class="card-actions">
        <button class="try-button" type="button" data-try-id="${escapeHtml(item.id)}">${escapeHtml(t("tryIt"))}</button>
        <a class="share-button" href="${escapeHtml(item.sourceUrl || "#")}" target="_blank" rel="noreferrer" aria-label="查看来源">↗</a>
      </div>
    </article>
  `;
}

function renderFeatured() {
  const scoped = state.model === ALL_MODELS ? state.prompts : state.prompts.filter((item) => modelMatches(item, state.model));
  const gpt = scoped.filter((item) => item.model === "GPT Image 2" && item.image);
  const withImages = scoped.filter((item) => item.image && item.model !== "GPT Image 2");
  const pool = gpt.concat(withImages, scoped.filter((item) => !item.image));
  const start = state.featuredOffset % Math.max(pool.length, 1);
  const items = [...pool.slice(start, start + 6), ...pool.slice(0, Math.max(0, start + 6 - pool.length))].slice(0, 6);
  els.featuredGrid.innerHTML = items.map(cardTemplate).join("");
}

function renderGrid() {
  els.promptGrid.innerHTML = state.filtered.map(cardTemplate).join("");
  els.emptyState.hidden = state.filtered.length > 0;
  els.resultCount.textContent = t("resultCount", state.filtered.length, state.prompts.length);
}

function buildFilter(container, values, active, allLabel, key, allValue) {
  const items = [{ label: allLabel, value: allValue }, ...values.map((value) => ({ label: value, value }))];
  container.innerHTML = items.map((item) => {
    const value = item.value;
    const isActive = value === active ? " active" : "";
    return `<button class="filter-chip${isActive}" type="button" data-filter="${key}" data-value="${escapeHtml(value)}">${escapeHtml(item.label)}</button>`;
  }).join("");
}

function buildSelect(select, items, active) {
  select.innerHTML = items.map((item) => {
    const selected = item.value === active ? " selected" : "";
    return `<option value="${escapeHtml(item.value)}"${selected}>${escapeHtml(item.label)}</option>`;
  }).join("");
}

function renderSortOptions() {
  buildSelect(els.sortSelect, [
    { label: t("sortFeatured"), value: "featured" },
    { label: t("sortNewest"), value: "newest" },
    { label: t("sortModel"), value: "model" },
    { label: t("sortCategory"), value: "category" },
    { label: t("sortAuthor"), value: "author" },
  ], state.sort);
}

function renderFilters() {
  const modelItems = [{ label: t("allModels"), value: ALL_MODELS }, ...Object.keys(modelAliases).map((value) => ({ label: value, value }))];
  const categoryItems = [{ label: t("allCategories"), value: ALL_CATEGORIES }, ...unique(state.prompts.map((item) => item.category)).map((value) => ({ label: value, value }))];
  buildFilter(els.modelFilters, Object.keys(modelAliases), state.model, t("allModels"), "model", ALL_MODELS);
  buildFilter(els.categoryFilters, unique(state.prompts.map((item) => item.category)), state.category, t("allCategories"), "category", ALL_CATEGORIES);
  buildSelect(els.libraryModelSelect, modelItems, state.model);
  buildSelect(els.libraryCategorySelect, categoryItems, state.category);
}

function sortPrompts(items) {
  const bySourceOrder = (a, b) => (a._index || 0) - (b._index || 0);
  const sorted = [...items];
  if (state.sort === "newest") {
    return sorted.sort((a, b) => (b._index || 0) - (a._index || 0));
  }
  if (state.sort === "model") {
    return sorted.sort((a, b) => compareText(a.model, b.model) || bySourceOrder(a, b));
  }
  if (state.sort === "category") {
    return sorted.sort((a, b) => compareText(a.category, b.category) || bySourceOrder(a, b));
  }
  if (state.sort === "author") {
    return sorted.sort((a, b) => compareText(authorLabel(a), authorLabel(b)) || bySourceOrder(a, b));
  }
  return sorted.sort(bySourceOrder);
}

function applyFilters() {
  const q = normalize(state.query);
  const filtered = state.prompts.filter((item) => {
    const modelMatch = modelMatches(item, state.model);
    const categoryMatch = state.category === ALL_CATEGORIES || item.category === state.category;
    const haystack = normalize([
      item.title,
      item.model,
      item.category,
      item.source,
      item.prompt,
    ].join(" "));
    return modelMatch && categoryMatch && (!q || haystack.includes(q));
  });
  state.filtered = sortPrompts(filtered);
  renderFilters();
  renderFeatured();
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
  showToast(t("copied"));
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
  els.modalAuthor.textContent = `${t("author")} ${authorLabel(item)} · ${item.model} · ${item.category}`;
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

function setLanguage(language) {
  state.language = language === "zh" ? "zh" : "en";
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  localStorage.setItem("ipg-language", state.language);
  renderStaticCopy();
  applyFilters();
  if (!els.generatedOutput.hidden) generatePrompt();
}

function setTheme(theme) {
  state.theme = theme === "dark" ? "dark" : "light";
  document.documentElement.dataset.theme = state.theme;
  localStorage.setItem("ipg-theme", state.theme);
  els.themeToggle.textContent = state.theme === "dark" ? t("themeLight") : t("themeDark");
  els.themeToggle.setAttribute("aria-label", state.theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
}

function setBackground(background) {
  const allowed = ["green", "blue", "pink", "yellow", "black"];
  state.background = allowed.includes(background) ? background : "green";
  document.documentElement.dataset.bg = state.background;
  localStorage.setItem("ipg-background", state.background);
  els.backgroundSelect.value = state.background;
}

function renderStaticCopy() {
  document.title = t("metaTitle");
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) metaDescription.setAttribute("content", t("metaDescription"));
  document.querySelector("#navGenerator").textContent = t("navGenerator");
  document.querySelector("#navHot").textContent = t("navHot");
  document.querySelector("#navLibrary").textContent = t("navLibrary");
  document.querySelector("#titleSticker").textContent = t("titleSticker");
  document.querySelector("#heroSubtitle").textContent = t("heroSubtitle");
  document.querySelector("#generateLabel").textContent = t("generateLabel");
  document.querySelector("#generatedTitle").textContent = t("generatedTitle");
  els.copyGeneratedButton.textContent = t("copy");
  document.querySelector("#statPill").textContent = t("statPill");
  document.querySelector("#hotTitle").textContent = t("hotTitle");
  els.shuffleButton.textContent = t("shuffle");
  document.querySelector("#libraryTitle").textContent = t("libraryTitle");
  els.searchLabel.textContent = t("searchLabel");
  els.search.placeholder = t("searchPlaceholder");
  els.modelFilterLabel.textContent = t("modelFilterLabel");
  els.categoryFilterLabel.textContent = t("categoryFilterLabel");
  els.sortLabel.textContent = t("sortLabel");
  renderSortOptions();
  els.emptyState.textContent = t("emptyState");
  document.querySelector("#faqTitle").textContent = t("faqTitle");
  document.querySelector("#faqOneTitle").textContent = t("faqOneTitle");
  document.querySelector("#faqOneBody").textContent = t("faqOneBody");
  document.querySelector("#faqTwoTitle").textContent = t("faqTwoTitle");
  document.querySelector("#faqTwoBody").textContent = t("faqTwoBody");
  document.querySelector("#faqThreeTitle").textContent = t("faqThreeTitle");
  document.querySelector("#faqThreeBody").textContent = t("faqThreeBody");
  els.copyModalButton.textContent = t("tryIt");
  els.modalSource.textContent = t("modalSource");
  els.languageToggle.textContent = t("languageToggle");
  els.backgroundPickerLabel.textContent = t("backgroundLabel");
  els.backToTopButton.setAttribute("aria-label", t("backToTop"));
  els.backToTopButton.setAttribute("title", t("backToTop"));
  setTheme(state.theme);
  setBackground(state.background);
}

function syncModelFilterFromSelect() {
  state.model = els.modelSelect.value || ALL_MODELS;
  state.category = ALL_CATEGORIES;
  state.featuredOffset = 0;
  applyFilters();
}

function updateBackToTopVisibility() {
  els.backToTopButton.classList.toggle("show", window.scrollY > 520);
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
  state.model = els.modelSelect.value;
  state.category = ALL_CATEGORIES;
  generatePrompt();
  applyFilters();
  copyText(item.prompt);
  document.querySelector("#generator").scrollIntoView({ behavior: "smooth", block: "start" });
}

function generatePrompt() {
  const subject = els.subjectInput.value.trim() || t("subjectFallback");
  const model = els.modelSelect.value;
  const ratio = els.ratioSelect.value;
  const modelHints = state.language === "zh" ? {
    "Seedream 5 Pro": "强调可控编辑、中文文字可读性、多轮改图、局部修改和商业设计落地。",
    "Nano Banana Pro": "强调创意发散、复杂画面、多图融合、风格化视觉和强烈视觉记忆点。",
    "GPT Image 2": "强调真实世界知识、文字渲染、精确构图、细节一致性和高质量成片。",
    "GPT Image 1.5": "强调稳定照片质感、自然光影、清晰主体和较少复杂文字的安全构图。",
    "Seedance 2.0": "按静帧图像和视频分镜两种方式组织；强调主体一致、动作瞬间、镜头语言、运动方向和动态构图。",
    "Grok Imagine": "强调热点语境、社交传播感、强反差创意和可快速理解的画面钩子。",
    "Gemini 3 Pro": "强调复杂指令理解、多模态推理、信息结构和长上下文一致性。",
  } : {
    "Seedream 5 Pro": "Prioritize controllable edits, readable text, iterative image changes, local refinements, and commercial design output.",
    "Nano Banana Pro": "Prioritize creative exploration, complex scenes, multi-image fusion, stylized visuals, and memorable compositions.",
    "GPT Image 2": "Prioritize real-world knowledge, accurate text rendering, precise composition, detail consistency, and polished final imagery.",
    "GPT Image 1.5": "Prioritize stable photographic realism, natural lighting, clear subjects, and safe compositions with minimal complex text.",
    "Seedance 2.0": "Structure the prompt for both image keyframes and video storyboards; emphasize subject consistency, action beats, camera language, motion direction, and dynamic composition.",
    "Grok Imagine": "Prioritize trend-aware concepts, social shareability, strong visual contrast, and a clear one-second visual hook.",
    "Gemini 3 Pro": "Prioritize complex instruction following, multimodal reasoning, information structure, and long-context consistency.",
  };
  const shared = [
    state.language === "zh" ? `主题：${subject}` : `Subject: ${subject}`,
    state.language === "zh" ? `目标模型：${model}` : `Target model: ${model}`,
    state.language === "zh" ? `模型策略：${modelHints[model] || "根据模型能力生成高质量视觉结果。"}` : `Model strategy: ${modelHints[model] || "Create a high-quality visual result based on the model's strengths."}`,
    state.language === "zh" ? `比例：${ratio}` : `Aspect ratio: ${ratio}`,
  ];
  const output = state.language === "zh" ? [
        ...shared,
        "画面结构：主体明确，前景/中景/背景层次清晰，保留足够留白，光影和材质细节完整。",
        model === "Seedance 2.0" ? "Seedance 静帧建议：把单张图当作视频关键帧来写，明确动作瞬间、运动方向、镜头焦段和动态张力。" : "",
        model === "Seedance 2.0" ? "可选分镜扩展：如果要做视频，继续补 3-5 个镜头，每个镜头写清景别、主体动作、镜头运动、时长和转场。" : "",
        "文本要求：如画面包含文字，必须短、清楚、可读，并与版式自然融合。",
        "质量要求：无水印，无多余畸变，不要破损手指、错误透视、脏乱背景或低质贴图感。",
        "可替换变量：把 [主体]、[品牌/人物]、[场景]、[文字] 替换成你的具体需求。",
      ].filter(Boolean) : [
        ...shared,
        "Composition: clear subject, readable foreground/midground/background layers, enough negative space, complete lighting and material details.",
        model === "Seedance 2.0" ? "Seedance keyframe note: write a single image as a video keyframe with a clear action moment, motion direction, lens focal length, and dynamic tension." : "",
        model === "Seedance 2.0" ? "Optional storyboard extension: for video, add 3-5 shots and specify framing, subject action, camera movement, duration, and transition for each shot." : "",
        "Text rule: if text appears in the image, keep it short, readable, and naturally integrated with the layout.",
        "Quality rule: no watermark, no extra distortions, no broken fingers, wrong perspective, messy background, or low-quality texture.",
        "Replaceable variables: swap [subject], [brand/person], [scene], and [text] with your specific need.",
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

  els.libraryModelSelect.addEventListener("change", (event) => {
    state.model = event.target.value || ALL_MODELS;
    state.featuredOffset = 0;
    if (state.model !== ALL_MODELS) els.modelSelect.value = state.model;
    applyFilters();
  });

  els.libraryCategorySelect.addEventListener("change", (event) => {
    state.category = event.target.value || ALL_CATEGORIES;
    state.featuredOffset = 0;
    applyFilters();
  });

  els.sortSelect.addEventListener("change", (event) => {
    state.sort = event.target.value || "featured";
    applyFilters();
  });

  els.modelSelect.addEventListener("change", () => {
    syncModelFilterFromSelect();
    generatePrompt();
  });

  els.ratioSelect.addEventListener("change", () => {
    if (!els.generatedOutput.hidden) generatePrompt();
  });

  document.addEventListener("click", (event) => {
    const filter = event.target.closest("[data-filter]");
    if (!filter) return;
    if (filter.dataset.filter === "model") state.model = filter.dataset.value;
    if (filter.dataset.filter === "category") state.category = filter.dataset.value;
    if (filter.dataset.filter === "model" && state.model !== ALL_MODELS) {
      els.modelSelect.value = state.model;
    }
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

  els.languageToggle.addEventListener("click", () => {
    setLanguage(state.language === "en" ? "zh" : "en");
  });

  els.themeToggle.addEventListener("click", () => {
    setTheme(state.theme === "dark" ? "light" : "dark");
  });

  els.backgroundSelect.addEventListener("change", (event) => {
    setBackground(event.target.value);
  });

  document.querySelectorAll(".nav-links a").forEach((link) => {
    link.addEventListener("click", () => document.body.classList.remove("menu-open"));
  });

  els.backToTopButton.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  window.addEventListener("scroll", updateBackToTopVisibility, { passive: true });
  updateBackToTopVisibility();
}

async function init() {
  const params = new URLSearchParams(window.location.search);
  state.query = params.get("q") || "";
  state.language = params.get("lang") === "zh" ? "zh" : (localStorage.getItem("ipg-language") || "en");
  state.theme = localStorage.getItem("ipg-theme") || "light";
  state.background = localStorage.getItem("ipg-background") || "green";
  els.search.value = state.query;

  const response = await fetch("data/prompts.json");
  const data = await response.json();
  state.prompts = [...(data.prompts || []), ...builtInPrompts].map((item, index) => ({ ...item, _index: index }));
  state.filtered = state.prompts;
  state.model = els.modelSelect.value || ALL_MODELS;

  renderStaticCopy();
  applyFilters();
  attachEvents();
}

init().catch((error) => {
  console.error(error);
  els.emptyState.hidden = false;
  els.emptyState.textContent = t("loadError");
});
