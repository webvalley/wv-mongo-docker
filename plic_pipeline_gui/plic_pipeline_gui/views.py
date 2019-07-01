# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from django.views.generic import View
from django.http import HttpResponse, StreamingHttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render
from shutil import copyfile
from . import forms, pipeline


class IndexView(TemplateView):
    template_name = "index.html"
    extra_context = {"form": forms.DatasetImportForm}


class preUpload(FormView):
    template_name = "index.html"
    form_class = forms.DatasetImportForm
    extra_context = {"form": forms.DatasetImportForm}

    def form_valid(self, form):
        print(type(form.cleaned_data["dataset"]))
        # The original tempfile is being deleted when the request finishes
        new_path = "/tmp/keep_%s" % form.cleaned_data["dataset"].temporary_file_path().split("/")[-1]
        copyfile(
            form.cleaned_data["dataset"].temporary_file_path(),
            new_path
        )
        return render(
            self.request,
            "upload-in-progress.html",
            {
                "f": form.cleaned_data,
                "fpath": new_path,
                "separation": pipeline.separation
            }
        )


class UploadAjax(View):
    def post(self, request):
        print(request.POST)
        return StreamingHttpResponse(
            pipeline.trigger(request.POST["filename"], request.POST["study"])
        )
