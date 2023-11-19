import os
from dataclasses import dataclass

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout

from models.DataFrameModel import DataFrameModel


@dataclass
class TableView(QWidget):
    table_model = None

    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.table_view = QTableView()
        lay = QVBoxLayout(self)
        lay.addWidget(self.table_view)
        self.resize(640, 480)

    @QtCore.pyqtSlot()
    def on_button_clicked(self):
        # df = None
        path = os.path.normpath("Widgets/train.csv")
        df = pd.read_csv(path)
        self.table_model = DataFrameModel(df=df)
        self.table_view.setModel(self.table_model)