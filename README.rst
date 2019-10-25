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
#. Clone this repository
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

Accessing this global tracer is easy, just add these lines to ``server.py`` under
``BLOCK 0``:

.. code:: python

    from opentelemetry import trace, propagators
    from opentelemetry.sdk.trace import Tracer
    from opentelemetry.sdk.context.propagation.b3_format import B3Format

Add these lines under ``BLOCK 1`` too:

.. code:: python

    trace.set_preferred_tracer_implementation(lambda T: Tracer())

    propagators.set_global_httptextformat(B3Format())

    tracer = trace.tracer()

The global tracer is now available as ``tracer``.


Instrument the HTTP requests
----------------------------

This is done in an automatic way by just adding this line under ``BLOCK 0``:

.. code:: python

    from opentelemetry.ext.http_requests import enable

Add also this line under ``BLOCK 1``:

.. code:: python

    enable(tracer)

Instrument Flask
----------------

This example uses Flask to expose the HTTP endpoints. Flask code can
be traced automatically by adding this line under ``BLOCK 0``:

.. code:: python

    from opentelemetry.ext.wsgi import OpenTelemetryMiddleware

Add this line under ``BLOCK 2`` also:

.. code:: python

    app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)

Add an exporter
---------------

An exporter is necessary for the span data to be displayed. We'll use the
``ConsoleExporter`` in this example, an exporter that simply prints the span data
into the console. Add these lines under ``BLOCK 0``:

.. code:: python

    from opentelemetry.sdk.trace.export import ConsoleSpanExporter
    from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

Add this line under ``BLOCK 1``:

.. code:: python

    tracer.add_span_processor(
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

``otel-trace`` allows to automatically instrument applications written in python.

Installation
------------

oteltrace-py doesn't have a PyPI packet yet, it has to be installed from source:

::

    # install oteltrace-py (will install opentelemetry as well)
    git clone https://github.com/lightstep/otel-trace-py -b mauricio/clean_code
    cd otel-trace-py
    pip install -e .

Running
-------

Before running the application, the console exporter has to be configured as the
exporter.

::

    # module where the opentelemetry SDK exporter is implemented
    export OTEL_EXPORTER_MODULE=opentelemetry.sdk.trace.export
    # factory function that returns an instance of the exporter
    # (constructor in this case)
    export OTEL_EXPORTER_FACTORY=ConsoleSpanExporter

Now you can run the microdonuts application:

::

    oteltrace-run python python-opentelemetry-walkthrough/walkthrough/server.py

Step 2: Have Fun
================

You can run the walkthrough again as explained before. You should see the span
data displayed in the console.

Thanks for playing, and welcome to OpenTelemetry!

Thanks for joining us in this walkthrough! Hope you enjoyed it. If you did, let
us know, and consider spreading the love!

*Aloha!*
