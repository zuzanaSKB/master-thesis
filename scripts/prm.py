import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

PAGE_SIZE = 4096        # 4KB pages
WINDOW_SIZE = 500       # References per window
SLIDE_STEP = WINDOW_SIZE // 10  # Step size for sliding window (90% overlap)


def create_page_reference_map(trace_file):
    # Read addresses and convert to page numbers ---
    pages = []
    with open(trace_file, "r") as f:
        for line in f:
            addr_str = line.strip()
            try:
                addr = int(addr_str, 16)
                page = addr // PAGE_SIZE
                pages.append(page)
            except ValueError:
                continue

    print(f"  Total references: {len(pages):,}")

    #Create sliding windows (Denning)
    windows = []
    for start in range(0, len(pages) - WINDOW_SIZE + 1, SLIDE_STEP):
        end = start + WINDOW_SIZE
        window_pages = set(pages[start:end])  # Unique pages in this window
        windows.append(window_pages)

    print(f"  Created {len(windows)} sliding windows (step={SLIDE_STEP})")

    # Map pages to compact row indexes
    all_pages = set()
    for w in windows:
        all_pages.update(w)
    sorted_pages = sorted(all_pages)
    page_to_row = {p: i for i, p in enumerate(sorted_pages)}

    num_unique_pages = len(sorted_pages)
    print(f"  Unique pages: {num_unique_pages}")

    # Build presence matrix
    matrix = np.zeros((num_unique_pages, len(windows)), dtype=int)
    for col, w in enumerate(windows):
        for page in w:
            row = page_to_row[page]
            matrix[row, col] = 1

    density = np.sum(matrix) / matrix.size
    print(f"  Matrix density: {density*100:.2f}%")

    # Compute working set sizes over time
    ws_sizes = [len(w) for w in windows]

    # Compute stability
    stable_phases = 0
    for i in range(1, len(windows)):
        overlap = len(windows[i] & windows[i - 1])
        total = len(windows[i] | windows[i - 1])
        similarity = overlap / total if total > 0 else 0
        if similarity > 0.7:
            stable_phases += 1

    stable_pct = 100 * stable_phases / (len(windows) - 1)
    print(f"\nLocality Analysis:")
    print(
        f"  Stable transitions: {stable_phases}/{len(windows)-1} "
        f"({stable_pct:.1f}%)"
    )
    print(f"  (Stable = >70% overlap between consecutive windows)")

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), constrained_layout=True)

    # Left: Page Reference Map
    ax_map = axes[0]
    cmap = ListedColormap(["white", "#1f77b4"])
    im = ax_map.imshow(
        matrix,
        aspect="auto",
        cmap=cmap,
        interpolation="nearest",
        origin="lower",
    )
    ax_map.set_title("Page Reference Map", fontsize=12, fontweight="bold")
    ax_map.set_xlabel("Sliding Window Index")
    ax_map.set_ylabel("Page ID (compact)")
    ax_map.legend(
        handles=[
            Patch(facecolor="#1f77b4", edgecolor="black", label="Referenced"),
            Patch(facecolor="white", edgecolor="black", label="Not Referenced"),
        ],
        loc="upper left",
        fontsize=8,
        frameon=True,
    )

    # Right: Working Set Size Curve
    ax_ws = axes[1]
    ax_ws.plot(ws_sizes, color="#ff7f0e")
    ax_ws.set_title("Working Set Size Over Time", fontsize=12, fontweight="bold")
    ax_ws.set_xlabel("Sliding Window Index (time)")
    ax_ws.set_ylabel("Working Set Size (unique pages)")
    ax_ws.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle(
        f"Working Set Analysis for {trace_file}\n"
        f"(WINDOW={WINDOW_SIZE}, STEP={SLIDE_STEP})",
        fontsize=14,
        fontweight="bold",
    )
    plt.show()

    # Stats summary
    print("\nWorking Set Statistics:")
    print(f"  Mean: {np.mean(ws_sizes):.1f} pages")
    print(f"  Max: {max(ws_sizes)} pages")
    print(f"  Min: {min(ws_sizes)} pages")
    print(f"  Std Dev: {np.std(ws_sizes):.1f} pages")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python prm.py <trace_file> [window_size]")
        sys.exit(1)

    trace_file = sys.argv[1]
    if len(sys.argv) > 2:
        WINDOW_SIZE = int(sys.argv[2])

    create_page_reference_map(trace_file)