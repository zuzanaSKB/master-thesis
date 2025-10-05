import sys
from collections import deque, Counter

def analyze_locality(file_path, window_size, alignment_sizes):
    with open(file_path, 'r') as file:
        addresses = [int(line.strip(), 16) for line in file]

    spatial_count = 0
    sequential_count = 0
    temporal_count = 0
    total_accesses = len(addresses)
    
    recent_addresses = deque(maxlen=window_size) # Sliding window for temporal locality
    alignment_counts = Counter()

    # Count alignment for all addresses
    for addr in addresses:
        for align in alignment_sizes:
            if addr % align == 0:
                alignment_counts[align] += 1
                break

    # Add first address to recent_addresses
    if addresses:
        recent_addresses.append(addresses[0])

    # Analyze locality starting from second address
    for i in range(1, total_accesses):
        curr_addr = addresses[i]
        prev_addr = addresses[i - 1]

        # Spatial locality
        # accesses to addresses within 'window_size' bytes (in either direction)
        if abs(curr_addr - prev_addr) <= window_size:
            spatial_count += 1

        # Sequential locality
        # accesses to the next address within +8 bytes (only forward)
        diff = curr_addr - prev_addr
        if 0 < diff <= 8:
            sequential_count += 1

        # Temporal locality 
        # current address appeared in recent window
        if curr_addr in recent_addresses:
            temporal_count += 1
        
        # Update window
        recent_addresses.append(curr_addr)  
    
    # Calculate percentages
    spatial_locality = (spatial_count / total_accesses) * 100
    sequential_locality = (sequential_count / total_accesses) * 100
    temporal_locality = (temporal_count / total_accesses) * 100

    # Print results
    print(f"Spatial Locality: {spatial_locality:.2f}%")
    print(f"Sequential Locality: {sequential_locality:.2f}%")
    print(f"Temporal Locality: {temporal_locality:.2f}%")

    print("Address Alignment Statistics:")
    for align in alignment_sizes:
        count = alignment_counts[align]
        percentage = (count / total_accesses) * 100
        print(f"  Aligned to {align}B: {count} ({percentage:.2f}%)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python locality_principles_analysis.py <input_file> <window_size>")
        sys.exit(1)

    trace_file = sys.argv[1]
    window_size = int(sys.argv[2])
    
    alignment_sizes = [128, 64, 32, 16, 8, 4, 2]
    analyze_locality(trace_file, window_size, alignment_sizes)