FROM mysql:5.7

MAINTAINER Michael Chong <wildcat.name@gmail.com>

RUN { \
    echo '[mysqld]'; \
    echo 'character-set-client-handshake = FALSE'; \
    echo 'character-set-server = utf8'; \
    echo 'collation-server = utf8_unicode_ci'; \
    echo '[client]'; \
    echo 'default-character-set=utf8'; \
    echo '[mysql]'; \
    echo 'default-character-set=utf8'; \
} > /etc/mysql/conf.d/charset.cnf