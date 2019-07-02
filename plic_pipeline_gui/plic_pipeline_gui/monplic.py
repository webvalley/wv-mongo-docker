# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

import pymongo
from django.conf import settings


def push_df(df, coll):
    client = pymongo.MongoClient(
        settings.MONGO_IP,
        27017,
        username=settings.MONGO_USER,
        password=settings.MONGO_PW
    )
    db = client.plic
    for idx, row in df.iterrows():
        db[coll].insert_one(dict(row))
    client.close()


def get_collections():
    client = pymongo.MongoClient(
        settings.MONGO_IP,
        27017,
        username=settings.MONGO_USER,
        password=settings.MONGO_PW
    )
    cls = [
        [x, client.plic[x].count()]
        for x in client.plic.list_collection_names() if x != "delete_me"
    ]
    client.close()
    return cls
