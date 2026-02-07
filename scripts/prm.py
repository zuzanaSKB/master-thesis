import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import sys
import re

PAGE_SIZE = 4096        # 4KB pages
WINDOW_SIZE = 5000      # References per window (overridden in main)
SLIDE_STEP = WINDOW_SIZE // 10  # Step size for sliding window (90% overlap)


# -----------------------------------------------------------------------------
# read hexadecimal addresses and convert to page numbers
# -----------------------------------------------------------------------------
def read_trace(trace_file):
    pages = []
    with open(trace_file, "r") as f:
        for line in f:
            addr_str = line.strip()
            try:
                addr = int(addr_str, 16)
                pages.append(addr // PAGE_SIZE)
            except ValueError:
                continue
    print(f"  Total references: {len(pages):,}")
    return pages


# -----------------------------------------------------------------------------
# Parse memory_map.txt
# -----------------------------------------------------------------------------
def parse_memory_map(map_file):
    """Parse a /proc/<pid>/maps-like file and classify ranges."""
    regions = []
    with open(map_file) as f:
        for line in f:
            m = re.match(
                r"^([0-9a-fA-F]+)-([0-9a-fA-F]+)\s+([rwxps\-]+)\s+\S+\s+\S+\s+\S+\s*(.*)$",
                line.strip(),
            )
            if not m:
                continue
            # Convert start and end addresses to integers
            start = int(m.group(1), 16)
            end = int(m.group(2), 16)
            perms = m.group(3)
            path  = (m.group(4) or "").strip()
            # Store as page
            regions.append({
                "start_page": start // PAGE_SIZE,
                "end_page":   end   // PAGE_SIZE,
                "perms": perms,
                "path":  path,
            })

    print(f"  Parsed {len(regions)} memory regions")
    return regions
    

def classify_page(page, regions, main_exec_path=None):
    """
    Classify by page number using perms + pathname.
    main_exec_path: optional full path to the main executable (best precision).
    """
    for r in regions:
        if r["start_page"] <= page < r["end_page"]:
            perms = r["perms"]
            path  = r["path"]

            lower = path.lower()

            # Special kernel / pseudo mappings
            if lower in ("[vdso]", "[vvar]", "[vvar_vclock]", "[vsyscall]") or "vdso" in lower or "vvar" in lower or "vsyscall" in lower:
                return "kernel"
            if lower == "[stack]":
                return "stack"
            if lower == "[heap]":
                return "heap"
            if lower.startswith("[") and lower.endswith("]"):
                return "anon"  # other

            # Anonymous mapping (no path)
            if path == "":
                return "anon"

            # Pin / instrumentation
            if "/opt/pin/" in lower or "pin" in lower:
                return "pin"

            # If caller provides the exact main exe path
            if main_exec_path and path == main_exec_path:
                return "exec"

            # Shared libraries
            is_shared_lib = (
                ".so" in lower
                or "/lib/" in lower
                or "/usr/lib/" in lower
                or lower.endswith(".so")
                or ".so." in lower 
            )
            if is_shared_lib:
                return "lib"

            # Other file-backed mappings
            # If it has execute perm, it's code -> executable
            if "x" in perms:
                return "exec"

            # File-backed but not executable
            return "file"

    return "unknown"


def find_main_executable_path(regions):
    candidates = []
    for r in regions:
        path = r["path"]
        if not path or path.startswith("["):
            continue
        lower = path.lower()
        if "x" not in r["perms"]:
            continue
        if ".so" in lower or "/lib/" in lower or "/usr/lib/" in lower:
            continue
        # skip pin runtime/tools
        if any(x in lower for x in ("pinbin", "itrace.so", "libxed", "libpindwarf", "libdwarf", "pincrt", "/opt/pin/intel64/")):
            continue
        candidates.append(path)
    return candidates[0] if candidates else None



def color_for_region(region_name):
    """Map classification -> color."""
    colors = {
        "stack": "#4daf4a",   # green
        "heap": "#377eb8",    # blue
        "pin": "#fff200",     # yellow
        "lib": "#ff7f00",     # orange
        "exec": "#984ea3",    # purple
        "anon": "#a65628",    # brown
        "kernel": "#e41a1c",  # red
        "file": "#66c2a5",    # turchese
        "unknown": "#999999", # gray
    }
    return colors.get(region_name, "#000000")


# -----------------------------------------------------------------------------
# Page Reference Map
# -----------------------------------------------------------------------------
def create_page_reference_map(trace_file, pages, map_file=None):
    global WINDOW_SIZE, SLIDE_STEP

    # Build sliding windows
    windows = []
    for start in range(0, len(pages) - WINDOW_SIZE + 1, SLIDE_STEP):
        end = start + WINDOW_SIZE
        window_pages = set(pages[start:end])
        windows.append(window_pages)

    print(f"  Created {len(windows)} sliding windows (step={SLIDE_STEP})")

    if not windows:
        print("No windows created (trace may be too short for this WINDOW_SIZE).")
        return

    # Map pages to compact row indices
    all_pages = set().union(*windows)
    sorted_pages = sorted(all_pages)
    page_to_row = {p: i for i, p in enumerate(sorted_pages)}
    num_unique_pages = len(sorted_pages)
    print(f"  Unique pages: {num_unique_pages}")

    # Build presence matrix
    matrix = np.zeros((num_unique_pages, len(windows)), dtype=int)
    for col, w in enumerate(windows):
        for page in w:
            matrix[page_to_row[page], col] = 1

    density = np.sum(matrix) / matrix.size
    print(f"  Matrix density: {density*100:.2f}%")

    # Legend defaults (no memory map given)
    region_colors = None
    legend_patches = [
        Patch(facecolor="white", edgecolor="black", label="Not Referenced"),
        Patch(facecolor="#1f77b4", edgecolor="black", label="Referenced"),
    ]

    # If memory map is provided, color rows accordingly
    if map_file:
        regions = parse_memory_map(map_file)
        main_exec = find_main_executable_path(regions)
        print("  Found main executable:", main_exec)

        region_labels = []
        for p in sorted_pages:  # match row order
            region_labels.append(classify_page(p, regions, main_exec_path=main_exec))

        region_colors = [color_for_region(r) for r in region_labels]
        legend_patches = [
            Patch(facecolor=color_for_region("stack"), label="Stack"),
            Patch(facecolor=color_for_region("heap"), label="Heap"),
            Patch(facecolor=color_for_region("pin"), label="Pin"),
            Patch(facecolor=color_for_region("lib"), label="Libraries"),
            Patch(facecolor=color_for_region("exec"), label="Executable"),
            Patch(facecolor=color_for_region("anon"), label="Anonymous"),
            Patch(facecolor=color_for_region("kernel"), label="Kernel/VDSO"),
            Patch(facecolor=color_for_region("file"), label="File (non-exec)"),
        ]
        print("  Memory coloring applied based on:", map_file)

    # Plot Page Reference Map
    plt.figure(figsize=(10, 8))

    if region_colors:
        # Use RGB mask to colorize referenced pages by region
        color_matrix = np.ones(
            (num_unique_pages, len(windows), 3), dtype=float
        )  # RGB
        for row_idx, color_hex in enumerate(region_colors):
            rgb = np.array(
                [int(color_hex[i : i + 2], 16) for i in (1, 3, 5)]
            ) / 255.0
            for channel in range(3):
                color_matrix[row_idx, :, channel] = np.where(
                    matrix[row_idx, :] == 1,
                    rgb[channel],
                    color_matrix[row_idx, :, channel],
                )
        plt.imshow(
            color_matrix,
            aspect="auto",
            interpolation="nearest",
            origin="lower",
        )
    else:
        cmap = ListedColormap(["white", "#1f77b4"])
        plt.imshow(
            matrix,
            aspect="auto",
            cmap=cmap,
            interpolation="nearest",
            origin="lower",
        )

    plt.title(
        f"Page Reference Map for {trace_file}\n"
        f"(WINDOW={WINDOW_SIZE}, STEP={SLIDE_STEP})",
        fontsize=12,
        fontweight="bold",
    )
    plt.xlabel("Sliding Window Index")
    plt.ylabel("Page ID (compact)")
    plt.legend(handles=legend_patches, loc="upper left", fontsize=8, frameon=True)
    plt.tight_layout()
    plt.show()


# -----------------------------------------------------------------------------
# Main entry
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python prm.py <trace_file> [window_size] [memory_map_file]"
        )
        sys.exit(1)

    trace_file = sys.argv[1]
    pages = read_trace(trace_file)

    # Window size
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        # user explicitly provided a window size
        WINDOW_SIZE = int(sys.argv[2])
    else:
        # automatic: 1/30 of total references
        WINDOW_SIZE = max(100, len(pages) // 30)

    SLIDE_STEP = max(1, WINDOW_SIZE // 10)

    # Optional memory map file
    map_file = None
    if len(sys.argv) > 2 and not sys.argv[2].isdigit():
        map_file = sys.argv[2]
    elif len(sys.argv) > 3:
        map_file = sys.argv[3]

    print(f"\nUsing WINDOW_SIZE = {WINDOW_SIZE}, SLIDE_STEP = {SLIDE_STEP}")
    create_page_reference_map(trace_file, pages, map_file)