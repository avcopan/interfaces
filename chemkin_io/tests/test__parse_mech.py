""" test chemkin_io.parser.mechanism
"""

import os
import chemkin_io


def _read_file(file_name):
    with open(file_name, encoding='utf8', errors='ignore') as file_obj:
        file_str = file_obj.read()
    return file_str


# Set paths
PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(PATH, 'data')
HEPTANE_MECH_NAME = 'heptane_mechanism.txt'
SYNGAS_MECH_NAME = 'syngas_mechanism.txt'
FAKE1_MECH_NAME = 'fake_mech1.txt'
FAKE2_MECH_NAME = 'fake_mech2.txt'
HEPTANE_CSV_NAME = 'heptane_species.csv'

# Read mechanism and csv files
HEPTANE_MECH_STR = _read_file(
    os.path.join(DATA_PATH, HEPTANE_MECH_NAME))
SYNGAS_MECH_STR = _read_file(
    os.path.join(DATA_PATH, SYNGAS_MECH_NAME))
FAKE1_MECH_STR = _read_file(
    os.path.join(DATA_PATH, FAKE1_MECH_NAME))
FAKE2_MECH_STR = _read_file(
    os.path.join(DATA_PATH, FAKE2_MECH_NAME))
HEPTANE_CSV_STR = _read_file(
    os.path.join(DATA_PATH, HEPTANE_CSV_NAME))


def test__species_block():
    """ test chemkin_io.parser.mechanism.species_block
    """

    mech_str = HEPTANE_MECH_STR
    block_str = chemkin_io.parser.mechanism.species_block(mech_str)
    assert len(block_str.splitlines()) == 278


def test__reaction_block():
    """ test chemkin_io.parser.mechanism.reaction_block
    """

    mech_str = HEPTANE_MECH_STR
    block_str = chemkin_io.parser.mechanism.reaction_block(mech_str)
    assert len(block_str.splitlines()) == 8186


def test__thermo_block():
    """ test chemkin_io.parser.mechanism.thermo_block
    """

    mech_str = SYNGAS_MECH_STR
    block_str = chemkin_io.parser.mechanism.thermo_block(mech_str)
    print(len(block_str.splitlines()))
    assert len(block_str.splitlines()) == 78


def test__reaction_units():
    """ test chemkin_io.parser.mechanism.reaction_units
    """
    units1 = chemkin_io.parser.mechanism.reaction_units(HEPTANE_MECH_STR)
    units2 = chemkin_io.parser.mechanism.reaction_units(SYNGAS_MECH_STR)
    units3 = chemkin_io.parser.mechanism.reaction_units(FAKE1_MECH_STR)
    units4 = chemkin_io.parser.mechanism.reaction_units(FAKE2_MECH_STR)
    assert units1 == ('cal/mole', 'moles')
    assert units2 == ('kcal/mole', 'moles')
    assert units3 == ('cal/mole', 'molecules')
    assert units4 == ('joules/mole', 'moles')


def test__species_name_dct():
    """ test chemkin_io.parser.species_name_dct
    """
    name_inchi_dct = chemkin_io.parser.mechanism.spc_name_dct(
        HEPTANE_CSV_STR, 'inchi')
    for key, val in name_inchi_dct.items():
        print(key)
        print(val)


def test__species_inchi_dct():
    """ test chemkin_io.parser.species_inchi_dct
    """
    inchi_name_dct = chemkin_io.parser.mechanism.spc_inchi_dct(
        HEPTANE_CSV_STR)
    for key, val in inchi_name_dct.items():
        print(key)
        print(val)


if __name__ == '__main__':
    test__species_block()
    test__reaction_block()
    test__thermo_block()
    test__reaction_units()
    test__species_name_dct()
    test__species_inchi_dct()