from openai import AsyncOpenAI
import json

from utils.error_handling import handle_openai_error


async def analyze_code(repo_contents: list, assignment_description: str, candidate_level: str, api_key: str) -> dict:
    """
    Analyze repository code using OpenAI GPT API.

    :param repo_contents: List of repository files.
    :param assignment_description: Description of the assignment.
    :param candidate_level: Candidate level (Junior, Middle, Senior).
    :param api_key: OpenAI API key.
    :return: Analysis results in a dictionary.
    """
    try:
        aclient = AsyncOpenAI(api_key=api_key)

        repo_summary = "\n".join([f"{file['name']}: {file['path']}" for file in repo_contents])

        prompt = f"""
        You are a picky and experienced code review assistant.
        
        The following is a summary of the repository contents:
        {repo_summary}
        
        Assignment Description: {assignment_description}
        Candidate Level: {candidate_level}
        
        Please analyze the repository and respond ONLY with a valid JSON object in the following format:
            {{
                "downsides": ["list of all potential issues and downsides in the code or project structure."],
                "suggestions": ["list of all suggestions for improvement (specific actions to address the downsides)."],
                "rating": "An overall rating for the repository on a scale of 1 to 10.",
                "conclusion": "string conclusion summarizing repository quality"
            }}
        
        Do not include any additional text outside of the JSON object.
        """

        response = await aclient.chat.completions.create(model="gpt-4-turbo",
                                                         messages=[
                                                             {"role": "system",
                                                              "content": "You are a code review assistant."},
                                                             {"role": "user", "content": prompt}
                                                         ])

        message_content = response.choices[0].message.content

        try:
            result = json.loads(message_content)
        except json.JSONDecodeError:
            raise ValueError("The response from OpenAI was not in the expected JSON format.")
    except Exception as e:
        handle_openai_error(e)

    print("Response from OpenAI:", result)

    return {
        "found_files": [file['name'] for file in repo_contents],
        "downsides": result.get("downsides", []),
        "suggestions": result.get("suggestions", []),
        "rating": result.get("rating", "N/A"),
        "conclusions": result.get("conclusion", "No conclusion provided.")
    }
