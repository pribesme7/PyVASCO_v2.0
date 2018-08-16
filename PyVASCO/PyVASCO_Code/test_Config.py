from Config import Config

def test_constants_Boltzman_constant():
    assert Config.kB < 1.3806488e-23 + 1.e-25
    assert Config.kB > 1.3806488e-23 - 1.e-25

def test_constants_elementary_charge():
    assert Config.e <  1.602176565e-19 + 1.e-23
    assert Config.e >  1.602176565e-19 - 1.e-23

def test_constants_Avogadro():
    assert Config.Avogadro <  6.022140857e-23 + 1.e-25
    assert Config.Avogadro >  6.022140857e-23 - 1.e-25