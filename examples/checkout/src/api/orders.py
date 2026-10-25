"""POST /payments/authorize — the only payment endpoint. Extend it; do not clone it (API-001).

pdd: implements OC-PAY-AUTH stratum=api id=A-API-AUTHORIZE
"""
from payments.authorize import authorize_payment
from shared.validation import validate  # SEC-004: the one shared boundary validator


def post_authorize(request, deps):
    body = validate("AuthorizeRequest", request.json)
    result = authorize_payment(deps.db, deps.psp, deps.events, request.principal,
                               body["cart_id"], body["amount_cents"])
    return {"approved": result.approved, "reference": result.reference}
