import pytest
def test_file1_method1():
	x=6
	y=6
	assert x+1 == y,"test failed"
	assert x == y,"test passed"
def test_file1_method2():
	x=5
	y=6
	assert x+1 == y,"test failed" 
