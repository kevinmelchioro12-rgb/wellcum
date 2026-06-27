"""Console operatore web (solo libreria standard: http.server).

Esegue la pipeline sullo scenario dimostrativo e pubblica una dashboard con:
- riepilogo (fotogrammi, veicoli, conformi, violazioni),
- tabella degli esiti per veicolo,
- elenco dei verbali emessi con dettaglio del testo.

Avvio:  python -m velocitai serve --port 8080
E' una vetrina dimostrativa: in produzione la UI e' un'app autenticata con
ruoli, audit-log e integrazione con il gestionale del Comando.
"""

from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional
from urllib.parse import urlparse, parse_qs

from .config import Config, load_config
from .pipeline import build_simulated_pipeline, PipelineResult
from .scenario import default_scenario
from .notifier import render_verbale_text
from .security import load_secret, constant_time_equals, RateLimiter
from .utils import format_timestamp, get_logger

log = get_logger(__name__)

# Header di sicurezza applicati a ogni risposta (difesa contro XSS/clickjacking/
# sniffing; i dati contengono PII -> niente cache).
_SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store, max-age=0",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}
_LOCAL = {"127.0.0.1", "::1", "localhost"}

_CSS = """
:root{--bg:#0b1020;--card:#141b30;--ink:#e7ecf5;--muted:#8a97b1;
--ok:#1db954;--bad:#ff4d57;--accent:#3a86ff;--warn:#ffb020}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;
background:var(--bg);color:var(--ink)}
header{padding:20px 28px;background:linear-gradient(90deg,#101a36,#0b1020);
border-bottom:1px solid #22304f;display:flex;align-items:center;gap:14px}
.logo{font-weight:800;font-size:22px;letter-spacing:.5px}
.logo span{color:var(--accent)}
.tag{color:var(--muted);font-size:13px}
.wrap{max-width:1080px;margin:0 auto;padding:24px}
.cards{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:24px}
.card{background:var(--card);border:1px solid #22304f;border-radius:14px;padding:16px}
.card .n{font-size:30px;font-weight:800}.card .l{color:var(--muted);font-size:12px;text-transform:uppercase}
table{width:100%;border-collapse:collapse;background:var(--card);border-radius:14px;overflow:hidden}
th,td{padding:12px 14px;text-align:left;border-bottom:1px solid #22304f;font-size:14px}
th{color:var(--muted);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.4px}
.badge{padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700}
.b-ok{background:rgba(29,185,84,.15);color:var(--ok)}
.b-bad{background:rgba(255,77,87,.15);color:var(--bad)}
.b-warn{background:rgba(255,176,32,.15);color:var(--warn)}
h2{margin:28px 0 12px;font-size:16px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
pre{background:var(--card);border:1px solid #22304f;border-radius:14px;padding:20px;
overflow:auto;font-size:13px;line-height:1.5}
.note{color:var(--muted);font-size:12px;margin-top:18px;border-top:1px solid #22304f;padding-top:14px}
"""


class _State:
    config: Config
    result: PipelineResult


def _render_dashboard(state: _State) -> str:
    r = state.result
    s = r.stats
    cfg = state.config
    cards = [
        ("Fotogrammi", s["frames"]), ("Veicoli", s["tracks"]),
        ("Conformi", s["compliant"]), ("Violazioni", s["violations"]),
        ("Da verificare", s["needs_review"]),
    ]
    card_html = "".join(
        f'<div class="card"><div class="n">{v}</div><div class="l">{html.escape(l)}</div></div>'
        for l, v in cards)

    rows = ""
    for o in sorted(r.outcomes, key=lambda x: x.track_id):
        if o.is_violation:
            badge = '<span class="badge b-warn">DA VERIFICARE</span>' if o.needs_review \
                else '<span class="badge b-bad">VIOLAZIONE</span>'
        else:
            badge = '<span class="badge b-ok">CONFORME</span>'
        rows += (f"<tr><td>{o.track_id}</td><td>{html.escape(o.plate or '-')}</td>"
                 f"<td>{o.measured_kmh:.1f} km/h</td><td>{o.contested_kmh:.1f} km/h</td>"
                 f"<td>{o.limit_kmh:.0f} km/h</td><td>{badge}</td></tr>")

    def _status_cls(status: str) -> str:
        if "DISPATCH" in status or status == "NOTIFIED":
            return "b-ok"
        if "DEAD_LETTER" in status or "FAIL" in status:
            return "b-bad"
        return "b-warn"

    verbali = ""
    for d in r.dispatches:
        cls = _status_cls(d["status"])
        verbali += (f'<tr><td><a href="/verbale?id={html.escape(d["protocol_number"])}">'
                    f'{html.escape(d["protocol_number"])}</a></td>'
                    f'<td>{html.escape(d.get("recipient") or "-")}</td>'
                    f'<td><span class="badge {cls}">{html.escape(d["status"])}</span></td></tr>')

    # Indicatore di resilienza/salute del sistema.
    health = r.health or {}
    healthy = health.get("healthy", True)
    hcls, htxt = ("b-ok", "OPERATIVO") if healthy else ("b-warn", "DEGRADATO")
    n_err = r.stats.get("errors", 0)
    health_html = (f'<span class="badge {hcls}">{htxt}</span>'
                   f' &middot; guasti isolati: {n_err}'
                   f' &middot; componenti monitorati: {len(health.get("components", {}))}')

    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VelociTAI - Console Operatore</title><style>{_CSS}</style></head><body>
<header><div class="logo">Veloci<span>TAI</span></div>
<div class="tag">Console operatore - {html.escape(cfg.location.road_name)}
 &middot; limite {cfg.location.speed_limit_kmh:.0f} km/h
 &middot; {html.escape(cfg.device.device_id)}</div></header>
<div class="wrap">
<div class="cards">{card_html}</div>
<h2>Esiti rilevamento</h2>
<table><thead><tr><th>Track</th><th>Targa</th><th>Misurata</th>
<th>Contestata</th><th>Limite</th><th>Esito</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Verbali emessi</h2>
<table><thead><tr><th>Protocollo</th><th>Destinatario PEC</th><th>Stato</th></tr></thead>
<tbody>{verbali or '<tr><td colspan=3>Nessun verbale</td></tr>'}</tbody></table>
<h2>Stato sistema (resilienza)</h2>
<div class="note" style="border-top:none;margin-top:0">{health_html}</div>
<div class="note">Demo a scopo dimostrativo. Gli importi e i parametri legali sono
configurabili; l'impiego in esercizio richiede omologazione MIT, taratura periodica
e conformita' GDPR (vedi LEGAL_COMPLIANCE.md). Endpoint dati: <a href="/api/violations">/api/violations</a>.</div>
</div></body></html>"""


def _render_verbale_page(state: _State, protocol: str) -> Optional[str]:
    for verbale in state.result.verbali:
        if verbale.protocol_number == protocol:
            text = render_verbale_text(verbale, state.config)
            return (f'<!doctype html><html lang="it"><head><meta charset="utf-8">'
                    f'<style>{_CSS}</style><title>{html.escape(protocol)}</title></head>'
                    f'<body><div class="wrap"><a href="/">&larr; Torna alla console</a>'
                    f'<pre>{html.escape(text)}</pre></div></body></html>')
    return None


class _Handler(BaseHTTPRequestHandler):
    state: _State = None        # iniettato in serve()
    token: bytes = None         # token bearer richiesto (None = nessun token)
    rate_limiter: RateLimiter = None
    require_localhost: bool = True
    protocol_version = "HTTP/1.1"

    def _send(self, code: int, body: str, ctype: str = "text/html; charset=utf-8",
              extra_headers: dict = None):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        for k, v in _SECURITY_HEADERS.items():
            self.send_header(k, v)
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _client_ip(self) -> str:
        return self.client_address[0] if self.client_address else "?"

    def _authorized(self) -> bool:
        """Controllo d'accesso: token bearer se configurato, altrimenti solo
        localhost (per non esporre PII a client remoti non autenticati)."""
        if self.token:
            hdr = self.headers.get("Authorization", "")
            if not hdr.startswith("Bearer "):
                return False
            return constant_time_equals(hdr[7:].strip(), self.token.decode("utf-8"))
        if self.require_localhost and self._client_ip() not in _LOCAL:
            return False
        return True

    def _guarded(self) -> bool:
        """Rate-limit + auth comuni a ogni richiesta. True se si puo' procedere."""
        if self.rate_limiter is not None and not self.rate_limiter.allow(self._client_ip()):
            self._send(429, "<h1>429</h1> Troppe richieste")
            return False
        if not self._authorized():
            self._send(401, "<h1>401</h1> Accesso non autorizzato",
                       extra_headers={"WWW-Authenticate": "Bearer"})
            log.warning("Accesso negato da %s a %s", self._client_ip(), self.path)
            return False
        return True

    def do_GET(self):  # noqa: N802
        # Anti-DoS: rifiuta URL abnormi prima di qualunque elaborazione.
        if len(self.path) > 2048:
            self._send(414, "<h1>414</h1> URI troppo lungo")
            return
        if not self._guarded():
            return
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send(200, _render_dashboard(self.state))
        elif parsed.path == "/api/violations":
            payload = {
                "stats": self.state.result.stats,
                "violations": [
                    {
                        "violation_id": v.violation_id,
                        "plate": v.plate.text,
                        "measured_kmh": v.measured_speed_kmh,
                        "contested_kmh": v.contested_speed_kmh,
                        "limit_kmh": v.speed_limit_kmh,
                        "overspeed_kmh": round(v.overspeed_kmh, 1),
                        "timestamp": format_timestamp(v.timestamp, self.state.config.tz_offset_hours),
                    }
                    for v in self.state.result.violations
                ],
            }
            self._send(200, json.dumps(payload, ensure_ascii=False, indent=2),
                       "application/json; charset=utf-8")
        elif parsed.path == "/verbale":
            qs = parse_qs(parsed.query)
            pid = (qs.get("id") or [""])[0]
            page = _render_verbale_page(self.state, pid)
            if page:
                self._send(200, page)
            else:
                self._send(404, "<h1>404</h1> Verbale non trovato")
        else:
            self._send(404, "<h1>404</h1>")

    def _reject_method(self):
        self._send(405, "<h1>405</h1> Metodo non consentito",
                   extra_headers={"Allow": "GET"})

    # Solo GET e' consentito: ogni altro metodo viene rifiutato (riduce la
    # superficie d'attacco; nessuna mutazione di stato via HTTP).
    do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_HEAD = _reject_method

    def log_message(self, fmt, *args):  # silenzia il log di default
        pass


def serve(config: Config, port: int = 8080, host: str = "127.0.0.1") -> None:
    pipeline = build_simulated_pipeline(config)
    result = pipeline.process_frames(default_scenario().frames())

    state = _State()
    state.config = config
    state.result = result
    _Handler.state = state

    # Sicurezza: token bearer (se configurato via env), rate-limit, e — in sua
    # assenza — accesso ristretto a localhost per non esporre PII.
    token = load_secret(config.security.dashboard_token_env)
    _Handler.token = token
    _Handler.rate_limiter = RateLimiter(rate_per_s=20.0, burst=40)
    _Handler.require_localhost = config.security.require_localhost_without_token

    if not token and host not in _LOCAL:
        log.warning("ATTENZIONE: binding su %s senza token (%s non impostato). "
                    "I client remoti saranno RIFIUTATi: imposta il token o usa "
                    "host=127.0.0.1.", host, config.security.dashboard_token_env)

    httpd = ThreadingHTTPServer((host, port), _Handler)
    auth = "token bearer" if token else "solo-localhost"
    log.info("Console VelociTAI su http://%s:%d  (%s violazioni, accesso: %s)",
             host, port, result.stats["violations"], auth)
    print(f"\n  VelociTAI console -> http://{host}:{port}\n  accesso: {auth}\n"
          f"  (Ctrl+C per uscire)\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info("Arresto console.")
        httpd.shutdown()
