CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'repl_user';
SELECT pg_create_physical_replication_slot('replication_slot');