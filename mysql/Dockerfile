FROM mysql:5.7

MAINTAINER Michael Chong <wildcat.name@gmail.com>

RUN { \
    echo '[mysqld]'; \
    echo 'character-set-client-handshake = FALSE'; \
    echo 'character-set-server = utf8'; \
    echo 'collation-server = utf8_unicode_ci'; \
    echo 'key-buffer-size = 32M'; \
    echo 'tmp-table-size = 32M'; \
    echo 'max-heap-table-size = 32M'; \
    echo 'innodb_buffer_pool_size=5M'; \
    echo 'innodb_log_buffer_size=256K'; \
    echo 'max_connections=10'; \
    echo 'innodb_ft_cache_size=1600000'; \
    echo 'innodb_ft_total_cache_size=32000000'; \
    echo '[client]'; \
    echo 'default-character-set=utf8'; \
    echo '[mysql]'; \
    echo 'default-character-set=utf8'; \
} > /etc/mysql/conf.d/charset.cnf