# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>
from django import forms
from django.forms.widgets import TextInput
from django.core.exceptions import ValidationError


class DatasetImportForm(forms.Form):
    study = forms.ChoiceField(choices=[
        ["milano", "Milano"],
        ["chiesa", "Chiesa in Valmalenco"]
    ])

    dataset = forms.FileField()

    mongo_push = forms.BooleanField(
        label="Push to Mongo",
        initial=True,
        required=False
    )


class UltrasoundDataForm(forms.Form):
    study = forms.ChoiceField(choices=[
        ["val_di_non", "Val di Non"],
        ["chiesa", "Chiesa in Valmalenco"],
    ])

    archive = forms.FileField()

    mongo_push = forms.BooleanField(
        label="Push to Mongo",
        initial=True,
        required=False
    )


    def clean(self):
        if not self.cleaned_data["archive"].temporary_file_path().endswith(".zip"):
            raise ValidationError("Uploaded file is not a zip archive")
        return self.cleaned_data


class PatientQueryForm(forms.Form):
    patient_id = forms.IntegerField(widget=TextInput(attrs=dict(size=10)))
