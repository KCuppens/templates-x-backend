from app.celery import app


@app.task(name="send_email", acks_late=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 3})
def send_email(key_name, to_name, to_email, params={}):
    """
    A celery task to send an email
    """
    try:
        return send_email(key_name, to_name, to_email, params)
    except Exception as e:
        return f'Exception raised, it would retry after 5 seconds! Exception: {e}'
