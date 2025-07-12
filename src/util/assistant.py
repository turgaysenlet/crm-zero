import logging
from ollama import chat

from pydantic import BaseModel

logging.basicConfig()
logger = logging.getLogger("Assistant")
logger.setLevel(logging.DEBUG)


class Assistant(BaseModel):
    model: str = "llama3.2:latest"
    system_prompt: str = "You are an support agent. Answer questions in concise, accurate and professional. Do not " \
                         "exceed 100 words in you responses."

    def chat(self, text: str):
        response = chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': f'{self.system_prompt}'
            },
            {
                'role': 'user',
                'content': text
            }
        ])
        return response.message.content

    def summarize(self, text: str) -> str:
        return self.chat(f'Summarize and shorten this text into one very short summary sentence: "{text}".')

    def give_initial_acknowledgement(self, text: str) -> str:
        return self.chat(f'Acknowledge that we have received this request and started working on it. '
                         f'Answer in a very short, polite and professional manner. Do not answer the question or detail anything about the question or answer: "{text}".')


if __name__ == "__main__":
    assistant: Assistant = Assistant()
    texts = [
        "I would to know more about your CRM product features and capabilities",
        "Program crashes when I try to open it three times in a row, gives an error 'No key found' - please help!"
    ]

    for t in texts:
        print("TEXT: " + t)
        print("SUMMARY: " + assistant.summarize(t))
        print("ACK: " + assistant.give_initial_acknowledgement(t))
        print("")
