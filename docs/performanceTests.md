# K6 Testing Framework

This project uses K6 for performance and load testing.

## Quick Start

Run tests using Docker Compose:
```bash
docker-compose -f docker-compose.k6.yml up
```

The Docker setup handles all K6 dependencies automatically.

## Project Structure

- **Test files**: Place your K6 test scripts in `./k6/tests/`
- **Results**: Test outputs are saved to `./k6/results/`
- **Dataset**: Test data should be placed in `./k6/data`. See `./k6/data/README.md` for initialization instructions.

## Configuration

By default, the docker compose command will run all .js files in `./k6/tests/`, but you can send more arguments to the docker command (in the docker-compose file or when using docker run) to specify the file that you want to run.
