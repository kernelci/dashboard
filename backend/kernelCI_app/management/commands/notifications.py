import jinja2
import json
import os
import sys
import yaml

from collections import defaultdict
from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.parse import quote_plus

from django.core.management.base import BaseCommand

from kernelCI_app.constants.general import DEFAULT_ORIGIN
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.helpers.system import is_production_instance

from kernelCI_app.helpers.email import (
    gmail_setup_service,
    gmail_send_email,
)
from kernelCI_app.helpers.trees import sanitize_tree
from kernelCI_app.queries.notifications import (
    get_checkout_summary_data,
    kcidb_new_issues,
    kcidb_issue_details,
    kcidb_build_incidents,
    kcidb_test_incidents,
    kcidb_last_test_without_issue,
    kcidb_tests_results,
)
from kernelCI_cache.queries.notifications import (
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

STORAGE_FILE = "found_issues.json"
SUMMARY_SIGNUP_FILE = "data/summary-signup.yaml"

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


def send_email_report(service, report, email_args, tree_name=None):
    sender_email = "KernelCI bot <bot@kernelci.org>"
    subject = report["title"]
    message_text = report["content"]

    if not email_args.send:
        print("\n==============================================")
        print(f"new report:\n> {subject}")
        print(message_text)
        return None

    cc = ""
    reply_to = None
    if email_args.add_mailing_lists:
        to = KERNELCI_RESULTS
        reply_to = KERNELCI_REPLYTO
    else:
        to = email_args.to

    if email_args.tree_name and not email_args.ignore_recipients:
        recipients = get_recipient_list(email_args.tree_name)
        cc = ", ".join([recipients, cc]) if cc else recipients

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

    return gmail_send_email(
        service, sender_email, to, subject, message_text, cc, reply_to
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


def read_yaml_file(file):
    """Reads a YAML file and returns the data as a dictionary."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, file)
    try:
        with open(filepath, "r") as file:
            data = yaml.safe_load(
                file
            )  # Use safe_load to avoid potential security issues
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
        return None


def get_recipient_list(tree_name):
    """
    Read recipients from a YAML file for a given tree name.

    Args:
        tree_name (str): Name of the tree (e.g., 'android', 'stable', 'next')

    Returns:
        str: Comma-separated list of email addresses for the specified tree
             Returns None if tree is not found
    """
    try:
        data = read_yaml_file("data/recipients.yaml")

        if tree_name in data["trees"]:
            recipients = data["trees"][tree_name]
            return ", ".join(recipients)

        return None

    except (KeyError, TypeError) as e:
        print(f"Error accessing tree data: {e}")
        return None


def look_for_new_issues(service, email_args):
    if is_production_instance():
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

    send_email_report(service, report, email_args)

    email_args.add_mailing_lists = True
    email_args.update = True
    for issue in new_build_issues:
        if issue["origin"] == "maestro":
            email_args.tree_name = issue["tree_name"]
            generate_issue_report(service, issue["id"], email_args)


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


def generate_issue_report(service, issue_id, email_args, ask_ignore=False):
    result = kcidb_issue_details(issue_id)
    if not result:
        print("issue not found!")
        sys.exit(-1)
    issue = result[0]
    issue_version = issue["version"]
    timestamp = issue["_timestamp"]
    comment = issue["comment"]

    print("=====================")
    print(f"# {issue["tree_name"]}/{issue["git_repository_branch"]} - {timestamp}")
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

    email_args.tree_name = issue["tree_name"]
    email_args.regression_report = True
    msg_id = send_email_report(service, report, email_args)

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
    path: str,
):
    tests = kcidb_tests_results(origin, giturl, branch, commit_hash, path)

    # Group by platform, then by config_name, then by path
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    new_issues = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    fixed_issues = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    unstable_tests = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for test in tests:
        platform = test.get("platform", "unknown platform")
        config_name = test.get("config_name", "unknown config")
        grouped[platform][config_name][test["path"]].append(test)

    for platform, configs in grouped.items():
        for config_name, paths in configs.items():
            for path, test_group in paths.items():
                unique_statuses = {t["status"] for t in test_group}
                if len(unique_statuses) == 1:
                    continue

                category = categorize_test_history(test_group)

                if category == "regression":
                    new_issues[platform][config_name][path] = test_group
                elif category == "fixed":
                    fixed_issues[platform][config_name][path] = test_group
                else:
                    unstable_tests[platform][config_name][path] = test_group

    return new_issues, fixed_issues, unstable_tests


def run_checkout_summary(service, signup_file, email_args):
    if is_production_instance():
        return

    tree_data = read_yaml_file(signup_file)

    tree_key_list: list[tuple[str, str, str]] = []
    tree_prop_map: dict[tuple[str, str, str], dict] = {}
    for tree_name, tree_values in tree_data["trees"].items():
        if "origin" in tree_values:
            origin = tree_values["origin"]
        else:
            origin = DEFAULT_ORIGIN
        branch = tree_values.get("branch")
        giturl = tree_values.get("giturl")
        tree_key = (branch, giturl, origin)

        tree_prop_map[tree_key] = tree_values
        tree_prop_map[tree_key]["name"] = tree_name

        tree_key_list.append(tree_key)

    records = get_checkout_summary_data(tuple_params=tree_key_list)

    for record in records:
        checkout = sanitize_tree(record)
        origin = checkout.origin
        giturl = checkout.git_repository_url
        branch = checkout.git_repository_branch
        tree_name = checkout.tree_name
        commit_hash = checkout.git_commit_hash
        git_url_safe = quote_plus(record["git_repository_url"])

        tree_key = (branch, giturl, origin)
        tree = tree_prop_map.get(tree_key)
        if tree is None:
            log_message("Found tree not in map")
            continue

        path = tree["path"] if "path" in tree else "%"

        new_issues, fixed_issues, unstable_tests = evaluate_test_results(
            origin=origin,
            giturl=giturl,
            branch=branch,
            commit_hash=commit_hash,
            path=path,
        )

        always = True if "always" in tree.keys() and tree["always"] else False

        if not always:
            if not new_issues and not fixed_issues and not unstable_tests:
                print(
                    f"No changes for {tree["giturl"]} branch: {tree["branch"]} (origin: {origin})"
                )
                continue

        build_status_group = group_status(checkout.build_status)
        boot_status_group = group_status(checkout.boot_status)
        test_status_group = group_status(checkout.test_status)

        report = {}
        template = setup_jinja_template("summary.txt.j2")
        report["content"] = template.render(
            checkout=record,
            new_issues=new_issues,
            fixed_issues=fixed_issues,
            unstable_tests=unstable_tests,
            git_url_safe=git_url_safe,
            build_status_group=build_status_group,
            boot_status_group=boot_status_group,
            test_status_group=test_status_group,
        )
        report["title"] = f"[STATUS] {tree_name}/{branch} - {record["git_commit_hash"]}"

        print(report["content"])
        email_args.tree_name = tree_name
        msg_id = send_email_report(service, report, email_args)

        if msg_id and email_args.update:
            mark_checkout_notification_as_sent(
                checkout_id=record["checkout_id"], msg_id=msg_id
            )


def create_and_send_issue_reports(service, email_args):
    unsent_issues = get_unsent_issues()
    for issue in unsent_issues:
        if issue.issue_type != "build":
            continue

        generate_issue_report(service, issue.issue_id, email_args, ask_ignore=True)


def run_fake_report(service, email_args):
    report = {}
    report["content"] = "Testing the email sending path..."
    report["title"] = "[IGNORE] Test report"

    send_email_report(service, report, email_args)


class Command(BaseCommand):
    help = "Run various email notification commands for issue reporting and summaries"

    def add_arguments(self, parser):
        # Email sending options (common to all actions)
        parser.add_argument(
            "--send", action="store_true", help="Send email report at the end."
        )
        parser.add_argument("--to", type=str, help="Recipient To: of the email")
        parser.add_argument("--cc", type=str, help="Recipient CC: of the email")
        parser.add_argument(
            "--add-mailing-lists",
            action="store_true",
            help="Add community mailing lists to recipients (See docs).",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Send email without asking for confirmation",
        )
        parser.add_argument(
            "--ignore-recipients",
            action="store_true",
            help="Ignore recipients.yaml file",
        )
        parser.add_argument(
            "--credentials-file", type=str, help="Credentials file for the Gmail API"
        )

        # Action argument (replaces subparsers)
        parser.add_argument(
            "--action",
            type=str,
            required=True,
            choices=["new_issues", "issue_report", "summary", "fake_report"],
            help="Action to perform: new_issues, issue_report, summary, or fake_report",
        )

        # Issue report specific arguments
        # TODO: add argument for a specific issue version once the query allows it
        parser.add_argument(
            "--id",
            type=str,
            help="Id of the issue in the Dashboard/KCIDB (for issue_report action)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Create reports for all issues not sent or not ignored (for issue_report action)",
        )
        parser.add_argument(
            "--update-storage",
            "-u",
            action="store_true",
            help="Update json storage as we manipulate and report issues (for issue_report action)",
        )

        # Summary specific arguments
        parser.add_argument(
            "--summary-signup-file",
            type=str,
            help="Pass alternative summary signup file",
        )

        # Fake report specific arguments
        parser.add_argument(
            "--tree",
            type=str,
            help="Add recipients for the given tree name (for fake_report action)",
        )

    def handle(self, *args, **options):
        # Setup connections
        service = gmail_setup_service(options.get("credentials_file"))

        # Create the email_args namespace
        email_args = SimpleNamespace()
        email_args.send = options.get("send", False)
        email_args.yes = options.get("yes", False)
        email_args.to = options.get("to")
        email_args.cc = options.get("cc")
        email_args.ignore_recipients = options.get("ignore_recipients", False)
        email_args.add_mailing_lists = options.get("add_mailing_lists", False)
        email_args.regression_report = False

        # Get the action and process accordingly
        action = options.get("action")

        # Get the tree name if in fake_report action
        email_args.tree_name = options.get("tree") if action == "fake_report" else None

        self.stdout.write(f"Running action: {action}")

        if action == "new_issues":
            look_for_new_issues(service, email_args)

        elif action == "issue_report":
            email_args.update = options.get("update_storage", False)
            if options.get("all", False):
                create_and_send_issue_reports(service, email_args)
            else:
                issue_id = options.get("id")
                if not issue_id:
                    self.stdout.write(
                        self.style.ERROR("You must provide an issue ID or use --all")
                    )
                    return
                generate_issue_report(service, issue_id, email_args)
                self.stdout.write(
                    self.style.SUCCESS(f"Issue report generated for issue {issue_id}")
                )

        elif action == "summary":
            email_args.update = options.get("update_storage", False)
            signup_file = options.get("summary_signup_file")
            if not signup_file:
                signup_file = SUMMARY_SIGNUP_FILE
            run_checkout_summary(service, signup_file, email_args)

        elif action == "fake_report":
            run_fake_report(service, email_args)
