import pytest
import os
import sys


if len(sys.argv) != 2:
    raise Exception("Correct usage: python startTests.py <test_name>")

args = sys.argv[1:]
test_to_run = args[0]

pytest.main([os.getcwd() + f"/tests/{test_to_run}.py", "-s", "-v"])
