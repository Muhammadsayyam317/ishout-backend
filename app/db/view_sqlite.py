import aiosqlite
import asyncio
from tabulate import tabulate


DB_PATH = "whatsapp_agent.db"


async def show_tables():
    print(f"\n🔍 Inspecting SQLite DB: {DB_PATH}\n")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get list of all tables
        tables = await db.execute_fetchall(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )

        if not tables:
            print("❌ No tables found.")
            return

        print("📌 Tables found:")
        for t in tables:
            print(f"   • {t['name']}")

        print("\n────────────────────────────\n")

        # Loop through all tables
        for table in tables:
            table_name = table["name"]
            print(f"📌 Table: {table_name}")
            print("══════════════════════════════")

            # Show schema
            schema = await db.execute_fetchall(f"PRAGMA table_info('{table_name}');")
            if schema:
                schema_table = [
                    [
                        col["cid"],
                        col["name"],
                        col["type"],
                        col["notnull"],
                        col["dflt_value"],
                        col["pk"],
                    ]
                    for col in schema
                ]
                print("🧩 Schema:")
                print(
                    tabulate(
                        schema_table,
                        headers=["cid", "name", "type", "notnull", "default", "pk"],
                        tablefmt="fancy_grid",
                    )
                )
            else:
                print("⚠ No schema info found.")

            # Count rows
            row_count = await db.execute_fetchone(
                f"SELECT COUNT(*) as count FROM '{table_name}'"
            )
            print(f"\n📊 Total rows: {row_count['count']}\n")

            # Show rows
            rows = await db.execute_fetchall(f"SELECT * FROM '{table_name}' LIMIT 20")

            if rows:
                rows_table = [dict(row) for row in rows]
                print(tabulate(rows_table, headers="keys", tablefmt="fancy_grid"))
            else:
                print("⚠ No rows in this table.")

            print("\n────────────────────────────\n")


if __name__ == "__main__":
    asyncio.run(show_tables())
