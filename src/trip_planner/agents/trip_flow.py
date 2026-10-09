from utils.model_load import ModelLoader
from prompts.prompt import SYSTEM_PROMPT

from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from trip_planner.tools.weather_info import get_weather_info
from trip_planner.tools.place_search import get_places
from trip_planner.tools.currency_convertor import convert_currency
from trip_planner.tools.total_expense import calculate_total_expense

class GraphBuilder:
    def __init__(self, llm=None):
        self.model_loader = ModelLoader()
        self.llm = llm or self.model_loader.load_llm()
        self.tools = [
            get_weather_info,
            get_places,
            convert_currency,
            calculate_total_expense
        ]
        self.system_prompt = SYSTEM_PROMPT

        if self.llm is not None:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = None

    def agent_function(self, state: MessagesState):
        if self.llm_with_tools is None:
            raise ValueError("LLM is not initialized.")

        user_question = state["messages"]
        input_question = [self.system_prompt] + user_question
        response = self.llm_with_tools.invoke(input_question)
        print(response)
        return {"messages": [response]}

    def build_graph(self):
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        

        self.graph = graph_builder.compile()
        return self.graph

    def __call__(self):
        return self.build_graph()