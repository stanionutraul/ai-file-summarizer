
import requests
import sys
import re
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")


def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def chunk_text(text, chunk_size=300):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks


def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize("NFD", text)

    return "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )


def retrieve_chunks(chunks, query):
    stop_words = {
        "de", "ce", "si", "in", "la", "cu",
        "este", "sunt", "un", "o", "the", "is", "are"
    }

    normalized_query = normalize_text(query)
    query_words = re.findall(r"\w+", normalized_query)

    query_words = [
        word for word in query_words
        if word not in stop_words and len(word) > 1
    ]

    relevant_chunks = []

    for chunk in chunks:
        normalized_chunk = normalize_text(chunk)
        chunk_words = set(
            re.findall(r"\w+", normalized_chunk)
        )

        score = 0

        for word in query_words:
            if word in chunk_words:
                score += 1

        if score > 0:
            relevant_chunks.append((score, chunk))

    relevant_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        chunk for score, chunk in relevant_chunks[:3]
    ]


def ask_llm(context, question):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": f"""
Răspunde în limba română folosind exclusiv contextul.

Reguli:
- Nu folosi cunoștințe externe contextului.
- Nu inventa explicații, cauze sau detalii.
- Dacă informația nu este prezentă clar în context,
  spune că nu ai suficiente informații în document.
- Dacă întrebarea se referă la o planetă, nu atribui
  informațiile altei planete.

Context:
{context}

Întrebarea:
{question}
""",
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]


def save_file(filename, text):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)


# 1. Read document
text = read_file("document.txt")

print("Documentul a fost citit cu succes.")
print(f"Număr caractere: {len(text)}")


# 2. Chunk
chunks = chunk_text(text, 300)

print(f"Textul a fost împărțit în {len(chunks)} chunks.")


# 3. User question
question = input("Pune o întrebare despre document: ")


# 4. Retrieval
relevant_chunks = retrieve_chunks(chunks, question)

print(
    f"Am găsit {len(relevant_chunks)} chunks relevante "
    "pentru întrebarea ta."
)


# 5. Build context and generate answer
if not relevant_chunks:
    answer = (
        "Nu am găsit informații relevante în document "
        "pentru a răspunde la această întrebare."
    )
else:
    context = "\n\n".join(relevant_chunks)
    answer = ask_llm(context, question)


# 6. Show answer
print("\n=== Răspuns ===\n")
print(answer)


# 7. Save answer
save_file("answer.txt", answer)

print("\nRăspunsul a fost salvat în 'answer.txt'.")