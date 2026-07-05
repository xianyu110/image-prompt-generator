const SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";
const DEFAULT_UPSTREAM_API_BASE_URL = "https://apipro.maynor1024.live";
const DEFAULT_PROMPT_TEXT_MODEL = "gpt-4o";
const ACCESS_TOKEN_TTL_SECONDS = 2 * 60 * 60;

const DEFAULT_ALLOWED_ORIGINS = [
  "https://image-prompt-generator.com",
  "https://www.image-prompt-generator.com",
  "https://xianyu110.github.io",
  "http://127.0.0.1:8765",
  "http://localhost:8765",
];

function json(data, init = {}, origin = "") {
  const headers = new Headers(init.headers || {});
  headers.set("content-type", "application/json; charset=utf-8");
  headers.set("vary", "Origin");
  if (origin) {
    headers.set("access-control-allow-origin", origin);
    headers.set("access-control-allow-methods", "POST, OPTIONS");
    headers.set("access-control-allow-headers", "Content-Type, Authorization");
  }
  return new Response(JSON.stringify(data), { ...init, headers });
}

function allowedOrigins(env) {
  const configured = String(env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean);
  return configured.length ? configured : DEFAULT_ALLOWED_ORIGINS;
}

function corsOrigin(request, env) {
  const origin = request.headers.get("origin") || "";
  return allowedOrigins(env).includes(origin) ? origin : "";
}

async function readJson(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

function base64url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

function base64urlToBytes(value) {
  const padded = value.replaceAll("-", "+").replaceAll("_", "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  const binary = atob(padded);
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function hmac(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
  return crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
}

async function createAccessToken(env, hostname) {
  const now = Math.floor(Date.now() / 1000);
  const payload = base64url(new TextEncoder().encode(JSON.stringify({
    iat: now,
    exp: now + ACCESS_TOKEN_TTL_SECONDS,
    hostname,
  })));
  const signature = base64url(new Uint8Array(await hmac(accessTokenSecret(env), payload)));
  return `${payload}.${signature}`;
}

function accessTokenSecrets(env) {
  return [
    env.PROMPT_ACCESS_TOKEN_SECRET,
    env.TURNSTILE_SECRET_KEY,
  ].filter(Boolean);
}

function accessTokenSecret(env) {
  return accessTokenSecrets(env)[0] || "";
}

async function verifyAccessToken(env, token) {
  if (!accessTokenSecret(env) || !token || !token.includes(".")) return false;
  const parts = token.split(".");
  if (parts.length !== 2) return false;
  const [payload, signature] = parts;
  if (!payload || !signature) return false;

  let a;
  try {
    a = base64urlToBytes(signature);
  } catch {
    return false;
  }

  let validSignature = false;
  for (const secret of accessTokenSecrets(env)) {
    const expected = base64url(new Uint8Array(await hmac(secret, payload)));
    const b = base64urlToBytes(expected);
    if (a.length !== b.length) continue;

    let diff = 0;
    for (let index = 0; index < a.length; index += 1) diff |= a[index] ^ b[index];
    if (diff === 0) validSignature = true;
  }
  if (!validSignature) return false;

  try {
    const parsed = JSON.parse(new TextDecoder().decode(base64urlToBytes(payload)));
    return Number(parsed.exp || 0) > Math.floor(Date.now() / 1000);
  } catch {
    return false;
  }
}

function cleanString(value, limit) {
  return String(value || "").trim().replace(/\s+/g, " ").slice(0, limit);
}

function promptSystem(language) {
  if (language === "zh") {
    return [
      "你是 Image Prompt Generator 的专业 AI 图像提示词编辑。",
      "根据用户主题、目标模型和比例，生成一个可直接复制到图像生成工具里的完整提示词。",
      "只输出最终提示词，不要解释，不要 Markdown，不要标题。",
      "提示词要具体、可执行，包含主体、场景、构图、镜头、光影、材质、风格、文字规则和质量约束。",
    ].join("\n");
  }
  return [
    "You are the expert prompt editor behind Image Prompt Generator.",
    "Given the user's subject, target image model, and aspect ratio, produce one polished prompt ready to paste into an AI image generator.",
    "Output only the final prompt. Do not include explanations, Markdown, or a heading.",
    "Make it specific and actionable: subject, scene, composition, lens/camera language, lighting, materials, style, text rules, and quality constraints.",
  ].join("\n");
}

function modelStrategy(model, language) {
  const zh = {
    "Seedream 5 Pro": "强调可控编辑、中文文字可读性、多轮改图、局部修改和商业设计落地。",
    "Nano Banana Pro": "强调创意发散、复杂画面、多图融合、风格化视觉和强烈视觉记忆点。",
    "GPT Image 2": "强调真实世界知识、文字渲染、精确构图、细节一致性和高质量成片。",
    "GPT Image 1.5": "强调稳定照片质感、自然光影、清晰主体和较少复杂文字的安全构图。",
    "Seedance 2.0": "按静帧图像和视频分镜两种方式组织；强调主体一致、动作瞬间、镜头语言、运动方向和动态构图。",
    "Grok Imagine": "强调热点语境、社交传播感、强反差创意和可快速理解的画面钩子。",
    "Gemini 3 Pro": "强调复杂指令理解、多模态推理、信息结构和长上下文一致性。",
  };
  const en = {
    "Seedream 5 Pro": "Prioritize controllable edits, readable text, iterative image changes, local refinements, and commercial design output.",
    "Nano Banana Pro": "Prioritize creative exploration, complex scenes, multi-image fusion, stylized visuals, and memorable compositions.",
    "GPT Image 2": "Prioritize real-world knowledge, accurate text rendering, precise composition, detail consistency, and polished final imagery.",
    "GPT Image 1.5": "Prioritize stable photographic realism, natural lighting, clear subjects, and safe compositions with minimal complex text.",
    "Seedance 2.0": "Structure the result as an image keyframe prompt with optional video storyboard language: subject consistency, action beats, camera language, motion direction, and dynamic composition.",
    "Grok Imagine": "Prioritize trend-aware concepts, social shareability, strong visual contrast, and a clear one-second visual hook.",
    "Gemini 3 Pro": "Prioritize complex instruction following, multimodal reasoning, information structure, and long-context consistency.",
  };
  return (language === "zh" ? zh : en)[model] || (language === "zh" ? "根据模型能力生成高质量视觉结果。" : "Create a high-quality visual result based on the model's strengths.");
}

function buildPromptUserMessage({ subject, model, ratio, language }) {
  if (language === "zh") {
    return [
      `主题：${subject}`,
      `目标模型：${model}`,
      `比例：${ratio}`,
      `模型策略：${modelStrategy(model, language)}`,
      "生成一个完整、自然、可直接复制的图像提示词。不要包含说明文字。",
    ].join("\n");
  }
  return [
    `Subject: ${subject}`,
    `Target model: ${model}`,
    `Aspect ratio: ${ratio}`,
    `Model strategy: ${modelStrategy(model, language)}`,
    "Generate one complete, natural, copy-ready image prompt. Do not include explanatory text.",
  ].join("\n");
}

function extractChatContent(result) {
  return result?.choices?.[0]?.message?.content?.trim()
    || result?.choices?.[0]?.text?.trim()
    || "";
}

async function verifyTurnstile(request, env) {
  const origin = corsOrigin(request, env);
  if (!origin) {
    return json({ success: false, error: "origin_not_allowed" }, { status: 403 });
  }
  if (!env.TURNSTILE_SECRET_KEY) {
    return json({ success: false, error: "turnstile_secret_missing" }, { status: 500 }, origin);
  }

  const body = await readJson(request);
  const token = typeof body?.token === "string" ? body.token.trim() : "";
  if (!token) {
    return json({ success: false, error: "token_required" }, { status: 400 }, origin);
  }

  const remoteip = request.headers.get("CF-Connecting-IP") || undefined;
  const payload = {
    secret: env.TURNSTILE_SECRET_KEY,
    response: token,
    remoteip,
    idempotency_key: crypto.randomUUID(),
  };

  const response = await fetch(SITEVERIFY_URL, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
  const outcome = await response.json().catch(() => ({ success: false, "error-codes": ["bad-response"] }));

  if (!response.ok || !outcome.success) {
    return json({
      success: false,
      error: "turnstile_failed",
      codes: outcome["error-codes"] || [],
    }, { status: 400 }, origin);
  }

  const accessToken = await createAccessToken(env, outcome.hostname || "");
  return json({ success: true, hostname: outcome.hostname || "", accessToken }, { status: 200 }, origin);
}

async function generatePrompt(request, env) {
  const origin = corsOrigin(request, env);
  if (!origin) {
    return json({ success: false, error: "origin_not_allowed" }, { status: 403 });
  }

  const body = await readJson(request);
  const accessToken = typeof body?.accessToken === "string" ? body.accessToken.trim() : "";
  if (!(await verifyAccessToken(env, accessToken))) {
    return json({ success: false, error: "human_check_required" }, { status: 401 }, origin);
  }
  if (!env.MAYNOR_API_KEY) {
    return json({ success: false, error: "prompt_api_key_missing" }, { status: 500 }, origin);
  }

  const subject = cleanString(body?.subject, 3000);
  const model = cleanString(body?.model, 80) || "GPT Image 2";
  const ratio = cleanString(body?.ratio, 20) || "1:1";
  const language = body?.language === "zh" ? "zh" : "en";
  if (!subject) {
    return json({ success: false, error: "subject_required" }, { status: 400 }, origin);
  }

  const baseUrl = String(env.UPSTREAM_API_BASE_URL || DEFAULT_UPSTREAM_API_BASE_URL).replace(/\/+$/, "");
  const textModel = String(env.PROMPT_TEXT_MODEL || DEFAULT_PROMPT_TEXT_MODEL);
  const response = await fetch(`${baseUrl}/v1/chat/completions`, {
    method: "POST",
    headers: {
      "accept": "application/json",
      "authorization": `Bearer ${env.MAYNOR_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: textModel,
      messages: [
        { role: "system", content: promptSystem(language) },
        { role: "user", content: buildPromptUserMessage({ subject, model, ratio, language }) },
      ],
      max_tokens: 900,
      temperature: 0.75,
      stream: false,
    }),
  });
  const result = await response.json().catch(() => ({}));
  const prompt = extractChatContent(result);

  if (!response.ok || !prompt) {
    return json({
      success: false,
      error: "upstream_generation_failed",
      status: response.status,
      detail: result?.error?.message || result?.message || "",
    }, { status: 502 }, origin);
  }

  return json({ success: true, prompt, model: textModel }, { status: 200 }, origin);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = corsOrigin(request, env);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: origin ? 204 : 403,
        headers: origin ? {
          "access-control-allow-origin": origin,
          "access-control-allow-methods": "POST, OPTIONS",
          "access-control-allow-headers": "Content-Type, Authorization",
          "access-control-max-age": "86400",
          "vary": "Origin",
        } : {},
      });
    }

    if (url.pathname === "/api/verify-turnstile" && request.method === "POST") {
      return verifyTurnstile(request, env);
    }
    if (url.pathname === "/api/generate-prompt" && request.method === "POST") {
      return generatePrompt(request, env);
    }

    return json({ success: false, error: "not_found" }, { status: 404 }, origin);
  },
};
