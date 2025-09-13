import pytest
from parser.parser import parse_cty_dat

def test_parse_cty_dat():
    pattern_map, exact_map = parse_cty_dat("tests/cty1.dat")
    assert exact_map == {'3A/4Z5KJ/LH': {'Monaco'}}
    assert pattern_map == {'1A': {'Sov Mil Order of Malta'}, '3A': {'Monaco'}}
