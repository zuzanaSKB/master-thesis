import sys
from collections import defaultdict

def read_addresses(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

def build_adjacency_list(addresses):
    graph = defaultdict(list)
    for i in range(len(addresses) - 1):
        src = addresses[i]
        dst = addresses[i + 1]
        weight = 1
        graph[src].append((dst, weight))
    return graph

def write_adjacency_list(graph, filename):
    with open(filename, 'w') as f:
        for node, neighbors in graph.items():
            neighbors_str = ' '.join([f"{dst}({weight})" for dst, weight in neighbors])
            f.write(f"{node}: {neighbors_str}\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 generate_graph.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    addresses = read_addresses(input_file)
    graph = build_adjacency_list(addresses)
    write_adjacency_list(graph, output_file)

    print(f"Graph printed in '{output_file}'.")

if __name__ == '__main__':
    main()
