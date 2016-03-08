#!/bin/bash

#for guidance check out this gist https://gist.github.com/leetreveil/7233677 by leetreveil

# create a directory if it's not already there, make keyfile inside, make keyfile hav right permission
mkdir -p ~/testshard/keyfiles
openssl rand -base64 741 > ~/testshard/keyfiles/mongodb-keyfile
chmod 600 ~/testshard/keyfiles/mongodb-keyfile

echo "Setting up first replica set..."

# setup first replica set
mkdir -p ~/testshard/srv/mongodb/rs0-0 ~/testshard/srv/mongodb/rs0-1 ~/testshard/srv/mongodb/rs0-2
mongod --dbpath ~/testshard/srv/mongodb/rs0-0 --port 27018 --replSet rs0 --smallfiles --oplogSize 128 --keyFile ~/testshard/keyfiles/mongodb-keyfile &
mongod --dbpath ~/testshard/srv/mongodb/rs0-1 --port 27019 --replSet rs0 --smallfiles --oplogSize 128 --keyFile ~/testshard/keyfiles/mongodb-keyfile &
mongod --dbpath ~/testshard/srv/mongodb/rs0-2 --port 27020 --replSet rs0 --smallfiles --oplogSize 128 --keyFile ~/testshard/keyfiles/mongodb-keyfile &

sleep 5

# create config structure
config="{
    _id:'rs0',
    members: [
        {_id: 0, host: 'localhost:27018'},
        {_id: 1, host: 'localhost:27019'},
        {_id: 2, host: 'localhost:27020'}
    ]
}"

# evaluate the replica set configuration
mongo localhost:27018 --eval "JSON.stringify(db.adminCommand({'replSetInitiate': $config}))"

echo "Finished setting up first replica set!"

echo "Setting up second replica set..."

# setup second replica set
mkdir -p ~/testshard/srv/mongodb/rs1-0 ~/testshard/srv/mongodb/rs1-1 ~/testshard/srv/mongodb/rs1-2
mongod --dbpath ~/testshard/srv/mongodb/rs1-0 --port 27021 --replSet rs1 --smallfiles --oplogSize 128 --keyFile ~/testshard/keyfiles/mongodb-keyfile &
mongod --dbpath ~/testshard/srv/mongodb/rs1-1 --port 27022 --replSet rs1 --smallfiles --oplogSize 128 --keyFile ~/testshard/keyfiles/mongodb-keyfile &
mongod --dbpath ~/testshard/srv/mongodb/rs1-2 --port 27023 --replSet rs1 --smallfiles --oplogSize 128 --keyFile ~/testshard/keyfiles/mongodb-keyfile &

sleep 5

# create config structure
config="{
    _id:'rs1',
    members: [
        {_id: 0, host: 'localhost:27021'},
        {_id: 1, host: 'localhost:27022'},
        {_id: 2, host: 'localhost:27023'}
    ]
}"

# evaluate the replica set configuration
mongo localhost:27021 --eval "JSON.stringify(db.adminCommand({'replSetInitiate': $config}))"

echo "Finished setting up second replica set!"

echo "Script going to sleep forever now..."

#sleep forver now child
sleep infinity
