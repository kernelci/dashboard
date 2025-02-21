def pytest_addoption(parser):
    parser.addoption(
        "--run-all", action="store_true", default=False, help="run all test cases"
    )
