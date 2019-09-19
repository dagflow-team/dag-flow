#!/usr/bin/env python

from __future__ import print_function
from legs import Legs
from input import Input, Inputs
from output import Output, Outputs

def test_01():
    inputs = Inputs()

    input1 = Input('i1', None)
    input2 = Input('i2', None)
    input3 = Input('i3', None)

    inputs += (input1, input2)
    inputs += input3

    print(inputs)

    print( inputs[0] )
    print( inputs[1] )
    print( inputs[2] )

    try:
        print( inputs[3] )
    except StopIteration:
        pass
    else:
        raise Exception('fail')

    print( inputs['i1'] )
    print( inputs['i2'] )
    print( inputs[('i1', 'i3')] )

    print( inputs.i1 )
    print( inputs.i2 )
    print( inputs.i3 )
    try:
        print( inputs.i4 )
    except KeyError:
        pass

def test_02():
    inputs = Inputs()
    print(inputs)

    output1 = Output('o1', None)

    try:
        inputs += output1
    except Exception:
        pass
    else:
        raise Exception('fail')

def test_03():
    print('test3')
    input1 = Input('i1', None)
    input2 = Input('i2', None)
    input3 = Input('i3', None)

    output1 = Output('o1', None)
    output2 = Output('o2', None)

    legs = Legs( (input1, input2, input3), (output1, output2) )
    print(legs)
    legs.print()
    print()

    legs1 = legs[None,'o1']
    print(legs1)
    # legs1.print()
    print()

    legs2 = legs[:,'o1']
    print(legs2)
    legs2.print()
    print()

    legs3 = legs[('i1', 'i3'),'o1']
    print(legs3)
    legs3.print()
    print()


if __name__ == "__main__":
    test_01()
    print()
    test_02()
    print()
    test_03()
    print()
