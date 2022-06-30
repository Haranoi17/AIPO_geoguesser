import fasttext
from pycountry import languages, countries

import os.path
import urllib.request
import pathlib

class LanguageIdentification:

    def __init__(self, large_model=True):
        self.large_model_url = 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin'
        current_package_path = pathlib.Path(__file__).parent.resolve()
        self.large_model_path = os.path.join(current_package_path, 'lang_model', 'lid.176.bin')
        self.small_model_path = os.path.join(current_package_path, 'lang_model', 'lid.176.ftz')

        # self.small_model_path = pathlib.Path(__file__).parent.resolve() + '/lang_model/lid.176.ftz'
        self.model_path = self.large_model_path if large_model else self.small_model_path

        link = self.large_model_url.strip()
        name = link.rsplit('/', 1)[-1]
        # filename = os.path.join('lang_model', name)
        # print("TEST: ", filename)
        if not os.path.isfile(self.large_model_path):
            print('Downloading fastText model: ' + self.large_model_path)
            try:
                urllib.request.urlretrieve(link, self.large_model_path)
            except Exception as inst:
                print(inst)
                print('  Encountered unknown error. Continuing.')
        # silences warnings as the package does not properly use the python 'warnings' package
        # see https://github.com/facebookresearch/fastText/issues/1056
        fasttext.FastText.eprint = lambda *args,**kwargs: None
        self.model = fasttext.load_model(self.model_path)

    def predict_lang(self, text):
        predictions = self.model.predict(text, k=5) # returns top 2 matching languages
        return predictions


    def get_most_acc_iso_country_label(self, predictions):
        iso_country_label = predictions[0][0].split("__label__",1)[1]
        accuracy = predictions[1][0]
        return iso_country_label, accuracy


    def get_most_acc_lang_name(self, predictions):
        iso_country_label = predictions[0][0].split("__label__",1)[1]
        accuracy = predictions[1][0]
        lang_name = languages.get(alpha_2=iso_country_label).name
        return lang_name, accuracy


    def get_country(self, text):
        lang = self.predict_lang(text)
        iso_country_label, accuracy = self.get_most_acc_iso_country_label(lang)
        # language_name = languages.get(alpha_2=iso_country_label).name
        country_name = countries.get(alpha_2=iso_country_label)

        if country_name:
            return country_name.name, iso_country_label, accuracy
        else:
            return None, iso_country_label, accuracy