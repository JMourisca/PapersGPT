import argparse
from dotenv import load_dotenv
from processor import Processor
from utils import Models, Prompts, AnsiCodes

load_dotenv()

parser = argparse.ArgumentParser("Process PDFs with ChatGPT")
parser.add_argument("-p", "--prompt", default="summary", help="Type of prompt. Default: summary", choices=Prompts.get_all().keys())
parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Model to be used. Default: gpt-3.5-turbo", choices=Models.get_all().keys())
parser.add_argument("-d", "--directory", default="toprocess", help="Folder with the files to be processed. Default: toprocess")
parser.add_argument("-mt", "--max-tokens", default=0, help="Max tokens. Default: The model's limit.", type=int)
parser.add_argument("-t", "--type", default="tokens", help="Whether the process is by page or by number of tokens. Default: tokens", choices=["page", "tokens"])

args = parser.parse_args()

directory = args.directory
model = args.model
prompt = args.prompt
max_tokens = args.max_tokens
page_tokens = args.type

if max_tokens > Models.get_model_max_tokens(model):
    print(f"{AnsiCodes.RED}[ERROR] Your max tokens, {max_tokens}, is greater than the model {model}'s max token, {Models.get_model_max_tokens(model)}.{AnsiCodes.RESET}")
    exit()
elif max_tokens <= 0:
    max_tokens = Models.get_model_max_tokens(model)
    print(f"{AnsiCodes.YELLOW}[INFO] Defaulting max tokens to {model}'s max token, {max_tokens}.{AnsiCodes.RESET}")

processor = Processor(directory, model, prompt, max_tokens, page_tokens)
processor.execute()
