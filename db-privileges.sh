#!/bin/bash

mongo --port 27017 -u root -p WV_19_Mongo --authenticationDatabase admin <<EOF
use plic;

db.createRole({
  role: "doctor",
  privileges: [{
    resource: {db: "plic", collection: ""},
    actions: [ "find", "update", "insert", "remove"],
  }],
  roles: []
});

db.createRole({
  role: "researcher",
  privileges: [{
    resource: {db: "plic", collection: "milan"},
    actions: [ "find", "update", "insert", "remove"],
  }],
  roles: []
});

db.createUser({
	user: "dr_chierici",
	pwd: "MarcoIlPianista",
	roles: [{role: "doctor", db: "plic"}]
});

db.createUser({
	user: "beatrice",
	pwd: "Biostatistica",
	roles: [{role: "researcher", db: "plic"}]
});
EOF

