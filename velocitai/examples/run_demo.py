"""Esempio d'uso programmatico della pipeline VelociTAI.

    python3 examples/run_demo.py

Mostra come costruire la pipeline, elaborare uno scenario e stampare il primo
verbale generato. In produzione si sostituisce ``default_scenario().frames()``
con un flusso di fotogrammi reali e i backend simulati con quelli ML.
"""

import os
import sys

# Rende l'esempio eseguibile standalone (``python3 examples/run_demo.py``) senza
# dover impostare PYTHONPATH: aggiunge la radice del progetto al path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from velocitai import (  # noqa: E402
    Config, build_simulated_pipeline, default_scenario, render_verbale_text,
)


def main() -> None:
    config = Config()
    pipeline = build_simulated_pipeline(config)

    result = pipeline.process_frames(default_scenario().frames())

    print(f"Violazioni accertate: {result.stats['violations']} "
          f"su {result.stats['tracks']} veicoli\n")
    for v in result.violations:
        print(f"  - {v.plate.text}: misurata {v.measured_speed_kmh:.0f} km/h, "
              f"contestata {v.contested_speed_kmh:.0f} km/h "
              f"(+{v.overspeed_kmh:.0f} sul limite di {v.speed_limit_kmh:.0f})")

    if result.verbali:
        print("\n--- Primo verbale ---\n")
        print(render_verbale_text(result.verbali[0], config))


if __name__ == "__main__":
    main()
