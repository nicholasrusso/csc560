\connect test
select 'drop materialized view ' || string_agg(oid::regclass::text, ', ') from pg_class where relkind = 'm';
