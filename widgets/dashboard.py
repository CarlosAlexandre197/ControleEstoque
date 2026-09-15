from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame
)


class DashboardWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.criar_interface()

    def criar_interface(self):

        layout_principal = QVBoxLayout(self)

        # ==========================================
        # TÍTULO
        # ==========================================

        titulo = QLabel("Dashboard")

        titulo.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                padding: 10px;
            }
        """)

        layout_principal.addWidget(titulo)

        # ==========================================
        # CARDS
        # ==========================================

        layout_cards = QHBoxLayout()

        self.card_produtos = self.criar_card(
            "Produtos cadastrados",
            "0"
        )

        self.card_estoque = self.criar_card(
            "Itens em estoque",
            "0"
        )

        self.card_minimo = self.criar_card(
            "Abaixo do mínimo",
            "0"
        )

        self.card_movimentacoes = self.criar_card(
            "Movimentações hoje",
            "0"
        )

        layout_cards.addWidget(self.card_produtos)
        layout_cards.addWidget(self.card_estoque)
        layout_cards.addWidget(self.card_minimo)
        layout_cards.addWidget(self.card_movimentacoes)

        layout_principal.addLayout(layout_cards)

        # ==========================================
        # ESPAÇO PARA FUTURAS INFORMAÇÕES
        # ==========================================

        titulo_movimentacoes = QLabel(
            "Últimas movimentações"
        )

        titulo_movimentacoes.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
            }
        """)

        layout_principal.addWidget(titulo_movimentacoes)

        layout_principal.addStretch()

    # ==========================================
    # CRIAR CARD
    # ==========================================

    def criar_card(self, titulo, valor):

        card = QFrame()

        card.setFrameShape(QFrame.Shape.StyledPanel)

        card.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 10px;
                background-color: white;
            }

            QLabel {
                border: none;
            }
        """)

        layout = QVBoxLayout(card)

        label_titulo = QLabel(titulo)

        label_titulo.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555555;
            }
        """)

        label_valor = QLabel(valor)

        label_valor.setStyleSheet("""
            QLabel {
                font-size: 30px;
                font-weight: bold;
            }
        """)

        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)

        return card