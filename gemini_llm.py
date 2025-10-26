import os
from google import genai
from google.genai import types
from gemini_tools import describe_image, generate_image, find_and_grab_object
from utils import take_a_photo, take_a_screenshot
from dotenv import load_dotenv
from PIL import Image
import arduino


# ----------------- Gemini Client ----------------- #
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = "You are a friendly, helpful, and charismatic assistant who communicates clearly, warmly, and confidently while assisting users effectively and respectfully. Dont use special characters or topics, respond in a conversational manner. Be very brief and concise with your answers. You are able to grab, release a claw. You are able to go forward, left forward and right forward"

# ------------ Function Declarations -------------- #
function_declarations = [
    {
        "name": "take_a_photo",
        "description": "Takes a photo and returns its path",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "take_a_screenshot",
        "description": "Takes a screenshot and returns its path",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "describe_image",
        "description": "Describes an image through its path",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path of the image to describe"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "generate_image",
        "description": "Generates an image from a prompt and returns the path",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to generate the image"}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "forward",
        "description": "Moves the car forward making objects that are infront of you closer ",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "right_forward",
        "description": "Moves the car forward and right making objects that are in your right of you closer ",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "left_forward",
        "description": "Moves the car forward and left making objects that are in your left of you closer",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "stop",
        "description": "Stops the car in place",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "grab",
        "description": "Grabs the objec by closing the claw",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "release",
        "description": "Releases the object by opening the claw",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "center_cam",
        "description": "Moves and centers the camera to face forward position",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "left_cam",
        "description": "Moves the camera to face left position",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {
        "name": "right_cam",
        "description": "Moves the camera to face right position",
        "parameters": {"type": "object", "properties": {}, "required": []}

    },
    {"name": "SpinRIGHT",
    "description": "Spins or Rotates to the right ",
    "parameters": {"type": "object", "properties": {
        "turns": {"type": "integer", "description": "Number of rotation steps"
        },
    }, "required": []}},
    {"name": "SpinLEFT",
    "description": "Spins or Rotates to the left ",
    "parameters": {"type": "object", "properties": {
        "turns": {"type": "integer", "description": "Number of rotation steps"
        },
    }, "required": []}},
    {
        "name": "find_and_grab_object",
        "description": "Finds and grabs an object that the user asked",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "The name of the object to be found"}
            },
            "required": ["object_name"]
        }
    }
]

tools = types.Tool(function_declarations=function_declarations)  #type: ignore
config = types.GenerateContentConfig(
    tools=[tools], 
    system_instruction=SYSTEM_INSTRUCTION,
    temperature=0.7,
    max_output_tokens=150,
    top_p=0.9,
    top_k=40,
    thinking_config=types.ThinkingConfig(thinking_budget=0)
)

# ----------------- Tool Execution Mapping ----------------- #
tool_map = {
    "take_a_photo": take_a_photo,
    "take_a_screenshot": take_a_screenshot,
    "describe_image": describe_image,
    "generate_image": generate_image,
    "forward":arduino.forward,
    "right_forward":arduino.right_forward,
    "left_forward":arduino.left_forward,
    "stop": arduino.stop,
    "grab": arduino.grab,
    "release": arduino.release,
    "center_cam": arduino.center_cam,
    "left_cam": arduino.left_cam,
    "right_cam": arduino.right_cam,
    "SpinRIGHT": arduino.SpinRIGHT,
    "SpinLEFT": arduino.SpinLEFT,
    "find_and_grab_object": find_and_grab_object

}

# --------------- Function Chaining Respond --------------- #
def respond(user_prompt: str) -> str:
    # Generate initial response with potential function calls
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[user_prompt],
        config=config
    )

    # Safety check: ensure response has candidates
    if not response.candidates:
        return "I couldn't generate a response. Try again?"
    
    primary_candidate = response.candidates[0]
    
    # Check if candidate has content with parts
    if not primary_candidate.content or not hasattr(primary_candidate.content, "parts"):
        return "Hmm, something went wrong..."
    
    # Process each part in the response
    for part in primary_candidate.content.parts:  #type: ignore
        # Handle function call if present
        if hasattr(part, "function_call") and part.function_call:
            function_call = part.function_call
            function_name = function_call.name
            function_args = dict(function_call.args) if function_call.args else {}
            
            # Execute the function if it exists in our tool map
            if function_name not in tool_map:
                continue
                
            function_output = tool_map[function_name](**function_args)
            
            # Special handling for image-producing functions
            if function_name == "take_a_photo":
                final_config = types.GenerateContentConfig(
                    system_instruction=(
                        SYSTEM_INSTRUCTION +
                        " Describe this photo naturally with relevant visual details. Be brief and concise."
                    ),
                    temperature=0.7,
                    max_output_tokens=150,
                    top_p=0.9,
                    top_k=40,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
                img = Image.open(function_output)
                final_response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[img],  # type: ignore
                    config=final_config
                )
                return final_response.text  # type: ignore
            
            elif function_name == "take_a_screenshot":
                final_config = types.GenerateContentConfig(
                    system_instruction=(
                        SYSTEM_INSTRUCTION +
                        " Describe what's visible in terms of text, layout and context. Be brief and concise."
                    ),
                    temperature=0.7,
                    max_output_tokens=150,
                    top_p=0.9,
                    top_k=40,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
                img = Image.open(function_output)
                final_response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[img],  # type: ignore
                    config=final_config
                )
                return final_response.text  # type: ignore
            
            elif function_name == "generate_image":
                final_config = types.GenerateContentConfig(
                    system_instruction=(
                        SYSTEM_INSTRUCTION +
                        " You generated an image. Describe what you created with enthusiasm and confidence. Be brief and concise."
                    ),
                    temperature=0.7,
                    max_output_tokens=150,
                    top_p=0.9,
                    top_k=40,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
                img = Image.open(function_output)
                final_response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[img],  # type: ignore
                    config=final_config
                )
                return final_response.text  # type: ignore
            
            # For non-image tools, return the output directly
            return str(function_output)
            
    
    
    # If no function calls, concatenate all text parts
    text_parts = [part.text for part in primary_candidate.content.parts if hasattr(part, "text") and part.text]  #type: ignore
    
    return "\n".join(text_parts) if text_parts else "..."