import os
from zipfile import ZipFile
from tqdm import tqdm

types_to_zip = ["rgb", "semseg"]

base_path = "_out/sequences/08_24_13_30_13"
folders = os.listdir(base_path)
paths_to_zip = []
for img_type in types_to_zip:
    for i, folder in enumerate(folders):
        imgs = os.listdir(f"{base_path}/{folder}/{img_type}/")
        for img in imgs:
            paths_to_zip.append(f"{base_path}/{folder}/{img_type}/{img}")
        if i == 0:
            paths_to_zip.append(f"{base_path}/{folder}/camera.txt")
            paths_to_zip.append(f"{base_path}/{folder}/focal.txt")


length = len(paths_to_zip)


with ZipFile('_out/full_longpath_extra_rgb_semseg.zip', "w") as zip_object:
    for path_to_zip in tqdm(paths_to_zip):
        zip_object.write(path_to_zip)

