from keras.models import load_model
import numpy as np
import skimage
import pydicom
import os


class CustomError(Exception):
    pass


class AxialClassifier:

    def __init__(self, in_dir, out_dir = False):
        self.files_in_dir = in_dir
        self.files_out_dir = out_dir
        self.files_out_new_dirs = []
        self.file_list = [x for x in os.listdir(in_dir) if x.endswith(".dcm")]
        self.x = []
        self.model = None
        self.classified_list = []

    def import_model(self, model_path):
        self.model = load_model(model_path)

    def img_to_array_list(self):
        for filename in self.file_list:
            img = pydicom.dcmread(os.path.join(self.files_in_dir, filename)).pixel_array[:, :, 0]
            im_rez = skimage.transform.resize(img, (256, 256, 1))
            self.x.append(im_rez)
        if len(self.x) > 0:
            self.x = np.array(self.x)
        else:
            raise CustomError(f"No Dicom files in directory: {self.files_in_dir}")

    def classify_axis(self):
        prediction = self.model.predict(self.x)
        view_list = []
        confidence_list = []
        for i in prediction:
            if i[0] >= 0.5:
                view_list.append(1)
            else:
                view_list.append(0)
            confidence_list.append(round(float(i[0]), 2))

        self.classified_list = list(zip(self.file_list, view_list, confidence_list))
        return self.classified_list

    def move_files_to_new_folders(self):
        if not self.files_out_dir:
            self.files_out_dir = self.files_in_dir

        new_folder_appendices = ["/sagittal", "/non_sagittal"]
        self.files_out_new_dirs = [os.path.join(self.files_out_dir + x) for x in new_folder_appendices]

        for nd in self.files_out_new_dirs:
            new_folder = os.path.join(self.files_out_dir, nd)
            if not os.path.exists(new_folder):
                os.makedirs(new_folder)

        for item in self.classified_list:
            if item[1] == 1:
                os.rename(os.path.join(self.files_in_dir, item[0]),
                          os.path.join(self.files_out_new_dirs[0], item[0]))
            else:
                os.rename(os.path.join(self.files_in_dir, item[0]),
                          os.path.join(self.files_out_new_dirs[1], item[0]))


if __name__ == "__main__":
    classifier = AxialClassifier("C:/Users/julix/Documents/temp/chierici eco/dcm/WV_PROVA_3_anonymized")
    classifier.import_model("NN_model/model_even_better.h5")
    classifier.img_to_array_list()
    print(classifier.classify_axis())
    classifier.move_files_to_new_folders()