class Component():
    def operation(self):
        pass

class Leaf(Component):
    def operation(self):
        return 'Leaf'
    
class Composite(Component):
    def __init__(self):
        self._children = []

    def add(self, child):
        self._children.append(child)
        return self
    
    def operation(self):
        return f"Composite({', '.join([child.operation() for child in self._children])})"
    
if __name__ == '__main__':
    root = Composite()\
        .add(Composite())\
            .add(Leaf())\
            .add(Composite()\
                .add(Leaf())\
                .add(Leaf()))\
        .add(Leaf())
    print(root.operation())  # Composite(Composite(Leaf, Composite(Leaf, Leaf)), Leaf)