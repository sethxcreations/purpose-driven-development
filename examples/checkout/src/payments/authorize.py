"""Card and wallet authorization.

pdd: implements OC-PAY-AUTH stratum=method id=A-PAY-AUTHORIZE
"""
from __future__ import annotations

from dataclasses import dataclass

from .resilience import psp_breaker


@dataclass(frozen=True)
class AuthResult:
    cart_id: str
    approved: bool
    reference: str | None


class Forbidden(Exception):
    pass


def authorize_payment(db, psp, events, principal, cart_id: str, amount_cents: int) -> AuthResult:
    # ReqPre: permission check (SEC-003) and amount equals the locked total.
    if not principal.can("payments:authorize", cart_id):
        raise Forbidden(cart_id)
    row = db.fetch_one("SELECT total_cents, locked FROM carts WHERE id = %s", (cart_id,))
    if row is None or not row["locked"] or row["total_cents"] != amount_cents:
        raise ValueError("cart is not locked at this amount")

    # ReqPost: idempotent per cart id.
    existing = db.fetch_one("SELECT approved, reference FROM authorizations WHERE cart_id = %s", (cart_id,))
    if existing is not None:
        return AuthResult(cart_id, existing["approved"], existing["reference"])

    # Obstacle X-PSP-TIMEOUT is resolved once, by the canonical breaker; no local retries here.
    response = psp_breaker.call("psp", lambda: psp.authorize(cart_id, amount_cents, timeout=2.0),
                                fallback=lambda: None)
    approved = bool(response and response.approved)
    reference = response.reference if response else None
    db.execute(
        "INSERT INTO authorizations (cart_id, approved, reference) VALUES (%s, %s, %s)",
        (cart_id, approved, reference),
    )
    events.emit("payment.authorized" if approved else "payment.declined", {"cart_id": cart_id})
    return AuthResult(cart_id, approved, reference)
