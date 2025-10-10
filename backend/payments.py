# backend/payments.py  (REPLACE ENTIRE FILE)
import os, stripe
from fastapi import HTTPException

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PRICE_ID_SINGLE = os.getenv("STRIPE_PRICE_ID_SINGLE")
PRICE_ID_SUB_MONTHLY = os.getenv("STRIPE_PRICE_ID_SUB_MONTHLY")

def create_checkout_session_payment(job_id: str, success_url: str, cancel_url: str):
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": PRICE_ID_SINGLE, "quantity": 1}],
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&job_id={job_id}",
            cancel_url=cancel_url,
            metadata={"job_id": job_id},
        )
        return {"id": session.id, "url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_checkout_session_subscription(job_id: str, email: str, success_url: str, cancel_url: str):
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": PRICE_ID_SUB_MONTHLY, "quantity": 1}],
            customer_email=email,                      # creates/links customer
            allow_promotion_codes=True,
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&job_id={job_id}",
            cancel_url=cancel_url,
            metadata={"job_id": job_id, "plan": "monthly"},
        )
        return {"id": session.id, "url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def verify_session_paid(session_id: str) -> bool:
    """Returns True if a one-time payment was paid, or a subscription is active/trialing."""
    try:
        s = stripe.checkout.Session.retrieve(session_id, expand=["subscription"])
        if s.mode == "payment":
            return s.payment_status == "paid"
        if s.mode == "subscription":
            # If subscription object exists and is active/trialing, allow
            sub = s.subscription
            if sub:
                if isinstance(sub, str):
                    sub = stripe.Subscription.retrieve(sub)
                return sub["status"] in ("active", "trialing")
        return False
    except Exception:
        return False

def is_active_subscriber(email: str) -> bool:
    """Check if there is an active or trialing subscription for the customer email."""
    try:
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            return False
        cust_id = customers.data[0].id
        subs = stripe.Subscription.list(customer=cust_id, status="all", limit=10)
        for sub in subs.data:
            if sub.status in ("active", "trialing"):
                return True
        return False
    except Exception:
        return False

