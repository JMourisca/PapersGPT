class AnsiCodes:
    # ANSI escape codes for colors
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # ANSI escape codes for styles
    BOLD = "\033[1m"
    ITALIC = "\033[3m"


class Models:
    _MODELS = {
        "gpt-4": {
            "input": 0.03,
            "output": 0.06,
            "max_tokens": 4000
        },
        "gpt-4-32k": {
            "input": 0.06,
            "output": 0.12,
            "max_tokens": 32000
        },
        "gpt-3.5-turbo": {
            "input": 0.0015,
            "output": 0.002,
            "max_tokens": 8000            
        }, 
        "gpt-3.5-turbo-16k": {
            "input": 0.0030,
            "output": 0.004,
            "max_tokens": 16000  
        }
    }
    
    @classmethod
    def get_model_input(cls, model_name):
        return cls._MODELS.get(model_name, {}).get("input")

    @classmethod
    def get_model_output(cls, model_name):
        return cls._MODELS.get(model_name, {}).get("output")
    
    @classmethod
    def get_model_max_tokens(cls, model_name):
        return cls._MODELS.get(model_name, {}).get("max_tokens")
    
    @classmethod
    def get_all(cls):
        return cls._MODELS
    

class Prompts:
    _PROMPTS = {
        "summary": {
            "system": "You are a helpful research assistant.", 
            "user": "Please, summarize the following text for a university-level understanding: "

        },
        "key-points": {
            "system": "You are a helpful research assistant.", 
            "user": "Please, summarize the key points of the following text for a university-level understanding: "
        },
        "bullet-points": {
            "system": "You are a helpful research assistant.", 
            "user": "Please, summarize the following text in bullet points for a university-level understanding: "
        },
        "extractive": {
            "system": "You are a helpful research assistant.", 
            "user": "Using extractive summarization, please summarize the main points of this report: "
        },
        "research": {
            "system": "You are a helpful research assistant.", 
            "user": "Please, create a detailed summary of this research paper, highlighting its methodology and findings: "
        },
        "eli5": {
            "system": "You are a helpful research assistant.", 
            "user": "Please, ELI5 these papers: "
        },
        "analysis": {
            "system": "You are a university professor.", 
            "user": "Please, analyse and grade my assignment: "
        },
        "empty": {
            "system": "You are a business analyst.", 
            "user": "Please tell explain the Siemens Approach to digitalization according to this article: "
        }
    }

    @classmethod
    def get_prompt(cls, prompt_type):
        return cls._PROMPTS.get(prompt_type)["user"]
    

    @classmethod
    def get_system(cls, prompt_type):
        return cls._PROMPTS.get(prompt_type)["system"]
    

    @classmethod
    def get_all(cls):
        return cls._PROMPTS