# K6 Performance Tests Database Setup

## Database Population

> ![NOTE]
> The test database will be used as a connection in the test backend. It should be in the same schema as the models you'll test.
> If you use the `pg_dump` tool you can dump not only the data but also the schema, meaning that no migrations are required.

### Method 1: Using init scripts (Automatic on container startup)

1. Place your SQL dump file as `dump.sql` in this directory
2. The `init-db.sh` script will automatically restore it when the container starts
3. Run: `docker-compose -f docker-compose.k6.yml up`

**Smart Restore**: The script will only restore the database if it's empty (no user tables in the 'public' schema).

This prevents duplicate data insertion on container restarts.

### Method 2: Using psql from host

From outside docker, you can run the following command
```bash
psql -h localhost -p 5436 -U admin -d dashboard < your_dump_file.sql
```

## Database Connection Details

- **Host**: k6-db (within docker network) or localhost (locally)
- **Port**: 5432 (within docker network) or 5436 (locally)
- **Database**: dashboard
- **Username**: admin
- **Password**: admin

## Restore Behavior

- **First run**: Database is empty (0 tables) → Script restores from dump.sql
- **Subsequent runs**: Database has tables → Script skips restoration
- **Force restore**: Delete the volume or run the clean start commands below

## Clean Start

To start with a fresh database:
```bash
docker-compose -f docker-compose.k6.yml down -v
docker-compose -f docker-compose.k6.yml up
```