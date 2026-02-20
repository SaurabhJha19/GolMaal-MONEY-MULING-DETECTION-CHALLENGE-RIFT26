import networkx as nx
import math
from collections import Counter


def compute_network_intelligence(graph):

    simple = nx.DiGraph()
    simple.add_nodes_from(graph.nodes())
    simple.add_edges_from(graph.edges())

    pagerank = nx.pagerank(simple)
    betweenness = nx.betweenness_centrality(simple)

    for node in graph.nodes():
        graph.nodes[node]["features"]["pagerank"] = pagerank.get(node, 0)
        graph.nodes[node]["features"]["betweenness"] = betweenness.get(node, 0)


def compute_behavioral_entropy(graph):

    for node in graph.nodes():

        in_edges = list(graph.in_edges(node, data=True))
        out_edges = list(graph.out_edges(node, data=True))

        counterparties = [e[0] for e in in_edges] + [e[1] for e in out_edges]
        amounts = [e[2]["amount"] for e in in_edges + out_edges]

        graph.nodes[node]["features"]["counterparty_entropy"] = _entropy(counterparties)
        graph.nodes[node]["features"]["amount_entropy"] = _entropy(amounts)
        graph.nodes[node]["features"]["burst_score"] = _burst_score(in_edges + out_edges)


def _entropy(values):
    if not values:
        return 0
    counts = Counter(values)
    total = sum(counts.values())
    entropy = 0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def _burst_score(edges):
    if not edges:
        return 0

    timestamps = sorted([e[2]["timestamp"] for e in edges])
    max_burst = 0
    start = 0

    for end in range(len(timestamps)):
        while (timestamps[end] - timestamps[start]).total_seconds() > 6 * 3600:
            start += 1
        max_burst = max(max_burst, end - start + 1)

    return min(max_burst / 10, 1.0)
