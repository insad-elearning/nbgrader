import os
import shutil
import subprocess

from textwrap import dedent
from traitlets import Unicode, List, Bool
from .baseapp import NbGrader
from .. import utils

aliases = {}
flags = {
    'force': (
        {'QuickStartApp': {'force': True}},
        "Overwrite existing files if they already exist."
    ),
}

class QuickStartApp(NbGrader):

    name = u'nbgrader-quickstart'
    description = u'Create an example class files directory with an example config file and assignment'

    aliases = aliases
    flags = flags

    examples = """
        You can run `nbgrader quickstart` just on its own from where ever you
        would like to create the example class files directory. It takes just
        one argument, which is the name of your course:

            nbgrader quickstart course101

        """

    force = Bool(False, config=True, help="Whether to overwrite existing files")

    def _classes_default(self):
        classes = super(QuickStartApp, self)._classes_default()
        classes.append(QuickStartApp)
        return classes

    def start(self):
        super(QuickStartApp, self).start()

        # make sure the course id was provided
        if len(self.extra_args) != 1:
            self.fail("Course id not provided. Usage: nbgrader quickstart course_id")

        # make sure it doesn't exist
        course_id = self.extra_args[0]
        course_path = os.path.abspath(course_id)
        if os.path.exists(course_path):
            if self.force:
                self.log.warning("Removing existing directory '%s'", course_path)
                utils.rmtree(course_path)
            else:
                self.fail("Directory '{}' already exists! Rerun with --force to overwrite.".format(course_path))

        # create the directory
        self.log.info("Creating directory '%s'...", course_path)
        os.mkdir(course_path)

        # populating it with an example
        self.log.info("Copying example from the user guide...")
        example = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'docs', 'source', 'user_guide', 'source'))
        shutil.copytree(example, os.path.join(course_path, "source"))

        # create the config file
        self.log.info("Generating example config file...")
        currdir = os.getcwd()
        os.chdir(course_path)
        subprocess.call(["nbgrader", "--generate-config"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        os.chdir(currdir)
        with open(os.path.join(course_path, "nbgrader_config.py"), "r") as fh:
            config = fh.read()
        with open(os.path.join(course_path, "nbgrader_config.py"), "w") as fh:
            fh.write("c = get_config()\n\n")
            fh.write("#" * 79 + "\n")
            fh.write("# Begin additions by nbgrader quickstart\n")
            fh.write("#" * 79 + "\n")
            fh.write(dedent(
                """
                # You only need this if you are running nbgrader on a shared
                # server set up.
                c.NbGrader.course_id = "{}"

                # Update this list with other assignments you want
                c.NbGrader.db_assignments = [dict(name="ps1")]

                # Change the students in this list with that actual students in
                # your course
                c.NbGrader.db_students = [
                    dict(id="bitdiddle", first_name="Ben", last_name="Bitdiddle"),
                    dict(id="hacker", first_name="Alyssa", last_name="Hacker"),
                    dict(id="reasoner", first_name="Louis", last_name="Reasoner")
                ]
                """
            ).format(course_id))
            fh.write("\n")
            fh.write("#" * 79 + "\n")
            fh.write("# End additions by nbgrader quickstart\n")
            fh.write("#" * 79 + "\n\n")
            fh.write(config)

        self.log.info("Done! The course files are located in '%s'", course_path)
