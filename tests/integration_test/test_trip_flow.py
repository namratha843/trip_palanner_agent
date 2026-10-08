import sys
from pathlib import Path

# Must run before importing trip_planner
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from trip_planner.agents.trip_flow import GraphBuilder


class FakeLLM(Runnable):
    def __init__(self, tool_name, location, final_answer):
        self.call_count = 0
        self.tool_name = tool_name
        self.location = location
        self.final_answer = final_answer

    def bind_tools(self, tools):
        return self

    def invoke(self, input, config=None, **kwargs):
        self.call_count += 1

        # First call: the LLM asks for the tool
        if self.call_count == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": self.tool_name,
                        "args": {"location": self.location},  # fixed: flat string
                        "id": "test-call-1",
                        "type": "tool_call",
                    }
                ],
            )

        # Second call: tool result is available, give the final answer
        return AIMessage(content=self.final_answer)


def test_agent_tool_workflow():
    fake_llm = FakeLLM(
        "get_weather_info",
        "New York",
        "The weather in New York is sunny and 25°C.",
    )
    graph = GraphBuilder(fake_llm).build_graph()

    result = graph.invoke(
        {"messages": [HumanMessage(content="What is the weather in New York?")]}
    )

    assert fake_llm.call_count == 2

    messages = result["messages"]
    assert len(messages) == 4

    assert isinstance(messages[0], HumanMessage)

    assert isinstance(messages[1], AIMessage)
    assert messages[1].tool_calls[0]["name"] == "get_weather_info"
    assert messages[1].tool_calls[0]["args"]["location"] == "New York"

    assert messages[2].type == "tool"
    assert "New York" in messages[2].content

    assert isinstance(messages[3], AIMessage)
    assert "New York" in messages[3].content


def test_agent_place_search_workflow():
    fake_llm = FakeLLM(
        "get_places",
        "Paris",
        "You should visit the Eiffel Tower and the Louvre in Paris.",
    )
    graph = GraphBuilder(fake_llm).build_graph()

    result = graph.invoke(
        {"messages": [HumanMessage(content="What places should I visit in Paris?")]}
    )

    messages = result["messages"]
    assert len(messages) == 4
    assert messages[1].tool_calls[0]["name"] == "get_places"
    assert messages[1].tool_calls[0]["args"]["location"] == "Paris"
    assert messages[2].type == "tool"
    assert "Paris" in messages[2].content
    assert isinstance(messages[3], AIMessage)