# WebValley 2019 MongoDB configuration stuff

## Work done by the database team, see [AUTHORS](AUTHORS) file

## License is AGPL v. 3 , see [LICENSE](LICENSE)


#### Privileges separation

The `db-debootstrap.sh` script copies the `db-privileges.sh` to the container
and runs it. That script creates two roles, doctor and researcher, and two
test users, dr\_chierici and beatrice.


The doctor can access the whole `plic` database. The researcher, instead,
can only read the anonimized data.


#### Database dump

To easily backup your Mongo PLIC database you can simply run `db-dump.sh` .
It will generate a directory under /tmp/mongo/plic with the export. You'll
be able to re-import the export with mongorestore.

