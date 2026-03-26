def truncate_text(text,max_length=120):

    if len(text) <= max_length:

        return text

    return text[:max_length] + "..."