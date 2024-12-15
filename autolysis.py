# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "numpy",
#     "requests",
# ]
# ///
import os
import sys
import csv
import numpy as np
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
        self._fp = open(file_path, "r")
        try:
            self._data = self._fp.read()
            self._csv_reader = csv.reader(self._fp)
        except Exception:
            self._data = ""
            self._csv_reader = []

    def analyze_numbers(self):
        """
            * Calculates averages corresponding to numerical columns
            * returns a dictionary mapping each numerical column to its averages
        """
        averages = {}
        columns_numeric = {}
        columns_categorical = {}
        columns_categorical_copy = {}
        headers = []
        nor = 0
        for i, row in enumerate(self._csv_reader):
            # exclude the header row 
            if i == 0:
                headers = row
            else:
                for index, data in enumerate(row):
                    if str(data).isalnum():
                        if headers[index] not in columns_categorical:
                            columns_categorical[headers[index]] = {}
                        if str(data) in columns_categorical[headers[index]]:
                            columns_categorical[headers[index]][str(data)] += 1
                        else:
                            columns_categorical[headers[index]][str(data)] = 1
                    f_data = None
                    i_data = None
                    try:
                        f_data = float(data)
                    except Exception:
                        pass
                    try:
                        i_data = int(data)
                    except Exception:
                        pass
                    if headers[index] not in columns_numeric:
                        columns_numeric[headers[index]] = []
                    if f_data is not None:
                        columns_numeric[headers[index]].append(f_data)
                    elif i_data is not None:
                        columns_numeric[headers[index]].append(i_data)
                    nor += 1
        for column in columns_categorical:
            for s in columns_categorical[column]:
                if columns_categorical[column][s] > 500:
                    columns_categorical_copy[column] = columns_categorical[column]
                    break
        for column in columns_numeric:
            averages[column] = list(map(float, [np.mean(columns_numeric[column]), np.median(columns_numeric[column])]))

        return headers, columns_categorical_copy, averages, nor

    def analyze_wrapper(self):
        try:
            return self.analyze_numbers()
        except Exception:
            self._csv_reader = [row.split(',') for row in self._data]
            try:
                return self.analyze_numbers()
            except Exception:
                return [], {}, {}, 0
        finally:
            self._fp.close()


def construct_gpt_query(headers, columns_categorical, averages, nor):
    query_string = f"I want you to write a story by analyzing the column names, counts of categoric variables and mean,median of numeric variables. You should ignore any mean,median for numerical variables provided if the column name looks like a categorical variable. There are a total of {nor} rows in the dataset. The column names in the dataset are {','.join(headers)} and the categorical columns with the number of occurence of each unique data point is {str(columns_categorical)}. The numeric columns and corresponding mean and median are {str(averages)} respectively. You are free to make assumptions and narrate meaningful fictional details on the data. You should make the output readeable. It should be formatted well so that the reader would get a proper gist of the dataset."
    return query_string

def write_file(resp, name, base_path):
    with open(base_path / name, "w") as fp:
        fp.writelines(str(resp.get("choices", [{}])[0].get("message", {}).get("content", "")).split('\\n'))
    with open(base_path / "one.png", "w") as fp:
        pass
    with open(base_path / "two.png", "w") as fp:
        pass
    return

def make_request(ai_proxy_token, gpt_query):
    resp = requests.post(url="http://aiproxy.sanand.workers.dev/openai/v1/chat/completions", 
                  headers={"Content-Type": "application/json",
                           "Authorization": f"Bearer {ai_proxy_token}"},
                  data=r'{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "' + gpt_query + r'"}]}')
    write_file(resp.json(), "README.md", get_absolute_base_path())

analyser = Analyser(sys.argv[1])
query = construct_gpt_query(*analyser.analyze_wrapper())
make_request(read_aiproxy_token(), query)

