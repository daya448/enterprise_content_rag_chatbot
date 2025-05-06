import asyncio

from chat import AnthropicChat

tool_subset = ["cat-indices", "index", "search-3", "indices-get-mapping-1"]
# model_id = us.anthropic.claude-3-7-sonnet-20250219-v1:0


async def main():
    """Main function to run the chat loop."""
    # Example query:
    # Index this document {"user.id":"alebaro"} to the corresponding mcp index.
    # query the indices if you need to (elasticsearch)'

    chat = AnthropicChat(
        tool_subset=tool_subset,
        # model_id=model_id,
        print_tool_results=False,
    )
    await chat.loop()


if __name__ == "__main__":
    asyncio.run(main())
