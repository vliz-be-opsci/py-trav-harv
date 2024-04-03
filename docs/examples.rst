Examples
========

Using the CLI
-------------

You can use the `travharv` package from the command line like this:

.. code-block:: bash

   python -m travharv <arguments>

For example, if you want to use the `TravHarvExecuter` module, you might do something like this:

.. code-block:: bash

   python -m travharv TravHarvExecuter --config <config_file>

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

Config File example
-------------------

Configuration options
^^^^^^^^^^^^^^^^^^^^^

**snooze-till-graph-age-minutes**
    This option specifies the number of minutes to wait before the graph is updated. The value is an integer.

**prefix**
    This section defines the prefixes used in the configuration file. Each prefix is defined by a key-value pair, where the key is the prefix and the value is the URI that the prefix represents.

**assert**
    This section contains a list of assertions. Each assertion is defined by a ``subjects`` section and a ``paths`` section.

    **subjects**
        The ``subjects`` section can contain either ``literal`` or ``SPARQL`` values.

        ``literal``
            A list of URIs that the assertion applies to.

        ``SPARQL``
            A SPARQL query that selects the subjects that the assertion applies to.

    **paths**
        The ``paths`` section contains a list of paths. Each path is a string that represents a sequence of predicates that form a path in the graph.

Example
^^^^^^^

Here is an example of an assertion:

.. code-block:: yaml

    - subjects:
        literal:
          - http://marineregions.org/mrgid/63523
          - http://marineregions.org/mrgid/2540
          - http://marineregions.org/mrgid/12548
      paths:
        - "mr:hasGeometry"
        - "mr:isPartOf"
        - "mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>"

In this example, the assertion applies to the subjects ``http://marineregions.org/mrgid/63523``, ``http://marineregions.org/mrgid/2540``, and ``http://marineregions.org/mrgid/12548``. The paths are ``mr:hasGeometry``, ``mr:isPartOf``, and ``mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>``.

Example of a full configuration file

.. code-block:: yaml

    snooze-till-graph-age-minutes: 5
    prefix:
      mr: "http://marineregions.org/mrgid/"
      schema: "https://schema.org/"
    assert:
      - subjects:
          SPARQL: "SELECT ?s WHERE { ?s a <http://marineregions.org/mrgid/Region> }"
        paths:
          - "mr:hasGeometry"
          - "mr:isPartOf"
          - "mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>"
      - subjects:
          literal:
            - http://marineregions.org/mrgid/63523
            - http://marineregions.org/mrgid/2540
            - http://marineregions.org/mrgid/12548
        paths:
          - "mr:hasGeometry"
          - "mr:isPartOf"
          - "mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>"

In the above example, the configuration file specifies that the graph should be updated every 5 minutes. It also specifies two assertions. The first assertion applies to all subjects that are instances of the class ``http://marineregions.org/mrgid/Region``. The second assertion applies to the subjects ``http://marineregions.org/mrgid/63523``, ``http://marineregions.org/mrgid/2540``, and ``http://marineregions.org/mrgid/12548``.
In the second case the paths to be asserted are ``mr:hasGeometry``, ``mr:isPartOf``, and ``mr:isPartOf / <https://schema.org/geo> / <https://schema.org/latitude>``.

Using the API
-------------

You can also use the `travharv` package directly in your Python code. Here's an example of how you might use the `TravHarvExecuter` and `TravHarvConfigBuilder` modules:

.. code-block:: python

  import os
  from travharv import TargetStore, TravHarvConfigBuilder, TravHarvExecuter

  config_folder = os.path.join(os.path.dirname(__file__), "cf") # path to the configuration folder

  url = "http://localhost:7200/repositories/lwua23" # URL of the triple store repository

  TARGETSTORE = TargetStore.TargetStore(url)
  CONFIGBUILDER = TravHarvConfigBuilder.TravHarvConfigBuilder(
    TARGETSTORE, str(config_folder)
  )

  CONFIGLIST = CONFIGBUILDER.build_from_folder()

  for travHarvConfig in CONFIGLIST:
    prefix_set = travHarvConfig.PrefixSet
    config_name = travHarvConfig.ConfigName
    tasks = travHarvConfig.tasks
    travharvexecutor = TravHarvExecuter.TravHarvExecutor(
      config_name, prefix_set, tasks, TARGETSTORE
    )
    travharvexecutor.assert_all_paths()

Replace `<config_file>` with the path to your configuration folder where the config file(s) are located.