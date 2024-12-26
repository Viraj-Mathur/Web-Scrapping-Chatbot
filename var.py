import pickle

with open("data.pkl", "rb") as file:
    scraped_data = pickle.load(file)

for section, content in scraped_data.items():
    print(f"Section: {section}")
    print(f"Content: {content.get('context', 'No Content Found')[:500]}")  # Print a preview of the content
    print("\n")
