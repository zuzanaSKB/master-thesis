import sys
from collections import deque

def analyze_locality(file_path, window_size):
    with open(file_path, 'r') as file:
        addresses = [int(line.strip(), 16) for line in file]

    spatial_count = 0
    sequential_count = 0
    temporal_count = 0
    total_accesses = len(addresses)
    
    recent_addresses = deque(maxlen=window_size)  # Sliding window for temporal locality

    for i in range(1, total_accesses):
        prev_addr = addresses[i - 1]
        curr_addr = addresses[i]

        # Spatial locality (current address is within range of previous address)
        if abs(curr_addr - prev_addr) <= window_size:
            spatial_count += 1

        # Sequential locality (current address is exactly previous +1)
        if curr_addr == prev_addr + 1:
            sequential_count += 1

        # Temporal locality (current address appeared in recent window)
        if curr_addr in recent_addresses:
            temporal_count += 1
        
        recent_addresses.append(curr_addr)  # Update window
    
    # Calculate percentages
    spatial_locality = (spatial_count / total_accesses) * 100
    sequential_locality = (sequential_count / total_accesses) * 100
    temporal_locality = (temporal_count / total_accesses) * 100

    # Print results
    print(f"Spatial Locality: {spatial_locality:.2f}%")
    print(f"Sequential Locality: {sequential_locality:.2f}%")
    print(f"Temporal Locality: {temporal_locality:.2f}%")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python locality_principles_analysis.py <input_file> <window_size>")
        sys.exit(1)

    trace_file = sys.argv[1]
    window_size = int(sys.argv[2])

    analyze_locality(trace_file, window_size)
