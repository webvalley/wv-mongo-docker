# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from django.views.generic import View
from django.http import HttpResponse, StreamingHttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render
from shutil import copyfile
from bokeh import embed
from . import forms, pipeline, monplic, somenzi_cazzo


class IndexView(TemplateView):
    template_name = "index.html"
    extra_context = {"form": forms.DatasetImportForm}

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["collections"] = monplic.get_collections()
        return ctx


class preUpload(FormView):
    template_name = "index.html"
    form_class = forms.DatasetImportForm
    extra_context = {"form": forms.DatasetImportForm}

    def form_valid(self, form):
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
        return StreamingHttpResponse(
            pipeline.trigger(
                request.POST["filename"],
                request.POST["study"],
                request.POST["push"] == "true" and True or False
            )
        )


class CollectionDetailView(TemplateView):
    template_name = "collection.html"

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        client = monplic.get_client()
        patients = [x for x in client.plic["milano"].find()]
        divs, scripts = [], []
        for plot in somenzi_cazzo.collection_graphs(patients):
            script, div = embed.components(plot)
            divs.append(div)
            scripts.append(script)
        ctx["scripts"] = scripts
        ctx["divs"] = divs
        return ctx
