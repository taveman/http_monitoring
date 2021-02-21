\set  passwd  `echo  "'${MONITORING_USER_PASSWD}'"`
\set  test_passwd  `echo  "'${TEST_DB_PASSWD}'"`

CREATE DATABASE monitoring;
CREATE DATABASE test_monitoring;


\c monitoring;

CREATE USER monitoring_user WITH ENCRYPTED PASSWORD :passwd;
ALTER ROLE monitoring_user SET client_encoding TO 'utf8';
ALTER ROLE monitoring_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE monitoring_user SET timezone TO 'UTC';
ALTER ROLE monitoring_user WITH CREATEDB;
CREATE USER docker;
ALTER USER docker WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE monitoring TO docker;
GRANT ALL PRIVILEGES ON DATABASE monitoring TO monitoring_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO monitoring_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO monitoring_user;

SET ROLE monitoring_user;


\c test_monitoring;

CREATE USER test_monitoring_user WITH ENCRYPTED PASSWORD :test_passwd;
ALTER ROLE test_monitoring_user SET client_encoding TO 'utf8';
ALTER ROLE test_monitoring_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE test_monitoring_user SET timezone TO 'UTC';
ALTER ROLE test_monitoring_user WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE test_monitoring TO test_monitoring_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_monitoring_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test_monitoring_user;

SET ROLE test_monitoring_user;
