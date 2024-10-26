from PyQt5.QtWidgets import (
    QWidget,
    QListWidgetItem,
    QGroupBox,
    QGridLayout,
    QListWidget,
    QPushButton,
)

from ActionViewer import ActionViewer
from Events import NextTurnEvent
from Player import Player
from Transform import Transform
from World import World


class Surroundings(QWidget):
    """周围东西"""

    def __init__(self, player: Player):
        super().__init__()
        self.resize(1000, 618)

        self.player = player
        self.player.installEventFilter(self)

        self.setLayout(QGridLayout())
        self.refresh()

    def refresh(self):
        world: World = self.player.get("/")[0]
        x, y, z = Transform.globalPos(self.player)

        self.setWindowTitle(f"{x},{y},{z}")

        while self.layout().count():
            item = self.layout().takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # 安排删除控件

        i, j = 0, 0
        for vec_id, vec_name, vec in [
            ("northwest", "西北", (-1, 1)),
            ("north", "北", (0, 1)),
            ("northeast", "东北", (1, 1)),
            ("west", "西", (-1, 0)),
            ("center", "中", (0, 0)),
            ("east", "东", (1, 0)),
            ("southwest", "西南", (-1, -1)),
            ("south", "南", (0, -1)),
            ("southeast", "东南", (1, -1)),
        ]:
            groupbox = QGroupBox(self)
            groupbox.setTitle(vec_name)

            listwidget = QListWidget(groupbox)
            for transform in world.get("*", Transform):
                if (
                    transform.x != x + vec[0]
                    or transform.y != y + vec[1]
                    or transform.z != z
                ):
                    continue
                obj = transform.parent()
                if obj == self.player or obj.parent() != world:
                    continue
                listitem = QListWidgetItem()
                viewer = QPushButton()
                viewer.adjustSize()
                viewer.setText(str(obj))
                viewer.clicked.connect(lambda _, o=obj: ActionViewer(o).show())
                listitem.setSizeHint(viewer.size())
                listwidget.addItem(listitem)
                listwidget.setItemWidget(listitem, viewer)

            groupbox.setLayout(QGridLayout())
            groupbox.layout().addWidget(listwidget)

            self.layout().addWidget(groupbox, i, j)
            j += 1
            if j == 3:
                i += 1
                j = 0

    def eventFilter(self, obj, e):
        if isinstance(e, NextTurnEvent):
            self.refresh()
        return super().eventFilter(obj, e)
