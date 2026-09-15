import sys

from PyQt6.QtWidgets import QApplication

from interface import Interface


app = QApplication(sys.argv)

janela = Interface()
janela.show()

sys.exit(app.exec())