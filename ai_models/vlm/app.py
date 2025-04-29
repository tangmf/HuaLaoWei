from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, validator
from transformers import AutoProcessor, Idefics3ForConditionalGeneration
from PIL import Image
import io, torch, json


app = FastAPI()
MODEL_NAME = "jerick5555/SmolVLM2-2.2B-Instruct-vqav2"
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = Idefics3ForConditionalGeneration.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        #_attn_implementation="flash_attention_2",
    ).to("cuda")
model.eval()

# ensure that text is a string
class TextInput(BaseModel):
    text: str

# ensure that the file is a jpg, jpeg or png
class ImageInput(BaseModel):
    file: UploadFile

    @validator('file')
    def validate_file_type(cls, file: UploadFile):
        allowed_content_types = ['image/jpeg', 'image/png']
        if file.content_type not in allowed_content_types:
            raise ValueError('Only JPEG and PNG images are allowed.')

        return file


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
    "Bee & Hornets", "Cockroaches in Food Establishment", "Mosquitoes", "Rodents in Common Areas", "Rodents in Food Establishment",
    "Covered Linkway Maintenance", "Damaged Road Signs", "Faulty Streetlight", "Footpath Maintenance", "Road Maintenance",
    "Anywheel", "HelloRide", "Other Bicycles",
    "Food Premises", "Other Public Areas", "Parks & Park Connectors"
]
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
# files are optional
# returns a JSON object with categories and severity
async def infer(text: TextInput, files: list[ImageInput] = File(None)):
    if files:
        # read image files and convert to PIL Image
        images = []
        for file in files:
            data = await file.read()
            image = Image.open(io.BytesIO(data)).convert("RGB")
            images.append(image)
    else:
        images = [torch.zeros((1, 3, 224, 224), dtype=torch.uint8)] # Dummy tensor for no image case

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

    # check if severity is in ["Low", "Medium", "High"]
    if assistant_response["severity"] not in ["Low", "Medium", "High"]:
        # default to None if no valid severity is found
        assistant_response["severity"] = None
    

    return assistant_response
