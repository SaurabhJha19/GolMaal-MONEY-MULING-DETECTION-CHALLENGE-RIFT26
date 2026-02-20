from datetime import timedelta
import networkx as nx


def compute_node_features(graph: nx.MultiDiGraph):
    for node in graph.nodes():

        in_edges = graph.in_edges(node, data=True)
        out_edges = graph.out_edges(node, data=True)

        total_in = sum(edge[2]["amount"] for edge in in_edges)
        total_out = sum(edge[2]["amount"] for edge in out_edges)

        all_timestamps = [
            edge[2]["timestamp"] for edge in list(in_edges) + list(out_edges)
        ]

        if all_timestamps:
            first_tx = min(all_timestamps)
            last_tx = max(all_timestamps)
            duration_hours = (last_tx - first_tx).total_seconds() / 3600
        else:
            duration_hours = 0

        graph.nodes[node]["features"] = {
            "in_degree": graph.in_degree(node),
            "out_degree": graph.out_degree(node),
            "total_in": total_in,
            "total_out": total_out,
            "transaction_count": graph.degree(node),
            "activity_duration_hours": duration_hours,
            "unique_counterparties":
                len(set([e[0] for e in in_edges] + [e[1] for e in out_edges]))
        }
