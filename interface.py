from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget
)

from widgets.dashboard import DashboardWidget
from widgets.produtos import ProdutosWidget
from widgets.estoque import EstoqueWidget
from widgets.transferencia import TransferenciaWidget


class Interface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Controle de Estoque")
        self.resize(1500, 900)

        self.criar_interface()

    # ========================================================
    # INTERFACE PRINCIPAL
    # ========================================================

    def criar_interface(self):

        central = QWidget()

        self.setCentralWidget(central)

        layout_principal = QHBoxLayout(central)

        # ====================================================
        # MENU LATERAL
        # ====================================================

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

        # ====================================================
        # PÁGINAS
        # ====================================================

        self.paginas = QStackedWidget()

        # Dashboard
        self.dashboard = DashboardWidget()

        # Produtos
        self.produtos = ProdutosWidget()

        # Estoque
        self.estoque = EstoqueWidget()
        
        # Transferência
        self.transferencia = TransferenciaWidget()

        # Adiciona as páginas
        self.paginas.addWidget(self.dashboard)
        self.paginas.addWidget(self.produtos)
        self.paginas.addWidget(self.estoque)

        # ====================================================
        # ORGANIZAÇÃO DA JANELA
        # ====================================================

        layout_principal.addWidget(menu)
        layout_principal.addWidget(self.paginas)

        # ====================================================
        # EVENTOS DOS BOTÕES
        # ====================================================

        self.botao_inicio.clicked.connect(
            self.mostrar_inicio
        )

        self.botao_produtos.clicked.connect(
            self.mostrar_produtos
        )

        self.botao_estoque.clicked.connect(
            self.mostrar_estoque
        )

    # ========================================================
    # MOSTRAR INÍCIO
    # ========================================================

    def mostrar_inicio(self):

        self.paginas.setCurrentWidget(
            self.dashboard
        )

    # ========================================================
    # MOSTRAR PRODUTOS
    # ========================================================

    def mostrar_produtos(self):

        self.produtos.carregar_produtos()

        self.paginas.setCurrentWidget(
            self.produtos
        )

    # ========================================================
    # MOSTRAR ESTOQUE
    # ========================================================

    def mostrar_estoque(self):

        self.estoque.carregar_locais()
        self.estoque.carregar_estoque()

        self.paginas.setCurrentWidget(
            self.estoque
        )