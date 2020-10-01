from collections import defaultdict, deque

import attr


class Eps(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance


eps = Eps()


class FiniteAutomation(object):
    @attr.s(frozen=True)
    class Iterator(object):
        def transition(self, letter):
            raise NotImplementedError

        def is_terminal(self) -> bool:
            raise NotImplementedError

    @classmethod
    def from_input(cls):
        sigma = input("sigma:")
        fa = cls(sigma)
        try:
            while True:
                state_from, state_to, letter = input(
                    "state_from state_to letter(or smth else for end):"
                ).split()
                if letter == "eps":
                    letter = eps
                fa.add_transition(int(state_from), int(state_to), letter)
        except Exception:
            pass
        start_state = input("start_state: ")
        fa.start_state = int(start_state)
        terminal_states = map(int, input("terminal_states: ").split())
        fa.terminal_states = set(terminal_states)
        return fa

    def print(self):
        for state in self.states:
            for letter, state_to in self.transition_function[state].items():
                print(str(state) + "----" + str(letter) + "--->" + str(state_to))
        print("start_state: " + str(self.start_state))
        print("terminal_states: " + str(self.terminal_states))

    def __init__(self, sigma, states=None, start_state=None, terminal_states=None):
        self.sigma = frozenset(sigma)
        self.start_state = start_state
        self.terminal_states = set(terminal_states) if terminal_states else set()
        self.states = set(states) if states is not None else set()

        if start_state is not None:
            self.states.add(start_state)
        self.states.update(self.terminal_states)

    def accept(self, word) -> bool:
        iterator = self.begin()
        for letter in word:
            iterator = iterator.transition(letter)
        return iterator.is_terminal()

    def add_transition(self, state_from, state_to, letter) -> None:
        raise NotImplementedError

    def add_state(self, state):
        self.states.add(state)

    def add_terminal_state(self, state):
        self.add_state(state)
        self.terminal_states.add(state)

    def set_start_state(self, state):
        self.add_state(state)
        self.start_state = state

    def begin(self) -> Iterator:
        raise NotImplementedError


class NFA(FiniteAutomation):
    @attr.s(frozen=True)
    class Iterator(FiniteAutomation.Iterator):
        nfa = attr.ib()
        states = attr.ib()

        def __attrs_post_init__(self):
            object.__setattr__(self, "states", self.eps_closure_(self.states))

        def transition(self, letter):
            new_states = set()
            for state in self.states:
                new_states.update(self.nfa.transition_function[state][letter])
            return NFA.Iterator(self.nfa, new_states)

        def is_terminal(self) -> bool:
            for state in self.states:
                if state in self.nfa.terminal_states:
                    return True
            return False

        def eps_closure_(self, states):
            state_queue = deque(states)
            while len(state_queue):
                new_state = state_queue.popleft()
                states.add(new_state)
                for state in self.nfa.transition_function[new_state][eps]:
                    if state not in states:
                        state_queue.append(state)
            return frozenset(states)

        def __eq__(self, other):
            return self.nfa == other.nfa and self.states == other.states

    def __init__(self, sigma, states=None, start_state=None, terminal_states=None):
        super().__init__(sigma, states, start_state, terminal_states)
        self.transition_function = defaultdict(lambda: defaultdict(set))

    def add_transition(self, state_from, state_to, letter) -> None:
        assert letter == eps or letter in self.sigma
        self.states.add(state_to)
        self.states.add(state_from)
        self.transition_function[state_from][letter].add(state_to)

    def begin(self) -> Iterator:
        return NFA.Iterator(self, {self.start_state})


class DFA(FiniteAutomation):
    @attr.s(frozen=True)
    class Iterator(FiniteAutomation.Iterator):
        dfa = attr.ib()
        current_state = attr.ib()

        def transition(self, letter):
            return DFA.Iterator(
                self.dfa, self.dfa.transition_function[self.current_state][letter]
            )

        def is_terminal(self) -> bool:
            return self.current_state in self.dfa.terminal_states

    def __init__(self, sigma, states=None, start_state=None, terminal_states=None):
        super().__init__(sigma, states, start_state, terminal_states)
        self.transition_function = defaultdict(dict)

    def add_transition(self, state_from, state_to, letter) -> None:
        assert letter in self.sigma
        self.transition_function[state_from][letter] = state_to
        self.states.add(state_to)
        self.states.add(state_from)

    def begin(self) -> Iterator:
        return DFA.Iterator(self, self.start_state)

    def renumbered(self):
        mapping = {}
        renumbered_dfa = DFA(self.sigma)
        for idx, state in enumerate(self.states):
            mapping[state] = idx

        for state in self.states:
            for letter, next_state in self.transition_function[state].items():
                renumbered_dfa.add_transition(
                    mapping[state], mapping[next_state], letter
                )

        for terminal_state in self.terminal_states:
            renumbered_dfa.add_terminal_state(mapping[terminal_state])
        if self.start_state is not None:
            renumbered_dfa.set_start_state(mapping[self.start_state])
        return renumbered_dfa

    def reversed_transition_function_(self):
        tf_reverse = defaultdict(lambda: defaultdict(set))
        for u in self.states:
            for letter, v in self.transition_function[u].items():
                tf_reverse[v][letter].add(u)
        return tf_reverse

    def reachable_states_(self):
        reachables = set()

        def dfs(state):
            if state in reachables:
                return
            reachables.add(state)
            for state_to in self.transition_function[state].values():
                dfs(state_to)

        dfs(self.start_state)
        return reachables

    def table_of_unequal_states_(self):
        queue = deque()
        marked = defaultdict(lambda: defaultdict(lambda: False))
        tf_reverse = self.reversed_transition_function_()

        for i in self.states:
            for j in self.states:
                if (
                    not marked[i][j]
                    and (i in self.terminal_states) != (j in self.terminal_states)
                ):
                    marked[i][j] = marked[j][i] = True
                    queue.append((i, j))

        while len(queue):
            u, v = queue.pop()
            for letter in self.sigma:
                for r in tf_reverse[u][letter]:
                    for s in tf_reverse[v][letter]:
                        if not marked[r][s]:
                            marked[r][s] = marked[s][r] = True
                            queue.append((r, s))
        return marked

    def minimized(self):
        fa = self
        if not self.is_full():
            fa = self.completed_to_full()

        unequal = fa.table_of_unequal_states_()
        reachables = fa.reachable_states_()
        component = {state: None for state in fa.states}

        cnt = 0
        for state in fa.states:
            if state not in reachables:
                continue
            if component[state] is None:
                component[state] = cnt
                cnt += 1
                for diff_state in fa.states:
                    if not unequal[state][diff_state]:
                        component[diff_state] = component[state]
        res = DFA(fa.sigma)
        for state in fa.states:
            for letter, state_to in fa.transition_function[state].items():
                res.add_transition(component[state], component[state_to], letter)
        if fa.start_state is not None:
            res.set_start_state(component[fa.start_state])
        for state in fa.terminal_states:
            res.add_terminal_state(component[state])
        return res

    def completed_to_full(self):
        renumbered = self.renumbered()
        devils_state = -1
        for letter in renumbered.sigma:
            renumbered.add_transition(devils_state, devils_state, letter)
        for state in renumbered.states:
            for sigma in renumbered.sigma:
                if state not in renumbered.transition_function:
                    renumbered.add_transition(state, devils_state, sigma)
                if sigma not in renumbered.transition_function[state]:
                    renumbered.add_transition(state, devils_state, sigma)

        assert renumbered.is_full()
        return renumbered

    def is_full(self):
        for state in self.states:
            for letter in self.sigma:
                if state not in self.transition_function:
                    return False
                if letter not in self.transition_function[state]:
                    return False
                if self.transition_function[state][letter] not in self.states:
                    return False
        return True

    @classmethod
    def from_nfa(cls, nfa: NFA):
        dfa = cls(nfa.sigma, start_state=nfa.begin())

        queue = deque({nfa.begin()})
        used_states = {nfa.begin()}
        while len(queue):
            state = queue.popleft()
            if state.is_terminal():
                dfa.add_terminal_state(state)
            for letter in dfa.sigma:
                next_state = state.transition(letter)
                dfa.add_transition(state, next_state, letter)
                if next_state not in used_states:
                    used_states.add(next_state)
                    queue.append(next_state)
        return dfa
