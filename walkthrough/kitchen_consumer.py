from requests import post, get
from json import dumps, loads

from donut import Donut
from status import NEW_ORDER, RECEIVED, COOKING, READY


class KitchenConsumer(object):

    def add_donut(self, donut_data, order_id):

        post(
            'http://127.0.0.1:8082/kitchen/add_donut',
            data={
                'flavor': donut_data['flavor'],
                'order_id': order_id
            }
        )

    def check_status(self, order_id):

        order_donuts = []

        for donut_data in loads(
            get('http://127.0.0.1:8082/kitchen/get_donuts').content
        ):

            donut = Donut(
                donut_data['flavor'],
                donut_data['order_id'],
                donut_data['status']
            )

            if donut.order_id == order_id:

                order_donuts.append(donut)

        estimated_time = 0

        status = READY

        for order_donut in order_donuts:

            status = order_donut.status

            if status == NEW_ORDER:

                estimated_time = estimated_time + 3

            elif status == RECEIVED:

                estimated_time = estimated_time + 2

            elif status == COOKING:

                estimated_time = estimated_time + 1

        return dumps(
            {
                'order_id': order_id,
                'estimated_delivery_time': estimated_time,
                'state': status
            }
        )


__all__ = ['KitchenConsumer']
