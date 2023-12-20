import os

import pandas as pd


def restructure(folder: str, csv_filename: str = "_classes.csv") -> None:
	csv_path = os.path.join(folder, csv_filename)
	df = pd.read_csv(csv_path)
	for column in df.columns[1:]:
		os.makedirs(os.path.join(folder, column), exist_ok=True)
	for i, row in df.iterrows():
		for column in df.columns[1:]:
			if row[column]:
				os.rename(os.path.join(folder, row.filename), os.path.join(folder, column, row.filename))
				break
	return


if __name__ == "__main__":
	folder = input("Input folder name to restructure: ")
	restructure(folder)