Quickstart Guide
================


Flask
-----

.. code-block:: python

    # wsgi.py
    from twelvefactor import config
    from flask import Flask

    app = Flask(__name__)

    app.config.update(config({
        'DEBUG': {
            'type': bool,
            'default': False,
        },
        'SECRET_KEY': str
    }))

The above will set two config values, the first named ``DEBUG`` a boolean
defaulting to :data:`False`, and the second named ``SECRET_KEY`` a string which
will throw an exception if not set. Both variables will be populated from the
processes environment variables.


Django
------

.. code-block:: python

    # settings.py
    from twelvefactor import config

    globals().update(config({
        'DEBUG': {
            'type': bool,
            'default': False,
        },
        'SECRET_KEY': str
    }))

The above will create two variables, the first named ``DEBUG`` a boolean
defaulting to :data:`False`, and the second named ``SECRET_KEY`` a string which
will throw an exception if not set. Both variables will be populated from the
processes environment variables.
