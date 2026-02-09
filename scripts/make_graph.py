import sys
from igraph import Graph

def main():
    if len(sys.argv) < 2:
        print("Usage: python make_graph.py <trace_file>")
        sys.exit(1)

    trace_path = sys.argv[1]

    # read trace file
    try:
        with open(trace_path) as f:
            trace = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: file '{trace_path}' not found.")
        sys.exit(1)

    if not trace:
        print("Trace file is empty.")
        sys.exit(1)

    # build address mapping and edges
    vertices = {}   # dictionary mapping address string → integer index (vertex id)
    edges = []         # list of pairs
    last_addr = None

    for addr in trace:
        if addr not in vertices:
            vertices[addr] = len(vertices)
        if last_addr is not None:
            edges.append((vertices[last_addr], vertices[addr]))
        last_addr = addr

    # build graph
    g = Graph(directed=True)
    g.add_vertices(len(vertices))
    g.add_edges(edges)
    g.vs["name"] = [addr for addr, _ in sorted(vertices.items(), key=lambda x: x[1])]

    print(f"Vertices: {g.vcount()}, Edges: {g.ecount()}")
    print(f"Unique addresses: {len(vertices)}")

    # save graph to a file
    output_file = "trace_graph.graphml"
    g.write_graphml(output_file)
    print(f"Graph saved as '{output_file}'.")

if __name__ == "__main__":
    main()