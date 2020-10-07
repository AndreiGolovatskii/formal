from finite_automations import NFA, DFA
from conftest import assert_compare_fa
from latex_format import latex_format


def main():
    nfa = NFA.from_input()
    print("-----IN-------")
    nfa.print()
    with open("tex.in", "w") as tex_in:
        tex_in.write(latex_format(nfa))

    dfa = DFA.from_nfa(nfa).renumbered().minimized()
    assert_compare_fa(nfa, dfa, 10)  # check on words with len <= 10
    print("-----OUT-------")
    dfa.print()
    with open("tex.out", "w") as out:
        out.write(latex_format(dfa))


if __name__ == "__main__":
    main()
