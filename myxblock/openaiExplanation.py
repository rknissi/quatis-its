# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import base64

def generate_full_explanation(apiToken, question):
    openai.api_key = base64.b64decode(apiToken)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "assistant", "content": question}
        ]
    )

    return response.choices[0].message.content

def answer_doubt(apiToken, question, step):
    openai.api_key = base64.b64decode(apiToken)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "assistant", "content": question + " \"" + step + "\""}
        ]
    )

    return response.choices[0].message.content

def generate_error_specific_feedback(apiToken, fromState, toState):
    openai.api_key = base64.b64decode(apiToken)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "assistant", "content": "Explicar por que de \"" + fromState + "\" para \"" + toState + "\" está errado"}
        ]
    )
    return response.choices[0].message.content

def generate_explanation(apiToken, fromState, toState):
    openai.api_key = base64.b64decode(apiToken)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "assistant", "content": "Explicar por que de \"" + fromState + "\" para \"" + toState + "\" está certo"}
        ]
    )
    return response.choices[0].message.content

def generate_hint(apiToken, fromState, toState):
    openai.api_key = base64.b64decode(apiToken)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "assistant", "content": "Qual a dica para irmos de \"" + fromState + "\" para \"" + toState + "\" ?"}
        ]
    )
    return response.choices[0].message.content