import networkx as nx
from typing import List
from app.models.transaction import Transaction


def build_graph(transactions: List[Transaction]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()

    for tx in transactions:
        graph.add_node(tx.sender_id)
        graph.add_node(tx.receiver_id)

        graph.add_edge(
            tx.sender_id,
            tx.receiver_id,
            transaction_id=tx.transaction_id,
            amount=tx.amount,
            timestamp=tx.timestamp
        )

    return graph
