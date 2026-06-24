"""Interfaccia a riga di comando di VelociTAI.

Esempi:
    python -m velocitai demo
    python -m velocitai demo --config config/default.yaml --show-verbale 1
    python -m velocitai demo --anpr-errors 0.05
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .config import load_config, Config
from .pipeline import build_simulated_pipeline, PipelineResult
from .scenario import default_scenario
from .notifier import render_verbale_text
from .utils import format_timestamp


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


def cmd_demo(args: argparse.Namespace) -> int:
    config = load_config(args.config) if args.config else Config()
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
