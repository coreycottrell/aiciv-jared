/**
 * Skills Hub Proxy Worker
 * skills.purebrain.ai/*  ->  http://hub-origin.purebrain.ai:8900/*   (AiCIV Skills Hub, FastAPI)
 * (hub-origin.purebrain.ai is a DNS-only / grey-cloud A record -> 87.99.131.49.
 *  Cloudflare Workers fetch() rejects raw IP literals with error 1003, so the origin
 *  MUST be reached via a hostname.)
 *
 * - HTTPS termination in front of an HTTP-only origin.
 * - Transparent reverse proxy: preserves path, querystring, method, headers, body,
 *   and the origin response status + content-type.
 * - Cosmetic reskin injected ONLY into the /docs Swagger UI page (text/html).
 *   The reskin function `reskinDocsHtml(html)` is authored by ptt-full-stack-developer
 *   (see .claude/memory/agent-learnings/ptt-full-stack-developer/
 *    2026-07-03--swagger-ui-purebrain-reskin-worker-inject.md). Until that verbatim
 *   artifact is dropped in, the call site below is wired but the function is a
 *   PASSTHROUGH stub (returns html unchanged) so the proxy is fully functional and
 *   the reskin becomes a one-function drop-in. See E-DEPS note at bottom.
 * - Defensive: origin unreachable / slow -> clean 502, never hangs (AbortController).
 */

import { reskinDocsHtml } from "./reskin.js";

const ORIGIN = "http://hub-origin.purebrain.ai:8900";
const ORIGIN_HOST = "hub-origin.purebrain.ai:8900";
const ORIGIN_TIMEOUT_MS = 12000;

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const backendUrl = ORIGIN + url.pathname + url.search;

    // Copy client headers, but re-point Host at the origin so the origin sees itself
    // and skills.purebrain.ai is not surfaced to the backend.
    const fwdHeaders = new Headers(request.headers);
    fwdHeaders.set("Host", ORIGIN_HOST);
    // Advisory forwarding headers (do not leak internal hostnames back to clients).
    fwdHeaders.set("X-Forwarded-Proto", "https");
    fwdHeaders.set("X-Forwarded-Host", url.host);

    const hasBody = request.method !== "GET" && request.method !== "HEAD";

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), ORIGIN_TIMEOUT_MS);

    let originResponse;
    try {
      originResponse = await fetch(backendUrl, {
        method: request.method,
        headers: fwdHeaders,
        body: hasBody ? request.body : undefined,
        redirect: "manual",
        signal: controller.signal,
      });
    } catch (err) {
      clearTimeout(timer);
      return new Response(
        JSON.stringify({
          error: "bad_gateway",
          detail: "Skills Hub origin unreachable.",
          message: String(err && err.message ? err.message : err),
        }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      );
    } finally {
      clearTimeout(timer);
    }

    const contentType = originResponse.headers.get("Content-Type") || "";
    const isDocsPage =
      (url.pathname === "/docs" || url.pathname === "/docs/") &&
      contentType.includes("text/html");

    // Fast path: stream everything through untouched (openapi.json, /redoc, swagger
    // static assets, all API routes, non-docs HTML). Preserves status + content-type.
    if (!isDocsPage) {
      const passHeaders = new Headers(originResponse.headers);
      return new Response(originResponse.body, {
        status: originResponse.status,
        statusText: originResponse.statusText,
        headers: passHeaders,
      });
    }

    // Reskin path: buffer the /docs HTML, inject branding, drop content-length so the
    // grown body is not truncated.
    let html = await originResponse.text();
    try {
      html = reskinDocsHtml(html);
    } catch (_e) {
      // Defensive: never let a reskin error break the proxied page.
    }

    const outHeaders = new Headers(originResponse.headers);
    outHeaders.delete("Content-Length"); // body size changed after injection
    outHeaders.set("Content-Type", "text/html; charset=utf-8");

    return new Response(html, {
      status: originResponse.status,
      statusText: originResponse.statusText,
      headers: outHeaders,
    });
  },
};
