import json
import os
from typing import Callable


def test(
	directory: str,
	json_path: str,
	out_path: str,
	func: Callable,
	**kwargs
) -> None:
	data = {}
	json_data = {}
	accuracies = {}
	filenames = [elem for elem in os.listdir(directory)]
	for filename in filenames:
		path = os.path.join(directory, filename)
		res1, res2 = func(stream=path, **kwargs)
		data[filename] = {"in": res1, "out": res2}
		break
	with open(json_path, "r", encoding="utf-8") as json_file:
		json_data = json.load(json_file)
	for filename in json_data:
		true_in = json_data[filename].get("in", 0)
		true_out = json_data[filename].get("out", 0)
		pred_in = data.get(filename, {}).get("in", 0)
		pred_out = data.get(filename, {}).get("out", 0)
		try:
			acc_in = round(1 - abs(pred_in-true_in)/true_in, 2)
		except ZeroDivisionError:
			if not pred_in:
				acc_in = 1.0
			else:
				acc_in = 0.0
		try:
			acc_out = round(1 - abs(pred_out-true_out)/true_out, 2)
		except ZeroDivisionError:
			if not pred_out:
				acc_out = 1.0
			else:
				acc_out = 0.0
		accuracies[filename] = {"in": acc_in, "out": acc_out}
	with open(out_path, "w", encoding="utf-8") as out_file:
		json.dump(accuracies, out_file, indent=4)
	return


if __name__ == "__main__":
	from main import main
	directory = "test_set"
	json_path = "test_data.json"
	out_path = "accuracy.json"
	weights = "models/model_2023-12-11.pt"
	test(directory, json_path, out_path, main, weights=weights)