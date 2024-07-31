******************************
Contributing to Fun with Flags
******************************

Contributions to Fun with Flags are always highly appreciated, thank you! Please notice that by contributing to Fun with Flags 
you confirm to adhere to our `Code of conduct <CODE_OF_CONDUCT.rst>`_.

General
#######

First time contribution
-----------------------
If you're inexperienced working with git then make sure to learn the basics first by doing one of the uncountable web-tutorials addressing
the topic. Next you'll find a typical git-workflow that might or might not fit your needs. A good git tutorial can be found on the 
website of the `w3c school <https://www.w3schools.com/git/default.asp?remote=github>`_.

.. code-block:: bash

  git clone https://github.com/joschobart/hattrick_fun_with_flags.git

2. Create working branch and change to branch.

.. code-block:: bash

  git checkout -b <name_for_super_cool_branch>

3. Set upstream repository.

.. code-block:: bash

  git remote add upstream https://github.com/joschobart/hattrick_fun_with_flags.git

4. Make your code-changes. If you're happy with your changes proceed with step 5.

5. Change to main branch and pull commits.

.. code-block:: bash

  git checkout main
  git pull upstream main

6. Change to your feature-branch and merge the main-branch into it.

.. code-block:: bash

  git checkout <name_for_super_cool_branch>
  git merge main

7. Push your changes to the upstream feature-branch. Choose a descriptive commit-message.

.. code-block:: bash

  git add .
  git commit -m <"my awesome changes!">
  git push origin <name_for_super_cool_branch>

8. Open a pull-request on `github <https://github.com/joschobart/hattrick_fun_with_flags>`_.



Contributing a translation
##########################

First time contribution
-----------------------
1. Make sure to have an up-to-date clone of the repo locally and that you are in your feature-branch. (See "General" for further instructions)
2. To be able to use pybabel, it must be installed in the PATH of your working directory. It is recommended to "install" FwF locally with the help of `rye <https://rye.astral.sh/>`_. And use a python `venv <https://docs.python.org/3/library/venv.html>`_. (don't worry: if you manage your local dev-copy of FwF with rye, you have everything you need already set in place)
3. Activate the venv

.. code-block:: bash

  source .venv/bin/activate

4. Extract a fresh messages.pot file. That file contains all translatable strings and snippets of which FwF consists.

.. code-block:: bash

  pybabel extract -F babel.cfg -o messages.pot .

5. Initialize your new language

.. code-block:: bash

  pybabel init -i messages.pot -d fun_with_flags/translations/ -l <ISO 639-1 language code>

6. Edit the messages.po file under fun_with_flags/translation/<ISO 639-1 language code>/LC_MESSAGES. If you need an example, you can take a look at the German po-file here: fun_with_flags/translation/de/LC_MESSAGES/messages.po.

7. Once finished, compile the strings into bytecode. This will generate the messages.mo-file.

.. code-block:: bash

  pybabel compile -d fun_with_flags/translations

8. Edit the sections "friendly", "locale", "quotes_ante" and "quotes_post" in the instance/config.py-file. (add your language-code and translations)

9. Push your changes to origin and open a pull-request.

10. All done! :)

Updating changes
----------------
Follow Steps 1-4 in the chapter "First time contribution" Step 5 requires another command that you'll find below. Then proceed with step 6 in chapter "First time contribution".

5. Update your messages.po-file.

.. code-block:: bash

  pybabel update -i messages.pot -d fun_with_flags/translations/
