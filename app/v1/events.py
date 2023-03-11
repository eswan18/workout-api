from typing import Any, TypeVar, Callable, cast
from enum import Enum
from functools import wraps

from app.db.database import Base


OrmModelType = type[Base]
F = TypeVar("F", bound=Callable[..., Any])


class Action(Enum):
    CREATE = 1
    READ = 2
    UPDATE = 3
    DELETE = 4


def publishes_event(resource: OrmModelType, action: Action) -> Callable[[F], F]:
    """
    Decorator to publish a resource creation, read, update, or deletion event.

    Meant to be applied to FastAPI routes. If the route is called with a `current_user`
    argument, the user will be recorded.

    Parameters
    ----------
    resource
        The resource class to publish events for.
    action
        The action type to publish an event for.

    Returns
    -------
    decorator
        A decorator that wraps a function and publishes the specified event when that
        function is invoked.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            publish_event(resource, action)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def publish_event(
    resource: OrmModelType, action: Action, metadata: dict[str, Any] | None = None
) -> None:
    """
    Publish an event.

    Parameters
    ----------
        resource: The resource class to publish events for.
        action: The action type to publish an event for.
    """
    # Todo
    ...
    print(f"Publishing {action.name} event for {resource.__name__} resource.")


def publish(message: str, exchange: str = "events", routing_key: str = "events"):
    """
    Publish a message to an exchange.

    Parameters
    ----------
        message: The message to publish.
        exchange: The exchange to publish the message to.
        routing_key: The routing key to publish the message to.
    """
    # Todo
    ...
