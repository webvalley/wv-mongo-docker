# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from django.contrib import messages
from django.http import HttpResponse, StreamingHttpResponse
from django.views.generic import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from shutil import copyfile
from bokeh import embed
from . import forms, pipeline, monplic, somenzi_cazzo


class IndexView(TemplateView):
    template_name = "index.html"
    extra_context = {
        "form_clinical": forms.DatasetImportForm,
        "form_ultrasound": forms.UltrasoundDataForm,
    }

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
        patients = [x for x in client.plic[self.kwargs["name"]].find()]
        divs, scripts = [], []
        for plot in somenzi_cazzo.collection_graphs(patients):
            script, div = embed.components(plot)
            divs.append(div)
            scripts.append(script)
        ctx["scripts"] = scripts
        ctx["divs"] = divs
        ctx["queryform"] = forms.PatientQueryForm
        return ctx


def split_in_category(pat):
    # [n. visit, {cat: {key: value}}]
    out = []
    if "visit:visit" in pat:
        out.append(pat["visit:visit"])
        del pat["visit:visit"]
    else:
        out.append(None)
    cats = {}
    for key in pat:
        if ":" in key and pat[key] != -1:
            cat, prop = key.split(":")
            prop = prop.replace("_", " ")
            if cat not in cats:
                cats[cat] = {}
            cats[cat][prop] = pat[key]
    out.append(cats)
    return out


class PatientDetailsView(FormView):
    template_name = "collection.html"
    form_class = forms.PatientQueryForm
    extra_context = {"queryform": forms.PatientQueryForm}

    def form_valid(self, form):
        self.study = self.kwargs["name"]
        self.client = monplic.get_client()
        q = list(self.client.plic[self.study].find(
            {"patient_id": form.cleaned_data["patient_id"]}
        ))
        if len(q) < 1:
            messages.warning(self.request, "Patient #%s does not exist in %s" % (
                form.cleaned_data["patient_id"], self.study.title()
            ))
            return redirect("collection", name=self.study)
        # We need q to be divided in sections
        not_q = [split_in_category(x) for x in q]
        plot_cols = ["score", "lab:calculated_ldl"] + [
            x for x in q[0] if "imt_cc_average" in x
        ]
        # Max and min for each col in dataset
        axes = {}
        for col in plot_cols:
            vals = [x for x in self.client.plic[self.study].distinct(col) if x > 0]
            axes[col] = [min(vals), max(vals)]
        # They want IMT to have the same scale
        imt = [0, 0]
        for col in [x for x in plot_cols if "imt_cc" in x]:
            if imt[0] > axes[col][0]:
                imt[0] = axes[col][0]
            if imt[1] < axes[col][1]:
                imt[1] = axes[col][1]
        for col in [x for x in plot_cols if "imt_cc" in x]:
            axes[col] = imt
        divs, scripts = [], []
        for plot in somenzi_cazzo.patient_plots(q, plot_cols, axes):
            script, div = embed.components(plot)
            divs.append(div)
            scripts.append(script)
        ctx = self.get_context_data(
            patient_id=form.cleaned_data["patient_id"],
            q=q,
            not_q=not_q,
            divs=divs,
            scripts=scripts,
            plot_cols=plot_cols,
            labels={
                'ana': 'Anagrafica',
                'ana_fis': 'Anamnesi Fisiologica',
                'ana_pat': 'Anamnesi Patologica',
                'ana_far': 'Anamnesi Farmacologica',
                'esa_obi': 'Esame Obiettivo',
                'lab': 'Laboratorio',
                'ult_tsa': 'Ultrasound Tsa',
                'end': 'Endotelio',
                'lun_bod_sca': 'Lunar Body Scan',
                'eco_art': 'Ecodoppler Arti'
            },
            **self.kwargs
        )
        return render(
            self.request,
            "patient_details.html",
            ctx
        )
