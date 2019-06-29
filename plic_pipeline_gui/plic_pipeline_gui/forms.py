# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>
from django import forms


class DatasetImportForm(forms.Form):
    study = forms.ChoiceField(choices=[
        ["milano", "Milano"],
        ["chiesa", "Chiesa in Valmalenco"]
    ])

    dataset = forms.FileField()