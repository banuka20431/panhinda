import requests


def upload_image_to_catbox(image_path: str) -> str:
    files = {"fileToUpload": image_path}
    response = requests.post(
        "https://catbox.moe/user/api.php", files=files, data={"reqtype": "fileupload"}
    )

    return response.text
