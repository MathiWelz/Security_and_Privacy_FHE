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
    # Cleanup command: uses Python's shutil to avoid CMD/PowerShell syntax issues
    CLEANUP_CMD = $(PYTHON_CMD) -c "import shutil, os; os.path.exists('data') and shutil.rmtree('data'); print('Data folder removed.')"
endif

# -------------------------------------------------------------------------
# Targets
# -------------------------------------------------------------------------

.PHONY: setup run clean

# Target 1: Install Dependencies
setup:
	@echo "Detected OS: $(OS)"
	@echo "Installing dependencies using $(PIP_CMD)..."
	$(PYTHON_CMD) -m pip install phe tenseal pandas numpy configparser
	@echo "Setup complete."

# Target 2: Run the Full Simulation
run:
	@echo "Generating Dataset..."
	$(PYTHON_CMD) dataset_gen.py
	@echo "Running Homomorphic Encryption Simulation..."
	$(PYTHON_CMD) main.py

# Target 3: Clean Generated Files
clean:
	@echo "Cleaning up generated files..."
	$(CLEANUP_CMD)
	@echo "Clean complete."