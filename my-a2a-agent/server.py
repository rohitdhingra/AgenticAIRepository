import uuid

from fastapi import FastAPI

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    Message,
    Part,
    Role,
    Task,
    TaskState,
    TaskStatus,
)


AGENT_CARD = AgentCard(
    name="Echo Agent",
    description="A minimal A2A agent that echoes text sent by a client.",
    version="0.1.0",
    supported_interfaces=[
        AgentInterface(
            url="http://127.0.0.1:8000",
            protocol_binding="JSONRPC",
            protocol_version="1.0",
        )
    ],
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="echo",
            name="Echo",
            description="Returns the text supplied by the user.",
            tags=["echo", "demo"],
            examples=["Hello, A2A!"],
            input_modes=["text/plain"],
            output_modes=["text/plain"],
        )
    ],
)


class EchoAgentExecutor(AgentExecutor):
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        message = context.get_user_input()
        text = message if isinstance(message, str) else str(message)
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or str(uuid.uuid4())
        updater = TaskUpdater(event_queue, task_id, context_id)

        await event_queue.enqueue_event(
            Task(
                id=task_id,
                context_id=context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_SUBMITTED),
            )
        )
        await updater.submit()
        await updater.start_work()
        await updater.add_artifact(
            [Part(text=f"Echo: {text}")],
            name="echo-response",
        )
        await updater.complete()

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or str(uuid.uuid4())
        updater = TaskUpdater(event_queue, task_id, context_id)
        await updater.cancel()


request_handler = DefaultRequestHandler(
    agent_executor=EchoAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=AGENT_CARD,
)

app = FastAPI(title="My A2A Agent")
add_a2a_routes_to_fastapi(
    app,
    agent_card_routes=create_agent_card_routes(AGENT_CARD),
    jsonrpc_routes=create_jsonrpc_routes(request_handler, rpc_url="/"),
    rest_routes=create_rest_routes(request_handler),
)
