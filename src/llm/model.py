import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_model(
    model_name: str = "gemini-2.5-flash",
    api_key: str = None,
    temperature: float = 0.05,
    top_p: float = 0.3,
    top_k: int = 10
):
    """
    Initializes and returns a ChatGoogleGenerativeAI model with customizable
    generation settings.

    Args:
        model_name (str): The name of the Gemini model to use.
                          Defaults to "gemini-2.5-flash".
        api_key (str): The Google API key.
        temperature (float): Controls the randomness of the output.
        top_p (float): Lowering top_p narrows the field of possible tokens.
        top_k (int): Limits the token selection to the top_k most likely tokens at
                     each step.

    Returns:
        ChatGoogleGenerativeAI: An instance of the initialized model.

    Raises:
        ValueError: If the API key is not provided and cannot be found
                    in the environment variables.
    """
    if api_key is None:
        api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("Google API key not found. Please provide it as an argument or set the 'GOOGLE_API_KEY' environment variable.")

    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )
    return model