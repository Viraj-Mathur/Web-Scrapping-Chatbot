import pickle

with open("processed_data.pkl", "rb") as file:
    processed_data = pickle.load(file)

for section, details in processed_data.items():
    print(f"Section: {section}")
    print(f"Number of Chunks: {len(details['chunks'])}")
    print(f"Sample Chunk: {details['chunks'][0][:200]}...\n")  # Preview first chunk
