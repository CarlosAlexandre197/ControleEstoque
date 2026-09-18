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
# BUSCAR ESTOQUE
# ============================================================

def buscar_estoque(local_id=None, pesquisa=""):

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
        SELECT
            produtos.id,
            produtos.codigo,
            produtos.descricao,
            produtos.categoria,
            produtos.unidade,
            produtos.estoque_minimo,
            locais.id AS local_id,
            locais.nome AS local_nome,
            estoque.quantidade
        FROM estoque

        INNER JOIN produtos
            ON produtos.id = estoque.produto_id

        INNER JOIN locais
            ON locais.id = estoque.local_id

        WHERE produtos.ativo = 1
    """

    parametros = []

    # --------------------------------------------------------
    # FILTRO POR LOCAL
    # --------------------------------------------------------

    if local_id is not None:

        sql += """
            AND locais.id = ?
        """

        parametros.append(local_id)

    # --------------------------------------------------------
    # PESQUISA
    # --------------------------------------------------------

    if pesquisa:

        sql += """
            AND (
                produtos.codigo LIKE ?
                OR produtos.descricao LIKE ?
            )
        """

        termo = f"%{pesquisa}%"

        parametros.append(termo)
        parametros.append(termo)

    sql += """
        ORDER BY produtos.descricao
    """

    cursor.execute(sql, parametros)

    estoque = cursor.fetchall()

    conexao.close()

    return estoque

# ============================================================
# BUSCAR PRODUTOS PARA TRANSFERÊNCIA
# ============================================================

def buscar_produtos_ativos():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            codigo,
            descricao,
            unidade
        FROM produtos
        WHERE ativo = 1
        ORDER BY descricao
    """)

    produtos = cursor.fetchall()

    conexao.close()

    return produtos


# ============================================================
# REALIZAR TRANSFERÊNCIA
# ============================================================

def realizar_transferencia(
    produto_id,
    quantidade,
    origem_id,
    destino_id,
    observacao="",
    usuario=""
):

    conexao = conectar()
    cursor = conexao.cursor()

    try:

        # ----------------------------------------------------
        # VALIDAÇÕES
        # ----------------------------------------------------

        if quantidade <= 0:
            return False, "A quantidade deve ser maior que zero."

        if origem_id == destino_id:
            return False, "A origem e o destino não podem ser iguais."

        # ----------------------------------------------------
        # VERIFICA ESTOQUE DA ORIGEM
        # ----------------------------------------------------

        cursor.execute("""
            SELECT quantidade
            FROM estoque
            WHERE produto_id = ?
              AND local_id = ?
        """, (
            produto_id,
            origem_id
        ))

        estoque_origem = cursor.fetchone()

        if not estoque_origem:

            return False, (
                "O produto não possui estoque "
                "registrado no local de origem."
            )

        quantidade_atual = estoque_origem["quantidade"]

        if quantidade > quantidade_atual:

            return False, (
                f"Estoque insuficiente. "
                f"Disponível: {quantidade_atual}"
            )

        # ----------------------------------------------------
        # DATA E HORA
        # ----------------------------------------------------

        agora = datetime.now()

        data = agora.strftime("%d/%m/%Y")
        hora = agora.strftime("%H:%M:%S")

        # ----------------------------------------------------
        # DIMINUI ESTOQUE DA ORIGEM
        # ----------------------------------------------------

        cursor.execute("""
            UPDATE estoque
            SET quantidade = quantidade - ?
            WHERE produto_id = ?
              AND local_id = ?
        """, (
            quantidade,
            produto_id,
            origem_id
        ))

        # ----------------------------------------------------
        # VERIFICA SE JÁ EXISTE ESTOQUE NO DESTINO
        # ----------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM estoque
            WHERE produto_id = ?
              AND local_id = ?
        """, (
            produto_id,
            destino_id
        ))

        estoque_destino = cursor.fetchone()

        if estoque_destino:

            # -----------------------------------------------
            # SOMA AO ESTOQUE EXISTENTE
            # -----------------------------------------------

            cursor.execute("""
                UPDATE estoque
                SET quantidade = quantidade + ?
                WHERE produto_id = ?
                  AND local_id = ?
            """, (
                quantidade,
                produto_id,
                destino_id
            ))

        else:

            # -----------------------------------------------
            # CRIA ESTOQUE NO DESTINO
            # -----------------------------------------------

            cursor.execute("""
                INSERT INTO estoque (
                    produto_id,
                    local_id,
                    quantidade
                )
                VALUES (?, ?, ?)
            """, (
                produto_id,
                destino_id,
                quantidade
            ))

        # ----------------------------------------------------
        # REGISTRA A MOVIMENTAÇÃO
        # ----------------------------------------------------

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
            "TRANSFERÊNCIA",
            quantidade,
            origem_id,
            destino_id,
            observacao,
            usuario,
            data,
            hora
        ))

        # ----------------------------------------------------
        # CONFIRMA TODAS AS ALTERAÇÕES
        # ----------------------------------------------------

        conexao.commit()

        return True, "Transferência realizada com sucesso."

    except Exception as erro:

        # ----------------------------------------------------
        # DESFAZ TUDO SE HOUVER ERRO
        # ----------------------------------------------------

        conexao.rollback()

        return False, f"Erro ao realizar transferência: {erro}"

    finally:

        conexao.close()


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