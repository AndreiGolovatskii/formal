from collections import defaultdict, deque

from common import alignment


def build_nodes(fa):
    layers = bfs(fa)
    position = build_nodes_position(layers)
    rows = []
    for states in layers.values():
        for state in states:
            node_type = "state"
            if state == fa.start_state:
                node_type += ",initial"
            if state in fa.terminal_states:
                node_type += ",accepting"
            node_pos = position[state]
            rows.append(
                [
                    "\\node[{}]".format(node_type),
                    "(q_{{{}}})".format(str(state)),
                    "[{}]".format(node_pos),
                    "{" + "$q_{{{}}}$;".format(str(state)) + "};",
                ]
            )

    alignment(rows)
    return "\n".join(map("".join, rows))


def build_nodes_position(layers):
    position = {}
    for layer, nodes in layers.items():
        if layer > 0:
            last_node = layers[layer - 1][0]
            position[nodes[0]] = "below of=q_{{{}}}".format(last_node)
        else:
            position[nodes[0]] = ""
        last_node = nodes[0]
        for node in nodes[1:]:
            position[node] = "right of=q_{{{}}}".format(last_node)
            last_node = node
    return position


def build_edges(fa):
    rows = []
    for state in sorted(fa.states):
        edges_to = defaultdict(list)
        for state_to, letter in fa.get_edges_from(state):
            edges_to[state_to].append(letter)

        for state_to, letters in edges_to.items():
            r1 = "(q_{{{}}})".format(str(state))
            r2 = "edge"
            r3 = "[bend left]" if state_to != state else "[loop above]"
            r4 = "node"
            r5 = "{" + ",".join(sorted(map(str, letters))) + "}"
            r6 = "(q_{{{}}})".format(str(state_to))
            rows.append([r1, r2, r3, r4, r5, r6])

    alignment(rows)
    return "\n".join(map("".join, rows))


def bfs(fa):
    layer = {}
    queue = deque()
    queue.append(fa.start_state)
    layer[fa.start_state] = 0

    layers = defaultdict(list)
    layers[0].append(fa.start_state)

    while len(queue):
        state = queue.pop()
        for next_state, _ in fa.get_edges_from(state):
            if next_state not in layer:
                layer[next_state] = layer[state] + 1
                layers[layer[state] + 1].append(next_state)
                queue.append(next_state)
    return layers


def latex_format(fa):
    nodes = build_nodes(fa)
    edges = build_edges(fa)

    return (
        "\\begin{tikzpicture}[shorten >=1pt,node distance=2cm,on grid,auto]\n"
        + "  \\tikzstyle{every state}=[fill={rgb:black,1;white,10}]\n"
        + nodes
        + "\\path[->]\n"
        + edges
        + " ;\n"
        + "\\end{tikzpicture}\\\\"
    )
