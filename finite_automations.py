import attr
from collections import defaultdict, deque


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
        for state in self.transition_function.keys():
            for letter in self.sigma:
                state_to = self.transition_function[state][letter]
                print(str(state) + "----" + str(letter) + "--->" + str(state_to))
        print("start_state: " + str(self.start_state))
        print("terminal_states: " + str(self.terminal_states))

    def __init__(self, sigma, start_state=None, terminal_states=None):
        self.sigma = frozenset(sigma)
        self.start_state = start_state
        self.terminal_states = set(terminal_states) if terminal_states else set()

    def accept(self, word) -> bool:
        iterator = self.begin()
        for letter in word:
            iterator = iterator.transition(letter)
        return iterator.is_terminal()

    def add_transition(self, state_from, state_to, letter) -> None:
        raise NotImplementedError

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
                states.update({new_state})
                for state in self.nfa.transition_function[new_state][eps]:
                    if state not in states:
                        state_queue.append(state)
            return frozenset(states)

        def __eq__(self, other):
            return self.nfa == other.nfa and self.states == other.states

    def __init__(self, sigma, start_state=None, terminal_states=None):
        super().__init__(sigma, start_state, terminal_states)
        self.transition_function = defaultdict(lambda: defaultdict(set))

    def add_transition(self, state_from, state_to, letter) -> None:
        assert letter == eps or letter in self.sigma
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

    def __init__(self, sigma, start_state=None, terminal_states=None):
        super().__init__(sigma, start_state, terminal_states)
        self.transition_function = defaultdict(dict)

    def add_transition(self, state_from, state_to, letter) -> None:
        assert letter in self.sigma
        self.transition_function[state_from][letter] = state_to

    def begin(self) -> Iterator:
        return DFA.Iterator(self, self.start_state)

    def renumbered(self):
        mapping = {}
        renumbered_dfa = DFA(self.sigma)
        for idx, state in enumerate(self.transition_function.keys()):
            mapping[state] = idx

        for idx, state in enumerate(self.transition_function.keys()):
            for letter in self.sigma:
                next_state = self.transition_function[state][letter]
                renumbered_dfa.add_transition(idx, mapping[next_state], letter)
        for terminal_state in self.terminal_states:
            renumbered_dfa.terminal_states.update({mapping[terminal_state]})
        renumbered_dfa.start_state = mapping[self.start_state]
        return renumbered_dfa

    @classmethod
    def from_nfa(cls, nfa: NFA):
        dfa = cls(nfa.sigma, start_state=nfa.begin())

        queue = deque({nfa.begin()})
        used_states = {nfa.begin()}
        while len(queue):
            state = queue.popleft()
            if state.is_terminal():
                dfa.terminal_states.add(state)
            for letter in dfa.sigma:
                next_state = state.transition(letter)
                dfa.add_transition(state, next_state, letter)
                if next_state not in used_states:
                    used_states.add(next_state)
                    queue.append(next_state)
        return dfa
