from keras.models import load_model
import numpy as np
import skimage
import pydicom
import os


class AxialClassifier:

    def __init__(self, in_dir, out_dir = ""):
        self.files_in_dir = in_dir
        self.files_out_dir = out_dir
        self.file_list = os.listdir(in_dir)
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

        self.x = np.array(self.x)

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


if __name__ == "__main__":
    classifier = AxialClassifier("C:/Users/julix/Documents/temp/chierici eco/anon/WV_PROVA_3")
    classifier.import_model("NN_model/model_even_better.h5")
    classifier.img_to_array_list()
    print(classifier.classify_axis())