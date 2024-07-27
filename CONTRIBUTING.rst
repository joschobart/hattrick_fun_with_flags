******************************
Contributing to Fun with Flags
******************************

Contributions to Fun with Flags are always highly appreciated, thank you! Please notice that by contributing to Fun with Flags 
you confirm to adhere to our `Code of conduct <CODE_OF_CONDUCT.rst>`_.

Contributing a translation
##########################

First time contribution
-----------------------

1. Edit the messages.po file under fun_with_flags/translation/<language-code e.g. de>/LC_MESSAGES. If you need an example, you can take a look at the German po-file here: fun_with_flags/translation/de/LC_MESSAGES/messages.po.
2. Once finished, compile the strings into bytecode. This will generate the messages.mo-file. (this step is optional)

.. code-block:: bash
   $ pybabel compile -d fun_with_flags/translations

3. Edit the sections "friendly", "locale", "quotes_ante" and "quotes_post" in the instance/config.py-file. (add your language-code and translations)
4. Put everything into the zip-file again and upload it to the cloud. Let joschobart know about your update
