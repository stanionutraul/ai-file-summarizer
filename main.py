import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def chunk_text(text, chunk_size=300):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

def retrieve_chunks(chunks, query):
    query_words = query.lower().split()
    relevant_chunks = []

    for chunk in chunks:
        chunk_lower = chunk.lower()

        score = 0
        for word in query_words:
            if word in chunk_lower:
                score += 1
        if score > 0:
            relevant_chunks.append((score, chunk))
        relevant_chunks.sort(reverse=True)                
    return [chunk for score, chunk in relevant_chunks]

def ask_llm(context, question):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
                   "prompt": f"""
Răspunde la întrebarea utilizatorului folosind DOAR informațiile
din contextul furnizat.

Dacă răspunsul nu se află în context, spune că nu ai suficiente
informații în document.

Context:
{context}

Întrebarea:
{question}
""",
            "stream": False
        }
    )
    return response.json()['response']


def save_file(filename, text):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)


# Read
text = read_file("document.txt")

print("Documentul a fost citit cu succes.")
print(f"Numar caractere: {len(text)}")


# Chunk
chunks = chunk_text(text, 300)

print(f"Textul a fost împărțit în {len(chunks)} chunks.")

# User question
question = input("Pune o întrebare despre document: ")

# Retrieval
relevant_chunks = retrieve_chunks(chunks, question)

print(f"Am găsit {len(relevant_chunks)} chunks relevante pentru întrebarea ta.")

#Build context
context = "\n\n".join(relevant_chunks)


# Ask AI

answer = ask_llm(context, question)

print("\n=== Răspuns ===")
print(answer)


# Write

save_file("answer.txt", answer)
print("\nRăspunsul a fost salvat în 'answer.txt'.")
