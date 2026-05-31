import os
import argparse
import sys
from prompts import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import available_functions,call_function

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt",type=str,help="User prompt")
    parser.add_argument("--verbose",action="store_true",help="Enable verbose output")
    args = parser.parse_args()
    messages: list[types.Content] = [
        types.Content(role="user",parts=[types.Part(text=args.user_prompt)])
    ]
    config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt,temperature=0
)
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("environment variable not found")
    client = genai.Client(api_key=api_key)
    for _ in range(20):
        function_call_results = []
        response = client.models.generate_content(model="gemini-2.5-flash",contents=messages,config=config)
        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)
        meta_data = response.usage_metadata
        if meta_data is None:
            raise RuntimeError("metadata is empty")
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {meta_data.prompt_token_count}\nResponse tokens: {meta_data.candidates_token_count}\n")
        if response.function_calls is None:
            print(response.text)
            return
        else:
            for function in response.function_calls:
                function_call_result = call_function(function,verbose=args.verbose)
                if not function_call_result.parts:
                    raise Exception("Error list is empty")
                if function_call_result.parts[0].function_response is None:
                    raise Exception("Function Response object is empty")
                if function_call_result.parts[0].function_response.response is None:
                    raise Exception("Response is empty")
                function_call_results.append(function_call_result.parts[0])
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
            messages.append(types.Content(role="user",parts=function_call_results))
    print("Error, looped through functions")
    sys.exit(1)
if __name__ == "__main__":
    main()