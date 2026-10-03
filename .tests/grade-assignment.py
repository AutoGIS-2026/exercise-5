#!/usr/bin/env python3


import contextlib
import json
import os
import pathlib
import re
import sys

import pytest


TESTS_PATH = pathlib.Path(__file__).parent
sys.path.insert(0, str(TESTS_PATH))

import import_notebook  # noqa: E402  (shares NOTEBOOK_ERRORS with the tests’ fixtures)


HELP = (
    "UH students: If you feel stuck, don’t hesitate to come to "
    "the work sessions or post a question on Discord!"
)
MAX_NOTEBOOK_ERRORS = 3


def explain_failure(excinfo):
    """If a test failed because a variable, column or tagged section is missing, say so."""
    if excinfo is None:
        return ""
    error = excinfo.value
    name = None
    if isinstance(error, KeyError) and error.args and isinstance(error.args[0], str):
        name = error.args[0]
        if re.fullmatch(r"Part \d+", name):
            return (
                f" (The autograder could not find the cells tagged `{name}`: "
                "please don’t delete the cells provided in the notebook.)"
            )
    elif isinstance(error, NameError) or (
        # a variable missing from a notebook loaded with import_notebook_namespace()
        isinstance(error, AttributeError) and "SimpleNamespace" in str(error)
    ):
        match = re.search(r"'(\w+)'(?: is not defined)?$", str(error))
        name = match.group(1) if match else None
    if name and name.isidentifier():
        return f" (The autograder could not find `{name}`.)"
    return ""


class PointsCounter:
    def __init__(self):
        self.points = 0
        self.possible_points = 0
        self.error_messages = []
        self.bonus_tasks = 0
        self.checks = 0
        self.checks_passed = 0
        self.tests_run = 0
        self.setup_errors = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """
        Summarise the points awarded by each test.

        This function is called for each phase (setup, call, teardown) of each test.
        """
        outcome = yield
        report = outcome.get_result()

        info = getattr(item.obj, "points_info", None)
        if info is None:
            return

        if report.when == "setup" and report.failed:
            # e.g., a fixture could not load a notebook: the test never ran
            self.setup_errors += 1
        elif report.when != "call":
            return

        self.tests_run += 1
        possible_points = info["points"]
        error_message = info["error_message"]
        is_check = not possible_points and not info["bonus_task"]

        self.possible_points += possible_points
        self.checks += is_check

        if report.passed:
            self.points += possible_points
            self.checks_passed += is_check
            if info["bonus_task"]:
                self.bonus_tasks += 1
        elif error_message:  # ignore empty error messages (e.g., bonus tasks)
            explanation = explain_failure(call.excinfo)
            if explanation and explanation.split("`")[1] not in error_message:
                error_message += explanation
            self.error_messages.append(error_message)


def format_number(number):
    return f"{number:.2f}".rstrip("0").rstrip(".")


def format_notebook_errors():
    """List errors raised by students’ cells (and by the test cells right after them)."""
    errors = sorted(
        import_notebook.NOTEBOOK_ERRORS,
        key=lambda error: error["test_cell"],  # students’ own cells first
    )[:MAX_NOTEBOOK_ERRORS]
    if not errors:
        return ""
    body = (
        "\n\n**Some notebook cells raised an error when the autograder ran them** "
        "(the rest of such a cell is skipped, which can cost points further down):\n"
    )
    for error in errors:
        where = f"`{error['notebook']}`, code cell {error['cell']}"
        if error["first_line"]:
            where += f" (starting with `{error['first_line']}`)"
        body += f"- {where}: `{error['error']}`\n"
    return body


def format_feedback(student_username, points_counter):
    """
    Phrase and format feedback to the student.

    Arguments
    =========
    points_counter : PointsCounter
        A PointsCounter instance that has recorded the possible and actually
        gained points of a suite of pytest tests.

    Returns
    =======
    tuple(str, str) :
        body and reaction that can be passed to
        https://github.com/peter-evans/create-or-update-comment
    """
    points = points_counter.points
    possible_points = points_counter.possible_points
    bonus_tasks = points_counter.bonus_tasks
    error_messages = points_counter.error_messages

    # The grader itself could not run (e.g., a notebook file could not be loaded)
    if points_counter.tests_run == 0 or (
        points_counter.setup_errors == points_counter.tests_run
    ):
        body = (
            "**The autograder could not check your submission this time.** "
            "This is most likely a problem with the autograder, not with your work: "
            "the course assistants will grade your exercise manually.\n\n"
            "If you see this message repeatedly, please let us know on Discord."
        )
        return body, "confused"

    # Manually graded exercises: report a checklist instead of points
    if possible_points == 0 and points_counter.checks:
        body = (
            "**Thanks for your submission!** This exercise is graded manually by the "
            "course assistants. The autograder ran some basic checks: "
            f"**{points_counter.checks_passed} of {points_counter.checks}** passed.\n\n"
        )
        if error_messages:
            body += "Please take a look at the following:\n"
            for error_message in error_messages:
                body += f"- {error_message}\n"
        else:
            body += "Everything the autograder can check looks good! 🎉\n"
        body += format_notebook_errors()
        return body, ("hooray" if not error_messages else "+1")

    body = ""
    reaction = ""

    if points:
        body = (
            "**Great job!**\n"
            "\n"
            "With the latest commit and push, your solution for the exercise "
            f"achieves **{format_number(points)} point{'s' if points != 1 else ''} "
            f"out of {format_number(possible_points)}** possible points. "
        )
        if points < possible_points:
            body += (
                "**Keep up the good work!**\n\n"
            )
            reaction = "+1"

            if bonus_tasks:
                body += (
                    f"Congratulations also on completing {bonus_tasks:0.0f} "
                    f"optional task{'s' if bonus_tasks > 1 else ''}. "
                    "You got the hang of it!\n\n"
                )

            body += (
                "We noticed that the following things could still be improved:\n"
            )
            for error_message in error_messages:
                body += f"- {error_message}\n"

        else:
            body += "**Amazing work! That’s full points! Well done!**\n\n"
            reaction = "hooray"

            if bonus_tasks:
                body += (
                    f"On top that, you also completed {bonus_tasks:0.0f} "
                    f"optional task{'s' if bonus_tasks > 1 else ''}. "
                    "**Fantastic job!** 💪\n\n"
                )

    else:  # 0 points so far
        body = (
            "So far, your solution to the exercise "
            "has not gained any points.\n"
            "No worries: until the deadline, you can submit as many new "
            "versions as you want.\n\n"
            f"{HELP}"
        )

    if points < possible_points:
        body += format_notebook_errors()

    body += (
        "\n\n*This is a preliminary, automatically computed grade. "
        "The course assistants also review every submission manually.*"
    )

    return body, reaction


def use_up_to_date_certificates():
    """
    Use certifi’s CA certificates for HTTPS downloads in students’ notebooks.

    The certificates of the `python` container image are outdated (e.g., they lack the
    root certificate of kartta.hsy.fi, used for WFS downloads in exercise 3).
    """
    try:
        import certifi
    except ImportError:
        return
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("CURL_CA_BUNDLE", certifi.where())


def main():
    use_up_to_date_certificates()
    points_counter = PointsCounter()

    # run pytest, but hide all of its output
    with open(os.devnull, "w") as devnull:
        with contextlib.redirect_stdout(devnull):
            with contextlib.redirect_stderr(devnull):
                pytest.main(
                    [str(TESTS_PATH), "-p", "no:cacheprovider"],
                    plugins=[points_counter],
                )

    try:
        student_username = os.environ["STUDENT_USERNAME"]
    except KeyError:
        student_username = ""
    body, reaction = format_feedback(student_username, points_counter)

    if sys.stdout.isatty():  # running interactively
        feedback = body
    else:  # piped into, e.g., $GITHUB_OUTPUT
        feedback = json.dumps({
            "body": body,
            "reaction": reaction
        })
        feedback = f"FEEDBACK={feedback:s}"
    print(feedback)


if __name__ == "__main__":
    main()
