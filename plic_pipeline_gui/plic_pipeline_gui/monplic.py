# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

import pymongo


def push_df(df, coll):
    client = pymongo.MongoClient(
        '172.18.0.3',
        27017,
        username="root",
        password="WV_19_Mongo"
    )
    db = client.plic
    for idx, row in df.iterrows():
        db[coll].insert_one(dict(row))
