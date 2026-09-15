import sqlite3
from pathlib import Path
from datetime import datetime


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
    PASTA_DATABASE.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row

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
# CADASTRAR PRODUTO
# ============================================================

def cadastrar_produto(
    codigo,
    descricao,
    categoria,
    unidade,
    estoque_minimo,
    estoque_inicial,
    local_nome="Almoxarifado"
):

    conexao = conectar()
    cursor = conexao.cursor()

    try:

        agora = datetime.now()

        data = agora.strftime("%d/%m/%Y")
        hora = agora.strftime("%H:%M:%S")

        # ----------------------------------------------------
        # Verifica se o código já existe
        # ----------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM produtos
            WHERE codigo = ?
        """, (codigo,))

        if cursor.fetchone():
            return False, "Já existe um produto com esse código."

        # ----------------------------------------------------
        # Cadastra o produto
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO produtos (
                codigo,
                descricao,
                categoria,
                unidade,
                estoque_minimo,
                data_cadastro
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            codigo,
            descricao,
            categoria,
            unidade,
            estoque_minimo,
            data
        ))

        produto_id = cursor.lastrowid

        # ----------------------------------------------------
        # Local do estoque
        # ----------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM locais
            WHERE nome = ?
        """, (local_nome,))

        local = cursor.fetchone()

        if not local:
            raise Exception(
                f"Local '{local_nome}' não encontrado."
            )

        local_id = local["id"]

        # ----------------------------------------------------
        # Cria estoque inicial
        # ----------------------------------------------------

        cursor.execute("""
            INSERT INTO estoque (
                produto_id,
                local_id,
                quantidade
            )
            VALUES (?, ?, ?)
        """, (
            produto_id,
            local_id,
            estoque_inicial
        ))

        # ----------------------------------------------------
        # Registra entrada inicial
        # ----------------------------------------------------

        if estoque_inicial > 0:

            cursor.execute("""
                INSERT INTO movimentacoes (
                    produto_id,
                    tipo,
                    quantidade,
                    origem_id,
                    destino_id,
                    observacao,
                    usuario,
                    data,
                    hora
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                produto_id,
                "ENTRADA",
                estoque_inicial,
                None,
                local_id,
                "Estoque inicial",
                "",
                data,
                hora
            ))

        conexao.commit()

        return True, "Produto cadastrado com sucesso."

    except sqlite3.IntegrityError as erro:

        conexao.rollback()

        return False, f"Erro ao cadastrar produto: {erro}"

    except Exception as erro:

        conexao.rollback()

        return False, f"Erro: {erro}"

    finally:

        conexao.close()


# ============================================================
# BUSCAR PRODUTOS
# ============================================================

def buscar_produtos():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            codigo,
            descricao,
            categoria,
            unidade,
            estoque_minimo,
            data_cadastro
        FROM produtos
        WHERE ativo = 1
        ORDER BY descricao
    """)

    produtos = cursor.fetchall()

    conexao.close()

    return produtos


# ============================================================
# BUSCAR LOCAIS
# ============================================================

def buscar_locais():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM locais
        WHERE ativo = 1
        ORDER BY nome
    """)

    locais = cursor.fetchall()

    conexao.close()

    return locais


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    criar_tabelas()

    print("========================================")
    print(" BANCO DE ESTOQUE")
    print("========================================")
    print()
    print("Banco criado/verificado com sucesso!")
    print()
    print(f"Local: {CAMINHO_BANCO}")
    print()
    print("Tabelas:")
    print("- produtos")
    print("- locais")
    print("- estoque")
    print("- movimentacoes")
    print()
    print("========================================")