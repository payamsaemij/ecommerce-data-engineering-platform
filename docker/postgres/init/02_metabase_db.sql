SELECT 'CREATE DATABASE metabase_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database
    WHERE datname = 'metabase_db'
)
\gexec