import logging
import time
from functools import wraps

# -------------------------------
# Logging Configuration
# -------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("API_MIDDLEWARE")


# -------------------------------
# Timing Decorator
# -------------------------------
def timing_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()

        result = func(*args, **kwargs)

        end = time.time()
        duration = end - start

        logger.info(f"{func.__name__} executed in {duration:.4f} seconds")

        return result

    return wrapper


# -------------------------------
# Input / Output Logging Decorator
# -------------------------------
def log_io(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        logger.debug(f"Calling {func.__name__}")
        logger.debug(f"Args={args}, Kwargs={kwargs}")

        result = func(*args, **kwargs)

        logger.debug(f"{func.__name__} returned {result}")

        return result

    return wrapper


# -------------------------------
# Role Based Access Decorator
# -------------------------------
def require_role(required_role):

    def decorator(func):

        @wraps(func)
        def wrapper(user_role, *args, **kwargs):

            if user_role != required_role:
                logger.warning(
                    f"Access denied for role '{user_role}' on {func.__name__}"
                )
                return {"error": "Unauthorized"}

            logger.info(
                f"Access granted for role '{user_role}' on {func.__name__}"
            )

            return func(user_role, *args, **kwargs)

        return wrapper

    return decorator


@timing_decorator
@log_io
@require_role("admin")
def delete_user(user_role, user_id):

    time.sleep(1)  # simulate database operation

    return {"status": f"user {user_id} deleted"}

delete_user("admin", 42)
delete_user("guest", 42)