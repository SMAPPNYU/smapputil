var chai = require('chai')
var expect = chai.expect
var assert = chai.assert
var config = require('../smapputilitiesconfig')
var mongo = require('../adduserstomongofuncs')

require('mocha-generators').install()

describe('adduserstomongo', function () {
    // set a longer timeout for these
    // tests to deal w/ async nature
    this.timeout(15000)

    it('should pass the control test', function * () {
        assert.ok(true)
    })

    it('should connect to mongodb through tunnel', function * () {
        var admindb = yield mongo.connect(config.mongo.mongotest)
        assert.ok(admindb)
        admindb.close()
    })

    it('should properly authenticate a user', function * () {
        // setUp
        var testdb = yield mongo.connect(config.mongo.mongotest)
        // existingtestuser is a per existing ser on your database
        // you'll need one for this test to pass
        var autheduser = yield mongo.authenticateuser(testdb, config.mongo.existingtestuser)
        assert.ok(autheduser)
        testdb.close()
    })

    it('should create a new user on a single database', function * () {
        // setUp
        var testdb = yield mongo.connect(config.mongo.mongotest)
        // test
        var newuser = yield mongo.adduser(testdb, {name:'test_adduserstomongo', pass:'test_adduserstomongo', roles: ['read']})
        assert.ok(newuser)
        var autheduser = yield mongo.authenticateuser(testdb, {name:'test_adduserstomongo', pass:'test_adduserstomongo'})
        assert.ok(autheduser)
        // tearDown
        var removeduser = yield mongo.removeuser(testdb, {name:'test_adduserstomongo', pass:'test_adduserstomongo'})
        assert.ok(removeduser)
        testdb.close()
    })
})


// c* http://jxcore.com/mongodb-2-6-with-jxcorenode-js-creating-admin-regular-users/
