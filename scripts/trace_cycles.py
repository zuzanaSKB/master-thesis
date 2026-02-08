import sys
from collections import defaultdict
import matplotlib.pyplot as plt


def plot_cycle_histogram(cycles, title="Cycle length histogram", zoom_max=200):
    """
    Plot histogram of cycle lengths:
      - zoomed view for small cycle lengths
      - full-range view
    """

    if not cycles:
        print("No cycles to plot.")
        return

    # Prepare sorted cycle lengths and their counts
    x = sorted(cycles.keys())
    y = [cycles[k] for k in x]

    # ---------- ZOOM: small cycle lengths ----------
    xz = [k for k in x if k <= zoom_max]
    yz = [cycles[k] for k in xz]

    plt.figure(figsize=(10, 5))
    plt.plot(xz, yz, marker="o", linestyle="None")

    plt.xlabel("Cycle length")
    plt.ylabel("Number of cycles")
    plt.title(f"{title} (zoom ≤ {zoom_max})")

    plt.yscale("log")
    plt.tight_layout()
    plt.show()

    # ---------- FULL RANGE ----------
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker="o", linestyle="None")

    plt.xlabel("Cycle length (pos - prev_pos)")
    plt.ylabel("Number of cycles")
    plt.title(f"{title} (full range)")

    plt.yscale("log")
    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 trace_cycles.py <itrace_file> [out_prefix]")
        sys.exit(1)

    trace_path = sys.argv[1]
    out_prefix = sys.argv[2] if len(sys.argv) >= 3 else "trace"

    # addr -> list of positions where the address appeared in trace
    addr_positions = defaultdict(list)

    # cycles[length] = number of times this cycle length occurred
    cycles = defaultdict(int)

    try:
        with open(trace_path, "r") as f:
            pos = 0
            for line in f:
                addr = line.strip()
                if not addr:
                    continue

                pos += 1    # global sequential index in the trace
                
                # Last occurrence of this address 
                prev_pos = addr_positions[addr][-1] if addr_positions[addr] else None

                # Store current occurrence
                addr_positions[addr].append(pos)

                # If address was seen before, we detected a cycle
                # Cycle length = distance from previous occurrence
                if prev_pos is not None:
                    cycle_len = pos - prev_pos
                    cycles[cycle_len] += 1

    except FileNotFoundError:
        print(f"Error: file not found: {trace_path}")
        sys.exit(1)

    # Basic statistics
    total_refs = sum(len(v) for v in addr_positions.values())
    unique_addrs = len(addr_positions)
    total_cycles = sum(cycles.values())

    print(f"Loaded: {trace_path}")
    print(f"Total references (non-empty lines): {total_refs:,}")
    print(f"Unique addresses: {unique_addrs:,}")
    print(f"Detected cycles (repeated addr events): {total_cycles:,}")
    if cycles:
        print(f"Min cycle length: {min(cycles.keys())}")
        print(f"Max cycle length: {max(cycles.keys())}")

    
    # ------------------------------------------------------------
    # Write to files outputs
    # ------------------------------------------------------------

    # File: address -> all positions where it occurred
    positions_file = f"{out_prefix}_positions.tsv"
    with open(positions_file, "w") as out:
        out.write("address\tpositions\n")
        for addr in sorted(addr_positions.keys()):
            out.write(f"{addr}\t{','.join(map(str, addr_positions[addr]))}\n")

    # File: histogram of cycle lengths
    cycles_file = f"{out_prefix}_cycle_hist.tsv"
    with open(cycles_file, "w") as out:
        out.write("cycle_length\tcount\n")
        for length in sorted(cycles.keys()):
            out.write(f"{length}\t{cycles[length]}\n")

    # Print top 15 most frequent cycle lengths
    if cycles:
        top = sorted(cycles.items(), key=lambda kv: kv[1], reverse=True)[:15]
        print("\nTop 15 most frequent cycle lengths (length -> count):")
        for length, cnt in top:
            print(f"  {length}\t{cnt}")

    print(f"\nWrote:")
    print(f"  {positions_file}")
    print(f"  {cycles_file}")

    # ---- PLOT ----
    plot_cycle_histogram(cycles,
        title=f"Cycle Length Histogram (N = {total_cycles} cycles)")


if __name__ == "__main__":
    main()
