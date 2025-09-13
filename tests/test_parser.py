import pytest
from parser.parser import parse_cty_dat

def test_parse_cty_dat_1():
    pattern_map, exact_map = parse_cty_dat("tests/cty1.dat")
    assert exact_map == {}
    assert pattern_map == {'1A': {'Sov Mil Order of Malta'}}

def test_parse_cty_dat_2():
    pattern_map, exact_map = parse_cty_dat("tests/cty2.dat")
    assert exact_map == {
          '9M2/PG5M': {'Spratly Islands'},
          '9M4SDX': {'Spratly Islands'},
          '9M4SLL': {'Spratly Islands'},
          '9M6/LA6VM': {'Spratly Islands'},
          '9M6/LA7XK': {'Spratly Islands'},
          '9M6/N1UR': {'Spratly Islands'},
          '9M6/OH2YY': {'Spratly Islands'},
          'DX0JP': {'Spratly Islands'},
          'DX0K': {'Spratly Islands'},
          'DX0NE': {'Spratly Islands'},
          'DX0P': {'Spratly Islands'}}

    assert pattern_map == {
          '9M0':  {'Spratly Islands'},
          'BM9S': {'Spratly Islands'},
          'BN9S': {'Spratly Islands'},
          'BO9S': {'Spratly Islands'},
          'BP9S': {'Spratly Islands'},
          'BQ9S': {'Spratly Islands'},
          'BU9S': {'Spratly Islands'},
          'BV9S': {'Spratly Islands'},
          'BW9S': {'Spratly Islands'},
          'BX9S': {'Spratly Islands'}}
