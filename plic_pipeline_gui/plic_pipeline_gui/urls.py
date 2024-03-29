"""plic_pipeline_gui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("upload", views.preUpload.as_view(), name="do-upload"),
    path("upload/ajax", views.UploadAjax.as_view(), name="do-ajax-upload"),
    path("anonymize", views.UploadImages.as_view(), name="do-images-upload"),
    path("collection/<str:name>", views.CollectionDetailView.as_view(), name="collection"),
    path("collection/<str:name>/patient/", views.PatientDetailsRedirect.as_view(), name="pat_details_form"),
    path("collection/<str:name>/patient/<int:pat_id>", views.PatientDetailsView.as_view(), name="pat_details"),
    path("imaging/<str:study>/<int:pat_id>/<int:img_id>", views.DisplayDICOM.as_view(), name="dicom-img"),
    path("imaging/<str:study>/<int:pat_id>/<int:img_id>/change",
        views.ChangeDICOMClassification.as_view(),
        name="dicom-img-change-flag"
    ),
]
