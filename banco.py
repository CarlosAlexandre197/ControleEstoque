import sqlite3
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO DO BANCO
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_DATABASE = PASTA_PROJETO / "database"
CAMINHO_BANCO = PASTA_DATABASE / "estoque.db"


# ============================================================
# CONEXÃO
# ============================================================

def conectar():
    """
    Cria a pasta database, caso não exista,
    e retorna uma conexão com o banco SQLite.
    """

    PASTA_DATABASE.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(CAMINHO_BANCO)

    # Permite acessar as colunas pelo nome
    conexao.row_factory = sqlite3.Row

    # Ativa integridade das chaves estrangeiras
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


# ============================================================
# CRIAÇÃO DAS TABELAS
# ============================================================

def criar_tabelas():

    conexao = conectar()
    cursor = conexao.cursor()

    # --------------------------------------------------------
    # PRODUTOS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            descricao TEXT NOT NULL,
            categoria TEXT,
            unidade TEXT NOT NULL DEFAULT 'UN',
            estoque_minimo INTEGER NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1,
            data_cadastro TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # LOCAIS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    # --------------------------------------------------------
    # ESTOQUE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            local_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (produto_id)
                REFERENCES produtos(id)
                ON DELETE CASCADE,

            FOREIGN KEY (local_id)
                REFERENCES locais(id)
                ON DELETE CASCADE,

            UNIQUE(produto_id, local_id)
        )
    """)

    # --------------------------------------------------------
    # MOVIMENTAÇÕES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            produto_id INTEGER NOT NULL,

            tipo TEXT NOT NULL,

            quantidade INTEGER NOT NULL,

            origem_id INTEGER,

            destino_id INTEGER,

            observacao TEXT,

            usuario TEXT,

            data TEXT NOT NULL,
            hora TEXT NOT NULL,

            FOREIGN KEY (produto_id)
                REFERENCES produtos(id),

            FOREIGN KEY (origem_id)
                REFERENCES locais(id),

            FOREIGN KEY (destino_id)
                REFERENCES locais(id)
        )
    """)

    # --------------------------------------------------------
    # LOCAIS INICIAIS
    # --------------------------------------------------------

    locais_iniciais = [
        "Almoxarifado",
        "Expedição",
        "Produção",
        "Administrativo"
    ]

    for nome in locais_iniciais:

        cursor.execute("""
            INSERT OR IGNORE INTO locais (nome)
            VALUES (?)
        """, (nome,))

    conexao.commit()
    conexao.close()


# ============================================================
# TESTE DO BANCO
# ============================================================

if __name__ == "__main__":

    criar_tabelas()

    print("========================================")
    print(" BANCO DE ESTOQUE")
    print("========================================")
    print()
    print("Banco criado com sucesso!")
    print()
    print(f"Local: {CAMINHO_BANCO}")
    print()
    print("Tabelas criadas:")
    print("- produtos")
    print("- locais")
    print("- estoque")
    print("- movimentacoes")
    print()
    print("Locais iniciais cadastrados:")
    print("- Almoxarifado")
    print("- Expedição")
    print("- Produção")
    print("- Administrativo")
    print()
    print("========================================")