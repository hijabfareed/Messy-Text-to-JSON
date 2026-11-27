
# Domain: Job Posts
# File: extract.py
# Purpose: Extract structured job information using
# Gemini API and validate it using Pydantic.

# 1. IMPORT REQUIRED LIBRARIES

# Read environment variables.
import os

# Handle standard error and program exit.
import sys

# Accept input from the command line.
import argparse

# Work with file and folder paths.
from pathlib import Path

# Load environment variables from the .env file.
from dotenv import load_dotenv

# Import Google's Gemini SDK.
from google import genai
from google.genai import types

# Handle Pydantic validation errors.
from pydantic import ValidationError

# Import our job information schema.
from schema import Extracted


# 2. LOAD ENVIRONMENT VARIABLES

# Find the root directory of this project.
BASE_DIR = Path(__file__).resolve().parent

# Load the .env file from the project root.
load_dotenv(BASE_DIR / ".env")

# Read the Gemini API key.
API_KEY = os.getenv("GEMINI_API_KEY")

# Read the Gemini model name.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

# Maximum total attempts allowed by the assignment.
MAX_ATTEMPTS = 3


# 3. LOAD THE EXTRACTION PROMPT

def load_prompt():

    # Locate the separate extraction prompt file.
    prompt_path = BASE_DIR / "prompts" / "extract.txt"

    # Read and return the prompt as a string.
    return prompt_path.read_text(encoding="utf-8")


# 4. CREATE THE GEMINI API FUNCTION

def ask(client, prompt, messy_text, feedback):

    # Prepare the input text for Gemini.
    # Include validation feedback if a previous attempt failed.
    contents = messy_text + feedback

    # Send the request to Gemini.
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(

            # Use the instructions from the separate prompt file.
            system_instruction=prompt,

            # Request JSON instead of ordinary text.
            response_mime_type="application/json",

            # Use our Pydantic model for structured output.
            response_schema=Extracted
        )
    )

    # Return the generated response text.
    return response.text


# 5. EXTRACT AND VALIDATE JOB INFORMATION

def extract_job(messy_text):

    # Check whether the Gemini API key is available.
    if not API_KEY:
        print(
            "Error: GEMINI_API_KEY is missing.",
            file=sys.stderr
        )
        return None

    # Create the Gemini API client.
    client = genai.Client(api_key=API_KEY)

    # Load instructions from prompts/extract.txt.
    prompt = load_prompt()

    # No validation error exists before the first attempt.
    feedback = ""

    # Repeat the extraction process at most three times.
    for attempt in range(1, MAX_ATTEMPTS + 1):

        # Display attempt information on standard error.
        print(
            f"Attempt {attempt}/{MAX_ATTEMPTS}",
            file=sys.stderr
        )

        try:

            # Send the text and previous feedback to Gemini.
            response = ask(
                client,
                prompt,
                messy_text,
                feedback
            )

            # Validate Gemini's JSON using our Pydantic model.
            result = Extracted.model_validate_json(response)

            # Return the validated result.
            # Returning also stops the retry loop.
            return result

        except ValidationError as error:

            # Display the actual validation error.
            print(
                f"Validation error: {error}",
                file=sys.stderr
            )

            # Prepare feedback for the next Gemini request.
            feedback = (
                "\n\nPrevious response failed validation."
                f"\nValidation error:\n{error}"
                "\nCorrect the response according to the schema."
            )

        except Exception as error:

            # Handle other errors, such as API or network errors.
            print(
                f"API or processing error: {error}",
                file=sys.stderr
            )

    # All three attempts have failed.
    print(
        "Extraction failed after 3 attempts.",
        file=sys.stderr
    )

    return None


# 6. CREATE THE MAIN FUNCTION

def main():

    # Create a command-line argument parser.
    parser = argparse.ArgumentParser(
        description="Extract job information from messy text."
    )

    # Accept messy text as a command-line argument.
    parser.add_argument(
        "text",
        help="Messy job advertisement text"
    )

    # Read the argument provided by the user.
    args = parser.parse_args()

    # Extract and validate job information.
    result = extract_job(args.text)

    # Exit with an error status if extraction failed.
    if result is None:
        sys.exit(1)

    # Print ONLY the validated JSON to standard output.
    print(result.model_dump_json(indent=2))


# 7. RUN THE APPLICATION

# Execute main() when this file is run directly.
if __name__ == "__main__":
    main()
