"""
Multi-User Swap Cycle Detection Service (Graph Engine)
Smart Coupon Swap System

Uses NetworkX directed graph modeling to detect 3-way circular swap opportunities:
User A (has Coupon X) -> wants Coupon Y (owned by User B)
User B (has Coupon Y) -> wants Coupon Z (owned by User C)
User C (has Coupon Z) -> wants Coupon X (owned by User A)
"""

import networkx as nx
from app.services.db import execute_all


def detect_swap_cycles(max_cycle_length=3):
    """Detects 3-way and multi-user circular swap opportunities from active requests."""
    sql = """
        SELECT r.requester_id AS requester_id, c.owner_id AS owner_id, r.coupon_id, c.title AS coupon_title
        FROM coupon_requests r
        JOIN coupons c ON r.coupon_id = c.coupon_id
        WHERE r.status IN ('PENDING', 'ACCEPTED')
          AND c.status = 'ACTIVE'
          AND r.requester_id != c.owner_id;
    """
    requests = execute_all(sql)

    G = nx.DiGraph()

    for req in requests:
        u_from = req["requester_id"]
        u_to = req["owner_id"]
        G.add_edge(u_from, u_to, coupon_id=req["coupon_id"], title=req["coupon_title"])

    all_cycles = list(nx.simple_cycles(G))

    detected_cycles = []
    for cycle in all_cycles:
        if 3 <= len(cycle) <= max_cycle_length:
            cycle_steps = []
            for i in range(len(cycle)):
                u_curr = cycle[i]
                u_next = cycle[(i + 1) % len(cycle)]
                edge_data = G.get_edge_data(u_curr, u_next)
                cycle_steps.append({
                    "from_user_id": u_curr,
                    "to_user_id": u_next,
                    "requested_coupon_id": edge_data["coupon_id"],
                    "coupon_title": edge_data["title"]
                })

            detected_cycles.append({
                "cycle_length": len(cycle),
                "users_involved": cycle,
                "cycle_steps": cycle_steps,
                "description": f"{len(cycle)}-Way Circular Swap Cycle ({' -> '.join(map(str, cycle))} -> {cycle[0]})"
            })

    return detected_cycles
