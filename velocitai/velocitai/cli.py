"""Interfaccia a riga di comando di VelociTAI.

Esempi:
    python -m velocitai demo
    python -m velocitai demo --config config/default.yaml --show-verbale 1
    python -m velocitai demo --anpr-errors 0.05
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from typing import List, Optional

from . import __version__
from .config import load_config, validate_config, Config, ConfigError
from .pipeline import build_simulated_pipeline, PipelineResult
from .scenario import default_scenario
from .notifier import render_verbale_text
from .resilience import DeadLetterQueue
from .utils import format_timestamp, sha256_of_files


def _data_root(config: Config) -> str:
    return os.path.dirname(config.recorder.output_dir) or "data"


def _print_summary(result: PipelineResult, config: Config) -> None:
    s = result.stats
    print("\n=== RIEPILOGO ACCERTAMENTO ===")
    print(f"Fotogrammi elaborati : {s['frames']}")
    print(f"Veicoli tracciati    : {s['tracks']}")
    print(f"Conformi             : {s['compliant']}")
    print(f"Violazioni           : {s['violations']}")
    print(f"Da verificare (ANPR) : {s['needs_review']}")
    print(f"Limite postazione    : {config.location.speed_limit_kmh:.0f} km/h "
          f"@ {config.location.road_name}\n")

    if result.outcomes:
        print(f"{'Track':>5}  {'Targa':<9}  {'Misurata':>9}  {'Contestata':>10}  Esito")
        print("-" * 56)
        for o in sorted(result.outcomes, key=lambda x: x.track_id):
            esito = "VIOLAZIONE" if o.is_violation else "conforme"
            if o.needs_review:
                esito += " (rev.)"
            print(f"{o.track_id:>5}  {(o.plate or '-'):<9}  "
                  f"{o.measured_kmh:>7.1f}  {o.contested_kmh:>9.1f}  {esito}")

    if result.dispatches:
        print("\n=== VERBALI EMESSI ===")
        for d in result.dispatches:
            print(f"  {d['protocol_number']}  [{d['status']}]  -> {d['txt_path']}")

    # Riepilogo resilienza: salute dei componenti e guasti isolati.
    health = result.health or {}
    if health:
        state = "OK" if health.get("healthy", True) else "DEGRADATO"
        print(f"\n=== RESILIENZA === stato: {state}")
        for name, h in health.get("components", {}).items():
            flag = "ok" if h["healthy"] else "!!"
            print(f"  [{flag}] {name:<16} successi={h['successes']} "
                  f"fallimenti={h['failures']} (consecutivi={h['consecutive_failures']})")
    if result.stats.get("errors") or result.stats.get("skipped_duplicate"):
        print(f"  Guasti isolati per-traccia : {result.stats.get('errors', 0)}")
        print(f"  Saltati (gia' verbalizzati): {result.stats.get('skipped_duplicate', 0)}")


def cmd_demo(args: argparse.Namespace) -> int:
    config = load_config(args.config) if args.config else Config()
    # Demo ripetibile: si azzera lo stato persistente (ledger idempotente e coda
    # dead-letter) cosi' ogni esecuzione riparte pulita. In esercizio reale
    # questo stato e' invece durevole e protegge dalla doppia sanzione.
    root = _data_root(config)
    for p in (os.path.join(root, "issued_ledger.json"), os.path.join(root, "deadletter")):
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        elif os.path.exists(p):
            os.remove(p)

    pipeline = build_simulated_pipeline(
        config,
        anpr_error_rate=args.anpr_errors,
        detection_prob=args.detection_prob,
        bbox_jitter=args.bbox_jitter,
    )
    scenario = default_scenario()
    # allinea il limite/metodo dello scenario alla config
    result = pipeline.process_frames(scenario.frames())
    _print_summary(result, config)

    if args.show_verbale is not None:
        idx = args.show_verbale - 1
        if 0 <= idx < len(result.verbali):
            print("\n" + render_verbale_text(result.verbali[idx], config))
        else:
            print(f"\n[!] Nessun verbale n.{args.show_verbale} "
                  f"(emessi: {len(result.verbali)}).")
    return 0


def _audit_evidence(root: str) -> dict:
    """Ricalcola gli hash di tutti i pacchetti-prova e ne verifica l'integrita'."""
    checked = ok = tampered = 0
    problems: List[str] = []
    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            folder = os.path.join(root, name)
            sha_file = os.path.join(folder, "evidence.sha256")
            clip = os.path.join(folder, "clip_manifest.json")
            if not (os.path.isdir(folder) and os.path.exists(sha_file)
                    and os.path.exists(clip)):
                continue
            checked += 1
            try:
                with open(sha_file, encoding="utf-8") as fh:
                    stored = fh.readline().split()[0]
            except (OSError, IndexError):
                tampered += 1
                problems.append(f"{name}: file hash illeggibile")
                continue
            files = [clip]
            plate = os.path.join(folder, "plate.txt")
            if os.path.exists(plate):
                files.append(plate)
            if sha256_of_files(files) == stored:
                ok += 1
            else:
                tampered += 1
                problems.append(f"{name}: hash NON corrispondente (prova alterata/corrotta)")
    return {"checked": checked, "ok": ok, "tampered": tampered, "problems": problems}


def cmd_doctor(args: argparse.Namespace) -> int:
    """Auto-diagnosi: valida la config, verifica le prove, ispeziona la coda
    dead-letter e — con ``--repair`` — ne tenta la ripresa automatica."""
    try:
        config = load_config(args.config, strict=False) if args.config else Config()
    except ConfigError as exc:
        print(f"[X] Configurazione: {exc}")
        return 2

    rc = 0
    print("=== DIAGNOSI VELOCITAI ===")

    errors = validate_config(config)
    if errors:
        rc = 1
        print(f"[X] Configurazione NON valida ({len(errors)} problemi):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("[ok] Configurazione valida.")

    audit = _audit_evidence(config.recorder.output_dir)
    if audit["checked"] == 0:
        print("[--] Nessun pacchetto-prova da verificare.")
    elif audit["tampered"] == 0:
        print(f"[ok] Prove integre: {audit['ok']}/{audit['checked']} verificate.")
    else:
        rc = 1
        print(f"[X] Prove compromesse: {audit['tampered']}/{audit['checked']}")
        for p in audit["problems"]:
            print(f"    - {p}")

    dlq = DeadLetterQueue(os.path.join(_data_root(config), "deadletter"))
    pending = dlq.pending()
    print(f"[{'!!' if pending else 'ok'}] Coda dead-letter: {len(pending)} elementi in attesa.")
    for rec in pending:
        print(f"    - {rec.get('kind')}/{rec.get('key')} "
              f"(tentativi={rec.get('attempts')}, errore={rec.get('error','')[:60]})")

    if args.repair and pending:
        print("\n[*] Ripresa automatica della coda dead-letter...")

        def _handler(rec: dict) -> None:
            # ripresa per le notifiche in modalita' simulata: i file del verbale
            # sono gia' su disco, la 'notifica' si considera completata.
            if rec.get("kind") == "notification" and config.notifier.mode == "simulated":
                return
            raise RuntimeError("ripresa non automatizzabile per questo elemento")

        res = dlq.retry_pending(_handler)
        print(f"    risolti={res['resolved']} ancora_in_errore={res['failed']}")
        if res["failed"]:
            rc = 1

    print(f"\nEsito: {'OK' if rc == 0 else 'ATTENZIONE'}")
    return rc


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="velocitai",
        description="Sistema di accertamento automatico dei limiti di velocita'.",
    )
    p.add_argument("--version", action="version",
                   version=f"VelociTAI {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo", help="Esegue lo scenario dimostrativo end-to-end.")
    d.add_argument("--config", help="Percorso del file YAML di configurazione.")
    d.add_argument("--show-verbale", type=int, default=None,
                   help="Stampa il testo del verbale n. (1-based).")
    d.add_argument("--anpr-errors", type=float, default=0.0,
                   help="Tasso d'errore OCR simulato per carattere (0..1).")
    d.add_argument("--detection-prob", type=float, default=1.0,
                   help="Probabilita' di rilevamento per fotogramma (0..1).")
    d.add_argument("--bbox-jitter", type=float, default=0.0,
                   help="Rumore additivo sulle bounding box (metri).")
    d.set_defaults(func=cmd_demo)

    sv = sub.add_parser("serve", help="Avvia la console operatore web (dashboard).")
    sv.add_argument("--config", help="Percorso del file YAML di configurazione.")
    sv.add_argument("--port", type=int, default=8080)
    sv.add_argument("--host", default="127.0.0.1")
    sv.set_defaults(func=cmd_serve)

    dr = sub.add_parser("doctor",
                        help="Auto-diagnosi: config, integrita' prove, dead-letter.")
    dr.add_argument("--config", help="Percorso del file YAML di configurazione.")
    dr.add_argument("--repair", action="store_true",
                    help="Tenta la ripresa automatica della coda dead-letter.")
    dr.set_defaults(func=cmd_doctor)
    return p


def cmd_serve(args: argparse.Namespace) -> int:
    from .dashboard import serve
    config = load_config(args.config) if args.config else Config()
    serve(config, port=args.port, host=args.host)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
