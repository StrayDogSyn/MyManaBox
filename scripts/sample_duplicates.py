import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cardforge.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        """
        SELECT c.name, c.set_code, cc.quantity, cc.foil, cc.condition, cc.language
        FROM collection_cards cc
        JOIN cards c ON c.id = cc.card_id
        WHERE cc.quantity > 1
        LIMIT 5
        """
    )
    print("Sample merged cards:")
    print("-" * 60)
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row['name']} ({row['set_code']}) - Qty: {row['quantity']}")
        print(
            f"  Foil: {row['foil']}, Condition: {row['condition']}, Language: {row['language']}"
        )


if __name__ == "__main__":
    main()
