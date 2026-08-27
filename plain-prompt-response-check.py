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


SYSTEM_PROMPT = "You are expert Software Engineer."
def get_loaded_model():
    try:
        response = requests.get("http://localhost:1234/v1/models")
        response.raise_for_status()
        models_data = response.json()
        if 'data' in models_data and len(models_data['data']) > 0:
            loaded_model = models_data['data'][0]
            print(Fore.GREEN + f"Currently loaded model: {loaded_model.get('id', 'Unknown')}")
            print(Fore.GREEN + f"Model details:")
            for key, value in loaded_model.items():
                if key != 'id':
                    print(Fore.GREEN + f"  {key}: {value}")
        else:
            print(Fore.RED + "No models found or no model currently loaded")
            
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
        get_loaded_model()
        example_prompt = "Explain the concept of machine learning in simple terms."
        print(Fore.GREEN + f"Prompt: {example_prompt}\n")
        spinner.stop()
        spinner.start("Prompting...")
        output = send_prompt(example_prompt)
        print(f"{output}")
        spinner.stop()
    except Exception as e:
        spinner.stop()
        print(Fore.RED + f"Error: {e}")


if __name__ == "__main__":
    main()