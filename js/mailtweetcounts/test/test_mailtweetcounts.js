var chai = require('chai')
var expect = chai.expect
var assert = chai.assert
var config = require('../mailtweetconfig')
var funcs = require('../mailtweetcountfuncs')

require('mocha-generators').install()

// these tests require a tunnel or connection
// to hades see docs in README.md

describe('mailtweetcounts', function() {
    // set a longer timeout for these
    // tests to deal w/ async nature
    this.timeout(15000)

    it('should connect to mongodb through tunnel', function * () {
        // throws an error and fails test if fails...
        var admindb = yield funcs.mongoConnectAsync(config.mongo.mongoadmin)
        admindb.close()
    })

    it('should properly list databases', function * () {
        var admindb = yield funcs.mongoConnectAsync(config.mongo.mongoadmin)
        var dbs = yield funcs.listDatabases(admindb)
        expect(dbs.databases).to.be.instanceof(Array)
        expect(dbs.databases.length).to.be.above(0)
        admindb.close()
    })

    it('should list collections from a  database', function * () {
        var admindb = yield funcs.mongoConnectAsync(config.mongo.mongoadmin)
        var dbs = yield funcs.listDatabases(admindb)
        expect(dbs.databases).to.be.instanceof(Array)
        expect(dbs.databases.length).to.be.above(0)
        admindb.close()
        var anydb = yield funcs.mongoConnectAsync(config.mongo.mongoanydb + dbs.databases[0].name)
        var collections = yield funcs.listCollections(anydb)
        expect(collections).to.be.instanceof(Array)
        expect(collections.length).to.be.above(0)
        anydb.close()
    })

    it('should produce today date', function * () {
        var testtoday = funcs.produceToday()
        var actualtoday = new Date()
        expect(testtoday.setHours(0,0,0,0)).to.be.equal(actualtoday.setHours(0,0,0,0))
    })

    it('should produce yesterday date', function * () {
        var today = funcs.produceToday()
        var testyesterday = funcs.produceYesterday(today)
        var actualyesterday =  new Date()
        actualyesterday.setDate(today.getDate() - 1)
        expect(testyesterday.setHours(0,0,0,0)).to.not.be.equal(today.setHours(0,0,0,0))
        expect(testyesterday.setHours(0,0,0,0)).to.be.equal(actualyesterday.setHours(0,0,0,0))
    })

    it('should count documents in a collection', function * () {
        var admindb = yield funcs.mongoConnectAsync(config.mongo.mongoadmin)
        var dbs = yield funcs.listDatabases(admindb)
        expect(dbs.databases).to.be.instanceof(Array)
        expect(dbs.databases.length).to.be.above(0)
        admindb.close()
        var anydb = yield funcs.mongoConnectAsync(config.mongo.mongoanydb + dbs.databases[0].name)
        var collections = yield funcs.listCollections(anydb)
        expect(collections).to.be.instanceof(Array)
        expect(collections.length).to.be.above(0)
        var today = funcs.produceToday()
        var yesterday = funcs.produceYesterday(today)
        var count = yield funcs.countDocs(collections[0], yesterday, today)
        expect(count).to.not.be.equal(null)
        assert.isNumber(count)
        anydb.close()
    })

    it('should produce the right email string from a json struct', function * () {
        var countstruct = {
            'test': {
                'script_testing': 2,
                'testsharding': 1
            }
        }
        var emailobjtest = funcs.produceEmailFromJSON(countstruct, config.mail.gmailuser, config.mail.toemails)
        expect(emailobjtest.html).to.be.equal('<p>test       tweets:      3<br>\n<br>\n</p>')
    })

    // this test will actually send the email and
    // check the resulting response code that returns
    // make sure it's only going to where you want in 
    // your config file
    it('should send email, i mean....yeah...', function * () {
        var countstruct = {
            'test': {
                'script_testing': 2,
                'testsharding': 1
            }
        }
        // send the mail
        var result = yield funcs.sendEmail(countstruct, config.mail.gmailuser, 'yns207@nyu.edu')
        expect(result.message.indexOf('250 2.0.0 OK') > -1).to.be.true
    })
})

// c* http://ricostacruz.com/cheatsheets/chai.html
