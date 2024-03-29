# Copyright (c) 2019 Daniel Marcon
# Copyright (c) 2019 Matteo Zigante
# Copyright (c) 2019 Pietro Moretto
# The code was adapted to django by
# Copyright (c) 2019 Julian Modanese <01modjul@rgtfo-me.it>

import os
import re
import pydicom


class CustomError(Exception):
    pass


def metacrop2(file):
    value = getattr(file, "SequenceOfUltrasoundRegions")[0]

    x0, x1, y0, y1 = None, None, None, None

    for key in value.dir():

        if key == "RegionLocationMinX0":
            x0 = getattr(value, key, "")

        if key == "RegionLocationMaxX1":
            x1 = getattr(value, key, "")

        if key == "RegionLocationMinY0":
            y0 = getattr(value, key, "")

        if key == "RegionLocationMaxY1":
            y1 = getattr(value, key, "")

    return file.pixel_array[y0:y1 + 1, x0:x1 + 1]


def person_names_callback(dataset, data_element):
    if data_element.VR == "PN":
        data_element.value = "anonymous"


def curves_callback(dataset, data_element):
    if data_element.tag.group & 0xFF00 == 0x5000:
        del dataset[data_element.tag]


def anonymize(root, root_out=False):

    # image expected dimensions
    rows = 576
    cols = 640

    if not root_out:
        root_out = root

    fileslist = [x for x in os.listdir(root) if x.endswith(".dcm")]
    outdirs = set()

    for file in fileslist:
        t2tag = 'PatientBirthDate'
        fn = os.path.join(root, file)
        ds = pydicom.read_file(fn)

        if ds.Manufacturer != "SAMSUNG MEDISON CO., LTD." or ds.ManufacturerModelName != "HM70A":
            raise CustomError(
             f"File '{file}' was created by unsupported machine model: {ds.Manufacturer} - {ds.ManufacturerModelName}")

        if ds.Rows == rows and ds.Columns == cols:

            # clear private data

            ds.walk(person_names_callback)
            ds.walk(curves_callback)

            # address/sanitize patient IDs (remove spaces and non alphanum characters)

            pid = re.sub("\s+", "_", ds.data_element('PatientID').value.strip().replace("PLICC", "PLIC"))
            ds.data_element('PatientID').value = re.sub(r'\W+', '', pid)

            # type 2 tags

            if t2tag in ds:
                ds.data_element(t2tag).value = ''

            patientID = ds.PatientID
            dicom_name = os.path.basename(fn).strip().replace(" ", "_")

            # throw away image header with private data

            pdata = metacrop2(ds)
            ds.Rows, ds.Columns, _ = pdata.shape
            ds.PixelData = pdata.tobytes()
            new_raw_path = os.path.join(root, str(patientID) + "_raw")
            os.makedirs(new_raw_path, exist_ok=True)
            os.rename(os.path.join(root, file), os.path.join(new_raw_path, file))
            out_dir = os.path.join(root_out, str(patientID) + "_anonymized")
            outdirs.add(out_dir)
            dicom_name = (str(patientID))
            os.makedirs(out_dir, exist_ok=True)
            out_dicom = \
                os.path.join(out_dir, dicom_name + \
                             f"_{str(len([x for x in os.listdir(out_dir) if x.endswith('.dcm')])).zfill(4)}" + ".dcm")

            # write DICOM Standard compliant file

            if not os.path.isfile(out_dicom):
                pydicom.filewriter.write_file(out_dicom, ds, write_like_original=False)

    return len(fileslist), outdirs


if __name__ == "__main__":
    anonymize("C:/Users/julix/Documents/temp/chierici eco/dcm")

# TODO get a demo selection of images to use, and prepare them by blurring sensitive data/inserting false names
# TODO check difference between Chiesa/Milano/Val di Non images, decide accordingly
