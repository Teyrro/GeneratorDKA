import sys
from dataclasses import dataclass

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt, QObject, pyqtSignal, QThread, QFile, QTextStream
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLineEdit,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
)

from AddWidget import create_line
from CheckChains import CheckChains
from GraphView import GraphView
from InputView import InputView
from TableView import TableView
from models.dka import DKA
from models.DataFrameModel import DataFrameModel


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.thread = None
        self.check_chains = None
        self.table_view = None
        self.input: InputView | None = None
        self.graph_view: GraphView | None = None
        self.dka_model = DKA(self)
        self.dka_model.setObjectName("DKA")

        self.setMinimumSize(QSize(800, 500))
        lay = QHBoxLayout()
        lay.addWidget(self.create_header())

        vbox = QVBoxLayout()
        tabs = QTabWidget()
        tabs.addTab(self.create_graph(), "Graph")
        tabs.addTab(self.create_table(), "Table")
        tabs.addTab(self.create_check_chains(), "Chains")
        vbox.addWidget(tabs)

        check_info = QLabel("Input data is empty")
        check_info.setAlignment(Qt.AlignmentFlag.AlignLeft)

        check_info.setObjectName("info")
        vbox.addWidget(check_info)

        self.chain_line: QLineEdit = QLineEdit()
        form = QFormLayout()
        create_line(form, self.chain_line, "chain", "Your chain", r"\w+", False)
        vbox.addLayout(form)

        button = QPushButton("Check Chain")
        button.setObjectName("check")
        button.clicked.connect(self.check_chain)
        vbox.addWidget(button)
        lay.addLayout(vbox)

        button: QPushButton = self.input.findChild(QPushButton, "setup")
        button.clicked.connect(self.run_long_task)

        self.setLayout(lay)

    @QtCore.pyqtSlot()
    def check_chain(self):
        info: QLabel = self.findChild(QLabel, "info")
        if self.dka_model.dt is None:
            text = "I guess, you should generate DKA before click this button"
            info.setStyleSheet("color: red")
            info.setText(text)
            return

        self.check_chains.set_dka(self.dka_model)
        text, color = self.check_chains.get_info(self.chain_line.text())
        info.setStyleSheet(color)
        info.setText(text)

    def create_check_chains(self):
        self.check_chains = CheckChains()
        self.check_chains.setObjectName("check_chains")
        return self.check_chains

    def create_table(self, connect_button=None):
        table = TableView(self)
        table.setObjectName("tableView")
        self.table_view = table
        return self.table_view

    def create_graph(self):
        self.graph_view = GraphView(self)
        self.graph_view.setObjectName("graph_view")
        return self.graph_view

    def create_header(self):
        self.input = InputView(self)
        self.input.setObjectName("header")
        return self.input

    @QtCore.pyqtSlot()
    def fill_info_to_dka(self):
        symb: QLineEdit = self.input.findChild(QLineEdit, "symb")
        subchain: QLineEdit = self.input.findChild(QLineEdit, "subchain")
        mult: QLineEdit = self.input.findChild(QLineEdit, "mult")
        if self.input.check_input(symb.text(), mult.text()):
            return
        self.dka_model.set_info(symb.text(), subchain.text(), mult.text())
        self.dka_model.create_dka()
        self.table_view.table_model = DataFrameModel(df=self.dka_model.dt)
        self.table_view.table_view.setModel(self.table_view.table_model)
        self.graph_view.on_button_clicked(self.dka_model)

    def run_long_task(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = self.Worker(self, self.fill_info_to_dka)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()
        button: QPushButton = self.input.findChild(QPushButton, "setup")
        # Final resets
        button.setEnabled(False)
        self.thread.finished.connect(lambda: button.setEnabled(True))

        # info: QLabel = self.input.findChild(QLabel, "log_dka")
        # info.setText("dka generation")
        # self.thread.finished.connect(
        #     lambda: info.setText("")
        # )

    class Worker(QObject):
        def __init__(self, parent=None, func=None):
            super().__init__(parent)
            self.func = func

        dka_model: DKA = None
        graph_view: GraphView = None

        finished = pyqtSignal()

        def run(self):
            self.func()
            self.finished.emit()


@dataclass
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DKA App")
        self.m_Widget = MainWidget()
        self.setCentralWidget(self.m_Widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
