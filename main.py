# main.py

import os
import pickle

from scraper_utility import extract_and_store
from text_processing_module import prepare_scraped_content
from bot_framework import IntelligentBot

def execute():
    print("Welcome to the InfoBot Assistant (Powered by HF Inference API)\n")

    # 1. Specify the target URLs for content extraction
    urls_to_scrape = {
        "Homepage": "https://botpenguin.com/",
        "Plans": "https://botpenguin.com/chatbot-pricing",
        "Affiliates": "https://botpenguin.com/partners/chatbot-affiliate-program",
        "Ecommerce": "https://botpenguin.com/chatbot-industry/ecommerce",
        "Solutions": "https://botpenguin.com/solutions/custom-chatgpt-plugins",
    }

    # 2. Verify the existence of prior scraped content in extracted_data.pkl
    extracted_data_file = "extracted_data.pkl"
    if not os.path.exists(extracted_data_file):
        print("No prior data located. Initiating website content extraction...")
        extract_and_store(urls_to_scrape, output_file=extracted_data_file)
    else:
        print(f"Utilizing pre-existing scraped content from {extracted_data_file}.")

    # 3. Retrieve the scraped data from extracted_data.pkl
    try:
        with open(extracted_data_file, "rb") as file:
            extracted_data = pickle.load(file)
    except FileNotFoundError:
        print("Error: Extracted data file missing. Terminating process.")
        return
    except Exception as error:
        print(f"Encountered an issue while loading extracted data: {error}")
        return

    # 4. Process the extracted data into usable chunks and embeddings if absent
    processed_data_file = "finalized_data.pkl"
    if not os.path.exists(processed_data_file):
        print("\nTransforming extracted content into manageable chunks and embeddings...")
        processed_data = prepare_scraped_content(
            data=extracted_data,
            embedding_model="all-MiniLM-L6-v2",  # Alternative embedding model can be used
            chunk_size=300,  # Adjust chunk size parameter if needed
            min_words=30     # Exclude excessively brief chunks
        )
        if not processed_data:
            print("Data processing unsuccessful. Terminating process.")
            return

        with open(processed_data_file, "wb") as output_file:
            pickle.dump(processed_data, output_file)
        print(f"Processed data successfully saved to {processed_data_file}.")
    else:
        print(f"Using pre-processed data from {processed_data_file}.")
        with open(processed_data_file, "rb") as input_file:
            processed_data = pickle.load(input_file)

    # 5. Instantiate the chatbot using the processed data
    assistant_bot = IntelligentBot(
        processed_data=processed_data,
        hf_model_id="google/flan-t5-base"  # Alternate IDs like "google/flan-t5-small" can be specified
    )

    print("\nAssistant is now operational! Type 'exit' to end the session.\n")

    # 6. Begin the interactive chat loop
    while True:
        try:
            user_query = input("User: ").strip()
            if user_query.lower() == "exit":
                print("Goodbye!")
                break
            if not user_query:
                print("Please enter a valid query.")
                continue

            # Fetch the bot's response to the user's query
            bot_response = assistant_bot.generate_response(user_query)
            print(f"Assistant: {bot_response}")

        except KeyboardInterrupt:
            print("\nTerminating session. Goodbye!")
            break
        except Exception as ex:
            print(f"Unexpected error occurred: {ex}")
            break

if __name__ == "__main__":
    execute()
