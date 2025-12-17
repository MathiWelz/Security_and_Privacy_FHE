# Makefile for Privacy-Preserving Salary Audit Project
# Compatible with Windows, Mac, and Linux

# -------------------------------------------------------------------------
# OS Detection & Command Setup
# -------------------------------------------------------------------------

# Default to Unix-style commands (Mac/Linux)
PYTHON_CMD = python3
PIP_CMD = pip3
# Cleanup command: uses standard 'rm'
CLEANUP_CMD = rm -rf data/

# If Windows_NT is detected, override with Windows-style commands
ifeq ($(OS),Windows_NT)
    PYTHON_CMD = python
    PIP_CMD = pip
    # Cleanup command: uses Python's shutil
    CLEANUP_CMD = $(PYTHON_CMD) -c "import shutil, os; os.path.exists('data') and shutil.rmtree('data'); print('Data folder removed.')"
endif

# -------------------------------------------------------------------------
# Default Arguments (Can be overridden via CLI: make run SIZE=5000)
# -------------------------------------------------------------------------
SIZE ?= 13000
PHE_BITS ?= 1024
TS_POLY ?= 8192
TS_COEFF ?= "[60, 40, 40, 60]"
CSV_OUT ?= benchmark_results.csv

# -------------------------------------------------------------------------
# Targets
# -------------------------------------------------------------------------

.PHONY: setup run clean

# Target 1: Install Dependencies
setup:
	@echo "Detected OS: $(OS)"
	@echo "Installing dependencies using $(PIP_CMD)..."
	$(PYTHON_CMD) -m pip install phe tenseal pandas numpy configparser tomli
	@echo "Setup complete."

# Target 2: Run the Full Simulation with Arguments
run:
	@echo "--- Configuration ---"
	@echo "Dataset Size: $(SIZE)"
	@echo "Paillier Bits: $(PHE_BITS)"
	@echo "TenSEAL Poly: $(TS_POLY)"
	@echo "---------------------"
	@echo "Generating Dataset..."
	$(PYTHON_CMD) dataset_gen.py --size $(SIZE)
	@echo "Running Homomorphic Encryption Simulation..."
	$(PYTHON_CMD) main.py --size $(SIZE) --phe_n $(PHE_BITS) --ts_poly $(TS_POLY) --ts_coeff $(TS_COEFF) --csv_file $(CSV_OUT)

# Target 3: Clean Generated Files
clean:
	@echo "Cleaning up generated files..."
	$(CLEANUP_CMD)
	@echo "Clean complete."