from collections import defaultdict

# Step 1: Stream log file line by line
def read_logs(filepath):
    with open(filepath, "r") as file:
        for line in file:
            yield line.strip()


# Step 2: Filter only ERROR and CRITICAL logs
def error_stream(lines):
    for line in lines:
        if "ERROR" in line or "CRITICAL" in line:
            yield line


# Step 3: Group errors and keep running counts
def error_counter(error_lines):
    counts = defaultdict(int)

    for line in error_lines:
        if "CRITICAL" in line:
            error_type = "CRITICAL"
        elif "ERROR" in line:
            error_type = "ERROR"
        else:
            error_type = "OTHER"

        counts[error_type] += 1

        yield error_type, counts[error_type], line


# Step 4: Pipeline execution
def stream_log_errors(filepath):
    logs = read_logs(filepath)
    errors = error_stream(logs)
    counted_errors = error_counter(errors)

    for error_type, count, line in counted_errors:
        print(f"[{error_type}] Count={count} | {line}")


# Run the system
stream_log_errors("server.log")