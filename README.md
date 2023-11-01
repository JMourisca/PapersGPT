
# PapersGPT

This is a Python project that processes all PDF files in a folder. Once the script runs, it displays the total spent in USD based on the pricing found here https://openai.com/pricing.

## Warning
Be careful with the amount of files you add to the folder you will use and their sizes. I'm not responsible for the amount spent. 

## Prerequisites

Make sure you have the latest version of Python installed. You can download it from [here](https://www.python.org/downloads/).

## Installation

### Step 1: Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/jmourisca/PapersGPT.git 
```

### Step 2: Create a Virtual Environment

Navigate to the project directory and create a Python virtual environment. This isolates the project dependencies. Run:

```bash
cd PapersGPT
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

Activate the virtual environment:

- **On macOS and Linux:**
    ```bash
    source venv/bin/activate
    ```

- **On Windows:**
    ```bash
    .\venv\Scripts\activate
    ```

### Step 4: Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### Step 5: Setup Environment Variables

Copy the `.env_sample` file and create a new `.env` file:

```bash
cp .env_sample .env
```

Now, open the `.env` file and replace the placeholder variables with your actual values.

### Step 6: Run the Script

Add the files you want to process in the ```toprocess``` folder inside this project, or the directory you will use with the -d argument.

Finally, run the script:

```bash
python main.py
```

## Usage

To use this script, you can choose from a variety of options to customize the output. Here's the basic command structure and the options you can use:

### Basic Command
```bash
python main.py [options]
```

### Options

#### `-h, --help`
Show the help message and exit.

#### `-p, --prompt {summary,key-points,bullet-points,extractive,research,eli5,analysis,empty}`
Set the type of prompt. The default is `summary`. See the section Prompts bellow for more details.

#### `-m, --model {gpt-4,gpt-3.5-turbo,gpt-3.5-turbo-16k}`
Choose the GPT model to be used. The default is `gpt-3.5-turbo`.

#### `-d, --directory DIRECTORY`
Specify the folder with the PDF files to be processed. The default folder is named `toprocess`.

#### `-mt, --max-tokens MAX_TOKENS`
Set the maximum number of tokens for the output. The default is `4000`. 

#### `-t, --type {page,tokens}`
Specify whether the processing should be done by page or by a number of tokens. The default is `tokens`. 

### Examples

1. To summarize using the default settings:
    ```bash
    python main.py
    ```

2. To summarize using GPT-4 and a custom directory:
    ```bash
    python main.py -m gpt-4 -d custom_folder
    ```

3. To create bullet-points with a maximum of 2000 tokens:
    ```bash
    python main.py -p bullet-points -mt 2000
    ```

4. To analyze by processing each page individually:
    ```bash
    python main.py -p analysis -t page
    ```

## Prompts

This script allows you to choose from various types of prompts to guide the summarization process. Here's what each type of prompt does:

### `summary`
- **System**: You are a helpful research assistant.
- **User**: Please, summarize the following text for a university-level understanding.
- **Description**: This will provide a concise summary of the given text suitable for a university-level understanding.

### `key-points`
- **System**: You are a helpful research assistant.
- **User**: Please, summarize the key points of the following text for a university-level understanding.
- **Description**: This will extract and summarize the key points of the given text.

### `bullet-points`
- **System**: You are a helpful research assistant.
- **User**: Please, summarize the following text in bullet points for a university-level understanding.
- **Description**: This will summarize the text in the form of bullet points.

### `extractive`
- **System**: You are a helpful research assistant.
- **User**: Using extractive summarization, please summarize the main points of this report.
- **Description**: This uses extractive summarization to pick out important sentences and phrases from the original text to construct a summary.

### `research`
- **System**: You are a helpful research assistant.
- **User**: Please, create a detailed summary of this research paper, highlighting its methodology and findings.
- **Description**: This will provide a comprehensive summary of a research paper, focusing on its methodology and key findings.

### `eli5`
- **System**: You are a helpful research assistant.
- **User**: Please, ELI5 these papers.
- **Description**: This will summarize the papers in a manner that's easy to understand, as if explaining it to a 5-year-old (ELI5 stands for "Explain Like I'm 5").

### `analysis`
- **System**: You are a university professor.
- **User**: Please, analyse and grade my assignment.
- **Description**: This will provide a detailed analysis and grade of your assignment, as if reviewed by a university professor.

### `empty`
- **System**: (Empty)
- **User**: (Empty)
- **Description**: No specific role or instruction is given. This is a blank template for custom queries.

## Limitations

For GPT-4, if the text is too big (more than 10k tokens), the script may crash because it will reach open ai's rate limit and I'm too lazy to handle this error. If you wanna fix it, be my guest. 