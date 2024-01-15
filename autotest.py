from itertools import product
import json
import os
from typing import Iterable, List, Tuple

import pandas as pd

from main import main


def make_grid(
    detect_confs: Iterable[float],
    tracker_ages: Iterable[int],
    line_heights: Iterable[int]
) -> Iterable[Tuple[float, int, int]]:
    return product(detect_confs, tracker_ages, line_heights)

def file_to_grid(path: str) -> Iterable[Tuple[float, int, int]]:
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".xlsx"):
        df = pd.read_excel(path)
    else:
        raise ValueError(
            "Invalid path provided. Only .csv and .xlsx files are acceptable."
        )
    detect_confs = df["detect_conf"].astype(float).to_list()
    tracker_ages = df["tracker_max_age"].astype(int).to_list()
    line_heights = df["line_height"].astype(int).to_list()
    return zip(detect_confs, tracker_ages, line_heights)

def run_tests(
    weights: str,
    test_dir: str,
    output_path: str,
    data_path: str,
    params: Iterable[Tuple[float, int, int]],
    *,
    exclude_dirs: List[str]|None = None
) -> None:
    if exclude_dirs is None:
        exclude_dirs = set()
    else:
        exclude_dirs = set(exclude_dirs)
    with open(data_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    true_in = data.get("count_in", 0)
    true_out = data.get("count_out", 0)
    for param_set in params:
        count_in = 0
        count_out = 0
        detect_conf, tracker_max_age, line_height = param_set
        for folder in os.listdir(test_dir):
            if folder in exclude_dirs:
                continue
            directory = os.path.join(test_dir, folder)
            for filename in os.listdir(directory):
                stream = os.path.join(directory, filename)
                kwargs = {
                    "stream": stream,
                    "weights": weights,
                    "detect_conf": detect_conf,
                    "tracker_max_age": tracker_max_age,
                    "line_height": line_height,
                }
                print(f"[INFO]: Starting processing {stream}...")
                cur_in, cur_out = main(**kwargs)
                count_in += cur_in
                count_out += cur_out
        accuracy_in = 1 - abs(count_in-true_in)/true_in
        accuracy_out = 1 - abs(count_out-true_out)/true_out
        results = {
            "detect_conf": detect_conf,
            "tracker_max_age": tracker_max_age,
            "line_height": line_height,
            "count_in": count_in,
            "count_out": count_out,
            "accuracy_in": accuracy_in,
            "accuracy_out": accuracy_out, 
        }
        with open(output_path, "a", encoding="utf-8") as out_file:
            json.dump(results, out_file, indent=4)
            out_file.write(",\n")
        print(f"[INFO]: Accuracy In: {round(accuracy_in, 2)}; Accuracy out: {round(accuracy_out, 2)}")
    return


if __name__ == "__main__":
    # detect_confs = [0.5, 0.55, 0.6]
    # tracker_ages = [10, 15, 30, 60, 120]
    # line_heights = [100, 115, 130, 160, 200]
    weights = "models/model_2023-12-19s.pt"
    test_dir = "testing_video"
    data_path = "autotest/data456.json"
    output_path = "autotest/results456.json"
    params_path = "autotest/params456.csv"
    # params = make_grid(detect_confs, tracker_ages, line_heights)
    exclude_dirs = ["test_set1", "test_set2", "test_set3"]
    params = file_to_grid(params_path)
    run_tests(
        weights,
        test_dir,
        output_path,
        data_path,
        params,
        exclude_dirs=exclude_dirs
    )