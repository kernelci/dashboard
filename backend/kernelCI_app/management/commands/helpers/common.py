import os
from typing import Optional

from django.conf import settings

from kernelCI_app.helpers.email import smtp_send_email
from kernelCI_app.helpers.logger import log_message
from kernelCI_app.management.commands.helpers.summary import SIGNUP_FOLDER
from kernelCI_app.utils import read_yaml_file
from jinja2 import Environment, FileSystemLoader, Template


KERNELCI_RESULTS = "kernelci-results@groups.io"
KERNELCI_REPLYTO = "kernelci@lists.linux.dev"
REGRESSIONS_LIST = "regressions@lists.linux.dev"


def setup_jinja_template(template_name: str) -> Template:
    """Gets the template file from management/commands/templates
    independently from where this function was called"""

    base_commands_path = os.path.dirname(os.path.abspath(__file__))
    parts = base_commands_path.split("management/commands")
    templates_dir = os.path.join(parts[0], "management/commands", "templates")

    jinja_env = Environment(loader=FileSystemLoader(templates_dir))
    return jinja_env.get_template(template_name)


def _get_default_tree_recipients(
    *,
    base_dir: Optional[str] = None,
    signup_folder: Optional[str] = None,
    search_url: Optional[str] = None,
) -> list[str]:
    """
    Searches in every subscription file to find the matching git_url from a tree,
    and returns the default recipients of that tree

    Params:
        base_dir: the base path for the signup folder;
        signup_folder: the relative path of the folder where all the subscription files are;
        search_url: the url of the tree that is being searched;

    Returns:
        A list of str with recipient emails.
        The list will be empty if there was an error or the tree was not found.
    """

    if not search_url:
        return []

    if not base_dir:
        base_dir = settings.BACKEND_DATA_DIR
    if not signup_folder:
        signup_folder = SIGNUP_FOLDER

    full_path = os.path.join(base_dir, signup_folder)
    for filename in os.listdir(full_path):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(signup_folder, filename)
            file_data = read_yaml_file(base_dir=base_dir, file=file_path)

            # Although there is a for loop here, there should only be a single tree per file
            for tree_values in file_data.values():
                tree_url = tree_values.get("url")
                default_recipients = tree_values.get("default_recipients", [])
                if search_url == tree_url:
                    return default_recipients
        else:
            log_message(
                f"Skipping file {filename} on loading summary files. Not a yaml file."
            )


def _ask_confirmation():
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
            recipients = _get_default_tree_recipients(
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
        if not _ask_confirmation():
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
