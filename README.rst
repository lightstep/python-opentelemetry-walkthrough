=========================================
MicroDonuts: An OpenTelemetry Walkthrough
=========================================


Welcome to MicroDonuts! This is a sample application and OpenTelemetry
walkthrough, written in Python.

OpenTelemetry is a vendor-neutral, open standard for distributed tracing. To
learn more, check out http://opentelemetry.io, and try the walkthrough below!

There are two versions of the example app, ``walkthrough/server.py`` does not
contain tracing while ``walkthrough/server_instrumented.py`` does.

This guide has two exclusive steps:

- `Step 1, Alternative A: Add Tracing`_ shows how to manually add tracing information to an
  application.
- `Step 1, Alternative B: Use oteltrace-run`_ shows how to use oteltrace-run to autoinstrument
  an application without adding tracing manually.

Step 0: Setup MicroDonuts
=========================

Getting it
----------

#. Install ``virtualenv``: ``sudo -H pip3 install virtualenv``
#. Create a virtual environment: ``mkdir microdonuts; virtualenv microdonuts``
#. Activate the virtual environment: ``source microdonuts/bin/activate``
#. Clone this repository: ``git clone git@github.com:lightstep/python-opentelemetry-walkthrough.git``
#. Install the dependencies ``pip3 install -r python-opentelemetry-walkthrough/requirements.txt``

Running
-------

#. ``python python-opentelemetry-walkthrough/walkthrough/server.py``
#. Open your web browser, navigate to ``http://127.0.0.1:8082`` and order yourself some µ-donuts.

MicroDonuts has 4 server endpoints:

#. ``/order``
#. ``/status``
#. ``/kitchen/add_donuts``
#. ``/kitchen/get_donuts``

The first 2 serve orders, the last 2 provide kitchen services.

Step 1, Alternative A: Add Tracing
==================================

When you go to add tracing to a system, the best place to start is by
installing OpenTelemetry plugins for the OSS components you are using.
Instrumenting your networking libraries, web frameworks, and service clients
quickly gives you a lot of information about your distributed system, without
requiring you to change a lot of code.

To do this, let's change the startup of the application to include tracing:
``cd python-opentelemetry-walkthrough/walkthrough``

Start the global tracer
-----------------------

In OpenTelemetry, there is a concept of a global tracer for everyone to access.

Accessing this global tracer is easy, just add these lines to ``server.py``
under ``BLOCK 0``:

.. code:: python

    from opentelemetry import trace, propagators
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.propagation.b3_format import B3Format

Add these lines under ``BLOCK 2`` too:

.. code:: python

    trace.set_tracer_provider(TracerProvider())

    propagators.set_global_httptextformat(B3Format())

    tracer = trace.get_tracer(__name__)

The global tracer is now available as ``tracer``.


Instrument the HTTP requests
----------------------------

This is done in an automatic way by just adding this line under ``BLOCK 0``:

.. code:: python

    from opentelemetry.ext.requests import RequestsInstrumentor

Add also this line under ``BLOCK 2``:

.. code:: python

    RequestsInstrumentor().instrument()

Instrument Flask
----------------

This example uses Flask to expose the HTTP endpoints. Flask code can
be traced automatically by adding this line under ``BLOCK 0``:

.. code:: python

    from opentelemetry.ext.flask import FlaskInstrumentor

Add this line under ``BLOCK 1`` also:

.. code:: python

    FlaskInstrumentor().instrument_app(app)

Add an exporter
---------------

An exporter is necessary for the span data to be displayed. We'll use the
``ConsoleExporter`` in this example, an exporter that simply prints the span data
into the console. Add these lines under ``BLOCK 0``:

.. code:: python

    from opentelemetry.sdk.trace.export import ConsoleSpanExporter
    from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

Add these lines under ``BLOCK 2``:

.. code:: python

    trace.get_tracer_provider().add_span_processor(
        SimpleExportSpanProcessor(ConsoleSpanExporter())
    )

Use the tracer
--------------

Now is time to use the tracer itself in the server code.

Change the ``order`` function to this:

.. code:: python

    @app.route('/order', methods=['POST'])
    def order():

        order_id = str(uuid4())

        with tracer.start_span('root_span'):

            for donut_data in loads(next(request.form.keys()))['donuts']:

                for _ in range(donut_data['quantity']):

                    kitchen_consumer.add_donut(donut_data, order_id)

            return kitchen_consumer.check_status(order_id)

Change the ``status`` function to this:

.. code:: python

    @app.route('/status', methods=['POST'])
    def status():

        with tracer.start_span('status_span'):

            return kitchen_consumer.check_status(
                loads(next(request.form.keys()))['order_id']
            )

This will automatically create a span every time each of these functions are
called.

Step 1, Alternative B: Use oteltrace-run
========================================

``opentelemetry-auto-instrumentation`` allows to automatically instrument
applications written in Python.

Installation
------------

The ``opentelemetry-auto-instrumentation`` package can be installed directly
from PyPi. It is already provided in the ``requirements.txt`` file so no more
installation is needed.

Running
-------

You can run the microdonuts application without any Flask instrumentation code.
The ``server_instrumented.py`` file already provides this code ready to be
exceuted. Notice how this file lacks any call to ``FlaskInstrumentor``.

::

    opentelemetry-auto-instrumentation python python-opentelemetry-walkthrough/walkthrough/server_instrumented.py

Step 2: Have Fun
================

You can run the walkthrough again as explained before. You should see the span
data displayed in the console.

Thanks for playing, and welcome to OpenTelemetry!

Thanks for joining us in this walkthrough! Hope you enjoyed it. If you did, let
us know, and consider spreading the love!

*Aloha!*
