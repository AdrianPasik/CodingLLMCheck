import string
from threading import Thread, Event
import time
import sys
import requests
import json
from colorama import init, Fore, Back, Style

init(autoreset=True)

class RESTSpinner:
    def __init__(self):
        self.chars = ['-', '\\', '|', '/']
        self.stop_event = Event()
        self.thread = None
    
    def start(self, message="Processing"):
        self.message = message
        self.stop_event.clear()
        self.thread = Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 5) + '\r')
        sys.stdout.flush()
    
    def _animate(self):
        while not self.stop_event.is_set():
            for char in self.chars:
                if self.stop_event.is_set():
                    break
                sys.stdout.write(f'\r{self.message} {char}')
                sys.stdout.flush()
                time.sleep(0.1)

class TextAnalysisItem:
    def __init__(self, text, right_strings, wrong_strings):
        self.text = text
        self.right_strings = right_strings
        self.wrong_strings = wrong_strings

def find_strings_in_prompt(text, right_strings, wrong_strings):
    found_right = []
    found_wrong = []
    for string in right_strings:
        if string in text:
            found_right.append(string)

    for string in wrong_strings:
        if string in text:
            found_wrong.append(string)
    
    return (found_right, found_wrong)


SYSTEM_PROMPT = "You are expert Software Engineer."
def get_loaded_model():
    try:
        response = requests.get("http://localhost:1234/v1/models")
        response.raise_for_status()
        models_data = response.json()
        if 'data' in models_data and len(models_data['data']) > 0:
            loaded_model = models_data['data'][0]
        else:
            print(Fore.RED + "No models found or no model currently loaded")
            return 'Unknown'
        return loaded_model.get('id', 'Unknown')
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error connecting to LM Studio API: {e}")
    except json.JSONDecodeError as e:
        print(Fore.RED + f"Error parsing JSON response: {e}")

def send_prompt(prompt) -> string:
    try:
        api_url = "http://localhost:1234/v1/chat/completions"
        messages = [
            {
                "role": "developer",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        payload = {
            "messages": messages,
            "temperature": 0
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        
        result = response.json()
        #print(f"Raw JSON {result}") #uncomment for debugging
        if len(result['choices']) == 0:
            return ""
        content = result['choices'][0]['message']['content']
        #print(f"\nResponse: {content}") #uncomment for debugging
        return content
        
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error sending prompt to LM Studio API: {e}")
    except json.JSONDecodeError as e:
        print(Fore.RED + f"Error parsing JSON response: {e}")
    except KeyError as e:
        print(Fore.RED + f"Unexpected response format: {e}")

def main():
    spinner = RESTSpinner()
    
    try:
        spinner.start("Getting model....")
        model_name = get_loaded_model()
        spinner.stop()
        collection = [
            TextAnalysisItem(f"In CSS how do I set margin left to 25 % of device width ?", ["margin-left: 25vw;"], ["margin-left: 25vh;"]), #25% is parent element not device width
        ]
        overall_right = []
        overall_wrong = []
        print(Fore.CYAN + f"Model: {model_name}\n")
        for item in collection:

            print(Style.RESET_ALL + f"Prompt: {item.text}\n")
            spinner.start("LM Studio is working...")
            output = send_prompt(item.text)
            right, wrong = find_strings_in_prompt(output, item.right_strings, item.wrong_strings)
            print("\n")
            print(Fore.GREEN + f"Got {len(right)} / {len(item.right_strings)} right strings")
            print(Fore.RED + f"Got {len(wrong)} / {len(item.wrong_strings)} wrong strings")
            overall_right.extend(right)
            overall_wrong.extend(wrong)
            #print(f"{output}") #uncomment for debugging
            spinner.stop()
            print(Style.RESET_ALL + "\n")
        print(f"Model {model_name} overall had ")
        print(Fore.GREEN + f"{len(overall_right)} overall right")
        print(Fore.RED + f"{len(overall_wrong)} overall wrong")
        if len(overall_right) > 0:
            print(Fore.GREEN + f"Right answers {overall_right}")
        if len(overall_wrong) > 0:
            print(Fore.RED + f"Wrong answers {overall_wrong}")
        else:
            print(Fore.GREEN + "No wrong answers!")
        print(Style.RESET_ALL + "\n")
    except Exception as e:
        spinner.stop()
        print(Fore.RED + f"Error: {e}")


if __name__ == "__main__":
    main()