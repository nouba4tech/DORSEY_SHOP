from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import stripe
from flask import current_app


ZERO_DECIMAL_CURRENCIES = {
    "BIF",
    "CLP",
    "DJF",
    "GNF",
    "JPY",
    "KMF",
    "KRW",
    "MGA",
    "PYG",
    "RWF",
    "UGX",
    "VND",
    "VUV",
    "XAF",
    "XOF",
    "XPF",
}


@dataclass
class StripeSession:
    id: str
    url: str
    payment_status: Optional[str] = None
    metadata: Optional[dict] = None


def _stripe_amount(amount: float, currency: str) -> int:
    currency = (currency or "xaf").upper()
    if currency in ZERO_DECIMAL_CURRENCIES:
        return int(round(float(amount)))
    return int(round(float(amount) * 100))


def _configure_stripe():
    stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY")


def stripe_is_configured() -> bool:
    return bool(current_app.config.get("STRIPE_SECRET_KEY"))


def create_checkout_session(order, success_url: str, cancel_url: str, currency: str):
    _configure_stripe()
    amount = _stripe_amount(order.total_amount, currency)
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": currency.lower(),
                    "product_data": {"name": f"Commande {order.order_number}"},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }
        ],
        customer_email=order.user.email,
        success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=cancel_url,
        client_reference_id=order.order_number,
        metadata={"order_id": str(order.id), "order_number": order.order_number},
    )
    return StripeSession(id=session.id, url=session.url)


def retrieve_checkout_session(session_id: str) -> StripeSession:
    _configure_stripe()
    session = stripe.checkout.Session.retrieve(session_id)
    return StripeSession(
        id=session.id,
        url=getattr(session, "url", ""),
        payment_status=session.payment_status,
        metadata=session.metadata,
    )


def construct_webhook_event(payload: str, sig_header: str):
    secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET not configured")
    return stripe.Webhook.construct_event(payload, sig_header, secret)
