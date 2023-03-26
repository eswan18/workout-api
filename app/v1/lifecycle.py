from uuid import UUID
from enum import Enum
import json
from typing import Any


from fastapi import Depends, Request

from app.db.database import Base
from app.v1.auth import get_current_user
from app.pubsub import publish
from app.db.models import User


OrmModelType = type[Base]


class Action(Enum):
    CREATE = 1
    READ = 2
    UPDATE = 3
    DELETE = 4


method_to_crud_map = {
    "POST": Action.CREATE,
    "GET": Action.READ,
    "PUT": Action.UPDATE,
    "PATCH": Action.UPDATE,
    "DELETE": Action.DELETE,
}


class LifecyclePublisher:
    def __init__(self, resource: OrmModelType):
        self.resource = resource
        self.resource_name = resource.__name__

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
    ):
        if request.method not in method_to_crud_map:
            # We don't publish events for methods that don't map to CRUD actions.
            yield
            return

        action = method_to_crud_map[request.method]
        resource_id = request.path_params.get("id")
        # Problem: we don't actually know if the request was successful, since we don't
        # have access to the response here.
        # If I can find a way to get at the response, it would be best to only send this
        # on 2xx responses.
        # Keep an eye on this issue: https://github.com/tiangolo/fastapi/issues/3500
        publish_lifeycle_event(
            resource=self.resource,
            action=action,
            resource_id=resource_id,
            user=current_user.email,
        )

        yield


def publish_lifeycle_event(
    resource: OrmModelType,
    action: Action,
    resource_id: UUID | None = None,
    user: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Publish a CRUD event for a resource.

    Parameters
    ----------
    resource
        The resource class to publish events for.
    action
        The action type to publish an event for.
    resource_id
        The id of the relevant resource, if applicable.
    user
        The username of the user that triggered the event, if applicable.
    metadata
        Any additional metadata to include in the event message.
    """
    routing_key = f"lifecycle.{resource.__tablename__}.{action.name}".lower()
    data = metadata or {}
    if user is not None:
        data["user"] = user
    if resource_id is not None:
        data["id"] = str(resource_id)
    payload = json.dumps(data)
    publish(exchange="lifecycle", message=payload, routing_key=routing_key)
