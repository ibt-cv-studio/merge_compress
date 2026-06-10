# merge_compress - Professional Document Merger & Compressor

A free web tool for students and job seekers to merge CVs, cover letters, transcripts, and certificates into one optimized PDF that meets exact size requirements from employers.

## Features
- Merge multiple PDFs, DOCX, and images
- Smart compression to user-specified size (MB/KB)
- Drag-and-drop reordering
- High visual quality preservation using Ghostscript
- Mobile-friendly

## How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment
- **Streamlit Cloud**: Connect this repo
- **Docker** (recommended for production):
  ```dockerfile
  FROM python:3.12-slim
  RUN apt-get update && apt-get install -y ghostscript
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  EXPOSE 8501
  CMD ["streamlit", "run", "app.py", "--server.port=8501"]
  ```

## Tech Stack
- Streamlit
- pypdf + Ghostscript
- PDFTools engine

Made for everyone who needs professional application packages.
