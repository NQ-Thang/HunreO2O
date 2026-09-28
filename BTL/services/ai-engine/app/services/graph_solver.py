"""
HUNRE E-COMMERCE AI ENGINE
Module: Barter Graph Solver 2.0 (Directed Cycle Detection & Matrix Cash Compensation)
Thuật toán: Johnson's Cycle Finding + Value Balancing Matrix
"""

import networkx as nx
from typing import List, Dict, Any

class BarterGraphSolver:
    @staticmethod
    def detect_and_balance_cycles(items: List[Dict[str, Any]], max_cycle_length: int = 3) -> List[Dict[str, Any]]:
        """
        Xây dựng đồ thị có hướng G = (V, E)
        Đỉnh V: Vật phẩm cần trao đổi (bao gồm thông tin chủ sở hữu và định giá)
        Cạnh E(u, v): Chủ sở hữu của u muốn nhận vật phẩm v
        Tìm tất cả các chu trình đơn có độ dài từ 2 đến max_cycle_length,
        tính toán ma trận bù trừ tiền mặt cho từng thành viên trong chu trình.
        """
        G = nx.DiGraph()

        # 1. Thêm các đỉnh vào đồ thị
        item_map = {}
        for item in items:
            item_id = str(item["id"])
            item_map[item_id] = item
            G.add_node(item_id, **item)

        # 2. Xây dựng các cạnh có hướng dựa trên mong muốn trao đổi
        # Một cạnh u -> v nghĩa là: "Người giữ món u đồng ý đưa u để nhận về v"
        for u in items:
            u_id = str(u["id"])
            desired = str(u.get("desired_category_or_title") or "").lower()
            for v in items:
                v_id = str(v["id"])
                if u_id != v_id and u["seller_id"] != v["seller_id"]:
                    v_title = str(v.get("title") or "").lower()
                    v_cat = str(v.get("category_name") or "").lower()
                    
                    # Khớp nếu món đồ v nằm trong mong muốn của chủ sở hữu món u
                    if (desired and (desired in v_title or desired in v_cat)) or u.get("accept_any_match", False):
                        G.add_edge(u_id, v_id)

        # 3. Tìm các chu trình đơn (Simple Directed Cycles)
        all_cycles = list(nx.simple_cycles(G))
        matched_cycles = []

        for cycle in all_cycles:
            cycle_len = len(cycle)
            if 2 <= cycle_len <= max_cycle_length:
                # 4. Tính toán ma trận bù trừ tiền mặt (Cash Compensation)
                # Trong chu trình: cycle[i] trao đồ cho cycle[(i+1)%n],
                # tức là người giữ cycle[i] nhận về món đồ cycle[(i-1)%n]!
                cycle_details = []
                net_transfers = []
                total_cycle_value = 0

                for i in range(cycle_len):
                    curr_item_id = cycle[i]
                    # Món đồ mình CHO ĐI:
                    given_item = item_map[curr_item_id]
                    # Món đồ mình NHẬN LẠI (từ người đứng trước trong chu trình):
                    received_item_id = cycle[(i - 1 + cycle_len) % cycle_len]
                    received_item = item_map[received_item_id]

                    given_val = float(given_item.get("current_price", 0))
                    received_val = float(received_item.get("current_price", 0))
                    total_cycle_value += given_val

                    # Khoản chênh lệch = Giá trị đồ nhận về - Giá trị đồ cho đi
                    # Nếu diff > 0: Bạn nhận đồ giá cao hơn đồ bạn cho đi -> Phải nạp bù tiền vào Escrow
                    # Nếu diff < 0: Bạn nhận đồ giá thấp hơn -> Được nhận lại tiền thặng dư từ Escrow
                    cash_diff = received_val - given_val

                    cycle_details.append({
                        "step": i + 1,
                        "student_id": given_item["seller_id"],
                        "student_name": given_item.get("seller_name", f"Sinh viên {given_item['seller_id']}"),
                        "gives_item": {
                            "id": given_item["id"],
                            "title": given_item["title"],
                            "value": given_val
                        },
                        "receives_item": {
                            "id": received_item["id"],
                            "title": received_item["title"],
                            "value": received_val
                        },
                        "cash_compensation": {
                            "amount": abs(cash_diff),
                            "action": "PAY_TO_ESCROW" if cash_diff > 0 else ("RECEIVE_FROM_ESCROW" if cash_diff < 0 else "ZERO_DIFF"),
                            "signed_amount": cash_diff
                        }
                    })

                matched_cycles.append({
                    "cycle_id": f"CYCLE-HUNRE-{'-'.join(cycle)}",
                    "cycle_type": f"{cycle_len}-Way Barter Swap",
                    "length": cycle_len,
                    "node_ids": cycle,
                    "total_cycle_value": total_cycle_value,
                    "steps": cycle_details,
                    "is_balanced": sum(item["cash_compensation"]["signed_amount"] for item in cycle_details) == 0
                })

        return matched_cycles
