import subprocess
import matplotlib.pyplot as plt
import sys
import re

if len(sys.argv) != 3:
    print("Usage: python plot_sequential_locality.py <analysis_script> <trace_file>")
    sys.exit(1)

analysis_script = sys.argv[1]
trace_file = sys.argv[2]

# Run the analysis script and capture output
result = subprocess.run(["python3", analysis_script, trace_file],
                        capture_output=True, text=True)

output_lines = result.stdout.splitlines()

# Parse stride histogram
stride_distribution = {}

in_histogram = False
for line in output_lines:
    if "Sequential Stride Histogram" in line:
        in_histogram = True
        continue
    if in_histogram and line.strip() == "":
        break 
    if in_histogram:
        match = re.match(r"\s*\+?([>\d]+)B: \d+ \(([\d\.]+)%\)", line)
        if match:
            stride = match.group(1)
            percentage = float(match.group(2))
            stride_distribution[stride] = percentage

# Prepare for plotting
stride_labels = sorted(stride_distribution.keys(), key=lambda x: int(x.strip(">")) if x != '>8' else 9)
percentages = [stride_distribution[k] for k in stride_labels]

# Plot
plt.figure(figsize=(8, 5))
plt.bar([f"{s}B" for s in stride_labels], percentages, color='lightcoral')
plt.xlabel("Forward Stride")
plt.ylabel("Percentage of Accesses (%)")
# plt.title("Sequential Stride Distribution")
plt.ylim(0, max(percentages) * 1.1)
plt.grid(axis='y')
plt.tight_layout()
plt.show()
