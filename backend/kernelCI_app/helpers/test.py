from kernelCI_app.typeModels.databases import FAIL_STATUS, PASS_STATUS
from kernelCI_app.typeModels.testDetails import PossibleRegressionType


# TODO: create unit tests for this method
def process_test_status_history(
    *, status_history: list[dict]
) -> PossibleRegressionType:
    history_task: PossibleRegressionType
    first_test_flag = True
    status_changed = False

    for test in status_history:
        test_status = test["status"]
        if first_test_flag:
            if test_status == PASS_STATUS:
                history_task = "pass"
                starting_status = PASS_STATUS
                opposite_status = FAIL_STATUS
            elif test_status == FAIL_STATUS:
                history_task = "fail"
                starting_status = FAIL_STATUS
                opposite_status = PASS_STATUS
            else:
                return "unstable"
            first_test_flag = False
            continue

        is_inconclusive = test_status != PASS_STATUS and test_status != FAIL_STATUS

        if test_status == opposite_status:
            status_changed = True
            if history_task == "pass":
                history_task = "fixed"
            elif history_task == "fail":
                history_task = "regression"
        if (status_changed and test_status == starting_status) or is_inconclusive:
            return "unstable"

    return history_task
