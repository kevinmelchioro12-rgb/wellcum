"""VelociTAI — sistema di accertamento automatico dei limiti di velocita'.

Pipeline: rilevamento veicoli -> tracciamento -> stima velocita' -> ANPR
(riconoscimento targa) -> registrazione prova -> calcolo sanzione (Art. 142 CdS)
-> generazione e notifica del verbale.

Tutto il core gira a dipendenza-zero (solo libreria standard); i backend di
produzione (YOLOv8, EasyOCR, OpenCV, PEC) sono pluggable.
"""

from .config import Config, load_config
from .pipeline import (
    EnforcementPipeline, PipelineResult, build_simulated_pipeline,
)
from .scenario import Scenario, default_scenario
from .notifier import render_verbale_text
from .fines import SanctionCalculator, apply_tolerance, classify

__version__ = "1.0.0"

__all__ = [
    "Config", "load_config",
    "EnforcementPipeline", "PipelineResult", "build_simulated_pipeline",
    "Scenario", "default_scenario",
    "render_verbale_text",
    "SanctionCalculator", "apply_tolerance", "classify",
    "__version__",
]
