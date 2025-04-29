from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, validator
from typing import Optional, List
from transformers import AutoProcessor, Idefics3ForConditionalGeneration
from PIL import Image
import io, torch, json
from helper import get_osm_tags_from_openstreetmap, extract_lat_lon
from accelerate import Accelerator
from peft import PeftModel

app = FastAPI()
accelerator = Accelerator()
device = accelerator.device

MODEL_NAME = "HuggingFaceTB/SmolVLM2-2.2B-Instruct"
ADAPTER_NAME = "jerick5555/SmolVLM2-2.2B-Instruct-vqav2-vqav3"
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = Idefics3ForConditionalGeneration.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        #_attn_implementation="flash_attention_2",
    )
model = PeftModel.from_pretrained(
        model,
        ADAPTER_NAME
).to(device)
model.eval()


class Coordinates(BaseModel):
    lat: float
    lon: float

    @validator('lat')
    def validate_latitude(cls, v):
        if not isinstance(v, float):
            raise TypeError('Latitude must be a float')
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v

    @validator('lon')
    def validate_longitude(cls, v):
        if not isinstance(v, float):
            raise TypeError('Longitude must be a float')
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v


ALL_CLASSES = [
    # Main classes
    "Abandoned Trolleys", "Animals", "Cleanliness", "Construction Sites",
    "Drains & Sewers", "Drinking Water", "Housing", "Illegal Parking",
    "Others", "Parks & Greenery", "Pests", "Roads & Footprints",
    "Shared Bicycles", "Smoking",
    "Others",  # this is often used as a catch-all category
    #Sub classes
    "Cold Storage", "FairPrice", "Giant", "Ikea", "Mustafa", "Other Trolleys", "ShengSong",
    "Bird Issues", "Cat Issues", "Dead Animal", "Dog Issues", "Injured Animal", "Other Animal Issues",
    "Bulky Waste in Common Areas", "Dirty Public Areas", "High-rise Littering", "Overflowing Litter Bin",
    "Construction Noise",
    "Choked Drain or Stagnant Water", "Damaged Drain", "Flooding", "Sewage Smell", "Sewer Choke or Overflow",
    "No Water", "Water Leak", "Water Pressure", "Water Quality",
    "Common Area Maintenance", "HDB Car Park Maintenance", "Lightning Maintenance", "Playground & Fitness Facilities Maintenance",
    "HDB or URA Car Park", "Motorcycle at Void Deck", "Road",
    "Fallen Tree or Branch", "Other Parks and Greenery Issues", "Overgrown Grass", "Park Facilities Maintenance", "Park Lighting Maintenance",
    "Bees & Hornets", "Cockroaches in Food Establishment", "Mosquitoes", "Rodents in Common Areas", "Rodents in Food Establishment",
    "Covered Linkway Maintenance", "Damaged Road Signs", "Faulty Streetlight", "Footpath Maintenance", "Road Maintenance",
    "Anywheel", "HelloRide", "Other Bicycles",
    "Food Premises", "Other Public Areas", "Parks & Park Connectors"
]

conversion_map = {
    "Abandoned Trolleys": "Abandoned Trolleys",
    "Animals": "Animals",
    "Cleanliness": "Cleanliness",
    "Construction Sites": "Construction Sites",
    "Drains & Sewers": "Drains & Sewers",
    "Drinking Water": "Drinking Water",
    "Housing": "Housing",
    "Illegal Parking": "Illegal Parking",
    "Others": "Others",
    "Parks & Greenery": "Parks & Greenery",
    "Pests": "Pests",
    "Roads & Footprints": "Roads & Footprints",
    "Shared Bicycles": "Shared Bicycles",
    "Smoking": "Smoking",
    "Others": "Others",  # duplicate catch-all
    "Cold Storage": "Cold Storage",
    "FairPrice": "FairPrice",
    "Giant": "Giant",
    "Ikea": "Ikea",
    "Mustafa": "Mustafa",
    "Other Trolleys": "Other Trolleys",
    "ShengSong": "ShengSong",
    "Bird Issues": "Bird Issues",
    "Cat Issues": "Cat Issues",
    "Dead Animal": "Dead Animal",
    "Dog Issues": "Dog Issues",
    "Injured Animal": "Injured Animal",
    "Other Animal Issues": "Other Animal Issues",
    "Bulky Waste in Common Areas": "Bulky Waste in Common Areas",
    "Dirty Public Areas": "Dirty Public Areas",
    "High-rise Littering": "High-rise Littering",
    "Overflowing Litter Bin": "Overflowing Litter Bin",
    "Construction Noise": "Construction Noise",
    "Choked Drain or Stagnant Water": "Choked Drain/Stagnant Water",
    "Damaged Drain": "Damaged Drain",
    "Flooding": "Flooding",
    "Sewage Smell": "Sewage Smell",
    "Sewer Choke or Overflow": "Sewer Choke or/Overflow",
    "No Water": "No Water",
    "Water Leak": "Water Leak",
    "Water Pressure": "Water Pressure",
    "Water Quality": "Water Quality",
    "Common Area Maintenance": "Common Area Maintenance",
    "HDB Car Park Maintenance": "HDB Car Park Maintenance",
    "Lightning Maintenance": "Lightning Maintenance",
    "Playground & Fitness Facilities Maintenance": "Playground & Fitness Facilities Maintenance",
    "HDB or URA Car Park": "HDB/URA Car Park",            # ↪ formatting fix
    "Motorcycle at Void Deck": "Motorcycle at Void Deck",
    "Road": "Road",
    "Fallen Tree or Branch": "Fallen Tree/Branch",
    "Other Parks and Greenery Issues": "Other Parks and Greenery Issues",
    "Overgrown Grass": "Overgrown Grass",
    "Park Facilities Maintenance": "Park Facilities Maintenance",
    "Park Lighting Maintenance": "Park Lighting Maintenance",
    "Bee & Hornets": "Bees & Hornets",
    "Bees & Hornets": "Bees & Hornets",
    "Cockroaches in Food Establishment": "Cockroaches in Food Establishment",
    "Mosquitoes": "Mosquitoes",
    "Rodents in Common Areas": "Rodents in Common Areas",
    "Rodents in Food Establishment": "Rodents in Food Establishment",
    "Covered Linkway Maintenance": "Covered Linkway Maintenance",
    "Damaged Road Signs": "Damaged Road Signs",
    "Faulty Streetlight": "Faulty Streetlight",
    "Footpath Maintenance": "Footpath Maintenance",
    "Road Maintenance": "Road Maintenance",
    "Anywheel": "Anywheel",
    "HelloRide": "HelloRide",
    "Other Bicycles": "Other Bicycles",
    "Food Premises": "Food Premises",
    "Other Public Areas": "Other Public Areas",
    "Parks & Park Connectors": "Parks & Park Connectors",
}



NUM_CLASSES = len(ALL_CLASSES)

system_prompt = (
    "You are an expert in municipal services issues. Your task is to analyze the provided input, "
    "which may include an image and a description, and categorize the issue into one or more categories "
    "from the predefined list of municipal service issue types. Additionally, assess the severity of the issue "
    "as one of the following: Low, Medium, or High.\n\n"
    "The predefined list of categories is as follows:\n"
    + "\n".join(f"- {category}" for category in ALL_CLASSES) +
    "\n\nYour response should be in the following JSON format:\n"
    "{\n"
    "    \"categories\": [categories],\n"
    "    \"severity\": severity\n"
    "}\n\n"
    "Ensure that the categories are selected from the provided list of issue types, and the severity is determined "
    "based on the details provided in the input."
)


@app.post("/infer")
# returns a JSON object with categories and severity
async def infer(
    text: str, 
    coordinates: Optional[Coordinates], 
    files: List[UploadFile] = File(default= [])
):
    # validation
    allowed_content_types = ['image/jpeg', 'image/png']
    valid_files = []
    for file in files:
        if file.content_type in allowed_content_types:
            valid_files.append(file)
        else:
            # Handle invalid file type
            pass
    
    if valid_files:
        # read image files and convert to PIL Image
        images = []
        for file in valid_files:
            data = await file.read()
            image = Image.open(io.BytesIO(data)).convert("RGB")
            images.append(image)
    else:
        images = [torch.zeros((1, 3, 224, 224), dtype=torch.uint8)] # Dummy tensor for no image case


    # get latitude and longitude from coordinates if provided
    if coordinates:
        lat = coordinates.lat
        lon = coordinates.lon
    # get latitude and longitude from first image if it is PIL Image
    elif isinstance(images[0], Image.Image):
        lat, lon = extract_lat_lon(images[0])
    else:        
        lat, lon = None, None


    tags = get_osm_tags_from_openstreetmap(lat, lon)

    # append the tags to the text input
    text.text += "\n\nNearby location tags: " + ", ".join([f"{k}: {v}" for tag in tags["nearby"] for k, v in tag.items()]) + "\n\n"
    text.text += "Enclosing location tags: " + ", ".join([f"{k}: {v}" for tag in tags["enclosing"] for k, v in tag.items()])

    user_content = [{"type": "text", "text": text.text}]

    # append images to user_content
    for image in images:
        user_content.append({"type": "image"})

    messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    # Process the inputs using the processor
    text = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
    )


    inputs = processor(text=text, images=images, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model.generate(**inputs)
    result = processor.decode(outputs[0], skip_special_tokens=True)

    # Extract the assistant's response using string manipulation
    assistant_response_start = result.find('Assistant:') + len('Assistant:')
    assistant_response = result[assistant_response_start:].strip()

    # verify that the result is in the following format
    # { "categories": [categories], "severity": severity }
    try:
        assistant_response = json.loads(assistant_response)
        if "categories" not in assistant_response or "severity" not in assistant_response:
            raise ValueError("Invalid response format. Expected keys: 'categories' and 'severity'.")
        if not isinstance(assistant_response["categories"], list) or not isinstance(assistant_response["severity"], str):
            raise ValueError("Invalid response format. 'categories' should be a list and 'severity' should be a string.")
        
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in the response."}
    
    # check if categories are in ALL_CLASSES
    for category in assistant_response["categories"]:
        # drop category if it is not in ALL_CLASSES
        if category not in ALL_CLASSES:
            assistant_response["categories"].remove(category)
        else:
            # convert category to its corresponding value in conversion_map
            if category in conversion_map.keys():
                assistant_response["categories"].remove(category)
                assistant_response["categories"].append(conversion_map[category])

    # check if severity is in ["Low", "Medium", "High"]
    if assistant_response["severity"] not in ["Low", "Medium", "High"]:
        # default to None if no valid severity is found
        assistant_response["severity"] = None
    

    return assistant_response
