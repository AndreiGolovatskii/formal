from finite_automations import NFA, DFA
from conftest import assert_compare_fa


def main():
    nfa = NFA.from_input()
    dfa = DFA.from_nfa(nfa).renumbered()
    assert_compare_fa(nfa, dfa, 10)  # check on words with len <= 10
    dfa.print()


if __name__ == "__main__":
    main()
