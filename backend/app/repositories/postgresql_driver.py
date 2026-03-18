import psycopg2


def conectar():
    return psycopg2.connect(
        host="localhost",
        database="ifesdoc",
        user="ifesdoc_user",
        password="ifesdoc_pass",
        port=5433,
    )

def executar(query, valores=None, fetch=False):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(query, valores)

            if fetch:
                return cur.fetchall()
