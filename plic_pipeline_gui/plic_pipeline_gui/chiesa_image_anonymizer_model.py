import os
import numpy as np
import pydicom
from keras.models import load_model, model_from_json
import re



class CustomError(Exception):
    pass


class ChiesaImageAnonymizerModel:

    def __init__(self, root, root_out=None):
        np.random.seed(42)
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        self.model = self.load_model()
        self.folder = root
        self.out_folder = root_out
        self.x_ts = []
        self.dimension = (576, 640, 1)
        self.prediction = None
        self.files_list = []

    def load_model(self):
        json_file = open('NN_model/model_struct.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights("NN_model/model_weights.h5")
        return model

    def load_images(self):
        self.x_ts = []
        self.imgs = []
        self.files_list = [x for x in os.listdir(self.folder) if x.endswith(".dcm")]

        for filename in self.files_list:
            file = pydicom.read_file(os.path.join(self.folder, filename))
            pixels = file.pixel_array
            if file.pixel_array[:, :, :1].shape == self.dimension:
                self.x_ts.append(pixels[:, :, :1])
                self.imgs.append(pixels)
        if len(self.x_ts) > 0:
            self.x_ts = np.array(self.x_ts)
        else:
            raise CustomError(f"No Dicom files in directory: {self.folder}")


    def predict(self):
        self.prediction = self.model.predict(self.x_ts, batch_size=2)

    def apply_mask(self, img, mask):
        assert img[:, :, :1].shape == mask.shape
        img = img.astype(np.uint8, casting='unsafe')
        mask[mask <= 0.38] = 0
        mask[mask > 0.38] = 1
        mask = mask.astype(np.uint8, casting='unsafe')
        for i in range(img.shape[-1]):
            # img[..., i] /= 255
            img[..., i] *= mask[..., 0]
        return img

    def person_names_callback(self, dataset, data_element):
        if data_element.VR == "PN":
            data_element.value = "anonymous"

    def curves_callback(self, dataset, data_element):
        if data_element.tag.group & 0xFF00 == 0x5000:
            del dataset[data_element.tag]

    def anonymize(self):
        self.load_model()
        self.load_images()
        self.predict()

        if not self.out_folder:
            self.out_folder = self.folder

        masked_imgs = []
        for i, mask in enumerate(self.prediction):
            masked_imgs.append(self.apply_mask(self.imgs[i], mask))

        t2tag = 'PatientBirthDate'
        outdirs = set()

        for file, pixel_array in zip(self.files_list, masked_imgs):

            fn = os.path.join(self.folder, file)

            ds = pydicom.read_file(os.path.join(self.folder, file))
            if ds.Manufacturer != "SAMSUNG MEDISON CO., LTD." or ds.ManufacturerModelName != "HM70A":
                raise CustomError(
                    f"File '{file}' was created by unsupported machine model: {ds.Manufacturer} - {ds.ManufacturerModelName}")

            if ds.Rows == self.dimension[0] and ds.Columns == self.dimension[1]:

                ds.walk(self.person_names_callback)
                ds.walk(self.curves_callback)

                pid = re.sub("\s+", "_", ds.data_element('PatientID').value.strip().replace("PLICC", "PLIC"))
                ds.data_element('PatientID').value = re.sub(r'\W+', '', pid)

                if t2tag in ds:
                    ds.data_element(t2tag).value = ''
                patientID = ds.PatientID
                dicom_name = os.path.basename(fn).strip().replace(" ", "_")

                ds.PixelData = pixel_array.tobytes()

                new_raw_path = os.path.join(self.folder, str(patientID) + "_raw")

                os.makedirs(new_raw_path, exist_ok=True)
                os.rename(os.path.join(self.folder, file), os.path.join(new_raw_path, file))
                out_dir = os.path.join(self.out_folder, str(patientID) + "_anonymized")
                outdirs.add(out_dir)
                dicom_name = (str(patientID))
                os.makedirs(out_dir, exist_ok=True)
                out_dicom = \
                    os.path.join(out_dir, dicom_name + \
                                 f"_{str(len([x for x in os.listdir(out_dir) if x.endswith('.dcm')])).zfill(4)}" + ".dcm")

                if not os.path.isfile(out_dicom):
                    pydicom.filewriter.write_file(out_dicom, ds, write_like_original=False)

        return len(self.files_list), outdirs


if __name__ == "__main__":
    anonymizer = ChiesaImageAnonymizerModel("C:/Users/julix/Documents/temp/chierici eco/dcm")
    anonymizer.anonymize()