Examples
========

Using the CLI
-------------

You can use the `pytravharv` package from the command line like this:

.. code-block:: bash

   python -m pytravharv <arguments>

For example, if you want to use the `TravHarvExecuter` module, you might do something like this:

.. code-block:: bash

   python -m pytravharv TravHarvExecuter --config <config_file>

Replace `<config_file>` with the path to your configuration file.

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Short Form
     - Long Form
     - Description
   * - ``-v``
     - ``--verbose``
     - Enable verbose output.
   * - ``-cf <path>``
     - ``--config-folder <path>``
     - Specify the folder containing configuration files. The path can be relative to the folder or file this was called from. By default, this is the `config` folder in the current working directory.
   * - ``-n <name>``
     - ``--name <name>``
     - Specify the name of the configuration to use.
   * - ``-o <path>``
     - ``--output-folder <path>``
     - Specify the folder to output files to. By default, this is the `output` folder in the current working directory.
   * - ``-ts <store>``
     - ``--target-store <store>``
     - Specify the target store to harvest. This can be a pointer to a triple store in memory or the base URI of a triple store.

Using the API
-------------

You can also use the `pytravharv` package directly in your Python code. Here's an example of how you might use the `TravHarvExecuter` and `TravHarvConfigBuilder` modules:

.. code-block:: python

   from pytravharv import TravHarvExecuter, TravHarvConfigBuilder

   # Create a config builder
   config_builder = TravHarvConfigBuilder()

   # Configure the builder
   config_builder.set_config_file('<config_file>')

   # Build the config
   config = config_builder.build()

   # Create an executer
   executer = TravHarvExecuter(config)

   # Execute
   executer.execute()

Replace `<config_file>` with the path to your configuration file.

For more detailed usage instructions and examples, please refer to the `examples.md` file in the `pre_docs` directory.