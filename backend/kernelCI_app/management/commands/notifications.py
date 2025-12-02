from typing import Optional
import jinja2
import json
import os
import sys

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from urllib.parse import quote_plus

from django.core.management.base import BaseCommand

from kernelCI_app.helpers.logger import log_message
from kernelCI_app.helpers.system import get_running_instance

from kernelCI_app.helpers.email import (
    smtp_setup_connection,
    smtp_send_email,
)
from kernelCI_app.helpers.trees import sanitize_tree
from kernelCI_app.management.commands.helpers.common import (
    get_default_tree_recipients,
)
from kernelCI_app.management.commands.helpers.summary import (
    SIGNUP_FOLDER,
    PossibleReportOptions,
    ReportConfigs,
    TreeKey,
    get_build_issues_from_checkout,
    process_submissions_files,
    process_hardware_submissions_files,
)
from kernelCI_app.queries.notifications import (
    get_checkout_summary_data,
    kcidb_new_issues,
    kcidb_issue_details,
    kcidb_build_incidents,
    kcidb_test_incidents,
    kcidb_last_test_without_issue,
    kcidb_tests_results,
)
from kernelCI_app.queries.test import get_test_details_data, get_test_status_history
from kernelCI_cache.queries.notifications import (
    RESEND_INTERVAL,
    check_sent_notifications,
    mark_checkout_notification_as_sent,
    mark_issue_notification_not_sent,
    mark_issue_notification_sent,
)
from kernelCI_app.utils import is_boot
from kernelCI_cache.queries.issues import (
    get_all_issue_keys,
    get_unsent_issues,
)
from kernelCI_cache.typeModels.databases import PossibleIssueType
from kernelCI_app.utils import group_status

from kernelCI_app.queries.hardware import (
    get_hardware_summary_data,
    get_hardware_listing_data_bulk,
)
from kernelCI_app.helpers.hardwares import sanitize_hardware

KERNELCI_RESULTS = "kernelci-results@groups.io"
KERNELCI_REPLYTO = "kernelci@lists.linux.dev"
REGRESSIONS_LIST = "regressions@lists.linux.dev"


def ask_confirmation():
    while True:
        choice = input(">> Do you want to send the email? (y/n): ").strip().lower()
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n'.")


def send_email_report(
    *,
    service,
    report,
    email_args,
    git_url: Optional[str] = None,
    signup_folder: Optional[str] = None,
    recipients: Optional[list[str]] = None,
):
    """Sets up the email arguments and sends the report.

    Params:
        service: the email service used to send the email itself
        report: the dict with information about the report, usually set up with jinja
        email_args: the SimpleNamespace with options for the email sending
        git_url: the git_repository_url of a tree that is used to retrieve the recipients for the email.\n
          Requires signup_folder to be set in order to take effect.
        signup_folder: the folder with the tree submissions files that is used
          to retrieve the recipients for the email.\n
          Is only used if git_url is set and default recipients are not ignored.
        recipients: a direct list of email recipients to use,
          this parameter overrides the use of git_url + signup_folder.
    """
    sender_email = "KernelCI bot <bot@kernelci.org>"
    subject = report["title"]
    message_text = report["content"]

    if not email_args.send:
        print("\n==============================================")
        print("DRY RUN (--send is False)")
        print(f"new report:\n> {subject}")
        print(message_text)
        print("==============================================")
        return None

    cc = ""
    reply_to = None
    if email_args.add_mailing_lists:
        to = KERNELCI_RESULTS
        reply_to = KERNELCI_REPLYTO
    else:
        to = email_args.to

    if not email_args.ignore_recipients:
        if not recipients:
            recipients = get_default_tree_recipients(
                signup_folder=signup_folder,
                search_url=git_url,
            )
        formatted_recipients = ", ".join(recipients) if recipients else ""
        cc = ", ".join([formatted_recipients, cc]) if cc else formatted_recipients

    if email_args.cc:
        cc = ", ".join([email_args.cc, cc]) if cc else email_args.cc

    if (
        email_args.add_mailing_lists
        and email_args.regression_report
        and (email_args.tree_name == "mainline" or email_args.tree_name == "next")
    ):
        cc = ", ".join([REGRESSIONS_LIST, cc]) if cc else REGRESSIONS_LIST

    if not email_args.yes:
        print("===================")
        print(f"Subject: {subject}")
        print(f"To: {to}")
        if cc:
            print(f"Cc: {cc}")
        print(message_text)
        if not ask_confirmation():
            print("Email sending aborted.")
            return None

    print(f"sending {subject}.")

    return smtp_send_email(
        service,
        sender_email,
        to,
        subject,
        message_text,
        cc,
        reply_to,
        email_args.in_reply_to,
    )


def setup_jinja_template(file):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates = os.path.join(base_dir, "templates")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))

    return env.get_template(file)


def exclude_already_found_and_store(issues: list[dict]) -> list[dict]:
    """
    Excludes issues that have already been found and stores the new ones in the database.

    Args:
        issues: A list of dictionaries, where each dictionary represents an issue.

    Returns:
        A list of dictionaries containing only the new issues (those that weren't in the database).
    """

    # Gets only the keys for all existing issues on the db,
    # they are the only necessary data for the following operations
    found_issues_keys = get_all_issue_keys()

    new_issues = []

    for issue in issues:
        issue_id = issue["id"]
        issue_version = issue["version"]

        if (issue_id, issue_version) not in found_issues_keys:
            new_issues.append(issue)
            mark_issue_notification_not_sent(
                issue_id=issue_id,
                issue_version=issue_version,
                issue_type=issue["type"],
            )

    return new_issues


def look_for_new_issues(*, service, signup_folder, email_args):
    if get_running_instance() == "staging":
        print("This command only runs on production or dev environments.")
        return

    issues = kcidb_new_issues()
    build_issues = []
    boot_issues = []
    for issue in issues:
        if issue["build_id"]:
            issue["type"] = "build"
            build_issues.append(issue)
        elif issue["test_id"]:
            issue["type"] = "boot"
            boot_issues.append(issue)

    new_build_issues = exclude_already_found_and_store(build_issues)
    new_boot_issues = exclude_already_found_and_store(boot_issues)
    if not new_build_issues and not new_boot_issues:
        print("No new issues")
        return

    template = setup_jinja_template("issues.txt.j2")
    report = {}
    now = datetime.now(timezone.utc)
    report["content"] = template.render(
        build_issues=new_build_issues, boot_issues=new_boot_issues
    )
    report["title"] = f"new issues summary - {now.strftime("%Y-%m-%d %H:%M %Z")}"

    send_email_report(
        service=service,
        report=report,
        email_args=email_args,
        signup_folder=signup_folder,
    )

    email_args.add_mailing_lists = True
    email_args.update = True
    for issue in new_build_issues:
        if issue["origin"] == "maestro":
            generate_issue_report(
                service=service,
                issue_id=issue["id"],
                email_args=email_args,
                signup_folder=signup_folder,
            )


def ask_ignore_issue():
    while True:
        choice = input(">> Do you want ignore this issue? (y/n): ").strip().lower()
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n'.")


def generate_build_issue_report(issue, incidents):
    template = setup_jinja_template("issue_build.txt.j2")
    report = {}
    report["content"] = template.render(issue=issue, builds=incidents)
    snippet = (
        issue["comment"]
        if len(issue["comment"]) <= 70
        else issue["comment"][:67] + "..."
    )
    report["title"] = (
        f"[REGRESSION] {issue["tree_name"]}/{issue["git_repository_branch"]}: (build){snippet}"
    )
    return report


def generate_boot_issue_report(issue, incidents):
    template = setup_jinja_template("issue_boot.txt.j2")
    report = {}
    report["content"] = template.render(issue=issue, boots=incidents)
    snippet = (
        issue["comment"]
        if len(issue["comment"]) <= 70
        else issue["comment"][:67] + "..."
    )
    report["title"] = (
        f"[REGRESSION] {issue["tree_name"]}/{issue["git_repository_branch"]}: (boot){snippet}"
    )
    return report


def generate_issue_report(
    *,
    service,
    issue_id,
    email_args,
    ask_ignore=False,
    signup_folder,
):
    result = kcidb_issue_details(issue_id)
    if not result:
        print("issue not found!")
        sys.exit(-1)

    issue = result[0]
    issue_version = issue["version"]
    timestamp = issue["_timestamp"]
    comment = issue["comment"]
    issue_tree_name = issue["tree_name"]

    print("=====================")
    print(f"# {issue_tree_name}/{issue["git_repository_branch"]} - {timestamp}")
    print(f"  comment: {comment}")
    print(f"  dashboard: https://d.kernelci.org/issue/{issue_id}")

    if ask_ignore and ask_ignore_issue():
        mark_issue_notification_not_sent(
            issue_id=issue_id,
            issue_version=issue_version,
            issue_type=None,
        )
        return

    if isinstance(issue["misc"], str):
        issue["misc"] = json.loads(issue["misc"])

    issue_type: PossibleIssueType
    if issue["build_id"]:
        issue_type = "build"
        incidents = kcidb_build_incidents(issue_id)
        report = generate_build_issue_report(issue, incidents)
    elif issue["test_id"]:
        incidents = kcidb_test_incidents(issue_id)
        issue_type = "boot" if is_boot(path=incidents[0]["path"]) else "test"
        for incident in incidents:
            last_test = kcidb_last_test_without_issue(issue, incident)
            incident["last_pass"] = last_test[0]["start_time"]
            incident["last_pass_commit"] = last_test[0]["git_commit_hash"]
            incident["last_pass_id"] = last_test[0]["id"]
        report = generate_boot_issue_report(issue, incidents)
    else:
        print(f"unable to generate issue report for {issue_id}", file=sys.stderr)
        sys.exit(-1)

    email_args.tree_name = issue_tree_name
    email_args.regression_report = True
    msg_id = send_email_report(
        service=service,
        report=report,
        email_args=email_args,
        signup_folder=signup_folder,
        git_url=issue["git_repository_url"],
    )

    if msg_id and email_args.update:
        mark_issue_notification_sent(
            msg_id=msg_id,
            issue_id=issue_id,
            issue_version=issue_version,
            issue_type=issue_type,
        )


# TODO: Unify with process_test_status_history
def categorize_test_history(test_group):
    first_test_flag = True
    status_changed = False

    for test in test_group:
        test_status = test["status"]
        if first_test_flag:
            if test_status == "PASS":
                history_task = "pass"
                starting_status = "PASS"
                opposite_status = "FAIL"
            elif test_status == "FAIL":
                history_task = "fail"
                starting_status = "FAIL"
                opposite_status = "PASS"
            else:
                return "unstable"
            first_test_flag = False
            continue

        is_inconclusive = test_status != "PASS" and test_status != "FAIL"

        if test_status == opposite_status:
            status_changed = True
            if history_task == "pass":
                history_task = "fixed"
            elif history_task == "fail":
                history_task = "regression"
        if (status_changed and test_status == starting_status) or is_inconclusive:
            return "unstable"

    return history_task


def evaluate_test_results(
    *,
    origin: str,
    giturl: str,
    branch: str,
    commit_hash: str,
    path: list[str],
    interval: str,
    group_size: int,
):
    tests = kcidb_tests_results(
        origin=origin,
        giturl=giturl,
        branch=branch,
        hash=commit_hash,
        paths=path,
        interval=interval,
        group_size=group_size,
    )

    # Group by platform, then by config_name, then by arch/compiler, then by path
    grouped = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )
    new_issues = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )
    fixed_issues = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )
    unstable_tests = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )

    for test in tests:
        platform = test.get("platform", "unknown platform")
        config_name = test.get("config_name", "unknown config")
        arch = test.get("architecture", "unknown architecture")
        compiler = test.get("compiler", "unknown compiler")
        grouped[platform][config_name][f"{arch}/{compiler}"][test["path"]].append(test)

    for platform, configs in grouped.items():
        for config_name, arch_compilers in configs.items():
            for arch_compiler, paths in arch_compilers.items():
                for path, test_group in paths.items():
                    unique_statuses = {t["status"] for t in test_group}
                    if len(unique_statuses) == 1:
                        continue

                    category = categorize_test_history(test_group)

                    if category == "regression":
                        new_issues[platform][config_name][arch_compiler][
                            path
                        ] = test_group
                    elif category == "fixed":
                        fixed_issues[platform][config_name][arch_compiler][
                            path
                        ] = test_group
                    else:
                        unstable_tests[platform][config_name][arch_compiler][
                            path
                        ] = test_group

    return new_issues, fixed_issues, unstable_tests


def process_submission_options(
    *,
    default_recipients: list[str],
    specific_recipients: list[str],
    options: list[PossibleReportOptions],
) -> list[str]:
    recipients = default_recipients + specific_recipients

    if "ignore_default_recipients" in options:
        recipients = specific_recipients

    return recipients


def discard_sent_reports(
    tree_key_set: set[TreeKey],
    tree_prop_map: dict[TreeKey, ReportConfigs],
    skip_sent_reports: bool,
) -> tuple[set[TreeKey], dict[TreeKey, ReportConfigs]]:
    if skip_sent_reports:
        return tree_key_set, tree_prop_map

    key_set_copy = tree_key_set.copy()
    prop_map_copy = tree_prop_map.copy()

    already_sent_report_checkouts = check_sent_notifications(prop_map_copy)
    for sent_checkout in already_sent_report_checkouts:
        key_set_copy.discard(sent_checkout)
        prop_map_copy.pop(sent_checkout, None)
    print(
        "Discarded %d reports already sent in the past %s"
        % (len(already_sent_report_checkouts), RESEND_INTERVAL)
    )

    return key_set_copy, prop_map_copy


# TODO: lower the complexity of this function, we are at the limit
def run_checkout_summary(
    *,
    service,
    signup_folder: Optional[str] = None,
    summary_origins: Optional[list[str]],
    email_args,
    skip_sent_reports: bool = True,
):
    if get_running_instance() == "staging":
        print("This command only runs on production or dev environments.")
        return

    tree_key_set, tree_prop_map = process_submissions_files(
        signup_folder=signup_folder,
        summary_origins=summary_origins,
    )

    tree_key_set, tree_prop_map = discard_sent_reports(
        tree_key_set=tree_key_set,
        tree_prop_map=tree_prop_map,
        skip_sent_reports=skip_sent_reports,
    )

    records = get_checkout_summary_data(tuple_params=list(tree_key_set))

    if not records:
        print("No data retrived for summary")
        return

    checkout_ids = [record["checkout_id"] for record in records]

    checkout_build_issues, _ = get_build_issues_from_checkout(checkout_ids=checkout_ids)

    for record in records:
        checkout = sanitize_tree(record)
        build_issues = checkout_build_issues[checkout.id]
        origin = checkout.origin
        giturl = checkout.git_repository_url
        branch = checkout.git_repository_branch
        tree_name = checkout.tree_name
        commit_hash = checkout.git_commit_hash
        git_url_safe = quote_plus(record["git_repository_url"])

        tree_key = (branch, giturl, origin)
        tree_report_list = tree_prop_map.get(tree_key)
        if not tree_report_list:
            log_message("Found tree not in map")
            continue

        for tree_report in tree_report_list:
            path = tree_report["path"] if "path" in tree_report else "%"

            # In case an error happens in the query, we don't want to send an empty report
            try:
                new_issues, fixed_issues, unstable_tests = evaluate_test_results(
                    origin=origin,
                    giturl=giturl,
                    branch=branch,
                    commit_hash=commit_hash,
                    path=path,
                    interval="7 days",
                    group_size=5,
                )
            except Exception as e:
                log_message("Error while evaluating test results")
                log_message(f"Query execution failed: {e}")
                sys.exit()

            always = (
                True
                if "always" in tree_report.keys() and tree_report["always"]
                else False
            )

            if not always and (
                not new_issues and not fixed_issues and not unstable_tests
            ):
                print(f"No changes for {giturl} branch: {branch} (origin: {origin})")
                continue

            build_status_group = group_status(checkout.build_status)
            boot_status_group = group_status(checkout.boot_status)
            test_status_group = group_status(checkout.test_status)

            report = {}
            template = setup_jinja_template("summary.txt.j2")
            report["content"] = template.render(
                checkout=record,
                build_issues=build_issues,
                new_issues=new_issues,
                fixed_issues=fixed_issues,
                unstable_tests=unstable_tests,
                git_url_safe=git_url_safe,
                build_status_group=build_status_group,
                boot_status_group=boot_status_group,
                test_status_group=test_status_group,
            )
            origin_tag = f"[{origin.upper()}]" if origin != "maestro" else ""
            report["title"] = (
                f"[STATUS]{origin_tag} {tree_name}/{branch} - {record["git_commit_hash"]}"
            )

            recipients = process_submission_options(
                default_recipients=tree_report.get("default_recipients", []),
                specific_recipients=tree_report.get("recipients", []),
                options=tree_report.get("options", []),
            )

            email_args.tree_name = tree_name
            msg_id = send_email_report(
                service=service,
                report=report,
                email_args=email_args,
                recipients=recipients,
            )

            if msg_id and email_args.update:
                mark_checkout_notification_as_sent(
                    msg_id=msg_id,
                    checkout_id=record["checkout_id"],
                    git_repository_branch=branch,
                    git_repository_url=giturl,
                    origin=origin,
                    path=path,
                )


def create_and_send_issue_reports(*, service, email_args, signup_folder):
    unsent_issues = get_unsent_issues()
    for issue in unsent_issues:
        if issue.issue_type != "build":
            continue

        generate_issue_report(
            service=service,
            issue_id=issue.issue_id,
            email_args=email_args,
            ask_ignore=True,
            signup_folder=signup_folder,
        )


def generate_test_report(*, service, test_id, email_args, signup_folder):
    """Generate a test regression report for a specific test ID."""

    test_data = get_test_details_data(test_id=test_id)
    if not test_data:
        print(f"Test {test_id} not found in database")
        return

    test = test_data[0]

    if isinstance(test.get("environment_misc"), str):
        test["environment_misc"] = json.loads(test["environment_misc"])
    if isinstance(test.get("misc"), str):
        test["misc"] = json.loads(test["misc"])

    test["platform"] = test.get("environment_misc", {}).get(
        "platform", "unknown platform"
    )

    platform = test.get("environment_misc", {}).get("platform")
    history = get_test_status_history(
        path=test["path"],
        origin=test["origin"],
        git_repository_url=test["git_repository_url"],
        git_repository_branch=test["git_repository_branch"],
        platform=platform,
        test_start_time=test["start_time"],
        config_name=test["config_name"],
        field_timestamp=test["_timestamp"],
    )

    status_symbols = []
    for entry in history:
        if entry["status"] == "PASS":
            status_symbols.append("✅")
        elif entry["status"] == "FAIL":
            status_symbols.append("❌")
        else:
            status_symbols.append("⚠️")

    # Reverse to show oldest first
    status_symbols.reverse()
    test["status_history"] = " → ".join(status_symbols)

    template = setup_jinja_template("test_report.txt.j2")
    report_content = template.render(test=test)

    if is_boot(path=test["path"]):
        subject_prefix = "[BOOT REGRESSION]"
    else:
        subject_prefix = "[TEST REGRESSION]"

    tree_name = test.get("tree_name", "unknown")
    branch = test["git_repository_branch"]
    title = (
        f"{subject_prefix} {tree_name}/{branch}: {test['path']} on {test['platform']}"
    )

    report = {
        "title": title,
        "content": report_content,
    }

    print("=====================")
    print(f"# {tree_name}/{branch}")
    print(f"  test: {test['path']} on {test['platform']}")
    print(f"  status: {test['status']}")
    print(f"  dashboard: https://d.kernelci.org/test/{test['id']}")

    email_args.regression_report = True
    email_args.tree_name = tree_name

    send_email_report(
        service=service,
        report=report,
        email_args=email_args,
        git_url=test["git_repository_url"],
        signup_folder=signup_folder,
    )


def generate_hardware_summary_report(
    *,
    service,
    hardware_origins: Optional[list[str]],
    email_args,
    signup_folder: Optional[str] = None,
):
    """
    Generate weekly hardware reports for hardware submission file.
    """

    if get_running_instance() == "staging":
        print("This command only runs on production or dev environments.")
        return

    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=7)
    end_date = now

    # process the hardware submission files
    hardware_key_set, hardware_prop_map = process_hardware_submissions_files(
        signup_folder=signup_folder,
        hardware_origins=hardware_origins,
    )

    # get detailed data for all hardware
    hardwares_data_raw = get_hardware_summary_data(
        keys=list(hardware_key_set),
        start_date=start_date,
        end_date=end_date,
    )

    hardwares_data_dict = defaultdict(list)
    for raw in hardwares_data_raw:
        try:
            environment_misc = json.loads(raw.get("environment_misc", "{}"))
            misc = json.loads(raw.get("misc", "{}"))
        except json.JSONDecodeError:
            print(f'Error decoding JSON for key: {raw.get("environment_misc")}')
            continue
        hardware_id = environment_misc.get("platform")
        raw["job_id"] = environment_misc.get("job_id")
        raw["runtime"] = misc.get("runtime")
        origin = raw.get("test_origin")
        key = (hardware_id, origin)
        hardwares_data_dict[key].append(raw)

    # get the total build/boot/test counts for each hardware
    hardwares_list_raw = get_hardware_listing_data_bulk(
        keys=list(hardware_key_set),
        start_date=start_date,
        end_date=end_date,
    )

    # Iterate through each hardware record to render report, extract recipient, send email
    for hardware_id, origin in hardware_key_set:
        hardware_data = hardwares_data_dict.get((hardware_id, origin), [])
        hardware_raw = next(
            (row for row in hardwares_list_raw if row.get("platform") == hardware_id),
            None,
        )
        if hardware_raw is None:
            print(f"Hardware {hardware_id} not found in listing data")
            continue

        hardware_item = sanitize_hardware(hardware_raw)
        build_status_group = group_status(hardware_item.build_status_summary)
        boot_status_group = group_status(hardware_item.boot_status_summary)
        test_status_group = group_status(hardware_item.test_status_summary)

        # render the template
        template = setup_jinja_template("hardware_report.txt.j2")
        report = {}
        report["content"] = template.render(
            hardware_id=hardware_id,
            hardware_data=hardware_data,
            build_status_group=build_status_group,
            boot_status_group=boot_status_group,
            test_status_group=test_status_group,
        )
        report["title"] = (
            f"hardware {hardware_id} summary - {now.strftime("%Y-%m-%d %H:%M %Z")}"
        )

        # extract recipient
        hardware_report = hardware_prop_map.get((hardware_id, origin), {})
        recipients = hardware_report.get("default_recipients", [])

        # send email
        send_email_report(
            service=service,
            report=report,
            email_args=email_args,
            signup_folder=signup_folder,
            recipients=recipients,
        )


def run_fake_report(*, service, email_args):
    report = {}
    report["content"] = "Testing the email sending path..."
    report["title"] = "[IGNORE] Test report"

    send_email_report(
        service=service,
        report=report,
        email_args=email_args,
    )


class Command(BaseCommand):
    help = "Run various email notification commands for issue reporting and summaries"

    def add_arguments(self, parser):
        # Email sending options (common to all actions)
        parser.add_argument(
            "--send",
            action="store_true",
            help="Send email report at the end (optional for all actions)",
        )
        parser.add_argument(
            "--to",
            type=str,
            help="Recipient To: of the email (optional for all actions)",
        )
        parser.add_argument(
            "--cc",
            type=str,
            help="Recipient CC: of the email (optional for all actions)",
        )
        parser.add_argument(
            "--in-reply-to",
            type=str,
            help="Message ID to reply to (sets In-Reply-To header, optional for all actions)",
        )
        parser.add_argument(
            "--add-mailing-lists",
            action="store_true",
            help="Add community mailing lists to recipients (optional for all actions, see docs)",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Send email without asking for confirmation (optional for all actions)",
        )
        parser.add_argument(
            "--ignore-recipients",
            action="store_true",
            help="Ignore recipients.yaml file (optional for all actions)",
        )

        # Action argument (replaces subparsers)
        parser.add_argument(
            "--action",
            type=str,
            required=True,
            choices=[
                "new_issues",
                "issue_report",
                "summary",
                "fake_report",
                "test_report",
                "hardware_summary",
            ],
            help="""Action to perform: new_issues, issue_report, summary, fake_report,
              test_report, or hardware_summary""",
        )

        # Issue report specific arguments
        # TODO: add argument for a specific issue version once the query allows it
        parser.add_argument(
            "--id",
            type=str,
            help=(
                "ID of the issue (required for issue_report unless --all is used) or test "
                "(required for test_report) in Dashboard/KCIDB"
            ),
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help=(
                "Create reports for all issues not sent or not ignored "
                "(issue_report only, alternative to --id)"
            ),
        )
        parser.add_argument(
            "--update-storage",
            "-u",
            action="store_true",
            help="Update JSON storage while generating/sending reports (issue_report only)",
        )

        # Summary specific arguments
        # TODO: add argument to pass custom base dir as well
        parser.add_argument(
            "--summary-signup-folder",
            type=str,
            help="Alternative summary signup folder (summary only, must be in /backend/data)",
        )
        parser.add_argument(
            "--summary-origins",
            type=lambda s: [origin.strip() for origin in s.split(",")],
            help="Limit checkout summary to specific origins (summary only, comma-separated list)",
        )
        parser.add_argument(
            "--skip-sent-reports",
            action="store_true",
            help="Skip reports that have already been sent (summary only)",
        )

        # Fake report specific arguments
        parser.add_argument(
            "--tree",
            type=str,
            help="Add recipients for the given tree name (fake_report only)",
        )

        # hardware summary report specific arguments
        parser.add_argument(
            "--hardware-origins",
            type=lambda s: [origin.strip() for origin in s.split(",")],
            help="Limit hardware summary to specific origins (hardware summary only, comma-separated list)",
        )

    def handle(self, *args, **options):
        # Setup connections
        service = smtp_setup_connection()

        # Create the email_args namespace
        email_args = SimpleNamespace()
        email_args.send = options.get("send", False)
        email_args.yes = options.get("yes", False)
        email_args.to = options.get("to")
        email_args.cc = options.get("cc")
        email_args.in_reply_to = options.get("in_reply_to")
        email_args.ignore_recipients = options.get("ignore_recipients", False)
        email_args.add_mailing_lists = options.get("add_mailing_lists", False)
        email_args.regression_report = False

        # Get the action and process accordingly
        action = options.get("action")

        self.stdout.write(f"Running action: {action}")

        signup_folder = options.get("summary_signup_folder", SIGNUP_FOLDER)

        match action:
            case "new_issues":
                look_for_new_issues(
                    service=service,
                    email_args=email_args,
                    signup_folder=signup_folder,
                )

            case "issue_report":
                email_args.update = options.get("update_storage", False)
                if options.get("all", False):
                    create_and_send_issue_reports(
                        service=service,
                        email_args=email_args,
                        signup_folder=signup_folder,
                    )
                else:
                    issue_id = options.get("id")
                    if not issue_id:
                        self.stdout.write(
                            self.style.ERROR(
                                "You must provide an issue ID or use --all"
                            )
                        )
                        return
                    generate_issue_report(
                        service=service,
                        issue_id=issue_id,
                        email_args=email_args,
                        signup_folder=signup_folder,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Issue report generated for issue {issue_id}"
                        )
                    )

            case "summary":
                email_args.update = options.get("update_storage", False)
                summary_origins = options.get("summary_origins")

                run_checkout_summary(
                    service=service,
                    signup_folder=signup_folder,
                    email_args=email_args,
                    summary_origins=summary_origins,
                    skip_sent_reports=options.get("skip_sent_reports", True),
                )

            case "fake_report":
                email_args.tree_name = options.get("tree")
                run_fake_report(service=service, email_args=email_args)

            case "test_report":
                test_id = options.get("id")
                if not test_id:
                    self.stdout.write(
                        self.style.ERROR(
                            "You must provide a test ID with --id for test_report action"
                        )
                    )
                    return
                generate_test_report(
                    service=service,
                    test_id=test_id,
                    email_args=email_args,
                    signup_folder=signup_folder,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Test report generated for test {test_id}")
                )

            case "hardware_summary":
                email_args.update = options.get("update_storage", False)
                hardware_origins = options.get("hardware_origins")
                generate_hardware_summary_report(
                    service=service,
                    signup_folder=signup_folder,
                    email_args=email_args,
                    hardware_origins=hardware_origins,
                )
