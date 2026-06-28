.PHONY: help demo serve test clean

help:
	@echo "VelociTAI - comandi disponibili:"
	@echo "  make demo     - esegue lo scenario dimostrativo end-to-end"
	@echo "  make serve     - avvia la console operatore su http://127.0.0.1:8080"
	@echo "  make test      - esegue la suite di test (zero dipendenze)"
	@echo "  make clean     - rimuove prove e verbali generati"

demo:
	python3 -m velocitai demo --config config/default.yaml --show-verbale 1

serve:
	python3 -m velocitai serve --config config/default.yaml --port 8080

test:
	python3 -m unittest discover -s tests

clean:
	rm -rf data/evidence data/verbali
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
