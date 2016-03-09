var expandHomeDir = require('expand-home-dir')
var funcs = require('./mailtweetcountfuncs')
var config = require('./mailtweetconfig')
var bunyan = require('bunyan')
var touch = require('touch')
var co = require('co')

const logfile = expandHomeDir('~/jslogs/mailtweetcounts-' + new Date())
touch.sync(logfile) //create a file for logging
var log = bunyan.createLogger({name: 'mailtweetcounts', streams: [{level: 'info', path: logfile}]})

// create an array of dbs to ignore, OWSUsers has no indexes built on it.
var ignorearray = ['admin', 'config', 'test', 'EgyptToleranceUsersNetworks', 'OWSUsers', 'FilterCriteriaAdmin']
// collections that we should ignore in our analysis 
var ignorearraycollections = ['tweets_limits', 'tweets_filter_criteria', 'system.indexes', 'smapp_metadata', 'tweets_deletes']

// co just lets us write async code
// with yield that looks sequential
// you put a generator function inside
// the co statement. each thing after 
// a 'yield' word, is aynchronous

co(function * () {
    // struct for tracking whether collections
    // have what they need to have
    var trackingstruct = {}
    // try to connect and wait for it to happen (what yield does)
    var admindb = yield funcs.mongoConnectAsync(config.mongo.mongoadmin)
    // get a list of ll databases, wait for it to finish
    var dbs = yield funcs.listDatabases(admindb)
    // close the original connection, we need a new one for each db in mongo
    admindb.close()

    // make a connection for each db...
    for (var i = dbs.databases.length; i--;) {
        var singledb = dbs.databases[i]
        log.info('db: ' + singledb.name)
        // only view things that we are not ignoring
        if (ignorearray.indexOf(singledb.name) <= -1) {
            trackingstruct[singledb.name] = {}
            var anydb = yield funcs.mongoConnectAsync(config.mongo.mongoanydb + singledb.name)
            // get collections for each db
            var collectionarray = yield funcs.listCollections(anydb)
            // count the amount of stuff specified by date range here.
            for (var j = collectionarray.length; j--;) {
                var onecollection = collectionarray[j]
                //get just the collection name
                var strpname = onecollection.namespace.replace(/^([^.]*)./,"")
                //if this is a collection we want to not ignore
                if (ignorearraycollections.indexOf(strpname) <= -1) {
                    var today = funcs.produceToday()
                    var yesterday = funcs.produceYesterday(today)
                    trackingstruct[singledb.name][strpname] = yield funcs.countDocs(onecollection, yesterday, today)
                    log.info('collection: ' + strpname + ': ' + trackingstruct[singledb.name][strpname])
                }
            }
            // close individual db connection
            anydb.close()
        }
    }

    // send the mail
    var result = yield funcs.sendEmail(trackingstruct, config.mail.gmailuser, config.mail.toemails)
    log.info("Daily Tweet Counts: " + result.message)

}).catch(function (err) {
    log.info(err)
    console.log(err)
    process.exit(1)
})

// c* http://mongodb.github.io/node-mongodb-native/
// c* http://mongodb.github.io/node-mongodb-native/2.1/api/
// c* http://stackoverflow.com/questions/29118835/mongodb-node-driver-2-0-with-bluebird-2-9-promisification
// c* http://stackoverflow.com/questions/6116474/how-to-find-if-an-array-contains-a-specific-string-in-javascript-jquery
// c* https://spring.io/understanding/javascript-promises
// c* http://alexperry.io/node/2015/03/25/promises-in-node.html
