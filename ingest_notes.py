import os
import re
import chromadb
from sentence_transformers import SentenceTransformer

VAULT_PATH = "<path_to_your_obsidian_vault>"
DB_PATH = "<path_to_chromadb_persistence>"

# Phase mapping based on folder structure
PHASE_MAP = {
    "01-Information Gathering": "enumeration",
    "02-Pre-Exploitation": "pre-exploitation", 
    "03-Exploitation": "exploitation",
    "04-Post-Exploitation": "post-exploitation",
    "05-Lateral Movement": "lateral-movement",
    "Documentation and Reporting": "reporting"
}

# Skip these - not useful for RAG
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".docx", ".pdf"}
SKIP_FILENAMES = {"Untitled", "Habits", "Weeks", "Categories", "Project Ideas"}

def detect_phase(filepath):
    for folder, phase in PHASE_MAP.items():
        if folder in filepath:
            return phase
    return "general"

def detect_service(filepath, content):
    services = {
        "SMB": ["smb", "445", "samba", "cifs"],
        "FTP": ["ftp", "21,20", "vsftpd"],
        "SSH": ["ssh", "22", "openssh"],
        "HTTP": ["http", "web", "80", "443", "nginx", "apache"],
        "MSSQL": ["mssql", "1433", "sql server"],
        "MySQL": ["mysql", "3306"],
        "RDP": ["rdp", "3389", "remote desktop"],
        "DNS": ["dns", "53", "zone transfer"],
        "SMTP": ["smtp", "25", "587", "mail"],
        "LDAP": ["ldap", "389", "active directory"],
        "WinRM": ["winrm", "5985", "5986", "evil-winrm"],
        "Kerberos": ["kerberos", "88", "kerberoast", "asrep"],
        "NFS": ["nfs", "111", "2049", "showmount"],
        "SNMP": ["snmp", "161", "162"],
        "IPMI": ["ipmi", "623", "bmc", "ilo", "idrac"],
        "LFI": ["lfi", "local file inclusion", "php://filter"],
        "SQLi": ["sql injection", "sqlmap", "union based"],
        "XSS": ["xss", "cross-site scripting"],
        "XXE": ["xxe", "xml external"],
        "ActiveDirectory": ["active directory", "domain controller", "bloodhound", "mimikatz"],
        "PrivEsc": ["privilege escalation", "privesc", "suid", "sudo", "linpeas", "winpeas"],
    }
    
    filepath_lower = filepath.lower()
    content_lower = content[:500].lower()  # Check first 500 chars
    
    for service, keywords in services.items():
        for kw in keywords:
            if kw in filepath_lower or kw in content_lower:
                return service
    return "general"

def chunk_markdown(content, filepath, max_chunk=800):
    chunks = []
    
    # Split by headers
    sections = re.split(r'\n(?=#{1,3} )', content)
    
    current_chunk = ""
    for section in sections:
        # Skip empty sections
        if not section.strip():
            continue
        # Skip pure image lines
        if re.match(r'^!\[.*\]\(.*\)$', section.strip()):
            continue
        # Skip obsidian callouts with no real content
        if len(section.strip()) < 30:
            continue
            
        if len(current_chunk) + len(section) > max_chunk:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = section
        else:
            current_chunk += "\n" + section
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def ingest():
    print("[*] Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Delete and recreate collection for fresh ingest
    try:
        client.delete_collection("cpts_notes")
        print("[*] Cleared existing collection")
    except:
        pass
    
    collection = client.create_collection(
        name="cpts_notes",
        metadata={"hnsw:space": "cosine"}
    )
    
    print("[*] Loading embedding model (first run downloads ~80MB)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    total_chunks = 0
    total_files = 0
    skipped = 0
    
    print(f"[*] Walking vault: {VAULT_PATH}\n")
    
    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        
        for filename in files:
            # Skip non-markdown
            ext = os.path.splitext(filename)[1].lower()
            if ext in SKIP_EXTENSIONS:
                continue
            if ext != ".md":
                continue
            
            # Skip junk files
            skip = False
            for skip_name in SKIP_FILENAMES:
                if skip_name.lower() in filename.lower():
                    skip = True
                    break
            if skip:
                skipped += 1
                continue
            
            filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(filepath, VAULT_PATH)
            
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                print(f"[!] Could not read {filename}: {e}")
                continue
            
            # Skip tiny files
            if len(content.strip()) < 100:
                skipped += 1
                continue
            
            phase = detect_phase(relative_path)
            service = detect_service(relative_path, content)
            chunks = chunk_markdown(content, filepath)
            
            if not chunks:
                skipped += 1
                continue
            
            # Embed and store
            for i, chunk in enumerate(chunks):
                chunk_id = f"{relative_path}::chunk_{i}".replace(" ", "_")
                
                try:
                    embedding = model.encode(chunk).tolist()
                    
                    collection.add(
                        ids=[chunk_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[{
                            "file": filename,
                            "path": relative_path,
                            "phase": phase,
                            "service": service,
                            "chunk_index": i
                        }]
                    )
                    total_chunks += 1
                except Exception as e:
                    print(f"[!] Error embedding chunk from {filename}: {e}")
            
            total_files += 1
            print(f"  [+] {relative_path} → {len(chunks)} chunks [{phase}] [{service}]")
    
    print(f"\n{'='*60}")
    print(f"INGESTION COMPLETE")
    print(f"  Files processed : {total_files}")
    print(f"  Files skipped   : {skipped}")
    print(f"  Total chunks    : {total_chunks}")
    print(f"  DB location     : {DB_PATH}")
    print(f"{'='*60}")

if __name__ == "__main__":
    ingest()
