""" functions operating on the reactions block string
"""


import itertools
from qcelemental import constants as qcc
import autoparse.pattern as app
import autoparse.find as apf
from autoparse import cast as ap_cast
from chemkin_io.parser import util


# Constants and Conversion factors
# NAVO = qcc.constants.avogadro_constant
NAVO = 6.0221409e+23
CAL2KCAL = qcc.conversion_factor('cal/mol', 'kcal/mol')
J2KCAL = qcc.conversion_factor('J/mol', 'kcal/mol')
KJ2KCAL = qcc.conversion_factor('kJ/mol', 'kcal/mol')
KEL2KCAL = qcc.conversion_factor('kelvin', 'kcal/mol')


# Various strings needed to parse the data sections of the Reaction block
CHEMKIN_ARROW = (app.maybe(app.escape('<')) + app.escape('=') +
                 app.maybe(app.escape('>')))
CHEMKIN_PLUS_EM = app.PLUS + 'M'
CHEMKIN_PAREN_PLUS_EM = app.escape('(') + app.PLUS + 'M' + app.escape(')')

SPECIES_NAME_PATTERN = (
    r'[^\s=+\-]' +
    app.zero_or_more(app.one_of_these(
        [app.LETTER, app.DIGIT, app.escape('(+)'), r'[#,()\-]',
         app.escape('['), app.escape(']')])) +
    app.zero_or_more(app.PLUS)
)
SPECIES_NAMES_PATTERN = app.series(
    app.padded(SPECIES_NAME_PATTERN), app.padded(app.PLUS))

REACTION_PATTERN = (SPECIES_NAMES_PATTERN + app.padded(CHEMKIN_ARROW) +
                    SPECIES_NAMES_PATTERN)
COEFF_PATTERN = (app.NUMBER + app.LINESPACES + app.NUMBER +
                 app.LINESPACES + app.NUMBER)

# Constants
NAVO = 6.02214076e23


# Functions which use thermo parsers to collate the data
def data_block(block_str):
    """ get the reaction data
    """
    rxn_dstr_lst = data_strings(block_str)
    rxn_dat_lst = tuple(zip(
        map(reactant_names, rxn_dstr_lst),
        map(product_names, rxn_dstr_lst),
        map(high_p_parameters, rxn_dstr_lst),
        map(low_p_parameters, rxn_dstr_lst),
        map(troe_parameters, rxn_dstr_lst),
        map(chebyshev_parameters, rxn_dstr_lst),
        map(plog_parameters, rxn_dstr_lst),
        map(buffer_enhance_factors, rxn_dstr_lst)))

    return rxn_dat_lst


def data_dct(block_str, data_entry='strings'):
    """ build a dictionary with the name dictionary
    """
    rxn_dstr_lst = data_strings(block_str)
    if data_entry == 'strings':
        rxn_dct = {}
        for string in rxn_dstr_lst:
            rct_names = reactant_names(string)
            prd_names = product_names(string)
            key = (rct_names, prd_names)
            if key not in rxn_dct:
                rxn_dct[key] = string
            else:
                rxn_dct[key] += '\n'+string
    # elif data_entry == 'block':
    #     rxn_dct = {}
    #     for block in rxn_block_lst:
    #         param_blocks = []
    #         rct_names = rxn_block_lst[0]
    #         prd_names = rxn_block_lst[1]
    #         key = (rct_names, prd_names)
    #         if key not in rxn_dct.keys():
    #             rxn_dct[key] = block[2:]
    #         else:
    #             rxn_dct[key]

    return rxn_dct


# Functions for parsing the reactuins block or single reaction string #
def data_strings(block_str):
    """ reaction strings
    """
    rxn_strs = util.headlined_sections(
        string=block_str.strip(),
        headline_pattern=CHEMKIN_ARROW
    )
    return rxn_strs


def reactant_names(rxn_dstr):
    """ reactant species names
    """
    pattern = _first_line_pattern(
        rct_ptt=app.capturing(SPECIES_NAMES_PATTERN),
        prd_ptt=SPECIES_NAMES_PATTERN,
        coeff_ptt=COEFF_PATTERN
    )
    string = apf.first_capture(pattern, rxn_dstr)
    names = _split_reagent_string(string)
    return names


def product_names(rxn_dstr):
    """ product species names
    """
    pattern = _first_line_pattern(
        rct_ptt=SPECIES_NAMES_PATTERN,
        prd_ptt=app.capturing(SPECIES_NAMES_PATTERN),
        coeff_ptt=COEFF_PATTERN
    )
    string = apf.first_capture(pattern, rxn_dstr)
    names = _split_reagent_string(string)
    return names


def high_p_parameters(rxn_dstr):
    """ high-pressure parameters
    """
    pattern = _first_line_pattern(
        rct_ptt=SPECIES_NAMES_PATTERN,
        prd_ptt=SPECIES_NAMES_PATTERN,
        coeff_ptt=app.capturing(COEFF_PATTERN)
    )
    # params_string = apf.first_capture(pattern, rxn_dstr)
    # if params_string is not None:
    #     params = list(ap_cast(params_string.split()))
    # else:
    #     params = None

    string_lst = apf.all_captures(pattern, rxn_dstr)
    if string_lst:
        params = []
        for string in string_lst:
            params.append(list(ap_cast(string.split())))
    else:
        params = None

    return params


def low_p_parameters(rxn_dstr):
    """ low-pressure parameters
    """
    pattern = (
        'LOW' +
        app.zero_or_more(app.SPACE) + app.escape('/') +
        app.SPACES + app.capturing(app.NUMBER) +
        app.SPACES + app.capturing(app.NUMBER) +
        app.SPACES + app.capturing(app.NUMBER) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )
    cap1 = apf.first_capture(pattern, rxn_dstr)
    if cap1 is not None:
        params = [[float(val) for val in cap1]]
    else:
        params = None
    # string_lst = apf.all_captures(pattern, rxn_dstr)
    # print(string_lst)
    # if string_lst:
    #     params = []
    #     for string in string_lst:
    #         print(string)
    #         params.append(list(ap_cast(string.split())))
    # else:
    #     print('here2')
    #     params = None

    return params


def troe_parameters(rxn_dstr):
    """ troe parameters
    """
    pattern1 = (
        'TROE' +
        app.zero_or_more(app.SPACE) + app.escape('/') +
        app.SPACES + app.capturing(app.NUMBER) +
        app.SPACES + app.capturing(app.NUMBER) +
        app.SPACES + app.capturing(app.NUMBER) +
        app.SPACES + app.maybe(app.capturing(app.NUMBER)) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )
    pattern2 = (
        'TROE' +
        app.zero_or_more(app.SPACE) + app.escape('/') +
        app.SPACES + app.capturing(app.NUMBER) +
        app.SPACES + app.capturing(app.NUMBER) +
        app.SPACES + app.capturing(app.NUMBER) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )
    cap1 = apf.first_capture(pattern1, rxn_dstr)
    cap2 = apf.first_capture(pattern2, rxn_dstr)
    if cap1 is not None:
        params = [float(val) for val in cap1]
    else:
        if cap2 is not None:
            params = [float(val) for val in cap2]
            params.append(None)
        else:
            params = None
    return params


def chebyshev_parameters(rxn_dstr):
    """ chebyshev parameters
    """
    temp_pattern = (
        'TCHEB' + app.zero_or_more(app.SPACE) + app.escape('/') +
        app.SPACES + app.capturing(app.FLOAT) +
        app.SPACES + app.capturing(app.FLOAT) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )
    pressure_pattern = (
        'PCHEB' + app.zero_or_more(app.SPACE) + app.escape('/') +
        app.SPACES + app.capturing(app.FLOAT) +
        app.SPACES + app.capturing(app.FLOAT) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )
    alpha_dimension_pattern = (
        'CHEB' + app.zero_or_more(app.SPACE) + app.escape('/') +
        app.SPACES + app.capturing(app.INTEGER) +
        app.SPACES + app.capturing(app.INTEGER) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )
    alpha_elements_pattern = (
        'CHEB' + app.zero_or_more(app.SPACE) + app.escape('/') +
        app.series(
            app.capturing(app.SPACES + app.capturing(app.EXPONENTIAL_FLOAT)),
            app.SPACES
        ) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )

    cheb_temps = apf.first_capture(temp_pattern, rxn_dstr)
    cheb_pressures = apf.first_capture(pressure_pattern, rxn_dstr)
    alpha_dims = apf.first_capture(alpha_dimension_pattern, rxn_dstr)
    alpha_elm = apf.all_captures(alpha_elements_pattern, rxn_dstr)
    if not alpha_elm:
        alpha_elm = None

    params_dct = {}
    if all(vals is not None
           for vals in (cheb_temps, cheb_pressures, alpha_dims, alpha_elm)):
        params_dct['t_limits'] = [float(val) for val in cheb_temps]
        params_dct['p_limits'] = [float(val) for val in cheb_pressures]
        params_dct['alpha_dim'] = [int(val) for val in alpha_dims]
        params_dct['alpha_elm'] = [list(map(float, row)) for row in alpha_elm]
    else:
        params_dct = None

    return params_dct


def plog_parameters(rxn_dstr):
    """ gets parameters associated with plog strings
    """
    pattern = (
        'PLOG' +
        app.zero_or_more(app.SPACE) + app.escape('/') +
        app.zero_or_more(app.SPACE) + app.capturing(app.NUMBER) +
        app.one_or_more(app.SPACE) + app.capturing(app.NUMBER) +
        app.one_or_more(app.SPACE) + app.capturing(app.NUMBER) +
        app.one_or_more(app.SPACE) + app.capturing(app.NUMBER) +
        app.zero_or_more(app.SPACE) + app.escape('/')
    )
    params_lst = apf.all_captures(pattern, rxn_dstr)

    # Build dictionary of parameters, indexed by parameter
    if params_lst:
        params_dct = {}
        for params in params_lst:
            pressure = float(params[0])
            vals = list(map(float, params[1:]))
            # params_dct[pressure] = vals
            if pressure not in params_dct:
                params_dct[pressure] = [vals]
            else:
                params_dct[pressure].append(vals)
    else:
        params_dct = None

    return params_dct


def buffer_enhance_factors(rxn_dstr):
    """ get the factors of speed-up from bath gas
        function currently only works if factors are
        on line directly after the reaction string
    """

    first_str = _first_line_pattern(
        rct_ptt=SPECIES_NAMES_PATTERN,
        prd_ptt=SPECIES_NAMES_PATTERN,
        coeff_ptt=COEFF_PATTERN)
    bad_strings = ('DUP', 'LOW', 'TROE', 'CHEB', 'PLOG', first_str)

    species_char = app.one_of_these([
        app.LETTER, app.DIGIT,
        app.escape('('), app.escape(')'),
        app.UNDERSCORE])
    species_name = app.one_or_more(species_char)

    # Loop over the lines and search for string with collider facts
    factors = None
    if apf.has_match('LOW', rxn_dstr) or apf.has_match('TROE', rxn_dstr):
        for line in rxn_dstr.splitlines():
            if not any(apf.has_match(string, line) for string in bad_strings):
                factor_pattern = (
                    app.capturing(species_name) +
                    app.escape('/') + app.maybe(app.SPACE) +
                    app.capturing(app.NUMBER) +
                    app.escape('/')
                )
                baths = apf.all_captures(factor_pattern, line)
                if baths:
                    factors = {}
                    for bath in baths:
                        factors[bath[0]] = float(bath[1])

    return factors


def ratek_fit_info(rxn_dstr):
    """ Read the information describing features of the fits to the
        rate constants
    """

    # Read the temperatures and the Errors from the lines
    trange_ptt = (
        'TempRange: ' +
        app.capturing(app.INTEGER) + '-' + app.capturing(app.INTEGER) +
        ' K'
    )
    mean_ptt = (
        'MeanAbsErr:' + app.SPACES +
        app.capturing(app.FLOAT) + app.escape('%') +
        ','
    )
    max_ptt = (
        'MaxErr:' + app.SPACES +
        app.capturing(app.FLOAT) + app.escape('%') +
        ','
    )
    trange_caps = apf.all_captures(trange_ptt, rxn_dstr)
    mean_caps = apf.all_captures(mean_ptt, rxn_dstr)
    max_caps = apf.all_captures(max_ptt, rxn_dstr)

    trange_vals = []
    for cap in trange_caps:
        temp1, temp2 = cap
        trange_vals.apppend(int(temp1), int(temp2))
    if mean_caps is not None:
        mean_vals = [float(val) for val in mean_caps]
    else:
        mean_vals = []
    if max_caps is not None:
        max_vals = [float(val) for val in max_caps]
    else:
        max_vals = []

    # Build the inf_dct
    inf_dct = {}
    for idx, pressure in max_vals: # in enumerate(pressures):
        inf_dct[pressure] = [trange_vals[idx], mean_vals[idx], max_vals[idx]]
    return inf_dct


# helper functions #
def _first_line_pattern(rct_ptt, prd_ptt, coeff_ptt):
    return (rct_ptt + app.padded(CHEMKIN_ARROW) + prd_ptt +
            app.LINESPACES + coeff_ptt)


def _split_reagent_string(rgt_str):

    def _interpret_reagent_count(rgt_cnt_str):
        _pattern = (app.STRING_START + app.capturing(app.maybe(app.DIGIT)) +
                    app.capturing(app.one_or_more(app.NONSPACE)))
        cnt, rgt = apf.first_capture(_pattern, rgt_cnt_str)
        cnt = int(cnt) if cnt else 1
        rgts = (rgt,) * cnt
        return rgts

    rgt_str = apf.remove(app.LINESPACES, rgt_str)
    rgt_str = apf.remove(CHEMKIN_PAREN_PLUS_EM, rgt_str)
    rgt_str = apf.remove(CHEMKIN_PLUS_EM, rgt_str)
    pattern = app.PLUS + app.not_followed_by(app.PLUS)
    rgt_cnt_strs = apf.split(pattern, rgt_str)
    rgts = tuple(itertools.chain(*map(_interpret_reagent_count, rgt_cnt_strs)))

    return rgts
