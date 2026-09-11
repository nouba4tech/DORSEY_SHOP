import smtplib
from email.message import EmailMessage

from flask import current_app


def _format_fcfa(amount):
    try:
        value = float(amount or 0)
    except (TypeError, ValueError):
        value = 0
    return f"{value:,.0f}".replace(",", " ") + " FCFA"


def send_order_email(order, items=None):
    config = current_app.config
    mail_server = config.get("MAIL_SERVER")
    mail_port = int(config.get("MAIL_PORT", 587))
    mail_use_tls = bool(config.get("MAIL_USE_TLS", True))
    mail_username = config.get("MAIL_USERNAME")
    mail_password = config.get("MAIL_PASSWORD")
    sender = config.get("MAIL_DEFAULT_SENDER") or mail_username

    if not (mail_server and mail_username and mail_password and sender):
        return False

    subject = f"Confirmation commande {order.order_number}"
    lines = [
        f"Bonjour {order.shipping_full_name},",
        "",
        f"Votre commande {order.order_number} a été enregistrée.",
        f"Statut: {order.status}",
        f"Paiement: {order.payment_status}",
        f"Total: {_format_fcfa(order.total_amount)}",
        "",
        "Merci pour votre confiance.",
    ]
    if items:
        lines.append("")
        lines.append("Articles:")
        for it in items:
            lines.append(f"- {it.product_name} x{it.quantity}")

    base_url = config.get("PUBLIC_BASE_URL", "").rstrip("/")
    if base_url:
        lines.append("")
        lines.append(f"Suivi: {base_url}/suivi-commande?order={order.order_number}")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = order.user.email
    msg.set_content("\n".join(lines))

    try:
        with smtplib.SMTP(mail_server, mail_port, timeout=15) as server:
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        return True
    except Exception:
        return False


def send_order_sms(order):
    config = current_app.config
    sid = config.get("TWILIO_ACCOUNT_SID")
    token = config.get("TWILIO_AUTH_TOKEN")
    from_phone = config.get("TWILIO_FROM")
    to_phone = order.shipping_phone

    if not (sid and token and from_phone and to_phone):
        return False

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        body = (
            f"Commande {order.order_number} - "
            f"Statut: {order.status} - "
            f"Total: {_format_fcfa(order.total_amount)}"
        )
        client.messages.create(to=to_phone, from_=from_phone, body=body)
        return True
    except Exception:
        return False


def send_order_notifications(order):
    items = order.items.all() if hasattr(order, "items") else []
    send_order_email(order, items=items)
    send_order_sms(order)


def send_order_shipped_email(order):
    config = current_app.config
    mail_server = config.get("MAIL_SERVER")
    mail_port = int(config.get("MAIL_PORT", 587))
    mail_use_tls = bool(config.get("MAIL_USE_TLS", True))
    mail_username = config.get("MAIL_USERNAME")
    mail_password = config.get("MAIL_PASSWORD")
    sender = config.get("MAIL_DEFAULT_SENDER") or mail_username

    if not (mail_server and mail_username and mail_password and sender):
        return False

    subject = f"Commande expédiée {order.order_number}"
    lines = [
        f"Bonjour {order.shipping_full_name},",
        "",
        f"Votre commande {order.order_number} a été expédiée.",
        f"Statut: {order.status}",
        f"Total: {_format_fcfa(order.total_amount)}",
    ]
    if order.carrier or order.tracking_number:
        lines.append("")
        lines.append("Suivi:")
        if order.carrier:
            lines.append(f"Transporteur: {order.carrier}")
        if order.tracking_number:
            lines.append(f"Numéro: {order.tracking_number}")

    base_url = config.get("PUBLIC_BASE_URL", "").rstrip("/")
    if base_url:
        lines.append("")
        lines.append(f"Suivi: {base_url}/suivi-commande?order={order.order_number}")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = order.user.email
    msg.set_content("\n".join(lines))

    try:
        with smtplib.SMTP(mail_server, mail_port, timeout=15) as server:
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        return True
    except Exception:
        return False


def send_order_shipped_sms(order):
    config = current_app.config
    sid = config.get("TWILIO_ACCOUNT_SID")
    token = config.get("TWILIO_AUTH_TOKEN")
    from_phone = config.get("TWILIO_FROM")
    to_phone = order.shipping_phone

    if not (sid and token and from_phone and to_phone):
        return False

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        body = f"Commande {order.order_number} expédiée."
        if order.tracking_number:
            body += f" Suivi: {order.tracking_number}"
        client.messages.create(to=to_phone, from_=from_phone, body=body)
        return True
    except Exception:
        return False


def send_order_shipped_notifications(order):
    send_order_shipped_email(order)
    send_order_shipped_sms(order)


def send_order_refunded_notifications(order):
    """Notifier le client qu'une commande a été remboursée."""
    config = current_app.config
    # Email
    mail_server = config.get("MAIL_SERVER")
    mail_port = int(config.get("MAIL_PORT", 587))
    mail_use_tls = bool(config.get("MAIL_USE_TLS", True))
    mail_username = config.get("MAIL_USERNAME")
    mail_password = config.get("MAIL_PASSWORD")
    sender = config.get("MAIL_DEFAULT_SENDER") or mail_username

    if mail_server and mail_username and mail_password and sender:
        subject = f"Remboursement commande {order.order_number}"
        lines = [
            f"Bonjour {order.shipping_full_name},",
            "",
            f"Votre commande {order.order_number} a été remboursée.",
            f"Total remboursé: {_format_fcfa(order.total_amount)}",
            "",
            "Si vous avez des questions, contactez le support.",
        ]
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = order.user.email
        msg.set_content("\n".join(lines))
        try:
            with smtplib.SMTP(mail_server, mail_port, timeout=15) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(msg)
        except Exception:
            pass

    # SMS
    sid = config.get("TWILIO_ACCOUNT_SID")
    token = config.get("TWILIO_AUTH_TOKEN")
    from_phone = config.get("TWILIO_FROM")
    to_phone = order.shipping_phone
    if sid and token and from_phone and to_phone:
        try:
            from twilio.rest import Client
            client = Client(sid, token)
            body = f"Commande {order.order_number} remboursée. Montant: {_format_fcfa(order.total_amount)}"
            client.messages.create(to=to_phone, from_=from_phone, body=body)
        except Exception:
            pass
