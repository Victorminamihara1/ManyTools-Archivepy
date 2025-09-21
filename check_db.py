from pathlib import Path
import sqlite3

# Ajuste se sua RAIZ for outra
raiz = r"C:\Users\victo\OneDrive\Desktop\projeto_rpa_gui"
db_path = str(Path(raiz) / "data" / "fechamento.db")
print("DB:", db_path)

with sqlite3.connect(db_path) as con:
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tabelas:", cur.fetchall())

    cur.execute("SELECT COUNT(*) FROM vendas")
    total, = cur.fetchone()
    print("Total linhas em vendas:", total)

    # últimas 5 inserções
    cur.execute("SELECT data, loja_id, produto_id, quantidade, preco_unitario, valor_total, source_file, import_ts FROM vendas ORDER BY id DESC LIMIT 5")
    for row in cur.fetchall():
        print(row)