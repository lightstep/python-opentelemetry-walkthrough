from json import loads, dumps
from uuid import uuid4

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.ext.http_requests import enable
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

from kitchen_service import KitchenService
from kitchen_consumer import KitchenConsumer
from donut import Donut
from status import NEW_ORDER

from flask import Flask, render_template, request

app = Flask(__name__)
app.static_folder = 'static'

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer(__name__)
enable(trace.get_tracer_provider())


kitchen_service = KitchenService()
kitchen_consumer = KitchenConsumer()


@app.route('/')
def home():

    return render_template('index.html')


@app.route('/order', methods=['POST'])
def order():

    order_id = str(uuid4())

    with tracer.start_span('root_span'):

        for donut_data in loads(next(request.form.keys()))['donuts']:

            for _ in range(donut_data['quantity']):

                kitchen_consumer.add_donut(donut_data, order_id)

        return kitchen_consumer.check_status(order_id)


@app.route('/status', methods=['POST'])
def status():

    with tracer.start_span('status_span'):

        return kitchen_consumer.check_status(
            loads(next(request.form.keys()))['order_id']
        )


@app.route('/kitchen/add_donut', methods=['POST'])
def add_donut(*args, **kwargs):

    kitchen_service.add_donut(
        Donut(
            request.form['flavor'],
            request.form['order_id'],
            NEW_ORDER
        )
    )

    return '200'


@app.route('/kitchen/get_donuts', methods=['GET'])
def get_donuts():

    return dumps(
        [
            {
                'flavor': donut.flavor,
                'order_id': donut.order_id,
                'status': donut.status
            } for donut in kitchen_service.get_all_donuts()
        ]
    )


if __name__ == "__main__":

    app.run(port=8082)
