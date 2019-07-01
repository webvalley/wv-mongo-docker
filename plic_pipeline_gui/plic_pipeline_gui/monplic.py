# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

import pymongo


def push_df(df, coll):
    client = MongoClient(
        '127.0.0.1',
        27017,
        username="root",
        password="testpw"
    )
    db = client.plic
    for idx, row in df.iterrows():
     db[coll].insert_one(dict(row))
