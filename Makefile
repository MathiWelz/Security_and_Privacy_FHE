# Makefile
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: setup generate encrypt analyze decrypt run-examples clean

# 1. Create venv and install dependencies
setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# 2. Generate the synthetic Loan CSV
generate:
	$(PYTHON) src/generate_data.py

# 3. Individual Steps
encrypt:
	$(PYTHON) src/data_holder.py --action encrypt

analyze:
	$(PYTHON) src/data_analyzer.py

decrypt:
	$(PYTHON) src/data_holder.py --action decrypt

# 4. Run the full flow in one command
run-examples: generate encrypt analyze decrypt
	@echo "-----------------------------------"
	@echo "Full Loan Application flow completed."

clean:
	rm -rf $(VENV)
	rm -rf data/*
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete