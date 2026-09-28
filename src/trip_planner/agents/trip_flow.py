from utils.model_load import ModelLoader
from prompts.prompt import SYSTEM_PROMPT

#from trip_planner.tools.weather_info import WeatherInfoTool
#from trip_planner.tools.place_search import PlaceSerachTool
#from trip_planner.tools.calculator_tool import CalculatorTool
#from trip_planner.tools.currency_convertor import CurrencyConvertorTool

from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition


class Graphbuilder():
    def __init__(self):
        self.tools = [
            #weather_info_tool,
            #place_search_tool,
            #calculator_tool,
            #currency_convertor_tool
        ]
        self.system_prompt = SYSTEM_PROMPT

    def agent_function(self, state: MessagesState):
        """
        This function is called when the agent node is executed.
        It takes the current state as input and returns the next state.
        """
        user_question = state["messages"]
        input_question = [self.system_prompt] + user_question
        response = self.llm_with_tools.invoke(input_question)
        return {"messages": [response]}

    def build_graph(self):
        graph_builder =  StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", "tools", tools_condition)
        graph_builder.add_edge("tools","agent")
        graph_builder.add_edge("agent", END)

        self.graph = graph_builder.compile()
        return self.graph
        

    def __call__(self):
        return self.build_graph()