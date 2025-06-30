import re
from typing import Any

import chainlit as cl
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain_agent import agent, clear_memory, get_memory_stats

load_dotenv()


class EnhancedChainlitCallbackHandler(BaseCallbackHandler):
    """Enhanced callback handler with selective step display"""

    def __init__(self):
        self.steps = []
        self.current_step = None
        self.step_count = 0
        self.reasoning_steps = []
        self.search_results = []
        self.show_thinking = True
        self.show_search = True
        self.show_final_reasoning = True

    def should_show_step(self, step_type: str) -> bool:
        """Determine if a step should be displayed"""
        if step_type == "thinking" and not self.show_thinking:
            return False
        if step_type == "search" and not self.show_search:
            return False
        if step_type == "final_reasoning" and not self.show_final_reasoning:
            return False
        return True

    async def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs):
        """Called when LLM starts - only show if relevant"""
        if not self.should_show_step("thinking"):
            return

        self.step_count += 1
        step_name = f"🧠 Agent Reasoning (Step {self.step_count})"

        self.current_step = cl.Step(name=step_name)
        await self.current_step.__aenter__()
        await self.current_step.stream_token("💭 Analyzing your question...\n")

    async def on_llm_end(self, response, **kwargs):
        """Called when LLM ends"""
        if self.current_step and self.should_show_step("thinking"):
            if hasattr(response, "generations") and response.generations:
                text = response.generations[0][0].text if response.generations[0] else ""

                # Extract meaningful reasoning parts
                reasoning = self._extract_reasoning(text)
                if reasoning:
                    await self.current_step.stream_token(f"🤔 **Thought Process**:\n{reasoning}\n")

            await self.current_step.__aexit__(None, None, None)
            self.current_step = None

    def _extract_reasoning(self, text: str) -> str:
        """Extract meaningful reasoning from LLM output"""
        # Look for "Thought:" patterns
        thought_pattern = r"Thought:\s*(.*?)(?=Action:|Final Answer:|$)"
        thoughts = re.findall(thought_pattern, text, re.DOTALL | re.IGNORECASE)

        if thoughts:
            # Clean up and format thoughts
            clean_thoughts = []
            for thought in thoughts:
                cleaned = thought.strip().replace("\n", " ")
                if len(cleaned) > 10:  # Only include substantial thoughts
                    clean_thoughts.append(f"• {cleaned}")

            if clean_thoughts:
                return "\n".join(clean_thoughts)

        # Fallback to first meaningful sentence
        sentences = text.split(".")
        for sentence in sentences:
            if len(sentence.strip()) > 20 and not sentence.strip().startswith("Action"):
                return sentence.strip()

        return "Processing your request..."

    async def on_agent_action(self, action, **kwargs):
        """Called when agent takes an action - only show search actions"""
        tool_name = getattr(action, "tool", "Unknown Tool")
        tool_input = getattr(action, "tool_input", "No input")

        # Skip error actions
        if "_Exception" in str(tool_name) or "Invalid Format" in str(tool_input):
            return

        # Only show search-related actions
        if "search" not in tool_name.lower():
            return

        if not self.should_show_step("search"):
            return

        # Create search step
        self.current_step = cl.Step(name=f"🔍 Search: {tool_input}")
        await self.current_step.__aenter__()
        await self.current_step.stream_token(f"**Query**: `{tool_input}`\n")
        await self.current_step.stream_token("⏳ Searching content indices...\n")

    async def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs):
        """Called when a tool starts"""
        if self.current_step:
            await self.current_step.stream_token("🔄 Executing search...\n")

    # async def on_tool_end(self, output: str, **kwargs):
    #     """Called when a tool ends"""
    #     if not self.current_step or not self.should_show_step("search"):
    #         return

    #     # Process and display search results
    #     if "FINAL_ANSWER:" in output:
    #         result = output.replace("FINAL_ANSWER:", "").strip()
    #     else:
    #         result = output

    #     # Format results nicely
    #     if "No relevant information" in result:
    #         await self.current_step.stream_token("❌ **No results found**\n")
    #     else:
    #         # Show condensed results
    #         preview = self._format_search_results(result)
    #         await self.current_step.stream_token(f"✅ **Found relevant content**:\n{preview}\n")

    #     await self.current_step.__aexit__(None, None, None)
    #     self.current_step = None

    # def _format_search_results(self, results: str) -> str:
    #     """Format search results for display"""
    #     # Limit length for dropdown display
    #     if len(results) > 400:
    #         preview = results[:400] + "..."
    #     else:
    #         preview = results

    #     # Add some basic formatting
    #     lines = preview.split('\n')
    #     formatted_lines = []
    #     for line in lines[:5]:  # Show max 5 lines
    #         if line.strip():
    #             formatted_lines.append(f"• {line.strip()}")

    #     return "\n".join(formatted_lines) if formatted_lines else preview

    async def on_agent_finish(self, finish, **kwargs):
        """Called when agent finishes - show final reasoning if enabled"""
        if not self.should_show_step("final_reasoning"):
            return

        # Create a final reasoning step
        final_step = cl.Step(name="✅ Final Analysis")
        await final_step.__aenter__()

        # Extract final answer reasoning
        output = getattr(finish, "return_values", {}).get("output", "")
        if output:
            reasoning = self._extract_final_reasoning(output)
            if reasoning:
                await final_step.stream_token(f"🎯 **Conclusion**: {reasoning}\n")

        await final_step.stream_token("✅ Response ready!\n")
        await final_step.__aexit__(None, None, None)

    def _extract_final_reasoning(self, output: str) -> str:
        """Extract final reasoning from agent output"""
        # Look for the actual answer content
        if len(output) > 100:
            # Get first sentence or two as reasoning
            sentences = output.split(".")
            if sentences:
                first_part = sentences[0].strip()
                if len(first_part) > 20:
                    return first_part

        return "Based on search results"

    async def on_chain_error(self, error, **kwargs):
        """Called when there's an error"""
        if self.current_step:
            await self.current_step.stream_token(f"❌ **Error**: {error!s}\n")
            await self.current_step.__aexit__(None, None, None)
            self.current_step = None


async def run_agent_with_selective_steps(
    query: str, show_thinking=True, show_search=True, show_final=True
):
    """Run agent with selective step display"""

    # Create callback handler with display preferences
    callback_handler = EnhancedChainlitCallbackHandler()
    callback_handler.show_thinking = show_thinking
    callback_handler.show_search = show_search
    callback_handler.show_final_reasoning = show_final

    try:
        # Run the agent with our enhanced callback
        result = await cl.make_async(lambda: agent.run(query, callbacks=[callback_handler]))()

        return result

    except Exception as e:
        # Fallback with error step
        async with cl.Step(name="⚠️ Fallback Search") as error_step:
            await error_step.stream_token(f"Primary agent failed: {e!s}\n")
            await error_step.stream_token("🔄 Trying direct search...\n")

            try:
                from langchain_agent import search_3_tool

                result = await cl.make_async(search_3_tool)(query)
                await error_step.stream_token("✅ Direct search completed\n")
                return result
            except Exception as e2:
                await error_step.stream_token(f"❌ All methods failed: {e2!s}\n")
                return "No relevant information was found in the available content indices."


@cl.on_chat_start
async def on_chat_start():
    # Define the elements you want to display
    elements = [
        # cl.Image(path="./cat.jpeg", name="image1"),
        # cl.Pdf(path="./dummy.pdf", name="pdf1"),
        cl.Text(
            content="what is the status for the database migration mentioned in the q3 project plan",
            name="text1",
        ),
        cl.Text(content="What is project alpha and what are its features", name="text2"),
    ]

    # Setting elements will open the sidebar
    await cl.ElementSidebar.set_elements(elements)
    await cl.ElementSidebar.set_title("Example Questions")

    # Store user preferences in session
    cl.user_session.set("show_thinking", True)
    cl.user_session.set("show_search", True)
    cl.user_session.set("show_final", True)

    await cl.Message(
        content=(
            "🤖 **Enhanced Elastic Search Assistant**\n\n"
            "Ask questions about your enterprise content. I'll show you my reasoning process "
            "with collapsible steps that you can expand to see details.\n\n"
            "**Features:**\n"
            "- RAG backed by Elasticsearch\n"
            "- Multi Step Searches\n"
            "- Multi Hop Reasoning\n"
            "- Guardrails for the search results\n"
            "- Context-aware conversations"
        ),
        author="assistant",
    ).send()

    await cl.Message(
        content="**Controls:**",
        author="assistant",
        actions=[
            cl.Action(
                name="toggle_thinking",
                label="🧠 Toggle Thinking Steps",
                description="Show/hide reasoning steps",
                payload={"action": "toggle_thinking"},
            ),
            cl.Action(
                name="toggle_search",
                label="🔍 Toggle Search Steps",
                description="Show/hide search details",
                payload={"action": "toggle_search"},
            ),
            cl.Action(
                name="toggle_final",
                label="✅ Toggle Final Analysis",
                description="Show/hide final reasoning",
                payload={"action": "toggle_final"},
            ),
            cl.Action(
                name="clear_memory",
                label="🧹 Clear Memory",
                description="Clear conversation history",
                payload={"action": "clear_memory"},
            ),
            cl.Action(
                name="memory_stats",
                label="📊 Memory Stats",
                description="Show memory usage",
                payload={"action": "memory_stats"},
            ),
        ],
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    try:
        # Get user preferences
        show_thinking = cl.user_session.get("show_thinking", True)
        show_search = cl.user_session.get("show_search", True)
        show_final = cl.user_session.get("show_final", True)

        # Run agent with selective steps
        result = await run_agent_with_selective_steps(
            message.content,
            show_thinking=show_thinking,
            show_search=show_search,
            show_final=show_final,
        )

        # Send final answer
        await cl.Message(content=f"**Answer:**\n{result}", author="assistant").send()

    except Exception as e:
        await cl.Message(content=f"Sorry, I encountered an error: {e!s}", author="assistant").send()


# Action handlers for step display toggles
@cl.action_callback("toggle_thinking")
async def toggle_thinking(action):
    current = cl.user_session.get("show_thinking", True)
    cl.user_session.set("show_thinking", not current)
    status = "enabled" if not current else "disabled"
    await cl.Message(content=f"🧠 Thinking steps {status}", author="assistant").send()
    await action.remove()


@cl.action_callback("toggle_search")
async def toggle_search(action):
    current = cl.user_session.get("show_search", True)
    cl.user_session.set("show_search", not current)
    status = "enabled" if not current else "disabled"
    await cl.Message(content=f"🔍 Search steps {status}", author="assistant").send()
    await action.remove()


@cl.action_callback("toggle_final")
async def toggle_final(action):
    current = cl.user_session.get("show_final", True)
    cl.user_session.set("show_final", not current)
    status = "enabled" if not current else "disabled"
    await cl.Message(content=f"✅ Final analysis {status}", author="assistant").send()
    await action.remove()


@cl.action_callback("clear_memory")
async def handle_clear_memory(action):
    await cl.make_async(clear_memory)()
    await cl.Message(content="🧹 Memory cleared!", author="assistant").send()
    await action.remove()


@cl.action_callback("memory_stats")
async def handle_memory_stats(action):
    stats = await cl.make_async(get_memory_stats)()

    # Get current display settings
    show_thinking = cl.user_session.get("show_thinking", True)
    show_search = cl.user_session.get("show_search", True)
    show_final = cl.user_session.get("show_final", True)

    msg = (
        f"📊 **System Status:**\n\n"
        f"**Memory:**\n"
        f"- Type: {stats['memory_type']}\n"
        f"- Messages: {stats['chat_memory_length']}\n"
        f"- Window Size: {stats['k']}\n\n"
        f"**Display Settings:**\n"
        f"- Thinking Steps: {'✅' if show_thinking else '❌'}\n"
        f"- Search Steps: {'✅' if show_search else '❌'}\n"
        f"- Final Analysis: {'✅' if show_final else '❌'}"
    )
    await cl.Message(content=msg, author="assistant").send()
    await action.remove()


@cl.on_chat_end
async def on_chat_end():
    await cl.make_async(clear_memory)()
    await cl.Message(
        content="👋 **Session ended.** Conversation memory cleared.", author="assistant"
    ).send()
