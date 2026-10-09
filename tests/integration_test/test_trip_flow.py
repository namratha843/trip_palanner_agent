import sys
from pathlib import Path

# Must run before importing trip_planner
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from trip_planner.agents.trip_flow import GraphBuilder


class FakeLLM(Runnable):
    def __init__(self, tool_name, tool_args, final_answer):
        self.call_count = 0
        self.tool_name = tool_name
        self.tool_args = tool_args
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
                        "args": self.tool_args,
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
        {"location": "New York"},
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
        {"location": "Paris"},
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



def test_agent_currency_conversion_workflow():
    fake_llm = FakeLLM(
        "convert_currency",
        {
            "amount": 100,
            "from_currency": "USD",
            "to_currency": "INR",
        },
        "100 USD = 8300 INR.",
    )

    graph = GraphBuilder(fake_llm).build_graph()

    result = graph.invoke({
        "messages": [
            HumanMessage(content="Convert 100 USD to INR.")
        ]
    })

    messages = result["messages"]

    # The agent requests the currency tool.
    assert messages[1].tool_calls[0]["name"] == "convert_currency"
    assert messages[1].tool_calls[0]["args"]["amount"] == 100
    assert messages[1].tool_calls[0]["args"]["from_currency"] == "USD"
    assert messages[1].tool_calls[0]["args"]["to_currency"] == "INR"

    # The tool actually executes and returns the conversion.
    assert messages[2].type == "tool"
    assert "8300.00 INR" in messages[2].content

    # The agent produces a final answer.
    assert isinstance(messages[3], AIMessage)
    assert "8300" in messages[3].content


def test_agent_expense_calculator_workflow():
    fake_llm = FakeLLM(
        "calculate_total_expense",
        {"expenses": [6000, 3000, 2000, 1500]},
        "The total trip expense is 12500.",
    )

    graph = GraphBuilder(fake_llm).build_graph()

    result = graph.invoke({
        "messages": [
            HumanMessage(
                content="Calculate my trip expenses: hotel 6000, food 3000, "
                        "transport 2000, activities 1500."
            )
        ]
    })

    messages = result["messages"]

    # Agent requests the correct tool with the correct arguments.
    assert messages[1].tool_calls[0]["name"] == "calculate_total_expense"
    assert messages[1].tool_calls[0]["args"]["expenses"] == [
        6000, 3000, 2000, 1500
    ]

    # The real Python tool calculates the total.
    assert messages[2].type == "tool"
    assert "12500.00" in messages[2].content

    # Agent produces a final response.
    assert isinstance(messages[3], AIMessage)
    assert "12500" in messages[3].content
