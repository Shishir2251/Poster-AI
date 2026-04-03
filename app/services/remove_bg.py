import requests
import os
from dotenv import load_dotenv
load_dotenv()
def remove_bg_api(image_path):

    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files = {"image_file": open(image_path, "rb")},
        data={"size": "auto"},
        headers = {"X-Api-Key": os.getenv("REMOVE_BG_API_KEY")}

    )

    output_path = image_path.replace(".", "_no_bg.")

    with open(output_path, "wb") as out:
        out.write(response.content)
    
    return output_path

