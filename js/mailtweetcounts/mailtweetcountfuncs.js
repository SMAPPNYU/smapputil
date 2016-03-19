var config = require('./mailtweetconfig')
var mailer = require('nodemailer')
var Promise = require('bluebird')
var co = require('co')

var mongodb = Promise.promisifyAll(require('mongodb'))
var mongoclient = Promise.promisifyAll(mongodb.MongoClient)

// function that lets us connect to mongo
var mongoConnectAsync = co.wrap(function * (mongouri) {
    return yield mongoclient.connectAsync(mongouri)
})

// func that lists dbs
var listDatabases = co.wrap(function * (db) {
    // make an admin usr
    var admindb = db.admin()
    return yield admindb.listDatabases()
})

// func that lists collections
var listCollections = co.wrap(function * (db) {
    return yield db.collections()
})

// func that counts documents in a collection in a db
var countDocs = co.wrap(function * (collection, dateone, datetwo) {
    return yield collection.count({'timestamp': { $gte: dateone, $lt: datetwo }})
})

// compose and send the email
var sendEmail = co.wrap(function * (countstruct, fromemail, toemails) {
    // mail settings for sending email
    // Use Smtp Protocol to send Email
    var smtpTransport = mailer.createTransport("SMTP", {
        service: 'Gmail',
        auth: {
            user: config.mail.gmailuser,
            pass: config.mail.gmaiipass
        }
    })
    var sendMail = Promise.promisify(smtpTransport.sendMail)
    return yield sendMail(produceEmailFromJSON(countstruct, fromemail, toemails)).finally(function () {
            smtpTransport.close()
    })
})

// takes a json object 
// and produces the string we want to send 
// via email
function produceEmailFromJSON (json, fromemail, toemails) {
    // the actual email string to send
    var email = ''
    // for each key in json
    for (key in json) {
        var notweets = true
        var subemail = ''
        var tweetsum = 0
        // if the collection has a non 0 
        // key that we are not ignoring
        for (secondkey in json[key]) {
            if (json[key][secondkey] > 0) {
                notweets = false
                tweetsum += json[key][secondkey]
            }
        }
        subemail += '       tweets:      ' + tweetsum + '<br>\n' + '<br>\n'
        // if a database's latest tweets_*
        // has no tweets add a warning
        if (notweets) {
            email += '<p>' + key + ' <b>WARNING: NO TWEETS</b>' + subemail + '</p>'
        } else {
            email += '<p>' + key + subemail + '</p>'
        }
    }
    // build the email
    // leave text blank
    // we're using html
    return {
        from: fromemail,
        to: toemails,
        subject: 'Daily Tweet Counts',
        text: '',
        html: email
    }   
}

// get today's date

function produceToday () {
    return new Date(new Date().toISOString())
}

// get yesterday's date

function produceYesterday (today) {
    var yesterday = new Date()
    yesterday.setDate(today.getDate() - 1)
    return new Date(yesterday.toISOString())
}

module.exports ={
    produceEmailFromJSON: produceEmailFromJSON,
    mongoConnectAsync: mongoConnectAsync,
    listCollections: listCollections,
    produceYesterday: produceYesterday,
    listDatabases: listDatabases,
    produceToday: produceToday,
    countDocs: countDocs,
    sendEmail: sendEmail
} 