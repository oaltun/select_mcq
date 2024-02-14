from pathlib import Path
import random
import re
from typing import List
from rich import print

import typer
from typer import Option


from yxlsx.schema.question_schema import Choice, ChoiceType, MultipleChoiceQuestion
from pathlib import Path
import random
from subprocess import run
from typing import List
from toolz import take


from pathlib import Path
import re
import random


app = typer.Typer()


def extract_question_tex_list(latex_file_path):
    # Open and read the LaTeX file
    with open(latex_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define the regular expression pattern for questions
    # This pattern looks for \question followed by any text up to the next \question or \end{questions}
    pattern = r'\\question(.*?)(?=\\question|\\end\{questions\})'

    # Use regular expression to find all matches
    matches = re.findall(pattern, content, re.DOTALL)

    # Clean and return the questions
    questions = [match.strip() for match in matches]
    return questions


def latex_to_mcq(latex_question: str) -> MultipleChoiceQuestion:
    # Extract the question text
    question_match = re.search(r'\\question\s*(.*?)\\begin\{(choices|oneparchoices)\}', latex_question, re.DOTALL)
    if not question_match:
        raise ValueError("Question text not found in the provided string.")
    question_text = question_match.group(1).strip()

    # Determine choices type
    choices_type_match = re.search(r'\\begin\{(choices|oneparchoices)\}', latex_question)
    if not choices_type_match:
        raise ValueError("Choices type not found in the provided string.")
    choices_type = choices_type_match.group(1).strip()
    pydantic_choices_type = ChoiceType.CHOICES if choices_type == "choices" else ChoiceType.ONE_PAR_CHOICES

    # Extract the choices
    choices_latex_match = re.search(
        rf'\\begin\{{{choices_type}\}}(.*?)\\end\{{{choices_type}\}}', latex_question, re.DOTALL
    )
    if not choices_latex_match:
        raise ValueError("Choices not found in the provided string.")
    choices_latex = choices_latex_match.group(1).strip()
    choices_matches = re.findall(r'\\(correct)?choice\s*(.*?)$', choices_latex, re.MULTILINE | re.IGNORECASE)

    choices = [Choice(text=match[1].strip(), is_correct=(match[0].lower() == 'correct')) for match in choices_matches]

    correct = any(choice.is_correct for choice in choices)
    if not correct:
        print("latex_question: ", latex_question, "choices:", choices)
        raise ValueError("No correct choice found in the provided question.")

    # Extract the solution if present
    solution_match = re.search(r'\\begin\{solution\}(.*?)\\end\{solution\}', latex_question, re.DOTALL)
    solution = solution_match.group(1).strip() if solution_match else None

    # Construct and return the Pydantic object
    return MultipleChoiceQuestion(
        question=question_text, choices=choices, choices_type=pydantic_choices_type, solution=solution
    )


def mcq_to_latex(mcq: MultipleChoiceQuestion) -> str:
    # State
    choices_env = "choices" if mcq.choices_type == ChoiceType.CHOICES else "oneparchoices"

    # Start with the question
    latex = f"\\question\n{mcq.question}\n"

    # Add the choices
    latex += f"\\begin{{{choices_env}}}\n"
    for choice in mcq.choices:
        choice_prefix = "correctchoice" if choice.is_correct else "choice"
        latex += f"\\{choice_prefix} {choice.text}\n"
    latex += f"\\end{{{choices_env}}}\n"

    # Add the solution if it exists
    if mcq.solution:
        latex += f"\\begin{{solution}}\n{mcq.solution}\n\\end{{solution}}\n"

    return latex


def fallback(if_correct, if_false, condition):
    """new if condition else"""
    if condition:
        return if_correct
    else:
        return if_false


def ternary(condition, if_correct, if_false):
    """new if condition else default"""
    if condition:
        return if_correct
    else:
        return if_false


def return_raise(e):
    raise e
    return -1


def shuffle_mcq_list(mcq_list: List[MultipleChoiceQuestion]):
    return_list = mcq_list
    for i, mcq in enumerate(return_list):
        choices = mcq.choices
        random.shuffle(choices)
        return_list[i].choices = choices
    random.shuffle(return_list)
    return return_list


def render_document(
    dst,
    questions,
    key_rep,
    tpl_str,
    middle_str,
    key_find,
    answer_switch_placeholder,
    answer_switch,
):
    text_questions_str = map(mcq_to_latex, questions)
    text_questions = '\n\n'.join(text_questions_str)
    text_full = tpl_str.replace(middle_str, text_questions)
    text_full = text_full.replace(key_find, key_rep)
    text_full = text_full.replace(answer_switch_placeholder, answer_switch)

    Path(dst).write_text(text_full)
    try:
        cwd = Path(dst).parent
        filename = Path(dst).name
        run(["lualatex", filename], cwd=cwd, capture_output=False)
        run(["lualatex", filename], cwd=cwd, capture_output=False)
        run(["lualatex", filename], cwd=cwd, capture_output=False)
    except Exception as e:
        print(e)


@app.command()
def select(
    out_dir: Path = Option(Path('/home/o/repo/yxlsx/tex_exam/out'), help="Path to output dir."),
    shuffle_options_enabled: bool = Option(True, help="options are to be shuffled?"),
    shuffle_questions_enabled: bool = Option(True, help="questions are to be shuffled?"),
    reverse_questions_enabled: bool = Option(True, help="questions are to be reversed?"),
    keys: List[str] = Option(["A", "B", "C", "D"], help="keys/exam-versions to generate"),
    tpl_path: Path = Option(Path("/home/o/repo/yxlsx/tex_exam/tpl/main.tex"), help="path to latex template"),
    questions_placeholder: str = Option(
        r"\input{questions.tex}", help="str that will be replaced by questions in the template"
    ),
    answer_switch_placeholder: str = Option(
        r"\input{print_answers_or_not.tex}", help="str that will be replaced by '\printanswers' or '% \printanswers'"
    ),
    key_find: str = Option(rf"""\newcommand{{\coursegroup}}{{A}}""", help="path to latex template"),
) -> None:
    tpl_str = tpl_path.read_text()
    dbs = [
        dict(path='/home/o/repo/yxlsx/tex_exam/db/statistics_baron_ch_9_10_11_but.tex', count=10),
    ]

    def extract_mcq_list(dbs):
        for i, db in enumerate(dbs):
            texes = extract_question_tex_list(db['path'])
            if len(texes) < db['count']:
                raise IndexError
            dbs[i]['mcq_list'] = list(map(lambda tex: latex_to_mcq('\\question ' + tex), texes))
        return dbs

    dbs = extract_mcq_list(dbs)

    for key in keys:
        questions = []
        for i, db in enumerate(dbs):
            count = db['count']

            full_list = db['mcq_list']
            if shuffle_questions_enabled:
                shuffle_mcq_list(full_list)

            if len(full_list) < count:
                raise IndexError
            if count == -1:
                selected = full_list
            else:
                selected = take(count, full_list)
            questions.extend(selected)
        random.shuffle(questions)
        render_document(
            dst=f"{out_dir}/key{key}questions.tex",
            questions=questions,
            key_rep=rf"\newcommand{{\coursegroup}}{{{key}}}",
            tpl_str=tpl_str,
            middle_str=questions_placeholder,
            key_find=key_find,
            answer_switch_placeholder=answer_switch_placeholder,
            answer_switch='% \printanswers',
        )
        render_document(
            dst=f"{out_dir}/key{key}solutions.tex",
            questions=questions,
            key_rep=rf"\newcommand{{\coursegroup}}{{{key}}}",
            tpl_str=tpl_str,
            middle_str=questions_placeholder,
            key_find=key_find,
            answer_switch_placeholder=answer_switch_placeholder,
            answer_switch='\printanswers',
        )
