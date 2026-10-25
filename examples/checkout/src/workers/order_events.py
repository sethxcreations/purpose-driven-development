"""Consumes payment.authorized and confirms the order.

pdd: implements OC-ORDER-CONFIRM stratum=worker id=A-ORDER-WORKER
"""
from harnesses.python.partition_consumer import PartitionConsumer  # OPS-003


def confirm_order(event, db, fulfilment):
    payment_id = event.payload["payment_id"]
    db.execute(
        "INSERT INTO orders (payment_id, status) VALUES (%s, 'confirmed') ON CONFLICT (payment_id) DO NOTHING",
        (payment_id,),
    )
    fulfilment.notify(payment_id)


def build_consumer(db, fulfilment, broker, dlq):
    return PartitionConsumer(
        handler=lambda ev: confirm_order(ev, db, fulfilment),
        commit=broker.commit,
        dead_letter=dlq.put,
    )
