import typing


class Node:
    def __call__(self):
        raise NotImplementedError()


class BinaryNode(Node):
    def __init__(self, left: Node, right: Node, func: typing.Callable[[float, float], float]):
        self.left = left
        self.right = right
        self.func = func

    def __call__(self) -> float:
        return self.func(self.left(), self.right())


class UnaryNode(Node):
    def __init__(self, child: Node, func: typing.Callable[[float], float]):
        self.child = child
        self.func = func

    def __call__(self) -> float:
        return self.func(self.child())


class ConstantNode(Node):
    def __init__(self, value: float):
        self.value = value

    def __call__(self) -> float:
        return self.value


class CompareNode(Node):
    def __init__(self, left: Node, right: Node, func: typing.Callable[[float, float], bool]):
        self.left = left
        self.right = right
        self.func = func

    def __call__(self) -> bool:
        return self.func(self.left(), self.right())