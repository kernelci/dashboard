import jinja2
import json
import os
import sys
import yaml

from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO
from types import SimpleNamespace
from urllib.parse import quote_plus

from django.core.management.base import BaseCommand

from kernelCI_app.management.commands.libs.email import (
    gmail_setup_service,
    gmail_send_email,
)
from kernelCI_app.management.commands.libs.kcidb import (
    kcidb_new_issues,
    kcidb_issue_details,
    kcidb_build_incidents,
    kcidb_test_incidents,
    kcidb_last_test_without_issue,
    kcidb_last_test_without_issue_koike,
    kcidb_latest_checkout_results,
    kcidb_tests_results,
    kcidb_connect,
)


STORAGE_FILE = "found_issues.json"

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


def found_issues_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, STORAGE_FILE)


def exclude_already_found_and_store(issues):
    """
    Excludes issues that have already been found and store in the storage file.

    Args:
        issues: A list of dictionaries, where each dictionary represents an issue.

    Returns:
        A list of dictionaries containing only the new issues (those not in the storage file).
    """
    found_issues = {}
    path = found_issues_path()

    # Load existing found issues from storage if the file exists
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                found_issues = json.load(f)
        except json.JSONDecodeError:
            print(
                f"Warning: Could not decode JSON from {path}. Starting with empty issue list."
            )

    new_issues = []
    for issue in issues:
        issue_id = issue["id"]  # Assuming 'id' is the unique identifier

        if not found_issues.get(issue_id):
            new_issues.append(issue)
            issue["sent"] = False
            issue["ignore"] = False
            found_issues[issue_id] = {
                "comment": issue["comment"],
                "type": issue["type"],
                "timestamp": issue["_timestamp"],
                "dashboard": f"https://dashboard.kernelci.org/issue/{issue["id"]}",
                "sent": issue["sent"],
                "ignore": issue["ignore"],
            }

    # Save the updated found issues to storage (overwriting the file)
    try:
        with open(path, "w") as f:
            json.dump(
                found_issues, f, indent=4, default=str
            )  # indent for readability, default=str to handle datetime
    except Exception as e:
        print(f"Error saving found issues to {path}: {e}")

    return new_issues


def get_unsent_issues():
    """Collects all issues where 'sent' is False and 'ignore' is False."""
    with open(found_issues_path(), "r", encoding="utf-8") as f:
        data = json.load(f)

    unsent_issues = {
        issue_id: details
        for issue_id, details in data.items()
        if not details.get("sent", False) and not details.get("ignore", False)
    }

    return unsent_issues


def mark_issue_as_sent(issue_id, msg_id):
    with open(found_issues_path(), "r", encoding="utf-8") as f:
        data = json.load(f)

    if issue_id in data:
        data[issue_id]["sent"] = True
        data[issue_id]["message_id"] = msg_id

        with open(found_issues_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def mark_issue_as_ignore(issue_id):
    with open(found_issues_path(), "r", encoding="utf-8") as f:
        data = json.load(f)

    if issue_id in data:
        data[issue_id]["ignore"] = True

        with open(found_issues_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


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


def generate_issues_summary(dbconn, service, origin, email_args):
    issues = kcidb_new_issues(dbconn, origin)
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
        return None

    template = setup_jinja_template("issues.txt.j2")
    report = {}
    now = datetime.now(timezone.utc)
    report["content"] = template.render(
        build_issues=new_build_issues, boot_issues=new_boot_issues
    )
    report["title"] = f"new issues summary - {now.strftime("%Y-%m-%d %H:%M %Z")}"

    send_email_report(service, report, email_args)


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


def generate_issue_report(service, conn, issue_id, email_args, ask_ignore=False):
    result = kcidb_issue_details(conn, issue_id)
    if not result:
        print("issue not found!")
        sys.exit(-1)
    issue = result[0]

    print("=====================")
    print(
        f"# {issue["tree_name"]}/{issue["git_repository_branch"]} - {issue["_timestamp"]}"
    )
    print(f"  comment: {issue["comment"]}")
    print(f"  dashboard: https://d.kernelci.org/issue/{issue["id"]}")

    if ask_ignore and ask_ignore_issue():
        mark_issue_as_ignore(issue["id"])
        return

    if issue["build_id"]:
        incidents = kcidb_build_incidents(conn, issue_id)
        report = generate_build_issue_report(issue, incidents)
    elif issue["test_id"]:
        incidents = kcidb_test_incidents(conn, issue_id)
        for incident in incidents:
            last_test = kcidb_last_test_without_issue(conn, issue, incident)
            print(f"https://dashboard.kernelci.org/test/{last_test[0]["id"]}")
            last_test = kcidb_last_test_without_issue_koike(conn, issue, incident)
            print(f"https://dashboard.kernelci.org/test/{last_test[0]["id"]}")
            incident["last_pass"] = last_test[0]["start_time"]
            incident["last_pass_commit"] = last_test[0]["git_commit_hash"]
            incident["last_pass_id"] = last_test[0]["id"]
        report = generate_boot_issue_report(issue, incidents)
    email_args.tree_name = issue["tree_name"]
    email_args.regression_report = True
    msg_id = send_email_report(service, report, email_args)

    if msg_id and email_args.update:
        mark_issue_as_sent(issue_id, msg_id)


def add_to_test_results_buffer(buffer, grouped):
    has_changes = False
    for platform, configs in grouped.items():
        printed_platform = False

        for config_name, paths in configs.items():
            for path, test_group in paths.items():
                unique_statuses = {t["status"] for t in test_group}
                if len(unique_statuses) == 1:
                    continue

                if not printed_platform:
                    buffer.write(f"\nHardware: {platform}\n")
                    printed_platform = True

                buffer.write(f"- {path} ({config_name})\n")
                buffer.write(
                    f"  last run: https://d.kernelci.org/test/{test_group[0]["id"]}\n"
                )

                has_changes = True
                status_line = ["history: "]

                for t in reversed(test_group):
                    if t["status"] == "PASS":
                        status_line.append("✅ ")
                    elif t["status"] == "FAIL":
                        status_line.append("❌ ")
                    else:  # Inconclusive or other statuses
                        status_line.append("⚠️ ")

                buffer.write(f"  {' '.join(status_line)}\n")
                buffer.write("\n")

    return has_changes


def evaluate_test_results(conn, checkout, path):
    buffer = StringIO()
    origin = checkout["origin"]
    giturl = checkout["git_repository_url"]
    branch = checkout["git_repository_branch"]
    commit_hash = checkout["git_commit_hash"]
    tests = kcidb_tests_results(conn, origin, giturl, branch, commit_hash, path)

    # Group by platform, then by config_name, then by path
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    new_issues = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    fixed_issues = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    unstable_tests = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for t in tests:
        platform = t.get("platform", "unknown platform")
        config_name = t.get("config_name", "unknown config")
        grouped[platform][config_name][t["path"]].append(t)

    for platform, configs in grouped.items():
        for config_name, paths in configs.items():
            for path, test_group in paths.items():
                first_test = True
                possible_regression = True
                fixed_regression = True
                status_changed = False
                for t in test_group:
                    if first_test:
                        if t["status"] == "PASS":
                            possible_regression = False
                        elif t["status"] == "FAIL":
                            fixed_regression = False
                        else:
                            possible_regression = False
                            fixed_regression = False
                        first_test = False
                    else:
                        if possible_regression:
                            if t["status"] == "FAIL" and not status_changed:
                                continue
                            elif t["status"] == "FAIL" and status_changed:
                                possible_regression = False
                            elif t["status"] == "PASS":
                                status_changed = True
                            elif t["status"] != "PASS" and t["status"] != "FAIL":
                                possible_regression = False

                        if fixed_regression:
                            if t["status"] == "PASS" and not status_changed:
                                continue
                            elif t["status"] == "PASS" and status_changed:
                                fixed_regression = False
                            elif t["status"] == "FAIL":
                                status_changed = True
                            elif t["status"] != "PASS" and t["status"] != "FAIL":
                                fixed_regression = False

                if possible_regression:
                    new_issues[platform][config_name][t["path"]] = test_group
                elif fixed_regression:
                    fixed_issues[platform][config_name][t["path"]] = test_group
                else:
                    unstable_tests[platform][config_name][t["path"]] = test_group

    buffer.write("\n### POSSIBLE REGRESSIONS\n")
    has_changes = add_to_test_results_buffer(buffer, new_issues)
    if not has_changes:
        buffer.write("\nNo possible regressions observed.\n")

    buffer.write("\n### FIXED REGRESSIONS\n")
    has_changes = add_to_test_results_buffer(buffer, fixed_issues)
    if not has_changes:
        buffer.write("\nNo fixed regressions observed.\n")

    buffer.write("\n### UNSTABLE TESTS\n")
    has_changes = add_to_test_results_buffer(buffer, unstable_tests)
    if not has_changes:
        buffer.write("\nNo unstable tests observed.\n")

    content = buffer.getvalue()
    buffer.close()
    return content


def run_checkout_summary(service, conn, origin, email_args):
    data = read_yaml_file("data/summary-signup.yaml")
    for tree in data["trees"].values():
        checkout = kcidb_latest_checkout_results(
            conn, origin, tree["giturl"], tree["branch"]
        )
        if not checkout:
            continue

        checkout["giturl_safe"] = quote_plus(checkout["git_repository_url"])
        path = tree["path"] if "path" in tree else "%"

        test_status = evaluate_test_results(conn, checkout, path)

        report = {}
        template = setup_jinja_template("summary.txt.j2")
        report["content"] = template.render(checkout=checkout, test_status=test_status)
        report["title"] = (
            f"[STATUS] {checkout["tree_name"]}/{checkout["git_repository_branch"]}"
            f" - {checkout["git_commit_hash"]}"
        )

        print(report["content"])
        email_args.tree_name = checkout["tree_name"]
        send_email_report(service, report, email_args)


def create_and_send_issue_reports(service, conn, email_args):
    unsent_issues = get_unsent_issues()
    for issue_id, details in unsent_issues.items():
        if details["type"] != "build":
            continue

        generate_issue_report(service, conn, issue_id, email_args, ask_ignore=True)


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

        # Fake report specific arguments
        parser.add_argument(
            "--tree",
            type=str,
            help="Add recipients for the given tree name (for fake_report action)",
        )

    def handle(self, *args, **options):
        # Setup connections
        service = gmail_setup_service(options.get("credentials_file"))
        dbconn = kcidb_connect()
        origin = "maestro"

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
            generate_issues_summary(dbconn, service, origin, email_args)

        elif action == "issue_report":
            email_args.update = options.get("update_storage", False)
            if options.get("all", False):
                create_and_send_issue_reports(service, dbconn, email_args)
            else:
                issue_id = options.get("id")
                if not issue_id:
                    self.stdout.write(
                        self.style.ERROR("You must provide an issue ID or use --all")
                    )
                    return
                generate_issue_report(service, dbconn, issue_id, email_args)
                self.stdout.write(
                    self.style.SUCCESS(f"Issue report generated for issue {issue_id}")
                )

        elif action == "summary":
            run_checkout_summary(service, dbconn, origin, email_args)

        elif action == "fake_report":
            run_fake_report(service, email_args)
