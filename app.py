"""
Basic chatbot with document analysis

A Python script that:
- Loads the required environment and libraries
- Connects to Azure AI Foundry endpoint
- Configures document reader
- Defines the chat function
    - Sets the system prompt
    - Includes the chat history for conversation
    - Streams the response for visual experience
- Creates an interface using Gradio
"""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
import gradio as gr

# Lazy import for docling to avoid initialization issues
DocumentConverter = None


def setup_environment():
    """Load environment variables, create .env if it doesn't exist."""
    env_path = Path(".env")
    
    # Check if .env file exists
    if not env_path.exists():
        print("\n.env file not found. Let's set up your Azure AI credentials.\n")
        
        # Prompt for credentials
        endpoint = input("Enter your Azure AI Endpoint (e.g., https://your-endpoint.inference.ai.azure.com): ").strip()
        api_key = input("Enter your Azure API Key: ").strip()
        
        # Validate inputs
        if not endpoint or not api_key:
            raise ValueError("Both endpoint and API key are required!")
        
        # Create .env file with the credentials
        with open(env_path, "w") as f:
            f.write(f"AZURE_ENDPOINT={endpoint}\n")
            f.write(f"AZURE_API_KEY={api_key}\n")
        
        print(f"\n✓ Credentials saved to {env_path.absolute()}")
        print("You can edit this file later if needed.\n")
    
    load_dotenv(override=True)
    print("Environment loaded")


def setup_client():
    """Setup the Azure AI Inference client pointing at Azure AI Foundry."""
    # Load credentials from environment variables
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    AZURE_API_KEY = os.getenv("AZURE_API_KEY")
    
    if not AZURE_ENDPOINT or not AZURE_API_KEY:
        raise ValueError("AZURE_ENDPOINT and AZURE_API_KEY must be set in .env file")
    
    client = ChatCompletionsClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_API_KEY),
    )
    return client


def setup_converter():
    """Setup converter for documents and create upload directory."""
    global DocumentConverter
    if DocumentConverter is None:
        from docling.document_converter import DocumentConverter as DC
        DocumentConverter = DC
    
    converter = DocumentConverter()

    # Folder to keep uploaded documents (so you can commit them if you want)
    UPLOAD_DIR = Path("uploaded_docs")
    UPLOAD_DIR.mkdir(exist_ok=True)

    return converter, UPLOAD_DIR


def extract_text_from_file(uploaded_file, converter, upload_dir):
    """
    Take a Gradio UploadedFile, save it into UPLOAD_DIR,
    run Docling on it, return markdown text.
    """
    if uploaded_file is None:
        return ""

    # Save a copy of the uploaded file into our repo folder
    dest_path = upload_dir / uploaded_file.name
    shutil.copy(uploaded_file.name, dest_path)

    # Use Docling to convert to a rich document, then export as markdown
    result = converter.convert(str(dest_path))
    doc_text = result.document.export_to_markdown()

    # You could also use export_to_text() if you prefer plain text
    return doc_text


def create_chat_function(client, model_name):
    """
    Create and return the chat function to interact with model.
    """
    def chat(message, history, uploaded_file):
        """
        Gradio ChatInterface callback.

        Parameters
        ----------
        message : str
            The latest user message.
        history : list[dict]
            Previous messages in OpenAI format:
            [{"role": "user"/"assistant", "content": "..."}, ...]
            (because we use type="messages" in ChatInterface).
        uploaded_file : str | None
            Path to the uploaded file (because we use type="filepath" in gr.File),
            or None if no file is provided this turn.
        """

        system_instruction = (
            "You are a helpful assistant. If a document is provided, "
            "use it as the main context for your answers."
        )

        # Convert history to Azure AI messages format
        messages = [SystemMessage(system_instruction)]
        
        if history:
            for msg in history:
                if msg["role"] == "user":
                    messages.append(UserMessage(msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AssistantMessage(msg["content"]))

        # Build the current user message, optionally including file contents
        if uploaded_file is not None:
            try:
                # Lazy load docling only when needed
                from docling.document_converter import DocumentConverter
                converter = DocumentConverter()
                
                # Use Docling to extract text from the document
                file_path = Path(uploaded_file)
                result = converter.convert(str(file_path))
                doc_text = result.document.export_to_markdown()
            except Exception as e:
                doc_text = f"[Error processing file {uploaded_file}: {e}]"

            user_content = (
                "Here is the document content:\n\n"
                f"{doc_text}\n\n"
                f"Now answer my question about this document:\n{message}"
            )
        else:
            user_content = message

        messages.append(UserMessage(user_content))

        # Call the model with streaming
        complete_kwargs = {
            "messages": messages,
            "stream": True,
        }
        if model_name is not None:
            complete_kwargs["model"] = model_name
            
        stream = client.complete(**complete_kwargs)

        response = ""
        for chunk in stream:
            # Azure AI Inference streaming format
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    response += delta.content
                    yield response

    return chat


def main():
    """Main function to run the chat interface."""
    # Azure AI Foundry model name - update this to match your deployment
    # Common model names: gpt-4o, gpt-4, gpt-35-turbo, gpt-4o-mini
    # Try without specifying model to use default, or check your Azure portal for deployed model name
    MODEL_NAME = "gpt-5-nano"  # Set to None to use default model, or specify your deployment name

    # Initialize components
    print("Setting up environment...")
    setup_environment()

    print("Setting up Azure AI Foundry client...")
    client = setup_client()

    # Create upload directory
    print("Setting up upload directory...")
    UPLOAD_DIR = Path("uploaded_docs")
    UPLOAD_DIR.mkdir(exist_ok=True)

    print("Creating chat function...")
    chat_fn = create_chat_function(client, MODEL_NAME)

    # Create a chat interface using Gradio
    print("Creating Gradio interface...")
    view = gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="Azure AI Foundry + Document Chat",
        description="Chat with Azure AI models. Optionally upload a document and ask about it.",
        additional_inputs=[
            gr.File(label="Upload a document (optional)", type="filepath")
        ],
    )

    # Launch the interface
    print("Launching interface...")
    view.launch(inbrowser=True, share=False)


if __name__ == "__main__":
    main()
