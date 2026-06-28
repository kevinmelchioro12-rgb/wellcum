.PHONY: help install demo serve doctor quote video onepager test clean

help:
	@echo "VelociTAI - comandi disponibili:"
	@echo "  make install   - installa il pacchetto in modalita' editable (pip)"
	@echo "  make demo      - scenario dimostrativo end-to-end (stampa un verbale)"
	@echo "  make serve     - console operatore su http://127.0.0.1:8080"
	@echo "  make doctor    - auto-diagnosi (config, integrita' prove, dead-letter)"
	@echo "  make quote     - preventivo/TCO indicativo (8 postazioni, SaaS, 3 anni)"
	@echo "  make video     - demo VIDEO reale (richiede opencv-python-headless)"
	@echo "  make onepager  - genera la scheda commerciale PDF (docs/sales/)"
	@echo "  make test      - suite di test (core a zero dipendenze)"
	@echo "  make clean     - rimuove artefatti generati"

install:
	python3 -m pip install -e ".[config]"

demo:
	python3 -m velocitai demo --config config/default.yaml --show-verbale 1

serve:
	python3 -m velocitai serve --config config/default.yaml --port 8080

doctor:
	python3 -m velocitai doctor --config config/default.yaml

quote:
	python3 -m velocitai quote --postazioni 8 --modello saas --anni 3

video:
	python3 examples/video_demo.py

onepager:
	python3 docs/sales/make_onepager.py

test:
	python3 -m unittest discover -s tests

clean:
	rm -rf data/evidence data/verbali data/deadletter data/issued_ledger.json data/audit.log
	rm -rf examples/_video_demo docs/sales/VelociTAI_OnePager.pdf
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
