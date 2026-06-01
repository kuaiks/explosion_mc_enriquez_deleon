.PHONY: install run run-csv run-verlet run-luna test test-pure clean help

PYTHON := python3

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py

run-csv:
	$(PYTHON) main.py --salida csv

run-verlet:
	$(PYTHON) main.py --metodo verlet

run-luna:
	$(PYTHON) main.py --g 1.62

test:
	$(PYTHON) -m pytest tests/ -v

test-pure:
	$(PYTHON) -m venv .venv_pure
	.venv_pure/bin/pip install pytest -q
	.venv_pure/bin/pytest tests/test_dominio.py -v
	@echo "OK - el dominio pasa sin numpy ni matplotlib"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f resultados.csv

help:
	@echo "Comandos disponibles:"
	@echo "  make install     - Instalar dependencias"
	@echo "  make run         - Ejecutar simulación (modo animación)"
	@echo "  make run-csv     - Ejecutar simulación (exportar CSV)"
	@echo "  make run-verlet  - Ejecutar con integrador Verlet"
	@echo "  make run-luna    - Ejecutar con gravedad lunar (g=1.62)"
	@echo "  make test        - Ejecutar todos los tests"
	@echo "  make test-pure   - Tests del dominio sin numpy/matplotlib"
	@echo "  make clean       - Limpiar archivos temporales"