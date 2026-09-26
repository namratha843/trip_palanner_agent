

class ConfigLoader:
    def __init(self):
        pass


class ModelLoader(BaseModel):
    model_provider: Literal["openai", "groq"] = "groq"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def model_post_init(self, _context: Any) -> None:
        self.config = ConfigLoader()


    class Config:
        arbitrary_types_allowed = True


    def load_llm(self):
        """
        load and return the llm model
        """
        print("llm loading...")
        print(f"Loading model from provider: {self.model_provider}")
        if self.model_provider == "groq":
            print("Loading Groq model...")
            groq_api_key = os.getenv("GROQ_API_KEY")
            model_name = self.config['llm']['groq']['model_name']
            llm = ChatGroq(model = model_name, api_key = groq_api_key)
        elif self.model_provider == "openai":
            print("Loading OpenAI model...")
            model_name = self.config['llm']['openai']['model_name']
            llm = ChatOpenAI(model_name=model_name)
        return llm