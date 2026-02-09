import sys
from collections import Counter
from igraph import Graph
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Compute degree sequences for the graph
# ---------------------------------------------------------------------------
def degree_histograms(g: Graph):
    indeg = g.degree(mode="IN")     # number of incoming edges per vertex
    outdeg = g.degree(mode="OUT")   # number of outgoing edges per vertex
    total = g.degree(mode="ALL")    # sum of in + out degrees
    return indeg, outdeg, total

# ---------------------------------------------------------------------------
# Print vertices with the highest degrees
# ---------------------------------------------------------------------------
def print_top_vertices(g, degrees, mode_name, top=15):
    print(f"\nTOP {top} vertices by {mode_name}-degree:")

    # create (vertex_id, degree) pairs and sort by degree descending
    items = list(enumerate(degrees))
    items.sort(key=lambda x: x[1], reverse=True)

    # print vertex name (address) if available
    for vid, deg in items[:top]:
        name = g.vs[vid]["name"] if "name" in g.vs.attributes() else vid
        print(f"  {name}\tdegree={deg}")


# ---------------------------------------------------------------------------
# Plot degree distribution using percentages
# - zoomed view on small degrees
# - full range view
# ---------------------------------------------------------------------------
def plot_hist_full(degrees, title, xlabel, zoom_max=50):
    hist = Counter(degrees)     # histogram: degree -> count of vertices
    total_vertices = len(degrees)
    x = sorted(hist.keys())     # all degree values present in the graph

    # convert counts -> percentages
    # y_percent = [(hist[k] / total_vertices) * 100 for k in x]
    y = [hist[k] for k in x]

    # ---------- ZOOM: small degrees ----------
    xz = [k for k in x if k <= zoom_max]
    # yz = [(hist[k] / total_vertices) * 100 for k in xz]  # for %
    yz = [hist[k] for k in xz]

    plt.figure(figsize=(10, 5))
    plt.bar(xz, yz)

    plt.xlabel(xlabel)
    # plt.ylabel("Percentage of vertices [%]")
    plt.ylabel("Number of vertices")
    plt.title(f"{title} (zoom <= {zoom_max}, N = {total_vertices} vertices)")

    plt.yscale("log")
    plt.tight_layout()
    plt.show()

    # ---------- FULL RANGE ----------
    plt.figure(figsize=(10, 5))
    # plt.scatter(x, y_percent, s=12)  # for %
    plt.scatter(x, y, s=12) 
    y = [hist[k] for k in x]


    plt.xlabel(xlabel)
    # plt.ylabel("Percentage of vertices [%]")
    plt.ylabel("Number of vertices")
    plt.title(f"{title} (full range, N = {total_vertices} vertices)")

    plt.yscale("log")
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# Main:
#  - load GraphML
#  - compute degree statistics
#  - print maxima and top vertices
#  - visualize histograms
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python degree_hist.py <graph.graphml>")
        sys.exit(1)

    graph_path = sys.argv[1]

    # Load graph produced from itrace
    try:
        g = Graph.Read_GraphML(graph_path)
    except Exception as e:
        print(f"Error loading graph: {e}")
        sys.exit(1)

    print(f"Loaded graph: {graph_path}")
    print(f"Vertices: {g.vcount():,}, Edges: {g.ecount():,}")

    # Compute degree sequences
    indeg, outdeg, total = degree_histograms(g)

    # ---- MAX VALUES ----
    print("\nMaximum degrees:")
    print("  Max IN-degree:   ", max(indeg))
    print("  Max OUT-degree:  ", max(outdeg))
    print("  Max TOTAL-degree:", max(total))

    # ---- TOP VERTICES ----
    print_top_vertices(g, indeg, "IN")
    print_top_vertices(g, outdeg, "OUT")
    print_top_vertices(g, total, "TOTAL")

    # ---- Visualizations ----
    plot_hist_full(indeg,  "In-Degree Histogram",  "In-degree")
    plot_hist_full(outdeg, "Out-Degree Histogram", "Out-degree")
    plot_hist_full(total,  "Total Degree Histogram", "Degree (in+out)")



if __name__ == "__main__":
    main()
