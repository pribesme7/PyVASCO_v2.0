from pytest import mark

from dataDensity import DensityClass

density_data = (""" H2
                    CH4
                    CO
                    CO2
                    result""".split(), 
                (
    ([1, 3, 5, 4],
     [1, 2, 3, 4],
     [5, 4, 3, 25],
     [7, 4, 3, 25],
     [14, 13, 14, 58]),
    ([1, 3, 5, 4, 34, 1],
     [1, 2, 3, 4, 24, 2],
     [5, 4, 3, 25, 3, 6],
     [7, 4, 3, 25, 11, 13],
     [14, 13, 14, 58, 72, 22])))

@mark.parametrize(*density_data)
def test_total_density(H2, CH4, CO, CO2, result):
    length = len(H2)
    x = range(length)
    Density = DensityClass(x, H2, CH4, CO, CO2)
    total = Density.total()
    assert len(total) == length
    for i in range(length):
        assert total[i] == result[i]