// Static server for the Momento Legal full-site clone.
// - Serves ./public at the site root
// - Clean URLs: /about -> about.html, /insights/foo -> insights/foo.html
// - /_next/image?url=...&w=...&q=... passthrough: serves the original asset so
//   the saved Next.js markup renders without the original image optimizer.
// - Unknown paths fall back to 404.html with status 404.
import { createServer } from "node:http";
import { promises as fsp, createReadStream } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(__dirname, "public");

const envPort = Number(process.env.PORT);
const PORT = Number.isFinite(envPort) && envPort > 0 ? envPort : 3000;
const HOST = process.env.HOST || "127.0.0.1";

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".mjs": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".ico": "image/x-icon",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".xml": "application/xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
};

async function tryFile(p) {
  try {
    const st = await fsp.stat(p);
    return st.isFile() ? p : null;
  } catch {
    return null;
  }
}

async function resolveFile(pathname) {
  let p = decodeURIComponent(pathname);
  try {
    p = decodeURI(p);
  } catch {
    /* keep raw */
  }
  // Neutralize traversal attempts.
  const safe = path.normalize(p).replace(/^(\.\.[/\\])+/, "");
  const base = path.join(PUBLIC_DIR, safe);
  if (!base.startsWith(PUBLIC_DIR)) return null;

  if (p.endsWith("/")) {
    return tryFile(path.join(base, "index.html"));
  }

  const direct = await tryFile(base);
  if (direct) return direct;

  // Clean URL -> html file
  if (!path.extname(base)) {
    const asHtml = await tryFile(base + ".html");
    if (asHtml) return asHtml;
    const asIndex = await tryFile(path.join(base, "index.html"));
    if (asIndex) return asIndex;
  }
  return null;
}

function send(res, status, headers, stream) {
  res.writeHead(status, headers);
  stream.pipe(res);
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  let pathname = url.pathname;

  // Next.js image optimizer shim: serve the original asset for every variant.
  if (pathname === "/_next/image") {
    const src = url.searchParams.get("url") || "";
    if (src.startsWith("/") && !src.includes("..")) {        const file = await resolveFile(src);
        if (file) {
          const ext = path.extname(file).toLowerCase();
          return send(res, 200, {
            "Content-Type": MIME[ext] || "application/octet-stream",
            "Cache-Control": "no-cache",
          }, createReadStream(file));
      }
    }
    res.writeHead(400, { "Content-Type": "text/plain" });
    return res.end("Bad image request");
  }

  if (pathname !== "/" && pathname.endsWith("/")) {
    pathname = pathname.slice(0, -1);
  }

  // Cookie-consent sync endpoint (live site had a route handler) — acknowledge and stop.
  if (pathname === "/api/cookie-consent" && req.method === "POST") {
    res.writeHead(204, { "Cache-Control": "no-store" });
    return res.end();
  }

  // React Router prefetches (?_rsc=...) expect an RSC stream, which a static clone
  // can't produce. Serve the page's HTML with a permissive content type so the
  // router's refetch succeeds; React then performs a full-page render from markup.
  if (url.searchParams.has("_rsc")) {
    const file = await resolveFile(pathname);
    if (file) {
      return send(res, 200, {
        "Content-Type": "text/x-component; charset=utf-8",
        "Cache-Control": "no-store",
      }, createReadStream(file));
    }
  }

  // Legacy URLs that redirect (old live-site paths + removed Turkish mirror).
  if (pathname === "/cookie-policy") {
    res.writeHead(308, { Location: "/policies/cookie-policy" });
    return res.end();
  }
  if (pathname === "/tr" || pathname.startsWith("/tr/")) {
    // Turkish mirror removed with the Momento rebrand -> route to English home.
    res.writeHead(308, { Location: "/" });
    return res.end();
  }

  const file = await resolveFile(pathname);
  if (file) {
    const ext = path.extname(file).toLowerCase();
    const isHtml = ext === ".html";
    return send(res, 200, {
      "Content-Type": MIME[ext] || "application/octet-stream",
      "Cache-Control": isHtml ? "no-cache" : "no-cache",
    }, createReadStream(file));
  }

  // Fallback: custom 404 page
  const notFound = await tryFile(path.join(PUBLIC_DIR, "404.html"));
  if (notFound) {
    return send(res, 404, { "Content-Type": MIME[".html"] }, createReadStream(notFound));
  }
  res.writeHead(404, { "Content-Type": "text/plain" });
  res.end("Not found");
});

server.listen(PORT, HOST, () => {
  console.log(`Momento Legal clone running at http://${HOST}:${PORT}`);
});
