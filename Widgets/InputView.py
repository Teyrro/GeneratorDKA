from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QFormLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from AddWidget import create_line


class InputView(QWidget):
    class EditLine(QLineEdit):
        def __init__(self):
            super().__init__()

        def keyPressEvent(self, e: QKeyEvent):
            if not e.text() in self.text():
                super().keyPressEvent(e)

    class NecessaryChain(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)

        def keyPressEvent(self, a0):
            text: QLineEdit = self.parent().findChild(QLineEdit, "symb")
            if a0.text() in text.text() or a0.key() == QtCore.Qt.Key.Key_Backspace:
                super().keyPressEvent(a0)

    class Multiplicity(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)

        def keyPressEvent(self, a0):
            if not (a0.text() == "0" and self.text() == ""):
                super().keyPressEvent(a0)

    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.parent = parent
        main_lay = QVBoxLayout()
        main_lay.addWidget(QLabel("Alphabet"))
        lay: QFormLayout = QFormLayout()
        create_line(lay, self.EditLine(), "symb", "available symbols:", r"\w+")
        create_line(
            lay, self.NecessaryChain(), "subchain", "Necessary subchain:", r"\w+"
        )
        create_line(lay, self.Multiplicity(), "mult", "Multiplicity:", "IntV")
        main_lay.addLayout(lay)
        self.input_info = QLabel()
        self.input_info.setObjectName("log_dka")
        self.input_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_lay.addWidget(self.input_info)

        self.button = QPushButton("Setup")
        self.button.setObjectName("setup")
        main_lay.addWidget(self.button)

        button = QPushButton("Save")
        button.setObjectName("save")
        button.clicked.connect(self.save_dka)

        main_lay.addWidget(button)
        main_lay.addStretch()
        self.setLayout(main_lay)

    @QtCore.pyqtSlot()
    def save_dka(self):
        dka = self.parent.dka_model
        msg = QMessageBox()
        msg.setWindowTitle("Information MessageBox")
        if dka.dt is None:
            msg.setText("Заполните поле начального состояния")
            msg.exec()
            return
        filename, _ = QFileDialog.getSaveFileName(
            None, "Save File", ".", "Text Files (*.csv);;All Files (*)"
        )
        if filename == "":
            return
        dka.dt.to_csv(filename, index=True, sep=";")

    @QtCore.pyqtSlot()
    def check_input(self, sym: str, mult: str) -> bool:
        if sym != "" and mult != "":
            return False
        self.input_info.setStyleSheet("color: red")
        if sym == "":
            info = "available characters must not be empty"
            self.input_info.setText(info)
        elif mult == "":
            info = "multiplicity must not be empty"
            self.input_info.setText(info)
        return True
