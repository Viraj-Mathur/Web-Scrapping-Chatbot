import re
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

def strip_html_tags(raw_text):
    """
    Removes HTML tags from the input text using a regex.
    """
    return re.sub(r'<[^>]+>', '', raw_text)

def collapse_whitespace(raw_text):
    """
    Replaces multiple spaces, newlines, or tabs with a single space.
    """
    return re.sub(r'\s+', ' ', raw_text).strip()

def clean_redundant_patterns(text):
    """
    Cleans text by removing headers, footers, or repetitive content patterns.
    """
    # Add website-specific patterns
    patterns = [
        r"Why BotPenguin.*?Resources",
        r"Login|Contact Us|Get Started FREE",
        r"IntegrationsExperience.*?tools!",
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    return text

def cleanse_text(input_text):
    """
    Sequentially cleans HTML tags, redundant patterns, and extra whitespace.
    """
    input_text = strip_html_tags(input_text)
    input_text = clean_redundant_patterns(input_text)
    input_text = collapse_whitespace(input_text)
    return input_text

def segment_text(text, size=500):
    """
    Divides the text into chunks, each containing about `size` words.

    Args:
        text (str): Input text to divide.
        size (int): Number of words per segment.

    Returns:
        list: Text chunks.
    """
    words = text.split()
    segments = [' '.join(words[i:i + size]) for i in range(0, len(words), size)]
    return segments

def prune_segments(segments, threshold=50):
    """
    Filters segments with word count below the threshold or without alphanumeric content.

    Args:
        segments (list): List of text segments.
        threshold (int): Minimum words required in a segment.

    Returns:
        list: Validated segments.
    """
    return [seg for seg in segments if len(seg.split()) >= threshold and any(c.isalnum() for c in seg)]

def generate_embeddings(segments, model_type='all-MiniLM-L6-v2'):
    """
    Generates embeddings for text segments using a sentence-transformers model.

    Args:
        segments (list): Text segments to embed.
        model_type (str): SentenceTransformer model name.

    Returns:
        tuple: Embeddings and model instance.
    """
    model = SentenceTransformer(model_type)
    embeddings = model.encode(segments, convert_to_tensor=True)
    return embeddings, model

def prepare_data(
    scraped_content,
    embedding_model='all-MiniLM-L6-v2',
    segment_size=500,
    min_words=50
):
    """
    Prepares scraped content for QA by cleaning, segmenting, filtering, and embedding.

    Args:
        scraped_content (dict): Sections with their content and links.
        embedding_model (str): SentenceTransformer model name.
        segment_size (int): Approximate word count for each segment.
        min_words (int): Minimum word threshold for segments.

    Returns:
        dict: Processed data with chunks, embeddings, and links.
    """
    if not scraped_content:
        return None

    structured_data = {}
    for section_name, data in scraped_content.items():
        original_text = data.get('context', '')
        associated_links = data.get('links', {})

        # Clean text
        refined_text = cleanse_text(original_text)

        # Segment text
        text_segments = segment_text(refined_text, size=segment_size)

        # Prune invalid segments
        text_segments = prune_segments(text_segments, threshold=min_words)

        if not text_segments:
            print(f"No valid segments found for section: {section_name}")
            continue

        # Embed segments
        segment_embeddings, _ = generate_embeddings(text_segments, model_type=embedding_model)

        structured_data[section_name] = {
            'chunks': text_segments,
            'embeddings': segment_embeddings,
            'links': associated_links
        }

    structured_data['_embedding_model'] = embedding_model
    return structured_data

if __name__ == "__main__":
    """
    Example usage to process scraped data and store embeddings.
    """
    try:
        with open("data.pkl", "rb") as raw_file:
            raw_content = pickle.load(raw_file)
    except FileNotFoundError:
        print("Missing 'data.pkl'. Run the scraper module first.")
        raw_content = None

    if raw_content:
        processed_output = prepare_data(
            scraped_content=raw_content,
            embedding_model='all-MiniLM-L6-v2',
            segment_size=500,
            min_words=50
        )
        with open("processed_data.pkl", "wb") as output_file:
            pickle.dump(processed_output, output_file)
        print("Processed data stored in 'processed_data.pkl'.")
    else:
        print("No content available for processing.")
