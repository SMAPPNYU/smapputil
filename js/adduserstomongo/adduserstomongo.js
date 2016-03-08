var expandHomeDir = require('expand-home-dir')
var mongo = require('./adduserstomongofuncs')
var config = require('./adduserstomongoconfig')
var bunyan = require('bunyan')
var touch = require('touch')
var co = require('co')

const logfile = expandHomeDir('~/jslogs/adduserstomongo-' + new Date())
touch.sync(logfile) //create a file for logging
var log = bunyan.createLogger({name: 'adduserstomongo', streams: [{level: 'info', path: logfile}]})

co(function * () {
    for (var i = config.addtodbs.length; i--;) {
        var dbname = config.addtodbs[i]
        log.info('trying to connect to: ' + dbname)
        // connect to mongo on the right database as a readWrite
        var db = yield mongo.connect(config.mongo.mongoanydb + dbname)
        log.info('connected to mongo' + db)
        // create the new users on that database
        for (var j = config.addusers.length; j--;) {
            var user = config.addusers[j]
            log.info({msg: 'trying to create users'}, user)
            var newuser = yield mongo.adduser(db, user)
        }
        log.info('closing db connection')
        db.close()
    }
}).catch(function (err) {
    log.info(err)
    console.log(err)
    process.exit(1)
})