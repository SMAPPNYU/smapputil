#!/bin/bash

echo "Setting up config servers..."

# setup config servers
mkdir -p ~/testshard/configdata0/configdb ~/testshard/configdata1/configdb ~/testshard/configdata2/configdb
mongod --configsvr --dbpath ~/testshard/configdata0/configdb/ --port 27024 --keyFile ~/testshard/keyfiles/mongodb-keyfile &
mongod --configsvr --dbpath ~/testshard/configdata1/configdb/ --port 27025 --keyFile ~/testshard/keyfiles/mongodb-keyfile &
mongod --configsvr --dbpath ~/testshard/configdata2/configdb/ --port 27026 --keyFile ~/testshard/keyfiles/mongodb-keyfile &

sleep 5

echo "Finished setting up config servers!"

echo "Setting up mongos instance..."

mongos --configdb localhost:27024,localhost:27025,localhost:27026 --port 49999 --keyFile ~/testshard/keyfiles/mongodb-keyfile &

sleep 5

mongo localhost:49999 --eval "JSON.stringify(sh._adminCommand({addShard:'rs0/localhost:27018'}, true))"
mongo localhost:49999 --eval "JSON.stringify(sh._adminCommand({addShard:'rs1/localhost:27021'}, true))"
mongo localhost:49999 --eval "JSON.stringify(sh._adminCommand({enableSharding: 'test'}))"
mongo localhost:49999/admin --eval "JSON.stringify(db.createUser({user:'testuser', pwd:'testpassword', roles:[{role:'root', db:'admin'}]}))"

echo "Finished sertting up mongos instance!"

echo "Script going to sleep forever now..."

sleep infinity
