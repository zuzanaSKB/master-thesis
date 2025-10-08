import sys
from collections import Counter

def analyze_sequential_locality(file_path, output_path=None):
    with open(file_path, 'r') as file:
        addresses = [int(line.strip(), 16) for line in file]

    total_accesses = len(addresses)
    if total_accesses < 2:
        print("Not enough addresses to analyze sequential locality.")
        return

    stride_histogram = Counter()

    for i in range(1, total_accesses):
        curr_addr = addresses[i]
        prev_addr = addresses[i - 1]
        stride = curr_addr - prev_addr

        if 1 <= stride <= 8:
            stride_histogram[stride] += 1

    lines = []
    lines.append("Sequential Stride Histogram (forward only, 1-8B):")
    for stride in range(1, 9):
        count = stride_histogram[stride]
        percentage = (count / (total_accesses - 1)) * 100
        lines.append(f"  +{stride}B: {count} ({percentage:.2f}%)")

    # Print to terminal
    for line in lines:
        print(line)

    # Optionally write to file
    # if output_path:
    #     with open(output_path, 'w') as out_file:
    #         for line in lines:
    #             out_file.write(line + '\n')

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python sequential_locality_analysis.py <input_file> [output_file]")
        sys.exit(1)

    trace_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else None

    analyze_sequential_locality(trace_file, output_file)
