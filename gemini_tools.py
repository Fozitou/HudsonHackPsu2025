from google import genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from utils import take_a_photo
import arduino
import os

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def describe_image(image_path: str):
    img = Image.open(image_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img, "Describe this image in detail."]
    )
    return response.text  # type: ignore


def generate_image(prompt: str, output_dir="./Generations", filename=None):
    os.makedirs(output_dir, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.png"
    
    output_path = os.path.join(output_dir, filename)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt]
    )
    for part in response.candidates[0].content.parts:  # type: ignore
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))  # type: ignore
            image.save(output_path)
            os.startfile(output_path)
            return output_path






def is_object_in_claw_range(image_path: str, object_name: str):
    f"""
    Detects if the {object_name} is within the claw's range (inside the claw).
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Boolean indicating if object is in claw range
    """
    img = Image.open(image_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img, "Is there an object inside or within the range of the claw to be picked up? Answer only 'yes' or 'no'."]
    )
    if not response.text:
        return "No object found"
    return response.text.strip().lower() == "yes"


def estimate_distance(image_path: str) -> str:
    """
    Estimates the distance of an object from the camera/claw.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Estimated distance as a string (e.g., "30 cm", "close", "far")
    """
    img = Image.open(image_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img, "Estimate the distance of the main object from the camera in centimeters or describe it as 'very close', 'close', 'medium', or 'far'. Be concise."]
    )
    if not response.text:
        return "No distance or object found"
    return response.text.strip()


def check_object_presence(image_path: str, object_name: str) -> bool:
    """Check if the specified object is present in the image."""
    img = Image.open(image_path)
    
    prompt = f"""Is there a {object_name} visible in this image?
Respond with ONLY 'yes' or 'no'."""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img, prompt]
    )
    
    answer = response.text.strip().lower() #type: ignore
    return answer == 'yes'

def add_grid_lines(image_path: str, num_lines: int = 9, output_path: str = "output_grid.png"):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    spacing = width / (num_lines + 1)
    center_index = num_lines // 2
    
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    for i in range(num_lines):
        x = int(spacing * (i + 1))
        distance_from_center = i - center_index
        
        if i == center_index:
            color = (0, 255, 0)
            line_width = 3
            label = "0"
        else:
            color = (128, 0, 128)
            line_width = 2
            label = f"{distance_from_center:+d}"
        
        draw.line([(x, 0), (x, height)], fill=color, width=line_width)
        
        label_bbox = draw.textbbox((0, 0), label, font=font)
        label_width = label_bbox[2] - label_bbox[0]
        label_x = x - label_width // 2
        
        draw.text((label_x, 20), label, fill=(255, 255, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
        draw.text((label_x, height - 80), label, fill=(255, 255, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    
    img.save(output_path)
    return img

def detect_object_position(image_path: str, object_name: str, num_lines: int = 9):
    # First check if object is present
    if not check_object_presence(image_path, object_name):
        print(f"Object '{object_name}' not found in the image.")
        return None
    
    img_with_grid = add_grid_lines(image_path, num_lines)

    prompt = f"""Each vertical line in this image has a LARGE YELLOW NUMBER label at the top and bottom.
The center line is labeled "0" and highlighted in GREEN.
PURPLE lines are labeled with negative numbers (left of center) or positive numbers (right of center).
Which labeled line is the {object_name} closest to?
Respond with ONLY that line's number closest to the {object_name}"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[img_with_grid, prompt]
    )
    
    try:
        return int(response.text.strip().replace('+', '')) # type: ignore
    except (ValueError, AttributeError):
        print(f"Could not parse response: {response.text}")
        return None




def center_robot(object_name):
    img = take_a_photo()
    pos = detect_object_position(img, object_name, 9)
    if pos:
        while pos != 0:
            if pos > 0: # type: ignore
                arduino.SpinRIGHT(pos)
            else:
                arduino.SpinLEFT(abs(pos))  # type: ignore
            
            img = take_a_photo()
            pos = detect_object_position(img, object_name, 9)


# def find_and_grab_object(object_name):
#     for cam_pos in [arduino.center_cam(), arduino.right_cam(), arduino.left_cam()]:
#         img = take_a_photo()
#         if check_object_presence(img, object_name):
#             center_robot(object_name)
#             while not is_object_in_claw_range(img, object_name):
#                 img = take_a_photo()
#                 arduino.avante()
#             arduino.grab()
#             break
#     return "No object found in field of view"

def find_and_grab_object(object_name):
    arduino.center_cam()
    print("starting center cam photo")
    img = take_a_photo()
    print("ending center cam photo")
    if check_object_presence(img, object_name):
        center_robot(object_name)
        while not is_object_in_claw_range(img, object_name):
            img = take_a_photo()
            arduino.avante()
        arduino.grab()
    else:
        arduino.right_cam()
        print("starting right cam")
        img = take_a_photo()
        print("ending right cam")
        if check_object_presence(img, object_name):
            arduino.SpinRIGHT(5)
            arduino.center_cam()
            center_robot(object_name)
            while not is_object_in_claw_range(img, object_name):
                img = take_a_photo()
                arduino.avante()
            arduino.grab()
        else:
            arduino.left_cam()
            print("starting left cam")
            img = take_a_photo()
            print("ending left cam")
            if check_object_presence(img, object_name):
                arduino.SpinLEFT(5)
                arduino.center_cam()
                center_robot(object_name)
                while not is_object_in_claw_range(img, object_name):
                    img = take_a_photo()
                    arduino.avante()
                arduino.grab()
    return "No object found in field of view"

