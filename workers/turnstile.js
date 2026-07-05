const SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";

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
    headers.set("access-control-allow-headers", "Content-Type");
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

  return json({ success: true, hostname: outcome.hostname || "" }, { status: 200 }, origin);
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
          "access-control-allow-headers": "Content-Type",
          "access-control-max-age": "86400",
          "vary": "Origin",
        } : {},
      });
    }

    if (url.pathname === "/api/verify-turnstile" && request.method === "POST") {
      return verifyTurnstile(request, env);
    }

    return json({ success: false, error: "not_found" }, { status: 404 }, origin);
  },
};
