# Variables
RESULT_DIR := experiments/results

# Phony targets for not actually building files
.PHONY: all clean setup train test

# Default target
all: setup train test

# Clear previous experiments
clean:
	rm -rf _magpie_logs _magpie_work

# Redirect output and run setup
setup:
	rm -rf $(RESULT_DIR)
	mkdir -p $(RESULT_DIR)
	python3 experiments/automate_run.py --step setup --results_dir $(RESULT_DIR) &> $(RESULT_DIR)/setup_full_logs.txt 2>&1

# Train
train:
	{ time python3 experiments/automate_run.py --step train --results_dir $(RESULT_DIR) &> $(RESULT_DIR)/train_full_logs.txt 2>&1 ; } 2>> $(RESULT_DIR)/time.txt

# Test
test:
	python3 experiments/automate_run.py --step test --results_dir $(RESULT_DIR) &> $(RESULT_DIR)/test_full_logs.txt 2>&1
