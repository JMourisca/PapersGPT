import PyPDF2
import openai
import os
import tiktoken
from utils import AnsiCodes, Models, Prompts
from slugify import slugify

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
    

    def __chat(self, text):
        self.lazy_initialize();

        messages=[
            {"role": "system", "content": self.system},
            {"role": "user", "content": f"{self.prompt}{text}"},
        ]

        return openai.ChatCompletion.create(model=self.model, messages=messages)
    

    def __price(self, usage: str) -> float:
        input = (Models.get_model_input(self.model) * usage["completion_tokens"])/1000
        output = (Models.get_model_output(self.model) * usage["prompt_tokens"])/1000
        return input + output
    

    def __count_tokens(self, text: str) -> int:
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))
    

    def __execute_part(self, page_num: int, page_text: str, final_file:str):
        model = self.model
        prompt = self.prompt

        response = self.__chat(page_text)
        total = self.__price(response["usage"])

        processed_reponse = response["choices"][0]["message"]["content"]
        pdf_text = f"├─ Page/Chunk {str(page_num)}:\n"
        pdf_text += processed_reponse + "\n=========\n"

        with open(final_file, "a") as file:
            file.write(pdf_text)

        return total
    
    def execute(self):
        total = 0
        directory = self.directory
        model = self.model
        prompt = self.prompt
        page_tokens = self.page_tokens
        max_tokens = self.max_tokens

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".pdf") : 
                print(f"\n─ File: {AnsiCodes.MAGENTA}{AnsiCodes.BOLD}{filename}{AnsiCodes.RESET}")

                # Set the string that will contain the summary     
                total_text = ""
                total_tokens = 0

                # Open the PDF file
                pdf_file_path = f"{directory}/{filename}"
                file_split = filename.split(".")
                final_file = f"{directory}/{slugify(file_split[0])}-{model}-processed.txt"
                
                # final_file = new_pdf_file_path.replace(os.path.splitext(new_pdf_file_path)[1], f"-{model}-processed.txt")

                # Read the PDF file using PyPDF2
                pdf_file = open(pdf_file_path, 'rb')
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Loop through all the pages in the PDF file
                total_pages = len(pdf_reader.pages)
                for page_num in range(total_pages):
                    # Extract the text from the page                
                    print(f"\r\t├─ Processing page: {AnsiCodes.CYAN}{AnsiCodes.BOLD}{page_num+1}/{total_pages}{AnsiCodes.RESET}", end="")
                    page_text = pdf_reader.pages[page_num].extract_text().lower()            
                    total_tokens += self.__count_tokens(page_text)               
                    
                    if page_tokens == "page":
                        total += self.__execute_part(page_num, page_text, final_file)                    
                    else: 
                        total_text += page_text                    
            
                pdf_file.close()
                
                if page_tokens == "tokens":
                    total_tokens = self.__count_tokens(total_text)
                    total_tokens_prompt = self.__count_tokens(prompt)
                    total_all_tokens = total_tokens + total_tokens_prompt
                    if total_all_tokens < max_tokens * 5:
                        if total_all_tokens > max_tokens:                    
                            chunks = self.__split_into_chunks(total_text)
                            print(f"\n\t├─ The text has {AnsiCodes.RED}{AnsiCodes.BOLD}{total_tokens + total_tokens_prompt}{AnsiCodes.RESET} tokens (max: {AnsiCodes.CYAN}{AnsiCodes.BOLD}{max_tokens}{AnsiCodes.RESET}). \t")
                            print(f"\t├─ It will process it in {AnsiCodes.CYAN}{AnsiCodes.BOLD}{len(chunks)}{AnsiCodes.RESET} chunks of maximum {AnsiCodes.CYAN}{AnsiCodes.BOLD}{max_tokens}{AnsiCodes.RESET} tokens.")                    
                            chunk_num = 1
                            
                            for chunk in chunks:
                                print(f"\r\t├─ Processing chunk: {AnsiCodes.CYAN}{AnsiCodes.BOLD}{chunk_num}/{len(chunks)}{AnsiCodes.RESET}", end="")
                                total += self.__execute_part(chunk_num, chunk, final_file)
                                chunk_num += 1
                        else:
                            total = self.__execute_part(1, total_text, final_file)
                    else:
                        print(f"\n\n{AnsiCodes.RED}{AnsiCodes.BOLD}Too many tokens: {total_all_tokens} and the maximum is {max_tokens}. \nThe limit is {max_tokens} * 5 so it can be done in 5 chunks.\n Increase the limit with the parameter {AnsiCodes.ITALIC}-mt <NUMBER>{AnsiCodes.RESET}{AnsiCodes.RED}{AnsiCodes.BOLD} and the model to gpt-4 with {AnsiCodes.ITALIC}-m gpt{AnsiCodes.RESET}{AnsiCodes.RED}{AnsiCodes.BOLD} if you are sure. {AnsiCodes.RESET}")
                        continue

                self.__summary(os.path.abspath(final_file), total_tokens, total)