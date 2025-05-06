from typing import Optional

from anthropic import AnthropicBedrock, BadRequestError
from anthropic.types import ContentBlock
from fastmcp.client import Client
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed


class AnthropicChat:
    """Chat that uses the Anthropic API and FastMCP clients."""

    def __init__(
        self,
        tool_subset: Optional[list] = None,
        client: Optional[Client] = None,
        provide_chat_hist: bool = True,
        model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        print_tool_results: bool = False,
    ):
        # Initialize session and client objects
        self.client = client or Client("http://localhost:8000/sse")
        self.anthropic = AnthropicBedrock(aws_profile="ml", aws_region="us-east-1")
        self.tool_subset = tool_subset or []
        self.model_id = model_id
        self.chat_hist = []
        self.provide_chat_hist = provide_chat_hist
        self.print_tool_results = print_tool_results

    @retry(
        retry=retry_if_exception_type(BadRequestError), stop=stop_after_attempt(3), wait=wait_fixed(2)
    )
    def _model_create(self, **kwargs):
        return self.anthropic.messages.create(**kwargs)

    async def query_model(self, query: str) -> list[ContentBlock]:
        """Query the model with a given query and return the response."""
        chat_hist = self.chat_hist if self.provide_chat_hist else []
        messages = [{"role": "user", "content": query}]

        server_tools = (await self.client.list_tools_mcp()).tools
        if self.tool_subset:
            server_tools = [tool for tool in server_tools if tool.name in self.tool_subset]

        available_tools = [
            {"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema}
            for tool in server_tools
        ]

        while True:
            # Error code 400 tool usage https://github.com/anthropics/claude-code/issues/586
            response = self._model_create(
                model=self.model_id,
                max_tokens=1000,
                messages=[*chat_hist, *messages],
                tools=available_tools,
            )

            # Process response and handle tool calls
            assistant_message_content = []
            for content in response.content:
                if content.type == "text":
                    print(f"[Assistant]: {content.text}")
                    assistant_message_content.append(content)
                elif content.type == "tool_use":
                    tool_name = content.name
                    tool_args = content.input

                    # Execute tool call
                    result = await self.client.call_tool_mcp(tool_name, tool_args)
                    print(f"[Tool call]: {tool_name} with args {tool_args}")
                    assistant_message_content.append(content)
                    if self.print_tool_results:
                        for tool_result in result.content:
                            print(f"[Tool result]: {tool_result.text}")
                    messages.append({"role": "assistant", "content": assistant_message_content})
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": result.content,
                                }
                            ],
                        }
                    )

            if response.stop_reason == "end_turn":
                messages.append({"role": "assistant", "content": assistant_message_content})
                break
        return messages

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools."""
        messages = await self.query_model(query=query)
        self.chat_hist.extend(messages)

    async def loop(self):
        """Run an interactive chat loop."""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        async with self.client:
            while True:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                await self.process_query(query)
