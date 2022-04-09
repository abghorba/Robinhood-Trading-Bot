import logging
import pytest
import os
import sys

from datetime import datetime


if len(sys.argv) != 2:
    raise Exception("Correct usage: python startTests.py <test_name>")

args = sys.argv[1:]
test_to_run = args[0]

log_filename = datetime.now().strftime("%d%m%Y%H%M%S") + f"-{test_to_run}"
log_filepath = os.getcwd() + f"/logs/{log_filename}.log"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(module)s.py - %(funcName)s - [%(levelname)s] %(message)s",
                    handlers=[logging.FileHandler(log_filepath),
                                logging.StreamHandler()])

pytest.main([os.getcwd() + f"/tests/{test_to_run}.py", "-v"])
