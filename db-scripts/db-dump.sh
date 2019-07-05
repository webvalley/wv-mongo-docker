#!/bin/bash

docker exec wv_mongo mongodump --port 27017 -u root -p WV_19_Mongo --db plic --out /tmp/mongo --authenticationDatabase admin
docker cp wv_mongo:/tmp/mongo /tmp
docker exec wv_mongo rm -rf /tmp/mongo
