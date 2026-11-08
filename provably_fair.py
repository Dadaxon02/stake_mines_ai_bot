"""
STAKE MINES AI - Official Provably Fair Algorithm
Pure Python HMAC-SHA256 implementation matching Stake.com's system
"""

import hmac
import hashlib
from typing import List, Tuple, Dict, Any


def get_server_seed_hash(server_seed: str) -> str:
    """Computes SHA-256 hash of the server seed"""
    return hashlib.sha256(server_seed.encode("utf-8")).hexdigest()


def verify_stake_mines(server_seed: str, client_seed: str, nonce: int, mines_count: int) -> Dict[str, Any]:
    """
    Computes exact bomb placements on a 5x5 board (indices 0 to 24).
    Uses Stake's exact Fisher-Yates float generation over HMAC-SHA256.
    """
    mines_count = max(1, min(24, mines_count))
    remaining_tiles = list(range(25))
    mines_positions: List[int] = []
    round_num = 0

    while len(mines_positions) < mines_count:
        message = f"{client_seed}:{nonce}:{round_num}".encode("utf-8")
        key = server_seed.encode("utf-8")
        h = hmac.new(key, message, hashlib.sha256)
        raw_bytes = h.digest()

        # Read 4 bytes at a time
        for i in range(0, 32, 4):
            if len(mines_positions) >= mines_count:
                break

            b0 = raw_bytes[i]
            b1 = raw_bytes[i + 1]
            b2 = raw_bytes[i + 2]
            b3 = raw_bytes[i + 3]

            # Convert 4 bytes to float in range [0, 1)
            float_val = (
                b0 / (256.0 ** 1) +
                b1 / (256.0 ** 2) +
                b2 / (256.0 ** 3) +
                b3 / (256.0 ** 4)
            )

            target_idx = int(float_val * len(remaining_tiles))
            selected_tile = remaining_tiles.pop(target_idx)
            mines_positions.append(selected_tile)

        round_num += 1
        if round_num > 10:
            break

    return {
        "mines_positions": sorted(mines_positions),
        "server_seed_hash": get_server_seed_hash(server_seed),
        "total_mines": len(mines_positions),
        "rounds_needed": round_num
    }


def format_board_ascii(mines_positions: List[int], revealed_safe: List[int] = None) -> str:
    """Formats 5x5 grid with emojis for Telegram text view"""
    if revealed_safe is None:
        revealed_safe = []
        
    grid_lines = []
    for r in range(5):
        row_str = []
        for c in range(5):
            idx = r * 5 + c
            if idx in mines_positions:
                row_str.append("💣")
            elif idx in revealed_safe:
                row_str.append("💎")
            else:
                row_str.append("🟩")
        grid_lines.append(" ".join(row_str))
    return "\n".join(grid_lines)
