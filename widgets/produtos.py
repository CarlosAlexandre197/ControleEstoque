from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView
)

from banco import cadastrar_produto, buscar_produtos


class ProdutosWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.criar_interface()
        self.carregar_produtos()

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        layout_principal = QVBoxLayout(self)

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = QLabel("Cadastro de Produtos")

        titulo.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)

        layout_principal.addWidget(titulo)

        # ----------------------------------------------------
        # FORMULÁRIO
        # ----------------------------------------------------

        formulario = QFormLayout()

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código do produto")

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Descrição do produto")

        self.categoria = QLineEdit()
        self.categoria.setPlaceholderText("Categoria")

        self.unidade = QComboBox()

        self.unidade.addItems([
            "UN",
            "CX",
            "KG",
            "MT",
            "PC",
            "PCT"
        ])

        self.estoque_minimo = QSpinBox()
        self.estoque_minimo.setMinimum(0)
        self.estoque_minimo.setMaximum(999999999)

        self.estoque_inicial = QSpinBox()
        self.estoque_inicial.setMinimum(0)
        self.estoque_inicial.setMaximum(999999999)

        formulario.addRow(
            "Código:",
            self.codigo
        )

        formulario.addRow(
            "Descrição:",
            self.descricao
        )

        formulario.addRow(
            "Categoria:",
            self.categoria
        )

        formulario.addRow(
            "Unidade:",
            self.unidade
        )

        formulario.addRow(
            "Estoque mínimo:",
            self.estoque_minimo
        )

        formulario.addRow(
            "Estoque inicial:",
            self.estoque_inicial
        )

        layout_principal.addLayout(formulario)

        # ----------------------------------------------------
        # BOTÃO
        # ----------------------------------------------------

        layout_botoes = QHBoxLayout()

        self.botao_cadastrar = QPushButton(
            "Cadastrar Produto"
        )

        self.botao_limpar = QPushButton(
            "Limpar"
        )

        layout_botoes.addWidget(
            self.botao_cadastrar
        )

        layout_botoes.addWidget(
            self.botao_limpar
        )

        layout_principal.addLayout(
            layout_botoes
        )

        # ----------------------------------------------------
        # TABELA
        # ----------------------------------------------------

        titulo_tabela = QLabel(
            "Produtos cadastrados"
        )

        titulo_tabela.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
            }
        """)

        layout_principal.addWidget(
            titulo_tabela
        )

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(6)

        self.tabela.setHorizontalHeaderLabels([
            "Código",
            "Descrição",
            "Categoria",
            "Unidade",
            "Estoque mínimo",
            "Data cadastro"
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.tabela.setAlternatingRowColors(True)

        layout_principal.addWidget(
            self.tabela
        )

        # ----------------------------------------------------
        # EVENTOS
        # ----------------------------------------------------

        self.botao_cadastrar.clicked.connect(
            self.cadastrar
        )

        self.botao_limpar.clicked.connect(
            self.limpar
        )

        self.codigo.returnPressed.connect(
            self.cadastrar
        )

    # ========================================================
    # CADASTRAR
    # ========================================================

    def cadastrar(self):

        codigo = self.codigo.text().strip()
        descricao = self.descricao.text().strip()
        categoria = self.categoria.text().strip()
        unidade = self.unidade.currentText()

        estoque_minimo = self.estoque_minimo.value()
        estoque_inicial = self.estoque_inicial.value()

        # ----------------------------------------------------
        # VALIDAÇÕES
        # ----------------------------------------------------

        if not codigo:

            QMessageBox.warning(
                self,
                "Atenção",
                "Digite o código do produto."
            )

            self.codigo.setFocus()

            return

        if not descricao:

            QMessageBox.warning(
                self,
                "Atenção",
                "Digite a descrição do produto."
            )

            self.descricao.setFocus()

            return

        # ----------------------------------------------------
        # SALVAR
        # ----------------------------------------------------

        sucesso, mensagem = cadastrar_produto(
            codigo,
            descricao,
            categoria,
            unidade,
            estoque_minimo,
            estoque_inicial
        )

        if sucesso:

            QMessageBox.information(
                self,
                "Sucesso",
                mensagem
            )

            self.limpar()
            self.carregar_produtos()

        else:

            QMessageBox.warning(
                self,
                "Erro",
                mensagem
            )

    # ========================================================
    # CARREGAR PRODUTOS
    # ========================================================

    def carregar_produtos(self):

        produtos = buscar_produtos()

        self.tabela.setRowCount(0)

        for produto in produtos:

            linha = self.tabela.rowCount()

            self.tabela.insertRow(linha)

            self.tabela.setItem(
                linha,
                0,
                QTableWidgetItem(
                    str(produto["codigo"])
                )
            )

            self.tabela.setItem(
                linha,
                1,
                QTableWidgetItem(
                    str(produto["descricao"])
                )
            )

            self.tabela.setItem(
                linha,
                2,
                QTableWidgetItem(
                    str(produto["categoria"] or "")
                )
            )

            self.tabela.setItem(
                linha,
                3,
                QTableWidgetItem(
                    str(produto["unidade"])
                )
            )

            self.tabela.setItem(
                linha,
                4,
                QTableWidgetItem(
                    str(produto["estoque_minimo"])
                )
            )

            self.tabela.setItem(
                linha,
                5,
                QTableWidgetItem(
                    str(produto["data_cadastro"])
                )
            )

    # ========================================================
    # LIMPAR
    # ========================================================

    def limpar(self):

        self.codigo.clear()
        self.descricao.clear()
        self.categoria.clear()

        self.unidade.setCurrentIndex(0)

        self.estoque_minimo.setValue(0)
        self.estoque_inicial.setValue(0)

        self.codigo.setFocus()