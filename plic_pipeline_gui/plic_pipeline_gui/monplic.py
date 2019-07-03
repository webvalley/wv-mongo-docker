# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

import pymongo
from django.conf import settings


def get_client():
    return pymongo.MongoClient(
        settings.MONGO_IP,
        27017,
        username=settings.MONGO_USER,
        password=settings.MONGO_PW
    )


def fix_chiesa(pat):
    if pat["esa_obi:pas_sx"] and pat["esa_obi:pas_sx"] != -1:
        pat["esa_obi:sbp"] = pat["esa_obi:pas_sx"]
    elif pat["esa_obi:pas_dx"] and pat["esa_obi:pas_dx"] != -1:
        pat["esa_obi:sbp"] = pat["esa_obi:pas_dx"]
    else:
        return None
    if pat["ana_fis:complete_smoke_CHIESA"] == 1:
        pat["ana_fis:smoking"] = "no"
    else:
        pat["ana_fis:smoking"] = "yes"
    return pat


def push_df(df, coll):
    client = get_client()
    db = client.plic
    for idx, row in df.iterrows():
        a = dict(row)
        a["patient_id"] = idx
        if "cod_pz:subject_id" in row:
            a["patient_id"] = a["cod_pz:subject_id"]
            del a["cod_pz:subject_id"]
        if coll == "chiesa":
            a = fix_chiesa(a)
        if a:
            db[coll].insert_one(a)
    client.close()


def get_collections():
    client = get_client()
    cls = [
        [x, client.plic[x].count()]
        for x in client.plic.list_collection_names() if x != "delete_me"
    ]
    client.close()
    return cls
