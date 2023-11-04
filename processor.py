import openai
import os
import tiktoken
import glob
from utils import AnsiCodes, Models, Prompts
from slugify import slugify
from PyPDF2 import PdfReader

class Processor:
    ai_initiallized = False

    def __init__(self, directory:str, model:str, prompt:str, max_tokens: int, page_tokens: str):
        self.max_tokens = max_tokens
        self.model = model
        self.prompt = Prompts.get_prompt(prompt)
        self.system = Prompts.get_system(prompt)
        self.directory = directory
        self.page_tokens = page_tokens
        

    @classmethod
    def lazy_initialize(cls):
        if not cls.ai_initiallized:
            openai.api_key = os.getenv('OPENAI_KEY')
            cls.ai_initiallized = True


    def __summary(self, final_file, tokens, total):
        print(f"\n\t└─ Summary:")
        print(f"\t\t├─ Model: \t\t{AnsiCodes.GREEN}{self.model}{AnsiCodes.RESET}")
        print(f"\t\t├─ Prompt: \t\t{AnsiCodes.GREEN}{self.prompt}{AnsiCodes.RESET}")
        print(f"\t\t├─ File: \t\t{AnsiCodes.GREEN}{final_file}{AnsiCodes.RESET}")
        print(f"\t\t├─ Total tokens: \t{AnsiCodes.GREEN}{tokens}{AnsiCodes.RESET}")
        print(f"\t\t└─ Total spent: \t{AnsiCodes.GREEN}${round(total, 6):.6f}{AnsiCodes.RESET}")

    
    def __split_into_chunks(self, text: str) -> [str]:
        max_tokens = self.max_tokens
        
        encoding = tiktoken.encoding_for_model(self.model)
        tokens = encoding.encode(text)
        chunks = [tokens[i:i+max_tokens] for i in range(0, len(tokens), max_tokens)]
        text_chunks = []

        for chunk in chunks:
            text_chunks.append(encoding.decode(chunk))
        
        return text_chunks
    

    def __chat(self, text, page_num):
        self.lazy_initialize();

        prompt = f"Return answer in Markdown. {self.prompt}"
        if page_num == 1:
            prompt = f"Return answer in Markdown and add the title as heading 1. {self.prompt}"

        messages=[
            {"role": "system", "content": self.system},
            {"role": "user", "content": f"Return answer in Markdown. {prompt}{text}"},
        ]

        try:
            self.__print_processing_chat()
            return openai.ChatCompletion.create(model=self.model, messages=messages)
            # mock = {
            #         "id": "chatcmpl-123",
            #         "object": "chat.completion",
            #         "created": 1677652288,
            #         "model": "gpt-3.5-turbo-0613",
            #         "choices": [{
            #             "index": 0,
            #             "message": {
            #             "role": "assistant",
            #             "content": "\n\nHello there, how may I assist you today?",
            #             },
            #             "finish_reason": "stop"
            #         }],
            #         "usage": {
            #             "prompt_tokens": 9,
            #             "completion_tokens": 12,
            #             "total_tokens": 21
            #         }
            #     }
            # return mock
        except openai.error.OpenAIError as e:
            # Handle general OpenAI errors
            print(f"An error occurred: {e}")
        except openai.error.RateLimitError as e:
            # Handle rate limiting specifically
            print("Rate limit exceeded, waiting before retrying...")
            # Implement retry logic or wait
        except openai.error.InvalidRequestError as e:
            # Handle invalid requests, such as invalid parameters
            print(f"Invalid request: {e}")
        except openai.error.AuthenticationError as e:
            # Handle authentication errors
            print("Authentication failed, check your API keys.")
        except Exception as e:
            # Handle other unforeseen errors
            print(f"An unexpected error occurred: {e}")

        return ""
    

    def __price(self, usage: str) -> float:
        input = (Models.get_model_input(self.model) * usage["completion_tokens"])/1000
        output = (Models.get_model_output(self.model) * usage["prompt_tokens"])/1000
        return input + output
    

    def __count_tokens(self, text: str) -> int:
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))
    

    def __execute_part(self, page_num: int, page_text: str, final_file:str):
        response = self.__chat(page_text, page_num)
        if response == "":
            return ""

        total_spent = self.__price(response["usage"])

        subtitle = "Chunk"
        if self.page_tokens == "page":            
            subtitle = "Page"

        processed_reponse = response["choices"][0]["message"]["content"]
        pdf_text = f"### {subtitle} {str(page_num)}:\n"
        pdf_text += processed_reponse + "\n\n---\n"

        with open(final_file, "a") as file:
            file.write(pdf_text)

        return total_spent

    def __print_text_information(self, max_tokens, total_tokens, total_tokens_prompt, chunks):
        print(f"\n\t├─ The text has {AnsiCodes.RED}{AnsiCodes.BOLD}{total_tokens + total_tokens_prompt}{AnsiCodes.RESET} tokens (max: {AnsiCodes.CYAN}{AnsiCodes.BOLD}{max_tokens}{AnsiCodes.RESET}). \t")
        print(f"\t├─ It will process it in {AnsiCodes.CYAN}{AnsiCodes.BOLD}{len(chunks)}{AnsiCodes.RESET} chunks of maximum {AnsiCodes.CYAN}{AnsiCodes.BOLD}{max_tokens}{AnsiCodes.RESET} tokens.")

    def __print_file_header(self, filename):
        print(f"\n─ File: {AnsiCodes.MAGENTA}{AnsiCodes.BOLD}{filename}{AnsiCodes.RESET}")

    def __print_processing_item(self, name, items, items_num):
        print(f"\r\t├─ Processing {name}: {AnsiCodes.CYAN}{AnsiCodes.BOLD}{items_num}/{items}{AnsiCodes.RESET}", end="")

    def __print_processing_chat(self):
        print(f"\n\t├─ OpenAI request...", end="")

    def __create_md_file(self, directory, model, filename):
        file_split = filename.split(".")
        final_file = f"{directory}/{slugify(file_split[0])}-{model}-processed.md"
        return final_file

    def __process_pdf_file(self, total, pdf_file_path, final_file):
        total_text = []
        reader = PdfReader(pdf_file_path)
        total_pages = len(reader.pages)
        for page_num_index, page in enumerate(reader.pages):
            page_num = page_num_index + 1
            self.__print_processing_item("page", total_pages, page_num)
            page_text = page.extract_text().lower()
            total_text.append(page_text)
        return total_text

    def __process_pdf_pages(self, total_text, final_file):
        total_spent = 0
        for index, page_text in enumerate(total_text):
            response = self.__execute_part(index + 1, page_text, final_file)                    
            if response != "":
                total_spent += response
        return total_spent
    
    def __process_pdf_chunks(self, total_text_arr, final_file):
        total_text = ' '.join(total_text_arr)
        total_tokens = self.__count_tokens(total_text)
        total_tokens_prompt = self.__count_tokens(self.prompt)
        total_all_tokens = total_tokens + total_tokens_prompt
        max_tokens = self.max_tokens                   
        chunks = self.__split_into_chunks(total_text)
        self.__print_text_information(max_tokens, total_all_tokens, total_tokens_prompt, chunks)                    
        chunk_num = 1
        total_spent = 0
        
        for chunk in chunks:
            self.__print_processing_item("chunk", len(chunks), chunk_num)
            response = self.__execute_part(chunk_num, chunk, final_file)                  
            if response == "":
                return "error"
            total_spent += response     
            chunk_num += 1
            
        return total_spent

    def execute(self):
        total = 0
        directory = self.directory
        model = self.model
        prompt = self.prompt
        page_tokens = self.page_tokens
        max_tokens = self.max_tokens

        # Find all PDF files in the directory
        pdf_files = glob.glob(directory + '/*.pdf')

        for pdf_file_path in pdf_files:
            filename = os.path.basename(pdf_file_path)
            self.__print_file_header(filename)

            # Set the string that will contain the summary                 
            total_tokens = 0

            # Open the PDF file
            final_file = self.__create_md_file(directory, model, filename)

            # Read the PDF file using PyPDF2
            total_text = self.__process_pdf_file(total, pdf_file_path, final_file)             
                        
            if page_tokens == "tokens":
                total = self.__process_pdf_chunks(total_text, final_file)
                if total == "error":
                    continue
            else:
                total = self.__process_pdf_pages(total_text, final_file)

            self.__summary(os.path.abspath(final_file), total_tokens, total)

