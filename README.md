# Web-Scrapping-Chatbot


## **Project Overview**
This project is an AI-powered chatbot designed to interact with a given website URL. The chatbot scrapes data from the website, processes it into structured formats, and generates meaningful responses to user queries using a pre-trained language model (Hugging Face Inference API). The chatbot runs via a console interface and showcases the integration of web scraping, natural language processing, and machine learning.

---

## **Features**
- **Web Scraping**: Dynamically fetches website content using Selenium.
- **Data Processing**: Cleans and structures data into meaningful chunks, with embeddings for efficient retrieval.
- **Natural Language Understanding**: Generates responses using the `google/flan-t5-base` model from Hugging Face.
- **Interactive Console**: Allows users to ask questions and receive accurate, context-aware answers.

---

## **How It Works**
1. **Scraping Data**:  
   The `scraper_mod.py` script extracts relevant content from the specified website (e.g., https://botpenguin.com/) using Selenium. The scraped data is saved in `data.pkl`.

2. **Processing Data**:  
   The `text_processing.py` script processes the scraped data by:
   - Cleaning unnecessary elements (e.g., navigation bars).
   - Splitting the content into smaller chunks (~300 words).
   - Embedding the chunks using Sentence Transformers for efficient similarity matching.  
   The processed data is saved in `processed_data.pkl`.

3. **Chatbot Initialization**:  
   The `chatbot_module.py` script loads the processed data, retrieves relevant chunks based on user queries, and generates responses using the Hugging Face API.

4. **Console Interaction**:  
   The `main.py` script orchestrates the entire workflow and provides a user-friendly console interface for interaction.

---

## **Project Files**
- **`scraper_mod.py`**:  
   Scrapes relevant data dynamically from the website using Selenium.
- **`text_processing.py`**:  
   Cleans, chunks, and embeds the scraped data for efficient retrieval.
- **`chatbot_module.py`**:  
   Retrieves the most relevant data chunks and generates responses using the Hugging Face API.
- **`main.py`**:  
   Coordinates all scripts and enables user interaction via the console.

---

## **Setup Instructions**

### **Prerequisites**
- Python 3.8 or higher
- Chrome browser and compatible ChromeDriver
- Hugging Face API key ([Sign up here](https://huggingface.co/join))

### **Installation**
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your Hugging Face API key:
   ```bash
   export HF_API_TOKEN="your_huggingface_api_key"
   ```

---

## **Usage**

1. **Scrape the Website**:  
   Run the following command to scrape website data:
   ```bash
   python scraper_mod.py
   ```

2. **Process the Data**:  
   Process the scraped data to create `processed_data.pkl`:
   ```bash
   python text_processing.py
   ```

3. **Run the Chatbot**:  
   Start the chatbot and interact via the console:
   ```bash
   python main.py
   ```

---

## **Example Interaction**

**Input**:  
```plaintext
You: What is BotPenguin?
```

**Output**:  
```plaintext
Chatbot: BotPenguin is a chatbot platform that allows businesses to create AI-powered bots for websites, WhatsApp, and other platforms.
```

**Input**:  
```plaintext
You: What features does BotPenguin offer?
```

**Output**:  
```plaintext
Chatbot: BotPenguin offers features such as lead generation, appointment booking, customer support, and marketing automation.
`

Feel free to raise issues or reach out with questions about the project!  
