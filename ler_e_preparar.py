# ler_e_preparar.py
from pathlib import Path
from datetime import datetime
import pandas as pd, sqlite3

REQUIRED = ['data','loja_id','produto_id','quantidade','preco_unitario']
VARIANTS = {
    'data': ['data','date','data_venda','data da venda','dt','dt_venda'],
    'loja_id': ['loja_id','loja','store_id','filial','id_loja','cod_loja','codigo_loja'],
    'produto_id': ['produto_id','produto','product_id','sku','id_produto','cod_produto','codigo_produto'],
    'quantidade': ['quantidade','qtd','quantity','qty','qte','qtde','quantidade_vendida','qtd_vendida'],
    'preco_unitario': [
        'preco_unitario','preco','unit_price','valor_unitario','preco_un','preco unit',
        'valor unitario','vl_unit','vlunit', 'preco_uni', 'preco_unit', 'precounit'
    ],
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    lower = {c.lower().strip(): c for c in df.columns}
    mapping = {}
    for dest, cands in VARIANTS.items():
        for c in cands:
            if c in lower:
                mapping[lower[c]] = dest
                break
    return df.rename(columns=mapping)

def _parse_date_series(col: pd.Series) -> pd.Series:
    col = col.astype(str).str.strip()
    s1 = pd.to_datetime(col, errors='coerce', format='%Y-%m-%d')
    s2 = pd.to_datetime(col, errors='coerce', dayfirst=True)
    return s1.fillna(s2).dt.date

def ler_e_preparar(raiz: str):
    """Lê todos os .xlsx em <raiz>/planilha, valida e calcula. Retorna (df, avisos)."""
    avisos = []
    p_plan = Path(raiz) / "planilha"
    files = list(p_plan.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"Nenhum .xlsx em {p_plan}")

    dfs = []
    for f in files:
        df = pd.read_excel(f)
        df = _normalize_columns(df)
        falt = [k for k in REQUIRED if k not in df.columns]
        if falt:
            avisos.append(f"{f.name}: colunas ausentes {falt} — arquivo ignorado")
            continue
        df = df[REQUIRED].copy()
        df['data'] = _parse_date_series(df['data'])
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').astype('Int64')
        df['preco_unitario'] = pd.to_numeric(df['preco_unitario'], errors='coerce')
        df['valor_total'] = df['quantidade'] * df['preco_unitario']
        df['source_file'] = f.name

        before = len(df)
        df = df.dropna(subset=REQUIRED + ['valor_total'])
        rem = before - len(df)
        if rem:
            avisos.append(f"{f.name}: {rem} linha(s) inválida(s) removida(s).")

        dfs.append(df)

    if not dfs:
        raise ValueError("Nenhum arquivo válido após validação.")
    return pd.concat(dfs, ignore_index=True), avisos

def init_db(db_path: str):
    p = Path(db_path); p.parent.mkdir(parents=True, exist_ok=True)
    ddl = """
    PRAGMA journal_mode = WAL;
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE NOT NULL,
        loja_id TEXT NOT NULL,
        produto_id TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario REAL NOT NULL,
        valor_total REAL NOT NULL,
        source_file TEXT,
        import_ts DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data);
    CREATE INDEX IF NOT EXISTS idx_vendas_loja ON vendas(loja_id);
    """
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        for stmt in filter(None, ddl.split(";")):
            cur.execute(stmt)
        con.commit()

def gravar_sqlite(db_path: str, df: pd.DataFrame) -> int:
    if df.empty: return 0
    with sqlite3.connect(db_path) as con:
        df.to_sql("vendas", con, if_exists="append", index=False)
        return len(df)

def gerar_relatorio(raiz: str, db_path: str, df: pd.DataFrame, avisos: list[str]) -> str:
    root = Path(raiz)
    out_dir = root / "relatorios"; out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_file = out_dir / f"relatorio_{ts}.txt"

    by_loja = df.groupby(['data','loja_id'])['valor_total'].sum().reset_index()

    linhas = []
    linhas.append(f"Relatório de Processamento - {ts}")
    linhas.append("")
    if avisos:
        linhas.append("Avisos/Anotações:")
        for a in avisos: linhas.append(f"- {a}")
        linhas.append("")
    linhas.append(f"Linhas válidas inseridas: {len(df)}")
    linhas.append("")
    linhas.append("Totais por dia e loja:")
    for _, row in by_loja.iterrows():
        linhas.append(f"- {row['data']} | Loja {row['loja_id']}: R$ {row['valor_total']:,.2f}")
    linhas.append("")
    linhas.append(f"Banco de dados: {db_path}")
    linhas.append(f"Pasta de origem: {root}")

    out_file.write_text("\n".join(linhas), encoding="utf-8")
    return str(out_file)
