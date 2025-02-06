import asyncio
import json
from typing import Any, Dict, List, Optional

from openai import OpenAI


class OpenAIService:
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4_VISION = "gpt-4-vision-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"

    ASSISTANT_SYS_PROMPT = (
        "You are a helpful Data Engineer that responds in JSON format."
    )

    def __init__(self, api_key=None):
        if api_key is None:
            raise Exception("API key is required")
        self.client = OpenAI(api_key=api_key)

    async def call_gpt_api_non_streamed(
        self,
        text: str,
        model: str = GPT_4_TURBO,
        sys_prompt: str = ASSISTANT_SYS_PROMPT,
        response_type: str = "json_object",
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[Any] = None,
        prev_messages: Optional[List[Dict]] = None,
    ) -> Any:
        """
        Makes a non-streamed API call to GPT with comprehensive error handling.
        Returns processed response based on specified response_type and tool_choice.
        """
        try:
            # Each step is broken into a method that can throw meaningful exceptions
            messages = self._prepare_message_list(text, sys_prompt, prev_messages)
            request_params = self._build_request_params(
                model, messages, tools, tool_choice
            )
            response = await self._make_api_call(request_params)
            return await self._process_response(response, response_type, tool_choice)
        except Exception as e:
            # Top-level error handling preserves the original exception chain
            print(f"Error calling OpenAI API: {e!s}")
            raise ValueError(
                str(e) or "Unexpected error occurred while processing request"
            ) from e

    def _prepare_message_list(
        self, text: str, sys_prompt: str, prev_messages: Optional[List[Dict]]
    ) -> List[Dict]:
        """
        Prepares and validates the message list for the API call.
        Raises ValueError if message content is empty.
        """
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})

        if prev_messages:
            messages.extend(
                [msg for msg in prev_messages if msg.get("content", "").strip()]
            )
        else:
            messages.append({"role": "user", "content": text})

        if not text.strip() and not prev_messages:
            raise ValueError("Message content cannot be empty")

        return messages

    def _build_request_params(
        self,
        model: str,
        messages: List[Dict],
        tools: Optional[List[Dict]],
        tool_choice: Optional[Any],
    ) -> Dict:
        """
        Builds the parameter dictionary for the API request.
        Includes tools and tool_choice if specified.
        """
        request_params = {
            "model": model,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        if tools:
            request_params["tools"] = tools
            if tool_choice:
                request_params["tool_choice"] = tool_choice

        return request_params

    async def _make_api_call(self, request_params: Dict) -> Any:
        """
        Makes the actual API call with error handling for context length.
        Preserves the original exception chain using 'from'.
        """
        try:
            return await self.client.chat.completions.create(**request_params)
        except Exception as e:
            if "maximum context length" in str(e).lower():
                raise ValueError(
                    "Request too long. Please break it into smaller parts."
                ) from e
            raise

    async def _process_response(
        self, response: Any, response_type: str, tool_choice: Optional[Any]
    ) -> Any:
        """
        Processes the API response based on tool_choice and response_type.
        Handles JSON parsing and validation.
        """
        if tool_choice:
            tool_response = response.choices[0].message.tool_calls[0].function
            if not tool_response:
                raise ValueError("Failed to generate expected tool response format")
            return tool_response

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Received empty response")

        if response_type == "json_object":
            try:
                return json.dumps(json.loads(content))
            except json.JSONDecodeError as e:
                raise ValueError("Failed to generate valid JSON response") from e

        return content


async def main():
    llm = OpenAIService(api_key="")
    res = await llm.call_gpt_api_non_streamed(
        text="""
Below is a python code. Please go through the code and give me the file or data connections that are being made/created in the code.

from preswald import text, connect, view, slider, plotly, connections, Workflow, workflow_dag
import pandas as pd
import plotly.express as px

# Create workflow
workflow = Workflow()

# Title
text("# Earthquake Analytics Dashboard 🌍")

# Load and connect data
connection_name = pd.read_csv("https://gist.githubusercontent.com/jayanth-kumar-morem/dbb6ed836d0744380f6072a0f660a896/raw/6e7633a61fee3d906364cf9f54c717f75bcf1f40/earthquake_data.csv")


engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")

        """,
        model=llm.GPT_4_TURBO,
        sys_prompt=llm.ASSISTANT_SYS_PROMPT,
        response_type="json_object",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "extract_connections",
                    "description": "Extract the file or data connections that are being made/created in the code",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "connections": {
                                "type": "array",
                                "description": "The connections that are being made/created in the code",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "The name of the connection",
                                        },
                                        "type": {
                                            "type": "string",
                                            "description": "The type of the connection",
                                        },
                                        "details": {
                                            "type": "string",
                                            "description": "Additional details about the connection",
                                        },
                                    },
                                    "required": ["name", "type", "details"],
                                },
                            }
                        },
                        "required": ["connections"],
                    },
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": "extract_connections"}},
        prev_messages=None,
    )
    # Parse the function response
    function_args = json.loads(res.arguments)
    print(function_args)


if __name__ == "__main__":
    asyncio.run(main())
