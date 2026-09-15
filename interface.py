from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)


class Interface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Controle de Estoque")
        self.resize(1500, 900)

        self.criar_interface()

    def criar_interface(self):

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        titulo = QLabel("CONTROLE DE ESTOQUE")

        layout.addWidget(titulo)