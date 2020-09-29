import pytest
from finite_automations import DFA, NFA, eps
from conftest import assert_compare_fa


@pytest.fixture
def nfa_ab6():
    auto = NFA("ab")
    auto.start_state = 0
    auto.add_transition(0, 1, "a")
    auto.add_transition(1, 1, "b")
    auto.add_transition(1, 2, "a")
    auto.add_transition(2, 4, "a")
    auto.add_transition(4, 2, "b")
    auto.add_transition(2, 3, "a")
    auto.add_transition(3, 5, "a")
    auto.add_transition(5, 3, "b")
    auto.add_transition(3, 1, eps)
    auto.terminal_states.add(1)
    return auto


@pytest.fixture
def nfa_ab6_many_eps():
    """same as above but with a lot of eps"""
    auto = NFA("ab")
    auto.start_state = 0
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
    auto.terminal_states.add(1)
    return auto


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


def test_compare_nfa_dfa(nfa_ab6):
    dfa = DFA.from_nfa(nfa_ab6)
    assert_compare_fa(nfa_ab6, dfa, 10)


def test_renumered_dfa(nfa_ab6):
    renum = DFA.from_nfa(nfa_ab6).renumbered()
    assert_compare_fa(renum, nfa_ab6, 10)
