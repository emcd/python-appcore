Integrate ``ictr`` as a first-class inscription subsystem alongside Python
logging. ``prepare()`` configures and optionally installs the ictr dispatcher;
``Control`` gains ``install_ictr``; CLI exposes ``--active-flavors`` and
``--trace-levels``. Flavor and trace configuration precedence is explicit
Control args, then ``{APP}_*`` env, then ``ICTR_*`` env, then defaults.
