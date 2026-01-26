#chain of thought prompting

import cmd
from pyexpat.errors import messages
import subprocess
from urllib import response
from dotenv import load_dotenv
from openai import OpenAI
import requests

from pydantic import BaseModel, Field
from typing import Optional


import json
import os

import asyncio
import speech_recognition as sr
from openai.helpers import LocalAudioPlayer
from openai import AsyncOpenAI

load_dotenv()

client = OpenAI()
async_client = AsyncOpenAI()


def run_command(cmd: str):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout or result.stderr

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+st"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    

async def tts(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        instructions="Always speak in a cheerful manner with full of delight and happy",
        input=speech,
        response_format="pcm",
    )as response:
        await LocalAudioPlayer().play(response)
        
available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
}       
        
SYSTEM_PROMPT = """

    You're an expert AI Assistant in resolving user queries using chain of thought.
    You work on START, PLAN and OUPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call a tool if required from the list of available tools. for every tool call wait for the observe step which is the output from the called tool.
    If the user asks to build an application, project, or codebase:
    - You MUST create the required files and folders
    - Use the run_command tool to create directories and files
    - Write code using shell redirection or echo
    - Do not just explain — take action

    
    Rules:
    - Strictly Follow the given JSON output format
    - Only run one step at a time.
    - The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally OUTPUT (which is
    Output JSON Format:
    { "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input"; "string" }
    Available Tools:
    - get_weather (city: str): Takes, city name as an input string and returns the weather info about the city.
    - run_command (cmd: str): Takes a system linux command as string and executes the command on user's system and returns the out
    PLAN: { "step": "PLAN": "content"; "Now finally lets perform the add 3.5" }
   
    Example 1:
    START: Hey, Can you solve 2 + 3 * 5 / 10
    PLAN: { "step": "PLAN": "content": "Seems like user is interested in math problem" }
    PLAN: { "step": "PLAN": "content": "looking at the problem, we should solve this using BODMAS method" }
    PLAN: { "step": "PLAN": "content": "Yes, The BODMAS is correct thing to be done here" }
    PLAN: { "step": "PLAN": "content": "first we must multiply 3 * 5 which is 15" }
    PLAN: { "step": "PLAN"; "content": "Now the new equation is 2 + 15 / 10" }
    PLAN: { "step": "PLAN": "content": "We must perform divide that is 15 / 10 = 1.5" }
    PLAN: { "step": "PLAN": "content": "Now the new equation is 2 + 1.5" }

    Example 2:
    START: What is the weather of Delhi?
    PLAN: { "step": "PLAN": "content": "Seems like user is interested in getting weather of Delhi in India" } 
    PLAN: { "step": "PLAN": "content": "Lets see if we have any available tool from the list of available tools" } 
    PLAN: { "step": "PLAN": "content": "Great, we have get _weather tool available for this query." } 
    PLAN: { "step": "PLAN": "content": "I need to call get_weather tool for delhi as input for city" } 
    PLAN: { "step": "TOOL": "tool": "get_weather", "input": "delhi" }
    PLAN: { "step": "OBSERVE": "tool": "get_weather","output": "The temp of delhi is cloudy with 20 C" }
    PLAN: { "step": "PLAN": "content": "Great, I got the weather info about delhi" }
    OUTPUT: { "step": "OUTPUT": "content": "The cuurent weather in delhi is 20 C with some cloudy sky." }

"""

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Examples: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content of the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call")
    input: Optional[str] = Field(None, description="The input params for the tool")
    
    
message_history = [{"role": "system", "content": SYSTEM_PROMPT}]



r = sr.Recognizer() 
with sr.Microphone() as source:  
    r.adjust_for_ambient_noise(source)
    r.pause_threshold = 2

    while True:
        print("Say something!...")
        audio = r.listen(source)
        
        print("Processing Audio.... (SST)")
        user_query = r.recognize_google(audio)
        
        print(f"You said: {user_query}")
        
        message_history.append({"role": "user", "content": user_query})
        
        while True:
            response = client.chat.completions.parse(
                model="gpt-4.1",
                messages=message_history,
                response_format=MyOutputFormat
            )
            
            ai_message = response.choices[0].message.content
            message_history.append({"role": "assistant", "content": ai_message})
            

            parsed_result = response.choices[0].message.parsed
            
            if parsed_result.step == "START":
                print("🔥", parsed_result.content)
                continue
            
            if parsed_result.step == "TOOL":
                tool_to_call = parsed_result.tool
                tool_input = parsed_result.input
                print(f"Calling Tool: {tool_to_call} with input: {tool_input}")
                
                tool_response = available_tools[tool_to_call](tool_input)
                print({tool_to_call : tool_response})
                message_history.append({"role": "developer", "content": json.dumps({ "step": "OBSERVE", "tool": tool_to_call, "output": tool_response })})
                
                continue
            
            if parsed_result.step == "PLAN":
                print("📝", parsed_result.content)
                continue
            
            
            if parsed_result.step == "OUTPUT":
                print("AI Final Output: ", parsed_result.content)
                asyncio.run(tts(speech=parsed_result.content))
                break