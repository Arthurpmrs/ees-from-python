import os
import re
import csv


def cleanup_csv(csv_filepath):
    """Read EES arrays CSV, cleans it up and saves a new cleaned CSV. Also returns CSV content."""
    regex = re.compile(r"\[.*\]")
    with open(csv_filepath, 'r') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        clean_data = []
        for i, line in enumerate(data):
            if not i:
                clean_line = []
                for item in line[0].split("\t"):
                    new_item = regex.sub("", item)
                    new_item = new_item.replace("'", "")
                    clean_line.append(new_item)
            else:
                clean_line = [item.replace(".", ",") for item in line]

            clean_data.append(clean_line)

    # Write new cleaned up CSV (Excel Ready)
    folderpath = os.path.dirname(csv_filepath)
    clean_csvfilepath = os.path.join(folderpath, "clean_arrays.csv")
    with open(clean_csvfilepath, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=";")
        for line in clean_data:
            csvwriter.writerow(line)

    return clean_data


def get_base_folder(model_path: str) -> str:
    model_filename = os.path.basename(model_path).split(".")[0]
    base_folder = os.path.join(os.path.dirname(model_path), model_filename)

    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    return base_folder


def add_folder(base_folder: str, *folders: str) -> str:
    new_folder = os.path.join(base_folder, *folders)

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    return new_folder


def main():
    base_folder = os.getcwd()
    print(add_folder(base_folder, 'teste', 'test2'))


if __name__ == "__main__":
    main()
