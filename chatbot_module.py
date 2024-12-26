import os
import json
import requests
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

# Set your Hugging Face API key here or through an environment variable
HUGGINGFACE_API_KEY = os.getenv("HF_API_KEY", "hf_your_token_here")

class AIChatAssistant:
    def __init__(self, data_store, model_id="google/flan-t5-base"):
        """
        AI Chat Assistant utilizing chunk-based retrieval and Hugging Face API for text generation.

        Args:
            data_store (dict): Preprocessed data output from a text processing script, expected structure:
                {
                  "SectionName": {
                    "chunks": [...],
                    "embeddings": <torch.Tensor of shape [num_chunks, embedding_dim]>,
                    "references": {...}
                  },
                  ...
                  "_embedding_model": <name of embedding model used>
                }
            model_id (str): ID of the Hugging Face model for text generation.
        """
        self.data_store = data_store

        # Load the embedding model used in preprocessing
        embedding_model_name = self.data_store.get("_embedding_model", "all-MiniLM-L6-v2")
        self.vectorizer = SentenceTransformer(embedding_model_name)

        # Hugging Face model information
        self.model_id = model_id
        self.api_key = HUGGINGFACE_API_KEY

        # Maintain conversation history if needed
        self.chat_history = []

    def get_response(self, query):
        """
        Generate a response based on user's query using retrieval and Hugging Face API.

        Steps:
          1) Retrieve the most suitable chunk for the query.
          2) Construct a prompt using the retrieved chunk.
          3) Generate a response via Hugging Face API.
        """
        try:
            # Find the most relevant chunk
            context_chunk = self._find_best_chunk(query)

            if not context_chunk or context_chunk == "No matching context found.":
                return "Apologies, I couldn't locate relevant information. Could you rephrase or elaborate?"

            # Create a prompt with the retrieved context
            prompt = (
                "You are an intelligent assistant. Use the given context to answer the query accurately and succinctly. "
                "If the context is inadequate, mention this.

"
                f"Context: {context_chunk}

"
                f"Query: {query}

"
                "Response:"
            )

            # Generate the answer via Hugging Face API
            response_text = self._use_huggingface_api(prompt)

            # Save conversation history
            self.chat_history.append({"role": "user", "content": query})
            self.chat_history.append({"role": "assistant", "content": response_text})

            return response_text
        except Exception as err:
            return f"Error in generating response: {err}"

    def _find_best_chunk(self, input_text, top_n=3, threshold=0.3):
        """
        Identify the most relevant chunk for the input query using cosine similarity.

        Args:
            input_text (str): User's input query.
            top_n (int): Number of top chunks to evaluate.
            threshold (float): Minimum similarity score.

        Returns:
            str: The best matching chunk text or fallback message if none is found.
        """
        input_vector = self.vectorizer.encode(input_text, convert_to_tensor=True)
        matching_chunks = []
        similarity_scores = []

        for section, section_data in self.data_store.items():
            if section.startswith("_"):  # Skip metadata
                continue

            section_embeddings = section_data["embeddings"]
            section_chunks = section_data["chunks"]

            if not section_chunks:
                continue

            # Compute similarity
            cosine_scores = torch.nn.functional.cosine_similarity(input_vector, section_embeddings, dim=-1)
            top_indices = torch.topk(cosine_scores, k=top_n).indices

            for index in top_indices:
                score = cosine_scores[index].item()
                if score >= threshold:
                    matching_chunks.append(section_chunks[index])
                    similarity_scores.append(score)

        if not matching_chunks:
            return "No matching context found."

        # Select the highest scoring chunk
        best_match_idx = np.argmax(similarity_scores)
        return matching_chunks[best_match_idx]

    def _use_huggingface_api(self, prompt, max_tokens=150):
        """
        Use the Hugging Face Inference API for text generation.

        Args:
            prompt (str): The text prompt to send to the model.
            max_tokens (int): Maximum number of tokens to generate.

        Returns:
            str: The generated text response or error message.
        """
        if not self.api_key:
            return "Hugging Face API key is missing. Please set it up to proceed."

        endpoint = f"https://api-inference.huggingface.co/models/{self.model_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,  # Control randomness
                "top_p": 0.9
            }
        }

        response = requests.post(endpoint, headers=headers, json=payload)
        if response.status_code != 200:
            return f"API Error {response.status_code}: {response.text}"

        try:
            output = response.json()
            # Extract the generated text
            return output[0].get("generated_text", "").strip()
        except Exception as err:
            return f"Error in API response parsing: {err}"

if __name__ == "__main__":
    """
    Demonstration of usage:
      1) Ensure the preprocessed data file is available as 'processed_data.pkl'.
      2) Use this script to interact with the chatbot via the terminal.
    """
    import pickle

    try:
        with open("processed_data.pkl", "rb") as file:
            data_store = pickle.load(file)
    except FileNotFoundError:
        print("Preprocessed data file not found. Please ensure text processing is completed.")
        data_store = None

    if data_store:
        assistant = AIChatAssistant(data_store, model_id="google/flan-t5-base")
        print("Chat Assistant is active! Type 'exit' to end the session.\n")

        while True:
            user_input = input("User: ").strip()
            if user_input.lower() == "exit":
                print("Session terminated. Goodbye!")
                break
            if not user_input:
                print("Input cannot be empty. Please try again.")
                continue

            bot_reply = assistant.get_response(user_input)
            print(f"Assistant: {bot_reply}")
    else:
        print("Exiting due to missing data.")
