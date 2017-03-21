{
    mongo: {
        mongotest:  'mongodb://smapptest:9saturnex)zuranus9%40persesn@localhost:27017/test',
        mongoanydb: 'mongodb://smapp_readOnly_Db:winter!is*coming^ppams@localhost:27017/',
        existingtestuser: {
            name:'USER_ON_TEST_DB', 
            pass:'PASSWORD'
        }
    },
    addusers: [
        {name: 'USER_NAME', pass: 'PASS_WORD', roles:['read']},
        {name: 'USER_NAME', pass: 'PASS_WORD', roles: ['readWrite']},
    ]
    dbs: [
    'DB_NAME_ONE'
    'DB_NAME_TWO'
    .
    .
    .
    'DB_NAME_THIRTY'
    'DB_NAME_THIRTYONE'
    'DB_NAME_THIRTYTWO'
    ]
}