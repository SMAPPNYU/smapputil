var config = require('./smapputilitiesconfig')
var Promise = require('bluebird')
var co = require('co')

// convert mongodb to make useable with promises
var mongodb = Promise.promisifyAll(require('mongodb'))
var mongoclient = Promise.promisifyAll(mongodb.MongoClient)

// function that lets us connect to mongo
var connect = co.wrap(function * (mongouri) {
    return yield mongoclient.connectAsync(mongouri)
})

var adduser = co.wrap(function * (db, user) {
    return yield db.addUser(user.name, user.pass, {roles: user.roles})
})

var authenticateuser = co.wrap(function * (db, user) {
    return yield db.authenticate(user.name, user.pass)
})

var removeuser = co.wrap(function * (db, user) {
    return yield db.removeUser(user.name)
})

module.exports = {
    authenticateuser: authenticateuser,
    removeuser: removeuser,
    connect: connect,
    adduser: adduser
}
