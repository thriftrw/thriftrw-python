Contributing to thriftrw
========================

We are happy to accept third-party pull requests. Please try to follow these
guidelines when making changes:

-   If the change you are making is a new feature or introduces significant new
    APIs, make sure that the design has been discussed with us. Open a GitHub
    Issue if one does not already exist and start the discussion there with an
    API proposal. This is not necessary for small changes or bugfixes. Use
    your judgement.

-   Avoid making changes to the Thrift IDL syntax. We want to maintain
    compatibility with Apache Thrift.

-   Ensure new files have the copyright notice at the top of the file. Run the
    `scripts/install-hooks.sh` script to install a pre-commit hook that will
    automate this for you.

-   `flake8` must not throw any warnings.

-   Changes should be self-contained and must have tests and documentation to
    accompany them.

-   Commit messages must follow the format:

        Short one line description

        More detailed description if necessary.

        References to related GitHub issues if any.

Making changes
==============

-   Clone the GitHub repo (or your fork of it).

        $ git clone https://github.com/thriftrw/thriftrw-python.git thriftrw
        $ cd thriftrw

-   Create a virtualenv and install the dependencies.

        $ virtualenv env
        $ source env/bin/activate
        $ pip install -r requirements.txt
        $ pip install -r requirements-test.txt

-   Make your change, build it, and test it.

        $ python setup.py develop

    To test the change with the version of Python used by the virtualenv,
    simply run,

        $ make test

    If you have multiple versions of Python installed, you can use `tox` to
    test against them. For example,

        $ tox -e py27,py35

-   Create a Pull Request with a meaningful title and description to get your
    changes reviewed and merged. Reference any relevant GitHub issues in
    the PR. Address review feedback, if any.


