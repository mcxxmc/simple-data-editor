# 一个容量默认为5的stack，用来处理DataEditor的撤销和重做两个功能
from typing import List, Optional, Type

class Stack:

    class Node:

        def __init__(self, name: str, op: str, content: str, next: Optional) -> None:
            """
            name对应词条名，op对应执行过的操作， content对应可能的文本，next对应下一个Node
            :param name: str
            :param op: str
            :param content: str
            :param next: None or Node
            """
            self.name = name
            self.op = op
            self.content = content
            self.next = next

    def __init__(self, maxNodeNumber: int =5) -> None:
        """
        initialize stack
        :param maxNodeNumber: int (>= 1)
        """
        if maxNodeNumber <= 0:
            print("Invalid stack volume!")

        self.maxNodeNumber = maxNodeNumber
        self.totalNodeNumber = 0
        self.startNode = None

    def get(self, i: int) -> Optional[Node]:
        """
        获得第i个Node（i=1，2，3...），i不可大于self.totalNodeNumber；返回一个指向该Node的指针
        :param i: int
        :return: Node or None
        """
        if i == 1:
            return self.startNode
        elif i > self.totalNodeNumber:
            return None
        else:
            pointer = self.startNode
            for n in range(i-1):
                pointer = pointer.next
            return pointer

    def pop(self) -> Optional[Node]:
        """
        放出stack的最上面的node（即最新的那个），作为返回值；注：可能在stack未满时就有pop操作，因此使用totalNodeNumber而非maxNodeNumber
        :return: Node or None
        """
        if self.totalNodeNumber is 0:
            return None
        elif self.totalNodeNumber is 1:
            poped = self.startNode
            self.startNode = None
            return poped

        poped = self.startNode
        self.startNode = self.startNode.next
        self.totalNodeNumber -= 1
        return poped

    def push(self, name: str, op: str, content: str) -> None:
        """
        将一个新的Node加入其中；如果Node总数将大于最大值，则删除最后一个Node； 没有返回值。
        :param name: str
        :param op: str
        :param content: str
        :return: None
        """
        if self.totalNodeNumber == self.maxNodeNumber:
            newEnd = self.get(self.maxNodeNumber - 1)
            newEnd.next = None
            n = Stack.Node(name, op, content, self.startNode)
            self.startNode = n

        else:
            n = Stack.Node(name, op, content, self.startNode)
            self.startNode = n
            self.totalNodeNumber += 1

    def clear(self) -> None:
        """
        清空所有内容
        :return: None
        """
        self.totalNodeNumber = 0
        self.startNode = None

    def is_empty(self) -> bool:
        """
        is the stack empty?
        :return: True or False
        """
        if self.startNode is None:
            return True
        else:
            return False
