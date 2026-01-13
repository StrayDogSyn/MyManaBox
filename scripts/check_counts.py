import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cardforge.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT COUNT(*) FROM collection_cards")
    total = cur.fetchone()[0]
    cur = conn.execute("SELECT SUM(quantity) FROM collection_cards")
    total_qty = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(*) FROM collection_cards WHERE quantity > 1")
    merged = cur.fetchone()[0]
    print(f"Total collection cards: {total}")
    print(f"Total card quantity: {total_qty}")
    print(f"Cards with merged quantities: {merged}")


if __name__ == "__main__":
    main()
