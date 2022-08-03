from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import DefaultDict, Dict
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView


@dataclass
class Node:
    count: int = 0
    vtime: datetime = datetime(1970, 1, 1)
    sub_nodes: DefaultDict[str, 'Node'] = field(
        default_factory=lambda: defaultdict(Node))

    def build_node(self, label: str, count: int, vtime: datetime):
        self.count += count
        self.vtime = max(self.vtime, vtime)
        if not label:
            return
        ind = label.find('/')
        part = label[:ind] if ind > 0 else label
        node = self.sub_nodes[part]
        node.build_node(label[ind + 1:] if ind > 0 else "", count, vtime)

    def build_tree(self, root: QTreeWidget | QTreeWidgetItem, expand: bool):
        items = sorted(self.sub_nodes.items(),
                       key=lambda item: (item[1].vtime, item[1].count), reverse=True)
        for key, node in items:
            item = QTreeWidgetItem(root)
            if len(node.sub_nodes) == 1:
                path = [key]
                while len(node.sub_nodes) == 1:
                    key = list(node.sub_nodes.keys())[0]
                    sub_node = node.sub_nodes[key]
                    if sub_node.count == node.count:
                        path.append(key)
                        node = node.sub_nodes[key]
                    else:
                        break
                key = '/'.join(path)
            item.setText(0, key)
            item.setText(1, str(node.count))
            if node.sub_nodes and expand:
                item.setExpanded(True)
            node.build_tree(item, False)


def build_tree(treeWidget: QTreeWidget, labels: list[tuple[str, int]]):
    root = Node()
    for label, count, vtime in labels:
        root.build_node(label, count, vtime)

    treeWidget.clear()
    treeWidget.header().setSectionResizeMode(
        0, QHeaderView.ResizeMode.ResizeToContents)

    root.build_tree(treeWidget, len(root.sub_nodes) < 10)
