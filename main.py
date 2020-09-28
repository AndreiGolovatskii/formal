from finite_automations import NFA, DFA


def main():
    nfa = NFA.from_input()
    DFA.from_nfa(nfa).renumbered().print()


if __name__ == "__main__":
    main()
