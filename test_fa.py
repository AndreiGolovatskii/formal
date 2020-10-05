from copy import deepcopy

import pytest
from conftest import assert_compare_fa
from finite_automations import DFA, NFA, eps
from latex_format import build_edges, build_nodes


@pytest.fixture
def nfa_ab6():
    auto = NFA("ab")
    auto.set_start_state(0)
    auto.add_transition(0, 1, "a")
    auto.add_transition(1, 1, "b")
    auto.add_transition(1, 2, "a")
    auto.add_transition(2, 4, "a")
    auto.add_transition(4, 2, "b")
    auto.add_transition(2, 3, "a")
    auto.add_transition(3, 5, "a")
    auto.add_transition(5, 3, "b")
    auto.add_transition(3, 1, eps)
    auto.add_terminal_state(1)
    return auto


@pytest.fixture
def dfa_ab6(nfa_ab6):
    return DFA.from_nfa(nfa_ab6)


@pytest.fixture
def nfa_ab6_many_eps():
    """same as above but with a lot of eps"""
    auto = NFA("ab")
    auto.set_start_state(0)
    auto.add_transition(0, 6, eps)
    auto.add_transition(6, 6, eps)
    auto.add_transition(0, 7, eps)
    auto.add_transition(7, 12, eps)
    auto.add_transition(12, 6, eps)
    auto.add_transition(6, 1, "a")
    auto.add_transition(1, 10, eps)
    auto.add_transition(10, 11, "b")
    auto.add_transition(11, 8, eps)
    auto.add_transition(8, 9, eps)
    auto.add_transition(9, 1, eps)
    auto.add_transition(1, 2, "a")
    auto.add_transition(2, 14, eps)
    auto.add_transition(14, 4, "a")
    auto.add_transition(4, 15, "b")
    auto.add_transition(15, 2, eps)
    auto.add_transition(2, 16, eps)
    auto.add_transition(2, 3, "a")
    auto.add_transition(16, 3, "a")
    auto.add_transition(3, 21, eps)
    auto.add_transition(21, 19, eps)
    auto.add_transition(21, 18, eps)
    auto.add_transition(19, 18, eps)
    auto.add_transition(18, 5, "a")
    auto.add_transition(5, 3, "b")
    auto.add_transition(5, 17, eps)
    auto.add_transition(17, 3, "b")
    auto.add_transition(3, 13, eps)
    auto.add_transition(13, 1, eps)
    auto.add_transition(5, 20, eps)
    auto.add_terminal_state(1)
    return auto


@pytest.fixture
def nfa_ab4():
    auto = NFA("ab")
    auto.add_transition(1, 2, "a")
    auto.add_transition(2, 1, "b")
    auto.add_transition(1, 3, "b")
    auto.add_transition(3, 1, "a")
    auto.add_transition(1, 4, "a")
    auto.add_transition(1, 4, "b")
    auto.add_transition(1, 4, eps)
    auto.set_start_state(1)
    auto.add_terminal_state(4)
    return auto


@pytest.fixture
def dfa_ab4(nfa_ab4):
    return DFA.from_nfa(nfa_ab4)


def test_nfa_empty():
    automation = NFA("abc")
    assert type(automation.sigma) is frozenset
    assert type(automation.terminal_states) is set


def test_nfa_transitions():
    automation = NFA("abc")
    automation.start_state = 0
    automation.terminal_states.add(1)
    automation.add_transition(0, 1, "a")
    automation.add_transition(0, 1, "b")
    automation.add_transition(0, 1, "c")
    automation.add_transition(0, 0, "c")

    assert automation.transition_function[0]["a"] == {1}
    assert automation.transition_function[0]["b"] == {1}
    assert automation.transition_function[0]["c"] == {1, 0}


def test_nfa_ab6_transitions(nfa_ab6):
    assert nfa_ab6.transition_function[0]["a"] == {1}
    assert nfa_ab6.transition_function[1]["b"] == {1}
    assert nfa_ab6.terminal_states == {1}


def test_simple_accept(nfa_ab6):
    assert nfa_ab6.accept("a")
    assert nfa_ab6.accept("ab")
    assert nfa_ab6.accept("aaa")
    assert nfa_ab6.accept("aaab")
    assert nfa_ab6.accept("aaabaabb")
    assert nfa_ab6.accept("aaaababbb")
    assert not nfa_ab6.accept("b")
    assert not nfa_ab6.accept("abc")
    assert not nfa_ab6.accept("aaaa")


def test_compare_ab6_ab6_eps(nfa_ab6, nfa_ab6_many_eps):
    assert_compare_fa(nfa_ab6, nfa_ab6_many_eps, 10)


def test_nfa_iterator_hash(nfa_ab6):
    begin_iterator = nfa_ab6.begin()
    mapping = {begin_iterator: "begin_iterator"}
    other_begin_iterator = nfa_ab6.begin()
    assert begin_iterator == other_begin_iterator
    assert mapping[other_begin_iterator] == "begin_iterator"


def test_dfa_from_nfa_simple(nfa_ab6):
    dfa = DFA.from_nfa(nfa_ab6)
    assert dfa.accept("a")
    assert dfa.accept("ab")
    assert dfa.accept("aaa")
    assert dfa.is_full()


def test_compare_nfa_dfa_6(nfa_ab6, dfa_ab6):
    assert dfa_ab6.is_full()
    assert_compare_fa(nfa_ab6, dfa_ab6, 10)


def test_compare_nfa_dfa_4(nfa_ab4, dfa_ab4):
    assert_compare_fa(nfa_ab4, dfa_ab4, 10)


def test_renumbered_dfa(dfa_ab6):
    renum = dfa_ab6.renumbered()
    assert renum.is_full()
    assert_compare_fa(renum, dfa_ab6, 10)


def test_complete_to_full():
    fa = DFA("ab")
    fa.add_transition(0, 1, "a")
    fa.add_transition(1, 1, "b")
    fa.add_state("UNREACHABLE")
    assert not fa.is_full()
    full_fa = fa.completed_to_full()
    assert full_fa.is_full()
    minimized = fa.minimized()
    assert len(minimized.states) < len(fa.states)


def test_dfa_minimization_simple(dfa_ab6):
    dfa = dfa_ab6.renumbered()
    min_dfa = dfa.minimized()
    assert min_dfa.is_full()
    assert min_dfa.accept("a")
    assert min_dfa.accept("ab")
    assert min_dfa.accept("aaa")
    assert len(min_dfa.states) < len(dfa.states)
    assert len(min_dfa.states) == len(min_dfa.minimized().states)


def test_dfa_minimization(dfa_ab6):
    min_dfa = dfa_ab6.renumbered().minimized()
    assert_compare_fa(min_dfa, dfa_ab6, 12)


def test_dfa_reverse(dfa_ab6):
    reversed_dfa = deepcopy(dfa_ab6)
    reversed_dfa.reverse_terminal_states()

    assert reversed_dfa.accept("a") != dfa_ab6.accept("a")
    assert reversed_dfa.accept("aaab") != dfa_ab6.accept("aaab")
    assert reversed_dfa.accept("b") != dfa_ab6.accept("b")


def test_auto_equals(dfa_ab6, dfa_ab4):
    other = dfa_ab6.minimized()
    assert other.is_equal_to(dfa_ab6)
    assert other.find_not_eq_word(dfa_ab4) is not None


def test_pretty_print():
    nfa = NFA("ab")
    nfa.add_transition(0, 1, "a")
    nfa.add_transition(1, 2, "a")
    nfa.add_transition(1, 2, "b")
    nfa.set_start_state(0)
    nfa.add_terminal_state(2)
    nodes_res = (
        "\\node[state,initial]  (q_{0})[]              {$q_{0}$;};\n"
        + "\\node[state]          (q_{1})[below of=q_{0}]{$q_{1}$;};\n"
        + "\\node[state,accepting](q_{2})[below of=q_{1}]{$q_{2}$;};"
    )
    assert build_nodes(nfa) == nodes_res
    edges_res = (
        "(q_{0})edge[bend left]node{a}  (q_{1})\n"
        + "(q_{1})edge[bend left]node{a,b}(q_{2})"
    )
    assert build_edges(nfa) == edges_res
