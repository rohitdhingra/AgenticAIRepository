import argparse
import asyncio
import uuid

import httpx

from a2a.client import ClientConfig, create_client
from a2a.types import Message, Part, Role, SendMessageRequest


async def send_message(base_url: str, text: str) -> None:
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        client = await create_client(
            base_url,
            client_config=ClientConfig(
                streaming=False,
                httpx_client=http_client,
            ),
        )
        request = SendMessageRequest(
            message=Message(
                message_id=str(uuid.uuid4()),
                role=Role.ROLE_USER,
                parts=[Part(text=text)],
            )
        )

        async for response in client.send_message(request):
            if response.task:
                print(response.task)
            elif response.message:
                print(response.message)
            elif response.status_update:
                print(response.status_update)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a message to an A2A agent")
    parser.add_argument("text", nargs="?", default="Hello from the A2A client!")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="Base URL of the A2A agent",
    )
    args = parser.parse_args()
    asyncio.run(send_message(args.url, args.text))


if __name__ == "__main__":
    main()
