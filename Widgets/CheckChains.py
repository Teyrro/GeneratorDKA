from dataclasses import dataclass, field

from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout
from models.DKA import DKA


class CheckChains(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dka: DKA | None = None
        self.list: QListWidget = QListWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.list)
        self.setLayout(vbox)

    def set_dka(self, dka_model):
        if self.dka == dka_model:
            return
        self.dka = dka_model

    def get_info(self, chain: str) -> str | tuple[str, str]:
        self.list.clear()
        dt = self.dka.dt
        current_state = self.dka.start_state
        chains: list[str] = []
        for ind, char in enumerate(chain):
            try:
                subchain = f"({current_state},{chain[ind:]})"
                chains.append(subchain)
                current_state = dt.loc[current_state][char]
                item = f"{current_state} {chain[ind:]}"
                self.list.addItem(item)
            except BaseException:
                return (f"current state: {current_state} don't "
                        f"contain transition - ({current_state},{char}) -> ())", "color: red")
        else:
            subchain = f"({current_state},_)"
            chains.append(subchain)
            item = f"{current_state} _"
            self.list.addItem(item)
            self.list.addItem("->".join(chains))
        if current_state != self.dka.end_state:
            return (f"current state {current_state} isn't final, final state: {self.dka.end_state},"
                    f" no transition to next state", "color: red")
        return f"this chain belong to DKA", "color: green"
