# MY PC REMEMBERS
> **Private, Local AI Memory for Your Computer**  
> *"Search your files by what you remember, not what they're called."*

Prepared for the **Snapdragon AI Lab Build & Present Challenge**.

---

## 1. Project Overview

**MY PC REMEMBERS** is a privacy-first, on-device AI memory layer for personal computers. Instead of forcing users to remember cryptic filenames, rigid folder paths, or exact syntax, the system indexes user-selected directories and allows users to search their personal files using natural human memory queries:

```
"Find the Dijkstra notes I worked on recently."
"Where did I implement minimum spanning tree using DSU?"
"I remember a PDF about graph algorithms."
```

The system retrieves the most relevant local documents and code files in milliseconds and provides **explainable results** detailing *why* each file matched based on its extracted content.

---

## 2. The Problem

Modern personal computers store thousands of files across deep nested directory trees. When people need to recall information:
1. **Filename Amnesia:** Users rarely remember exact filenames (e.g. `dijkstra_v2_final.cpp` vs `graph_notes_week4.pdf`).
2. **Keyword Fragility:** Standard OS search relies on exact keyword substrings, failing when concepts are described in different words (e.g., searching for *"shortest path priority queue"* fails to match files containing *"single-source minimum distance with binary heap"*).
3. **Cloud Privacy Dilemma:** Existing AI search solutions upload personal documents, source code, and private notes to third-party cloud servers.
4. **Hardware Underutilization:** Modern client hardware (Apple Silicon M1, Snapdragon X Elite NPUs) sits idle while cloud APIs incur latency, subscription fees, and bandwidth overhead.

---

## 3. The Solution

An **on-device semantic memory layer** that runs 100% locally on personal laptops:
- **Zero Cloud Dependence:** All text extraction, embedding generation, vector indexing, and RAG explanations execute on the client machine.
- **Semantic Understanding:** Translates natural memory descriptions into dense vector embeddings and retrieves matching concepts.
- **Explainable RAG:** Never produces black-box matches. Every search result includes a grounded explanation of *why* it matched.
- **Incremental & Battery-Friendly:** Hashes file contents with SHA-256 and skips unchanged files, minimizing CPU and battery consumption.
- **Hardware-Agnostic with Snapdragon Readiness:** Developed on Apple Silicon (M1 8GB) using modular inference abstractions (`InferenceBackend`) that map directly to the Qualcomm Hexagon NPU on Snapdragon-powered PCs.

---

## 4. Key Features

- **Semantic Memory Search:** Query files by conceptual memory, algorithms, libraries, or document content.
- **Format Affinity & Recency Weighting:** Boosts relevant file formats (e.g., PDFs vs code) and recent modifications when queries contain temporal hints (*"worked on recently"*).
- **Explainable Results:** Clear, grounded reasoning for every search result derived directly from indexed excerpts.
- **Safe Directory Boundaries:** Scans only explicitly chosen user folders. System paths (`/System`, `/etc`, `~/.ssh`, `keychains`) are strictly forbidden.
- **Native OS File Opener:** Open files directly into system viewers using platform-native handlers (`open` on macOS, `start` on Windows, `xdg-open` on Linux).
- **Graceful Fallback:** If local LLM is offline or not installed, semantic search operates uninterrupted with deterministic grounded explanations.
- **Low RAM Footprint:** Peak memory usage is under 500 MB (ideal for 8 GB RAM machines).

---

## 5. Architecture & Data Flow

```
+-----------------------------------------------------------------------+
|                              USER QUERY                               |
|       "Find the Dijkstra notes I worked on recently"                  |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    QUERY ANALYSIS & EMBEDDING                         |
|   Temporal Extraction ("recently") -> Date filter active              |
|   Local Embedding: ONNX Quantized BAAI/bge-small-en-v1.5 (384-dim)   |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                     LOCAL VECTOR SEARCH (FAISS)                       |
|   IndexFlatIP Cosine Nearest Neighbor Lookup                          |
|   Retrieves Top-K matching chunks from local data/faiss.index         |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                CHUNKS-TO-FILE AGGREGATION & RANKING                   |
|   Groups chunks by File ID                                            |
|   Computes composite score = best_chunk + log(chunks) + recency_boost |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|               GROUNDED EXPLANATION (LOCAL LLM / RAG)                  |
|   Ollama (Llama 3.2 1B) / Grounded Fallback Provider                  |
|   "Contains Dijkstra's algorithm, shortest paths, priority queues."   |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                           REACT DESKTOP UI                            |
|   1. graph_notes.pdf  - 86% relevant  [Open File]  [Show Context]     |
|   2. dijkstra.cpp     - 80% relevant  [Open File]  [Show Context]     |
+-----------------------------------------------------------------------+
```

---

## 6. Technology Stack

### Backend
- **Python 3.10+ / 3.11+**
- **FastAPI & Uvicorn:** High-performance local REST API server.
- **SQLite (WAL Mode):** Embedded metadata repository tracking files, hashes, documents, chunks, and search history.
- **FAISS (`faiss-cpu`):** In-memory and persisted local vector index for high-speed nearest-neighbor search.
- **PyMuPDF (`fitz`):** Fast local PDF extraction.
- **python-docx & python-pptx:** Word and PowerPoint text parsing.
- **FastEmbed (`onnxruntime`):** Quantized, lightweight local embedding generation without PyTorch bloat.

### Frontend
- **React 19, TypeScript, Vite**
- **Tailwind CSS:** Restrained, desktop-oriented UI adhering to zero-pill discipline and unboxed metadata.
- **Lucide Icons:** Clean system icons.

---

## 7. Supported File Types

| Category | File Extensions |
| :--- | :--- |
| **Documents** | `.pdf`, `.docx`, `.txt`, `.md`, `.csv` |
| **Presentations** | `.pptx` |
| **Source Code** | `.py`, `.cpp`, `.c`, `.h`, `.hpp`, `.java`, `.js`, `.ts`, `.tsx`, `.html`, `.css`, `.sql`, `.json`, `.xml`, `.yaml`, `.yml`, `.sh` |

---

## 8. Privacy & Security Model

1. **No External Network Calls:** Embeddings and database storage run on `127.0.0.1`.
2. **Explicit Folder Opt-In:** The indexer never scans whole disks or traverses beyond folders selected by the user.
3. **Sensitive Path Sanitization:** Blocklists prevent scanning of `.ssh`, `.gnupg`, `.aws`, `.git`, keychains, or system directories.
4. **Zero Code Execution:** File contents are parsed strictly as text data; code files are never executed.
5. **No Telemetry:** No analytical tracking, third-party beacons, or telemetry logging.

---

## 9. Installation & Setup

### Prerequisites
- macOS (Apple Silicon M1/M2/M3) or Linux / Windows
- Python 3.10+
- Node.js 18+

### Setup Commands
```bash
# Clone the repository
git clone https://github.com/example/my-pc-remembers.git
cd my-pc-remembers

# Run automated setup
bash scripts/setup.sh
```

Or manually:
```bash
# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
npm install

# Setup environment variables
cp .env.example .env
```

---

## 10. Running the Application

### Option A: Unified Dev Server (Recommended)
Runs the complete stack with Express proxy on port 3000 and auto-spawns the FastAPI backend:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Option B: Running Services Separately
Terminal 1 (Backend on 127.0.0.1:8001):
```bash
bash scripts/start_backend.sh
```

Terminal 2 (Frontend on 127.0.0.1:3000):
```bash
bash scripts/start_frontend.sh
```

---

## 11. Optional Local LLM (Ollama)

To use Ollama for on-device natural language explanations:
1. Install [Ollama](https://ollama.ai/).
2. Pull a compact quantized model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Start the Ollama server:
   ```bash
   ollama serve
   ```
4. In the app's **Settings** tab, switch **LLM Provider** to `Ollama`.

*Note: If Ollama is not running, MY PC REMEMBERS automatically falls back to deterministic grounded matching without interrupting search.*

---

## 12. Testing

Run the full automated test suite covering scanner, extraction, chunking, embeddings, vector store, ranking, and API endpoints:
```bash
python3 -m pytest backend/tests/ -v
```

All 20 test cases run locally in under 2 seconds.

---

## 13. Benchmarking

Run the local benchmark script to measure real hardware performance:
```bash
python3 scripts/benchmark.py
```

### Benchmark Results on MacBook Air M1 (8 GB RAM):
- **Embedding Latency:** ~9.2 ms / chunk
- **Average Retrieval Latency:** ~13.0 ms
- **Peak Process Memory (RSS):** ~454 MB
- **Output:** Stored in `data/benchmark_results.json`

---

## 14. Snapdragon Architecture Strategy

The application is architected from day one to deploy on Qualcomm Snapdragon-powered AI PCs (Snapdragon X Elite / Snapdragon X Plus):

```
+-------------------------------------------------------------------+
|                     InferenceBackend (Abstract)                   |
|                   backend/app/runtime/inference.py                |
+---------------------------------+---------------------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
+-------------------------------+       +-------------------------------+
|     CPUInferenceBackend       |       |    FutureSnapdragonBackend    |
| (Current: Apple Silicon Mac)  |       |  (Target: Snapdragon X Elite) |
| - ONNX CPUExecutionProvider   |       | - Qualcomm Hexagon NPU        |
| - ARM NEON vector instructions|       | - ONNX QNNExecutionProvider   |
| - RAM: < 500 MB               |       | - 45+ TOPS NPU Acceleration   |
+-------------------------------+       +-------------------------------+
```

When deployed on a Snapdragon PC:
1. The `InferenceBackend` routes ONNX models through `QNNExecutionProvider` (DirectML / Qualcomm Neural Processing SDK).
2. Embedding generation offloads entirely from the CPU to the 45 TOPS Hexagon NPU.
3. Search latency drops into single-digit milliseconds while preserving system battery life.

---

## 15. Known Limitations & Next Steps

### Current Limitations:
- Scans text-based document and source code files (images and scanned PDFs without embedded text layers require OCR).
- Optimized for single-user local workstation storage.

### Planned Enhancements:
1. **On-Device Vision / Multimodal:** Snapdragon NPU accelerated image embeddings (CLIP / MobileNet) for screenshot search.
2. **Audio / Voice Memory:** Local Whisper voice queries.
3. **Cross-Document Relationship Graph:** Link notes and code implementing the same algorithms.

---

## 16. License

MIT License. Designed and built for the Snapdragon AI Lab Build & Present Challenge.
