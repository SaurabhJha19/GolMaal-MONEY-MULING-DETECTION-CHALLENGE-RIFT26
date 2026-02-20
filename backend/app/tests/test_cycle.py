def test_simple_cycle():

    from app.core.graph_builder import build_graph
    from app.patterns.cycle_detector import CycleDetector
    from app.models.transaction import Transaction

    txs = [
        Transaction(transaction_id="1", sender_id="A", receiver_id="B", amount=100, timestamp="2024-01-01 00:00:00"),
        Transaction(transaction_id="2", sender_id="B", receiver_id="C", amount=100, timestamp="2024-01-01 01:00:00"),
        Transaction(transaction_id="3", sender_id="C", receiver_id="A", amount=100, timestamp="2024-01-01 02:00:00"),
    ]

    graph = build_graph(txs)
    detector = CycleDetector()
    results = detector.detect(graph)

    assert len(results) == 1
