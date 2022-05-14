from collections import defaultdict
from dataclasses import dataclass, field
from tkinter.ttk import Treeview
from typing import DefaultDict, Dict


@dataclass
class Node:
    count: int = 0
    sub_nodes: DefaultDict[str, 'Node'] = field(
        default_factory=lambda: defaultdict(Node))

    def build_node(self, label: str, count: int):
        self.count += count
        if not label:
            return
        ind = label.find('/')
        part = label[:ind] if ind > 0 else label
        node = self.sub_nodes[part]
        node.build_node(label[ind + 1:] if ind > 0 else "", count)

    def build_tree(self, tree_view: Treeview, prefix: str = ""):
        for key, node in self.sub_nodes.items():
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
            complete = f"{prefix}/{key}" if prefix else key
            tree_view.insert(
                prefix, 'end', complete, text=key, values=(node.count,), open=len(node.sub_nodes))
            node.build_tree(tree_view, complete)


def build_tree(tree_view: Treeview, labels: list[tuple[str, int]]):
    root = Node()
    for label, count in labels:
        root.build_node(label, count)

    tree_view.delete(*tree_view.get_children())

    root.build_tree(tree_view)
