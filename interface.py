from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget
)

from widgets.dashboard import DashboardWidget


class Interface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Controle de Estoque")

        self.resize(1500, 900)

        self.criar_interface()

    # ==========================================
    # INTERFACE PRINCIPAL
    # ==========================================

    def criar_interface(self):

        central = QWidget()

        self.setCentralWidget(central)

        layout_principal = QHBoxLayout(central)

        # ==========================================
        # MENU LATERAL
        # ==========================================

        menu = QWidget()

        menu.setFixedWidth(220)

        layout_menu = QVBoxLayout(menu)

        self.botao_inicio = QPushButton("Início")
        self.botao_produtos = QPushButton("Produtos")
        self.botao_estoque = QPushButton("Estoque")
        self.botao_transferencia = QPushButton("Transferências")
        self.botao_movimentacoes = QPushButton("Movimentações")

        layout_menu.addWidget(self.botao_inicio)
        layout_menu.addWidget(self.botao_produtos)
        layout_menu.addWidget(self.botao_estoque)
        layout_menu.addWidget(self.botao_transferencia)
        layout_menu.addWidget(self.botao_movimentacoes)

        layout_menu.addStretch()

        # ==========================================
        # ÁREA PRINCIPAL
        # ==========================================

        self.paginas = QStackedWidget()

        self.dashboard = DashboardWidget()

        self.paginas.addWidget(self.dashboard)

        # ==========================================
        # LAYOUT
        # ==========================================

        layout_principal.addWidget(menu)
        layout_principal.addWidget(self.paginas)

        # ==========================================
        # EVENTOS
        # ==========================================

        self.botao_inicio.clicked.connect(
            self.mostrar_inicio
        )

    # ==========================================
    # MOSTRAR DASHBOARD
    # ==========================================

    def mostrar_inicio(self):

        self.paginas.setCurrentWidget(
            self.dashboard
        )