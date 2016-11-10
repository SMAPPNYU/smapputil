# makes an sqlite db for use with json1 extension
sqlite testingjson.db "SELECT load_extension('/Users/yvanscher/smappwork/sqlite_testing/json1'); insert into testtable (id, json_field) values (1, json('{\"test\":\"dacmd\"}'));"
sqlite testingjson.db "SELECT load_extension('json1'); insert into testtable (id, json_field) values (1, json('{\"test\":\"dacmd2\"}'));"
sqlite testingjson.db "select * from testtable;"
# https://mailliststock.wordpress.com/2007/03/01/sqlite-examples-with-bash-perl-and-python/