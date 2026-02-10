import subprocess
import matplotlib.pyplot as plt
import numpy as np
import sys
import re

if len(sys.argv) != 3:
    print("Usage: python3 batch_la.py la.py <trace_file>")
    sys.exit(1)

script_path = sys.argv[1]  # Path to the analysis script
trace_file = sys.argv[2]   # Path to the address trace file

# Logarithmic window sizes to test (in a range from 1 to 1000)
window_sizes = np.logspace(0, 3, num=10, dtype=int)

# Storage for results
spatial_results = []
temporal_results = []

# Alignment stats (only need to collect from the first run)
alignment_stats = {}

# Run the script for each window size
for idx, window_size in enumerate(window_sizes):
    result = subprocess.run(["python3", script_path, trace_file, str(window_size)],
                            capture_output=True, text=True)
    output_lines = result.stdout.split("\n")

    try:
        spatial = float(output_lines[0].split(": ")[1].strip('%'))
        temporal = float(output_lines[2].split(": ")[1].strip('%'))

        spatial_results.append(spatial)
        temporal_results.append(temporal)

        # On first run collect alignment statistics
        if idx == 0:
            alignment_start = output_lines.index("Address Alignment Statistics:")
            for line in output_lines[alignment_start+1:]:
                if line.strip() == "":
                    continue
                match = re.match(r"\s*Aligned to (\d+)B: \d+ \(([\d\.]+)%\)", line)
                if match:
                    align_size = int(match.group(1))
                    percentage = float(match.group(2))
                    alignment_stats[align_size] = percentage

    except Exception as e:
        print(f"Error parsing output for window size {window_size}: {e}")

# Plot Locality graph
plt.figure(figsize=(10, 6))
plt.plot(window_sizes, spatial_results, 'o-', linestyle='-', label='Spatial locality')
plt.plot(window_sizes, temporal_results, '^-', linestyle='-', label='Temporal locality')

plt.xscale('log')
plt.xticks(window_sizes, labels=[str(w) for w in window_sizes])

plt.xlabel("Window size (log scale)")
plt.ylabel("Locality (%)")
#plt.title("Locality analysis of the program /bin/ls - data addresses")
#plt.title("Locality analysis of the program echo 'Hello world!'- data addresses")
#plt.title("Locality analysis of the program num_gen_sort.c that sorts 1000 numbers - instruction addresses")
plt.title("Locality analysis of the program fib.c that computes F(10) - instruction addresses")
plt.legend()
plt.grid(False)
plt.tight_layout()
plt.show()

# Plot Alignment graph
alignments = sorted(alignment_stats.keys())
percentages = [alignment_stats[a] for a in alignments]

plt.figure(figsize=(8, 5))
plt.bar([f"{a}B" for a in alignments], percentages, color='skyblue')

plt.xlabel("Alignment size")
plt.ylabel("Percentage of accesses (%)")
#plt.title("Address Alignment Statistics - /bin/ls (data addresses)")
#plt.title("Address Alignment Statistics - echo 'Hello world!' (data addresses)")
# plt.title("Address Alignment Statistics - num_gen_sort.c that sorts 1000 numbers (instruction addresses)")
plt.title("Address Alignment Statistics - fib.c that computes F(10) (instruction addresses)")
plt.ylim(0, 100)
plt.grid(axis='y')
plt.tight_layout()
plt.show()
