from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QLineEdit, QSizePolicy


def create_line(
    lay_for_adding,
    line: QLineEdit,
    obj_name: str = None,
    label: str = "i'm label",
    reg_text: str = None,
    is_set_policy=True,
):
    if reg_text == "IntV":
        validator = QIntValidator(0, 10)
        line.setValidator(validator)
    elif not (reg_text is None):
        reg_ex = QRegularExpression(reg_text)
        validator = QRegularExpressionValidator(reg_ex, line)
        line.setValidator(validator)
    if is_set_policy:
        line.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )
    line.setObjectName(obj_name)
    lay_for_adding.addRow(label, line)
