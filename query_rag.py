import sys
import subprocess
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "<path_to_chromadb_persistence>"
MODEL = "qwen3.5:4b"

def load_db():
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection("cpts_notes")
    return collection

def search(collection, model, query, phase_filter=None, service_filter=None, n=5):
    embedding = model.encode(query).tolist()
    
    where = {}
    if phase_filter and service_filter:
        where = {"$and": [{"phase": phase_filter}, {"service": service_filter}]}
    elif phase_filter:
        where = {"phase": phase_filter}
    elif service_filter:
        where = {"service": service_filter}
    
    kwargs = {
        "query_embeddings": [embedding],
        "n_results": n,
        "include": ["documents", "metadatas", "distances"]
    }
    if where:
        kwargs["where"] = where
    
    results = collection.query(**kwargs)
    return results

def ask_ollama(prompt):
    OLLAMA_EXE = "<path_to_ollama_executable>"
    
    try:
        print("[*] Waiting for model response (may take 60-90s on first run)...")
        result = subprocess.run(
            [OLLAMA_EXE, "run", MODEL],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=360,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            return f"[!] Ollama subprocess error: {result.stderr}"

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "[!] Timed out after 360s — model may be loading, try again"
    except Exception as e:
        return f"[!] Ollama error: {e}"

def query_rag(question, phase=None, service=None):
    print(f"\n[*] Loading knowledge base...")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection("cpts_notes")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print(f"[*] Searching {collection.count()} chunks for: '{question}'")
    
    results = search(collection, embed_model, question, phase, service)
    
    if not results["documents"][0]:
        print("[!] No relevant chunks found")
        return
    
    # Build context from retrieved chunks
    context_parts = []
    print(f"\n[+] Retrieved {len(results['documents'][0])} relevant chunks:")
    
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        relevance = round((1 - dist) * 100, 1)
        print(f"  [{i+1}] {meta['file']} [{meta['phase']}][{meta['service']}] — {relevance}% match")
        context_parts.append(f"--- From: {meta['file']} ---\n{doc}")
    
    context = "\n\n".join(context_parts)
    
    prompt = f"""You are ToTheRoot, a CPTS-level penetration testing assistant.
Answer ONLY using the context from the user's personal CPTS notes below.
Be specific, technical, and actionable. Include exact commands where present in the notes.
If the notes don't cover the question, say so clearly.

=== CONTEXT FROM YOUR CPTS NOTES ===
{context}

=== QUESTION ===
{question}

=== ANSWER ==="""

    print(f"\n[*] Querying Ollama ({MODEL})...")
    response = ask_ollama(prompt)
    
    print(f"\n{'='*60}")
    print("TOTHEROOT ANSWER")
    print(f"{'='*60}")
    print(response)
    print(f"{'='*60}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 query_rag.py '<question>' [phase] [service]")
        print("       phase: enumeration, exploitation, post-exploitation, lateral-movement")
        print("       service: SMB, FTP, SSH, HTTP, MSSQL, PrivEsc, Kerberos, etc.")
        print("\nExamples:")
        print("  python3 query_rag.py 'how do I exploit SMB null sessions'")
        print("  python3 query_rag.py 'privesc via SUID binaries' post-exploitation PrivEsc")
        print("  python3 query_rag.py 'kerberoasting from linux' lateral-movement Kerberos")
        return
    
    question = sys.argv[1]
    phase = sys.argv[2] if len(sys.argv) > 2 else None
    service = sys.argv[3] if len(sys.argv) > 3 else None
    
    query_rag(question, phase, service)

if __name__ == "__main__":
    main()
