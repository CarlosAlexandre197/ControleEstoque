from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QFrame
)

from banco import (
    buscar_produtos_ativos,
    buscar_locais,
    realizar_transferencia
)


class TransferenciaWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.produtos = []
        self.locais = []

        self.criar_interface()

        self.carregar_produtos()
        self.carregar_locais()

        self.atualizar_estoque_disponivel()

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        layout_principal = QVBoxLayout(self)

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = QLabel("Transferência de Estoque")

        titulo.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)

        layout_principal.addWidget(titulo)

        # ----------------------------------------------------
        # SUBTÍTULO
        # ----------------------------------------------------

        subtitulo = QLabel(
            "Transfira produtos entre o Almoxarifado e os setores."
        )

        subtitulo.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #555555;
                padding-bottom: 15px;
            }
        """)

        layout_principal.addWidget(subtitulo)

        # ----------------------------------------------------
        # ÁREA DO FORMULÁRIO
        # ----------------------------------------------------

        formulario_frame = QFrame()

        formulario_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 10px;
                background-color: #ffffff;
            }
        """)

        formulario = QFormLayout(formulario_frame)

        # ----------------------------------------------------
        # PRODUTO
        # ----------------------------------------------------

        self.produto = QComboBox()

        self.produto.setMinimumHeight(35)

        formulario.addRow(
            "Produto:",
            self.produto
        )

        # ----------------------------------------------------
        # ESTOQUE DISPONÍVEL
        # ----------------------------------------------------

        self.estoque_disponivel = QLabel(
            "Estoque disponível: 0"
        )

        self.estoque_disponivel.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                padding: 5px;
            }
        """)

        formulario.addRow(
            "",
            self.estoque_disponivel
        )

        # ----------------------------------------------------
        # QUANTIDADE
        # ----------------------------------------------------

        self.quantidade = QSpinBox()

        self.quantidade.setMinimum(1)
        self.quantidade.setMaximum(999999999)

        self.quantidade.setValue(1)

        self.quantidade.setMinimumHeight(35)

        formulario.addRow(
            "Quantidade:",
            self.quantidade
        )

        # ----------------------------------------------------
        # ORIGEM
        # ----------------------------------------------------

        self.origem = QComboBox()

        self.origem.setMinimumHeight(35)

        formulario.addRow(
            "Origem:",
            self.origem
        )

        # ----------------------------------------------------
        # DESTINO
        # ----------------------------------------------------

        self.destino = QComboBox()

        self.destino.setMinimumHeight(35)

        formulario.addRow(
            "Destino:",
            self.destino
        )

        # ----------------------------------------------------
        # OBSERVAÇÃO
        # ----------------------------------------------------

        self.observacao = QLineEdit()

        self.observacao.setPlaceholderText(
            "Observação opcional"
        )

        self.observacao.setMinimumHeight(35)

        formulario.addRow(
            "Observação:",
            self.observacao
        )

        layout_principal.addWidget(
            formulario_frame
        )

        # ----------------------------------------------------
        # BOTÃO
        # ----------------------------------------------------

        self.botao_transferir = QPushButton(
            "TRANSFERIR ESTOQUE"
        )

        self.botao_transferir.setMinimumHeight(45)

        self.botao_transferir.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #e5e5e5;
            }
        """)

        layout_principal.addWidget(
            self.botao_transferir
        )

        # ----------------------------------------------------
        # INFORMAÇÃO
        # ----------------------------------------------------

        informacao = QLabel(
            "A transferência será registrada automaticamente "
            "no histórico de movimentações."
        )

        informacao.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 10px;
            }
        """)

        layout_principal.addWidget(
            informacao
        )

        layout_principal.addStretch()

        # ----------------------------------------------------
        # EVENTOS
        # ----------------------------------------------------

        self.produto.currentIndexChanged.connect(
            self.atualizar_estoque_disponivel
        )

        self.origem.currentIndexChanged.connect(
            self.atualizar_estoque_disponivel
        )

        self.botao_transferir.clicked.connect(
            self.transferir
        )

    # ========================================================
    # PRODUTOS
    # ========================================================

    def carregar_produtos(self):

        self.produto.clear()

        self.produtos = buscar_produtos_ativos()

        for produto in self.produtos:

            texto = (
                f'{produto["codigo"]} - '
                f'{produto["descricao"]}'
            )

            self.produto.addItem(
                texto,
                produto["id"]
            )

    # ========================================================
    # LOCAIS
    # ========================================================

    def carregar_locais(self):

        self.origem.clear()
        self.destino.clear()

        self.locais = buscar_locais()

        for local in self.locais:

            self.origem.addItem(
                local["nome"],
                local["id"]
            )

            self.destino.addItem(
                local["nome"],
                local["id"]
            )

    # ========================================================
    # ESTOQUE DISPONÍVEL
    # ========================================================

    def atualizar_estoque_disponivel(self):

        produto_id = self.produto.currentData()
        origem_id = self.origem.currentData()

        if produto_id is None or origem_id is None:

            self.estoque_disponivel.setText(
                "Estoque disponível: 0"
            )

            return

        from banco import conectar

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT quantidade
            FROM estoque
            WHERE produto_id = ?
              AND local_id = ?
        """, (
            produto_id,
            origem_id
        ))

        resultado = cursor.fetchone()

        conexao.close()

        quantidade = (
            resultado["quantidade"]
            if resultado
            else 0
        )

        self.estoque_disponivel.setText(
            f"Estoque disponível: {quantidade}"
        )

        self.quantidade.setMaximum(
            max(1, quantidade)
        )

    # ========================================================
    # REALIZAR TRANSFERÊNCIA
    # ========================================================

    def transferir(self):

        produto_id = self.produto.currentData()
        quantidade = self.quantidade.value()
        origem_id = self.origem.currentData()
        destino_id = self.destino.currentData()
        observacao = self.observacao.text().strip()

        # ----------------------------------------------------
        # VALIDAÇÕES
        # ----------------------------------------------------

        if produto_id is None:

            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um produto."
            )

            return

        if origem_id is None:

            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione o local de origem."
            )

            return

        if destino_id is None:

            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione o local de destino."
            )

            return

        if origem_id == destino_id:

            QMessageBox.warning(
                self,
                "Atenção",
                "A origem e o destino não podem ser iguais."
            )

            return

        if quantidade <= 0:

            QMessageBox.warning(
                self,
                "Atenção",
                "Informe uma quantidade maior que zero."
            )

            return

        # ----------------------------------------------------
        # CONFIRMAÇÃO
        # ----------------------------------------------------

        produto_texto = self.produto.currentText()
        origem_texto = self.origem.currentText()
        destino_texto = self.destino.currentText()

        resposta = QMessageBox.question(
            self,
            "Confirmar transferência",
            (
                f"Produto:\n{produto_texto}\n\n"
                f"Quantidade: {quantidade}\n\n"
                f"Origem: {origem_texto}\n"
                f"Destino: {destino_texto}\n\n"
                "Deseja realizar esta transferência?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        # ----------------------------------------------------
        # SALVAR
        # ----------------------------------------------------

        sucesso, mensagem = realizar_transferencia(
            produto_id=produto_id,
            quantidade=quantidade,
            origem_id=origem_id,
            destino_id=destino_id,
            observacao=observacao
        )

        if sucesso:

            QMessageBox.information(
                self,
                "Transferência realizada",
                mensagem
            )

            self.observacao.clear()

            self.quantidade.setValue(1)

            self.atualizar_estoque_disponivel()

        else:

            QMessageBox.warning(
                self,
                "Erro",
                mensagem
            )