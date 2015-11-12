[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8
collation-server = utf8_unicode_ci

key-buffer-size = 32M
tmp-table-size = 32M
max-heap-table-size = 32M

# INNODB #
innodb-flush-method            = O_DIRECT
innodb-log-files-in-group      = 2
innodb-log-file-size           = 64M
innodb-flush-log-at-trx-commit = 1
innodb-file-per-table          = 1
innodb-buffer-pool-size        = 32M
[client]
default-character-set=utf8
[mysql]
default-character-set=utf8