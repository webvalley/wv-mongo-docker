#!/bin/bash

docker cp db-privileges.sh wv_mongo:/tmp
docker exec wv_mongo /tmp/db-privileges.sh

