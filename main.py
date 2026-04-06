import os
import argparse
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
import prompts
from call_function import available_functions, call_function

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise RuntimeError
    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    for _ in range(20):
        time.sleep(3)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=prompts.system_prompt,
                temperature=0))
    
        for candidate in response.candidates:
            messages.append(candidate.content)
    
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
        if response.function_calls is None:
            print(f"Response: \n{response.text}")
            break
    
        function_results = []
        for f in response.function_calls:
            function_call_result = call_function(f, args.verbose)
            if not function_call_result.parts:
                raise Exception("No parts in function call result")
            if function_call_result.parts[0].function_response is None:
                raise Exception("No function response in parts")
            if function_call_result.parts[0].function_response.response is None:
                raise Exception("No response in function response")
            function_results.append(function_call_result.parts[0])
            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
    
        messages.append(types.Content(role="user", parts=function_results))

    else:
        print("Max iterations reached, agent did not produce a final response")
        exit(1)

if __name__ == "__main__":
    main()
