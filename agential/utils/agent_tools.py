"""Utility functions providing agents with tools to use."""
import os

import requests

from langchain_community.utilities.google_search import GoogleSearchAPIWrapper


def execute_python(input_code: str) -> str:
    """Takes in Python code and executes, returning the namespace.

    Args:
        input_code (str): String representation of lines of executable python.

    Returns:
        str: A string containing the variables and values from the executed code.

    Example:
        code = "a = 1*100"
        execute(code)
        # "a = 100"
    """
    local_vars = {}
    # print(f"INPUT CODE AT BEGINNING: {input_code}")
    input_code = input_code.split(";")
    input_code = [line.strip() for line in input_code]
    input_code = "\n".join(input_code)
    # print(f"INPUT CODE ABOUT TO BE PARSED: {input_code}")
    try:
        exec(input_code, globals(), local_vars)
    except Exception as e:
        return str(e)

    # Convert the local namespace to a dictionary
    variables_dict = {
        var: local_vars[var] for var in local_vars if not var.startswith("__")
    }

    # Convert the dictionary to a string representation
    result = ", ".join([f"{key} = {value}" for key, value in variables_dict.items()])
    # print(f"LOCAL_VARS = {local_vars}")

    return result


def execute_wolfram(query: str) -> str:
    """Executes a Wolfram Alpha query and returns the results as a string.

    Args:
        query (str): The query to be sent to Wolfram Alpha.

    Returns:
        str: The result of the query as a string.
    """
    app_id = os.environ.get(
        "WOLFRAM_ALPHA_APP_ID"
    )  # Note to self, not sure how to handle testing this given the google api stuff
    if not app_id:
        return "Wolfram Alpha API key not found in environment variables. Use a different tool."

    base_url = "https://api.wolframalpha.com/v2/query"
    params = {"input": query, "format": "plaintext", "output": "JSON", "appid": app_id}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        result = response.json()
        if "queryresult" in result:
            pods = result["queryresult"]["pods"]
            output_string = ""
            for pod in pods:
                if pod["title"] != "Input interpretation":
                    output_string += pod["title"] + ":\n"
                    for subpod in pod["subpods"]:
                        output_string += subpod["plaintext"] + "\n"
            return output_string.strip()
        else:
            return "No results found using Wolfram Alpha API."
    else:
        return "Error occurred: " + str(response.status_code)


def search_google(query: str) -> str:
    """Perform a Google search for the given query and return a snippet of the top search result.

    Args:
        query (str): The search query to be performed.

    Returns:
        str: A snippet of the top search result relevant to the query.
    """
    cse_id = os.environ.get(
        "GOOGLE_CSE_ID"
    )  # Note to self, not sure how to handle testing this
    google_key = os.environ.get("GOOGLE_API_KEY")
    if not cse_id or not google_key:
        return "Google search key(s) not found in environment variables. Use a different tool."
    search = GoogleSearchAPIWrapper(google_api_key=google_key, google_cse_id=cse_id)
    search_result = search.results(query, num_results=1)[-1]
    return search_result["snippet"]


if __name__ == "__main__":
    # Example usage:
    code = """total_pages = 15 #Sheila has a 15-page research paper;finished_pages = total_pages * (1/3) #She already finished 1/3 of the paper;pages_left = total_pages - finished_pages #The pages left to write is the total minus the finished pages"""
    print(execute_python(code))
