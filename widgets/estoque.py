from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)

from banco import buscar_estoque, buscar_locais


class EstoqueWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.criar_interface()
        self.carregar_locais()
        self.carregar_estoque()

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        layout_principal = QVBoxLayout(self)

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = QLabel("Controle de Estoque")

        titulo.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)

        layout_principal.addWidget(titulo)

        # ----------------------------------------------------
        # FILTROS
        # ----------------------------------------------------

        layout_filtros = QHBoxLayout()

        label_pesquisa = QLabel("Pesquisar:")

        self.pesquisa = QLineEdit()

        self.pesquisa.setPlaceholderText(
            "Código ou descrição do produto"
        )

        label_local = QLabel("Local:")

        self.local = QComboBox()

        self.local.setMinimumWidth(200)

        layout_filtros.addWidget(
            label_pesquisa
        )

        layout_filtros.addWidget(
            self.pesquisa
        )

        layout_filtros.addWidget(
            label_local
        )

        layout_filtros.addWidget(
            self.local
        )

        layout_principal.addLayout(
            layout_filtros
        )

        # ----------------------------------------------------
        # RESUMO
        # ----------------------------------------------------

        self.resumo = QLabel(
            "Produtos exibidos: 0 | Quantidade total: 0"
        )

        self.resumo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)

        layout_principal.addWidget(
            self.resumo
        )

        # ----------------------------------------------------
        # TABELA
        # ----------------------------------------------------

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(7)

        self.tabela.setHorizontalHeaderLabels([
            "Código",
            "Produto",
            "Categoria",
            "Unidade",
            "Local",
            "Estoque",
            "Estoque mínimo"
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabela.setAlternatingRowColors(True)

        self.tabela.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabela.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout_principal.addWidget(
            self.tabela
        )

        # ----------------------------------------------------
        # EVENTOS
        # ----------------------------------------------------

        self.pesquisa.textChanged.connect(
            self.carregar_estoque
        )

        self.local.currentIndexChanged.connect(
            self.carregar_estoque
        )

    # ========================================================
    # CARREGAR LOCAIS
    # ========================================================

    def carregar_locais(self):

        self.local.blockSignals(True)

        self.local.clear()

        self.local.addItem(
            "Todos os locais",
            None
        )

        locais = buscar_locais()

        for local in locais:

            self.local.addItem(
                local["nome"],
                local["id"]
            )

        self.local.blockSignals(False)

    # ========================================================
    # CARREGAR ESTOQUE
    # ========================================================

    def carregar_estoque(self):

        pesquisa = self.pesquisa.text().strip()

        local_id = self.local.currentData()

        produtos = buscar_estoque(
            local_id=local_id,
            pesquisa=pesquisa
        )

        self.tabela.setRowCount(0)

        quantidade_total = 0

        for produto in produtos:

            linha = self.tabela.rowCount()

            self.tabela.insertRow(linha)

            quantidade = produto["quantidade"]

            quantidade_total += quantidade

            # ------------------------------------------------
            # CÓDIGO
            # ------------------------------------------------

            self.tabela.setItem(
                linha,
                0,
                QTableWidgetItem(
                    str(produto["codigo"])
                )
            )

            # ------------------------------------------------
            # PRODUTO
            # ------------------------------------------------

            self.tabela.setItem(
                linha,
                1,
                QTableWidgetItem(
                    str(produto["descricao"])
                )
            )

            # ------------------------------------------------
            # CATEGORIA
            # ------------------------------------------------

            self.tabela.setItem(
                linha,
                2,
                QTableWidgetItem(
                    str(produto["categoria"] or "")
                )
            )

            # ------------------------------------------------
            # UNIDADE
            # ------------------------------------------------

            self.tabela.setItem(
                linha,
                3,
                QTableWidgetItem(
                    str(produto["unidade"])
                )
            )

            # ------------------------------------------------
            # LOCAL
            # ------------------------------------------------

            self.tabela.setItem(
                linha,
                4,
                QTableWidgetItem(
                    str(produto["local_nome"])
                )
            )

            # ------------------------------------------------
            # ESTOQUE
            # ------------------------------------------------

            item_estoque = QTableWidgetItem(
                str(quantidade)
            )

            self.tabela.setItem(
                linha,
                5,
                item_estoque
            )

            # ------------------------------------------------
            # ESTOQUE MÍNIMO
            # ------------------------------------------------

            self.tabela.setItem(
                linha,
                6,
                QTableWidgetItem(
                    str(produto["estoque_minimo"])
                )
            )

            # ------------------------------------------------
            # DESTAQUE DO ESTOQUE
            # ------------------------------------------------

            minimo = produto["estoque_minimo"]

            if quantidade <= minimo:

                for coluna in range(7):

                    item = self.tabela.item(
                        linha,
                        coluna
                    )

                    item.setToolTip(
                        "Estoque igual ou abaixo do mínimo"
                    )

        # ----------------------------------------------------
        # RESUMO
        # ----------------------------------------------------

        self.resumo.setText(
            f"Produtos exibidos: {len(produtos)} | "
            f"Quantidade total: {quantidade_total}"
        )