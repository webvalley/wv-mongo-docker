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

def push_df(df, coll):
    client = get_client()
    db = client.plic
    for idx, row in df.iterrows():
        a = dict(row)
        a["patient_id"] = idx
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
