CYCLE_MIN_LENGTH = 3
CYCLE_MAX_LENGTH = 5
SMURFING_THRESHOLD = 10
SMURFING_WINDOW_HOURS = 72
SHELL_MAX_INTERMEDIATE_DEGREE = 3
MAX_UPLOAD_ROWS = 100000

# Risk weights (must sum <= 1.0 before feature additions)
WEIGHTS = {
    "cycle": 0.30,
    "smurfing": 0.25,
    "shell_chain": 0.25,
    "velocity": 0.10,
    "anomaly": 0.10
}

MIN_SUSPICION_SCORE = 15.0  # production threshold
