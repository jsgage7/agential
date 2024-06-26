"""Functional module for Self-Refine."""

from langchain.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages.human import HumanMessage

from agential.cog.prompts.self_refine import (
    SELF_REFINE_FEEDBACK_INSTRUCTION_GSM8K,
    SELF_REFINE_INSTRUCTION_GSM8K,
    SELF_REFINE_REFINE_INSTRUCTION_GSM8K,
)


def _build_agent_prompt(
    question: str,
    examples: str,
    prompt: str = SELF_REFINE_INSTRUCTION_GSM8K,
) -> str:
    """Constructs a formatted prompt for the agent based on the question and provided fewshot examples.

    Parameters:
        question (str): The main question for which the agent is to generate an answer.
        examples (str): Pre-formatted few-shot examples that provide context for the question.
        prompt (str): The base template string into which all other components will be inserted. This
            template must have placeholders for the 'question', 'examples', 'question_prefix',
            'intra_example_sep', and 'answer_prefix'. Defaults to SELF_REFINE_INSTRUCTION_GSM8K.

    Returns:
        str: The fully constructed and formatted prompt ready to be processed by the agent.
    """
    prompt = PromptTemplate.from_template(prompt).format(
        question=question,
        examples=examples,
    )
    return prompt


def _prompt_agent(
    llm: BaseChatModel,
    question: str,
    examples: str,
    prompt: str = SELF_REFINE_INSTRUCTION_GSM8K,
) -> str:
    """Generates a response from the LLM based on a given question with fewshot examples.

    This function creates a prompt using `_build_agent_prompt` and then gets the LLM's
    output.

    Args:
        llm (BaseChatModel): The language model to be prompted.
        question (str): The main question for which the agent is to generate an answer.
        examples (str): Pre-formatted few-shot examples that provide context for the question.
        prompt (str): The base template string into which all other components will be inserted. This
            template must have placeholders for the 'question', 'examples', 'question_prefix',
            'intra_example_sep', and 'answer_prefix'. Defaults to SELF_REFINE_INSTRUCTION_GSM8K.

    Returns:
        str: The processed response from the language model.
    """
    prompt = _build_agent_prompt(question=question, examples=examples, prompt=prompt)
    out = llm(
        [
            HumanMessage(
                content=prompt,
            )
        ]
    ).content
    assert isinstance(out, str)
    return out.strip()


def _build_feedback_prompt(
    examples: str, solution: str, prompt: str = SELF_REFINE_FEEDBACK_INSTRUCTION_GSM8K
) -> str:
    """Builds feedback prompt.

    This function compiles a detailed prompt with contextual examples and a specific question format, then
    prompts the language model for a response.

    Parameters:
        llm (BaseChatModel): The language model to prompt for a response.
        question (str): The question to be answered by the language model.
        examples (str): Pre-formatted examples that provide context to the question.
        prompt (str): Prompt template string. Defaults to SELF_REFINE_FEEDBACK_INSTRUCTION_GSM8K.

    Returns:
        str: The language model's response to the question, trimmed of extraneous whitespace.
    """
    prompt = PromptTemplate.from_template(prompt).format(
        examples=examples,
        solution=solution,
    )
    return prompt


def _prompt_feedback(
    llm: BaseChatModel,
    examples: str,
    solution: str,
    prompt: str = SELF_REFINE_FEEDBACK_INSTRUCTION_GSM8K,
) -> str:
    """Requests feedback from the language model based on a provided solution and contextual examples.

    A feedback prompt is constructed using the provided examples and solution.

    Parameters:
        llm (BaseChatModel): The language model to prompt for feedback.
        examples (str): Contextual examples related to the solution.
        solution (str): The solution for which feedback is being sought.
        prompt (str): Prompt template string. Defaults to SELF_REFINE_FEEDBACK_INSTRUCTION_GSM8K.

    Returns:
        str: The language model's feedback, with no leading or trailing whitespace.
    """
    prompt = _build_feedback_prompt(examples=examples, solution=solution, prompt=prompt)
    out = llm(
        [
            HumanMessage(
                content=prompt,
            )
        ]
    ).content
    assert isinstance(out, str)
    return out.strip()


def _build_refine_prompt(
    examples: str,
    solution: str,
    feedback: str,
    prompt: str = SELF_REFINE_REFINE_INSTRUCTION_GSM8K,
) -> str:
    """Builds a refinement prompt.

    Parameters:
        llm (BaseChatModel): The language model to prompt for a response.
        question (str): The question to be answered by the language model.
        examples (str): Pre-formatted examples that provide context to the question.
        feedback (str): The feedback on the solution.
        prompt (str): Prompt template string. Defaults to SELF_REFINE_REFINE_INSTRUCTION_GSM8K.

    Returns:
        str: The language model's response to the question, trimmed of extraneous whitespace.
    """
    prompt = PromptTemplate.from_template(prompt).format(
        examples=examples, solution=solution, feedback=feedback
    )
    return prompt


def _prompt_refine(
    llm: BaseChatModel,
    examples: str,
    solution: str,
    feedback: str,
    prompt: str = SELF_REFINE_REFINE_INSTRUCTION_GSM8K,
) -> str:
    """Refines solution based on feedback from the language model.

    A refine prompt is constructed using the provided solution, examples, and feedback.

    Parameters:
        llm (BaseChatModel): The language model to prompt for feedback.
        examples (str): Contextual examples related to the solution.
        solution (str): The solution for which feedback is being sought.
        feedback (str): The feedback on the solution.
        prompt (str): Prompt template string. Defaults to SELF_REFINE_REFINE_INSTRUCTION_GSM8K.

    Returns:
        str: The language model's feedback, with no leading or trailing whitespace.
    """
    prompt = _build_refine_prompt(
        examples=examples, solution=solution, feedback=feedback, prompt=prompt
    )
    out = llm(
        [
            HumanMessage(
                content=prompt,
            )
        ]
    ).content
    assert isinstance(out, str)
    return out.strip()


def _is_halted(feedback: str) -> bool:
    """Returns True if 'it is correct' is in feedback.lower().

    Parameters:
        feedback (str): The feedback string.

    Returns:
        bool: True if 'it is correct' in feedback.lower() else False.
    """
    return "it is correct" in feedback.lower()
