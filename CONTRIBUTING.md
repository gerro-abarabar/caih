# Contribute (for students)

The project is run on formatted reviewers that make it possible for AI Generation to create a mock test for you.

To improve this project as a student, I recommend you to **contribute to the reviewers** here's a guide on how:

## Requirements

You need to install 2 applications in your system. 

### Python and Ollama

First [Python](https://www.python.org/downloads/) (3.12 or higher) and [Ollama](https://ollama.com/). The guides on how to install it are in their respective links.

### Datalabs
Create an account in [datalabs.to](https://www.datalab.to) (Platform where you're going to convert PDF to Markdown, a simplified text).

### Project setup
Download the source code by clicking: `Code > Download Zip` or `git clone https://github.com/gerro-abarabar/caih.git` in your terminal.

#### Mac and Linux
Setup your Python environment by running `python -m venv .venv` and **activate** it by doing `source .venv/bin/activate` (`source .venv/bin/activate` for Mac and Linux)

#### Install Libraries

Install the required libraries by doing `pip install -r requirements.txt` or `pip3 install -r requirements.txt` if you're in Mac or Linux.

Install the notable language models by doing the commands:
- `ollama pull deepseek-v3.2:cloud`
- `ollama pull qwen3.5:397b-cloud`
- `ollama pull ministral-3:14b-cloud`

## Convert PDF to Markdown

Prepare your PDF reviewer, by **providing your own** or grab one from [Raw UPCAT Reviewers](https://www.kaggle.com/datasets/gerroabarabar/raw-upcat-reviewers).

As of the moment the **reviewers must not be heavilly depended on images**, because there is no known solution for it yet.

### Convert the PDF

Do the command `python data_processing/datalabs.py` (`python3 data_processing/datalabs.py` for Mac and Linux) in your terminal, and pick the reviewer you chose.

Your files will be saved in the same directory of your reviewer. A `.json` and a `.md` can be found there. 

## Check your Markdown

It's important to check your Markdown if it is correctly converted. Here are your guidelines to check if it is good to move to the next stage:

1. The questions make sense
2. The options are all present
3. The instructions are there
4. There are no images *(reviewers must not be heavilly depended on images)*
5. There are no unnecessary information (e.g. introduction, website links)

After checking that your markdown looks good, proceed with the next step.

## Convert to JSON

Paste your Markdown to [DeepSeek](https://chat.deepseek.com/) starting with this prompt:

```
Format every question of this exam, written in markdown, into json like this:
{
    "id":"question number",
    "instruction": "instruction prior to before",
    "question":"question",
    "choices":[
        "A. choice a",
        "B. choice b",
        "C. choice c",
        "D. choice d"
    ],
    "correct_answer": correct answer index (like for b, it's 1),
} 

Don't remove the latex written it it.

Markdown exam:
<Markdown>
```

Put the output from DeepSeek into a file, name it whatever you want, but let the file extension be `.json`


    As of the moment, there is no quicker way to convert to JSON

## Add explanations
Go back to the project and do `python data_processing/explanations.py` (`python3 data_processing/explanations.py` for Linux and Mac)

Pick your `.json` file and let it run until it's finished. 


## Submit your file and support the project

Go to [caih-reviewers](https://github.com/gerro-abarabar/caih-reviewers/) and submit a new issue by clicking `Issues > New Issue`

Put your source, `.pdf`, `.json`, `.md` in your issue, then click `Create`

Wait for your reviewer to be accepted into the project.

Refer to the video to do it:
<video src="assets/new_reviewer.webm" controls="controls" style="max-width: 100%;">
  Your browser does not support the video tag.
</video>

## TL;DR
1. **Convert:** PDF ➔ Markdown (using Datalabs)
2. **Clean:** Remove images and weird text.
3. **Format:** Markdown ➔ JSON (using DeepSeek)
4. **Enhance:** Add AI explanations (using our script)
5. **Submit:** Upload your files to a GitHub Issue.