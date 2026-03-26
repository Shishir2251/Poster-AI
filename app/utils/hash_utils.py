import hashlib


# -----------------------------------
# Generate Prompt Hash
# -----------------------------------

def generate_prompt_hash(prompt: str) -> str:

    hash_object = hashlib.sha256(
        prompt.encode("utf-8")
    )

    return hash_object.hexdigest()


# -----------------------------------
# Generate Content Hash
# -----------------------------------

def generate_content_hash(headline: str, content: str) -> str:

    combined = f"{headline}-{content}"

    hash_object = hashlib.sha256(
        combined.encode("utf-8")
    )

    return hash_object.hexdigest()


# -----------------------------------
# Generate Image Hash
# -----------------------------------

def generate_image_hash(image_bytes: bytes) -> str:

    hash_object = hashlib.sha256(image_bytes)

    return hash_object.hexdigest()