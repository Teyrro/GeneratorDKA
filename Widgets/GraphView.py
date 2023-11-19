from collections import defaultdict, Counter

from IPython.external.qt_for_kernel import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from pyvis.network import Network
import pyvis._version
import networkx as nx

from models.DKA import DKA


class GraphView(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.m_output = QWebEngineView()

        lay = QVBoxLayout(self)
        lay.addWidget(self.m_output)
        self.setLayout(lay)

    @staticmethod
    def generate_graph(dka: DKA, path: str):
        G = nx.MultiDiGraph()
        for i in dka.dt.index:
            G.add_node(i, label=i)

        for i in dka.dt.index:
            for j, m in dka.dt.loc[i].to_dict().items():
                G.add_edge(i, m, label=j, physics=False)
        # for i in dt[:]

        scale = 10
        scale *= dka.dt.size
        pos: dict = nx.circular_layout(G, scale=scale)

        nt = Network(directed=True, bgcolor='#222222', font_color='white')
        nt.options.edges.smooth.type = "curvedCW"
        nt.options.edges.smooth.roundness = 0.4

        nG = nx.MultiDiGraph()
        for i in G.nodes:
            nG.add_node(i,
                        lable=i,
                        shape='circle',
                        color="blue",
                        x=pos[i][0],
                        y=pos[i][1],
                        physics=True,
                        )
        nG.add_node(dka.start_state, color="red")
        nG.add_node(dka.end_state, color="red")
        labels = defaultdict(list)
        columns = {}
        for ind, it in enumerate(dka.dt.columns):
            columns[it] = ind

        for j in dka.dt.index:
            val: dict = dka.dt.loc[j].to_dict()
            states: list = list(val.values())
            count = Counter(states)
            for i in dka.dt.columns:
                state = val[i]
                m_state = count[state]
                if m_state > 1:
                    labels[(j, state)].append(i)
                elif m_state == 1:
                    labels[(j, state)].append(i)

        for i in dka.dt.index:
            for j, m in dka.dt.loc[i].to_dict().items():
                nG.add_edge(i,
                            m,
                            label=",".join(labels[(i, m)]),
                            physics=False,
                            )

        if pyvis._version.__version__ > '0.1.9':
            nt.from_nx(nG, show_edge_weights=False)
        else:
            nt.from_nx(nG)
        nt.show_buttons(filter_=['physics'])
        nt.show_buttons()
        nt.save_graph(path)

    @QtCore.pyqtSlot()
    def on_button_clicked(self, dt: DKA):
        filename = "graph.html"
        path = "Widgets/" + filename
        self.generate_graph(dt, path)
        with open(path, "r") as file:
            html: str = file.read()
        self.m_output.setHtml(html, QUrl(path))

# if __name__ == "__main__":
# import sys
#
# app = QApplication(sys.argv)
# w = GraphView()
# w.show()
#
# sys.exit(app.exec_())
