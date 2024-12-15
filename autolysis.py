# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///
import os
import sys
import csv
import pathlib as pl
import logging as lg

import requests

# Define helper functions
def read_aiproxy_token() -> str | None:
    """
        * Read aiproxy token from environment variable
        * returns aiproxy token as a string
    """
    try:
        if (token := os.getenv("AIPROXY_TOKEN")):
            return token
        else:
            raise Exception("AIPROXY_TOKEN not found!")
    except Exception as e:
        lg.error(e)

def get_absolute_base_path() -> pl.Path:
    """
        * returns pathlib.Path object pointing to current directory
    """
    return pl.Path(__file__).parent.absolute()


# Main Analysiser class definition

class Analyser():
    def __init__(self, file_path: str):
        _fp = open(file_path, "r")
        self._csv_reader = csv.reader(_fp)
        self._base_path = get_absolute_base_path()

    def classify_attributes(self) -> dict[str, [str]]:
        """
            * Classifies each data column as numerical or categorical
            * returns a dictionary mapping each column as NUMERICAL or CATEGORICAL
        """
        labelled_attributes = {"Numerical":[], "Categorical":[]}
        headers = []
        for row in self._csv_reader:
            # exclude the header row 
            if self._csv_reader.line_num == 1:
                headers = row
            else:
                for column, data in enumerate(row):
                    if str(data).isdecimal() or str(data).isnumeric():
                        labelled_attributes["Numerical"]\
                                            .append(headers[column])
                    else:
                        labelled_attributes["Categorical"]\
                                            .append(headers[column])
                break
        return labelled_attributes

with open("README.md", "w") as fp:
    pass

with open("one.png", "w") as fp:
    pass

with open("two.png", "w") as fp:
    pass

analyser = Analyser(sys.argv[1])
attributes = analyser.classify_attributes()
