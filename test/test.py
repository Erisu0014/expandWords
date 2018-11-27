from expand.Node import Node

if __name__ == '__main__':
    nodes = set()
    node = Node('cookiezi')
    node2 = Node('angelsim')
    node3 = Node('hvick')
    nodes_input = set()
    nodes_input.add(node2)
    nodes_input.add(node3)
    node.inputMap['svg'] = nodes_input
    print(node.inputMap['svg'])
    for input in node.inputMap['svg']:
        print(input.word)
    node4 = Node('erisu')
    node.input_update('svg', node4)
    for input in node.inputMap['svg']:
        print(input.word)
    node5 = Node('siwu')
    node.input_update('qwq', node5)
    for input in node.inputMap['qwq']:
        print(input.word)