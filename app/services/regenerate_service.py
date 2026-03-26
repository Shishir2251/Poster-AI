import hashlib

PROMPT_MEMORY = {}

def get_prompt_hash(text):

    return hashlib.sha256(text.encode()).hexdigest()


def can_regenerate(prompt_hash):

    count = PROMPT_MEMORY.get(prompt_hash, 0)

    return count < 3


def register_generation(prompt_hash):

    PROMPT_MEMORY[prompt_hash] = PROMPT_MEMORY.get(prompt_hash, 0) + 1