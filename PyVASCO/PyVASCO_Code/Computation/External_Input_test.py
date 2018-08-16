from __future__ import division

from pytest import mark

from External_Input import External_Ph_Flux

@mark.parametrize("length array ph".split(), [
    ((3,0.01,0.99,2,3.99,0.01), (1,2,3,4,5,6,7,8,9,10),(5,4,3,25,3,7,5,6,5,12)),
	((3,0.01,0.99,2,3.99,0.01), (1,2,3,4,5,6,7,8,9,10),(5,4,3,25,3,7,5,6,5,12))
])
def test_eval(length, array, ph):
	ph_per_segment = External_Ph_Flux(length, (array, ph))
	assert ph_per_segment[0]  ==  4
	assert ph_per_segment[1]  ==  3
	assert ph_per_segment[2]  ==  25
	assert ph_per_segment[3]  ==  5
	assert ph_per_segment[4]  ==  16/3
	assert ph_per_segment[5]  ==  12
	assert len(length) == 6 
	assert len(array)  == 10
	assert len(ph) == 10