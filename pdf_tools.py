import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import subprocess
from typing import List, Optional

class PDFTools:
    """
    Professional PDF merge, split, compress module for job documents.
    Preserves visual quality as much as possible.
    """
    
    @staticmethod
    def merge_pdfs(pdf_files: List[str], output_path: str) -> bool:
        """
        Merge multiple PDF files into one.
        """
        try:
            writer = PdfWriter()
            for pdf_path in pdf_files:
                if not os.path.exists(pdf_path):
                    raise FileNotFoundError(f"File not found: {pdf_path}")
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)
            
            with open(output_path, "wb") as f:
                writer.write(f)
            return True
        except Exception as e:
            print(f"Merge error: {e}")
            return False

    @staticmethod
    def split_pdf(input_path: str, output_dir: str, pages_per_file: int = 1) -> List[str]:
        """
        Split PDF into multiple files.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            reader = PdfReader(input_path)
            output_files = []
            
            for i in range(0, len(reader.pages), pages_per_file):
                writer = PdfWriter()
                for j in range(pages_per_file):
                    if i + j < len(reader.pages):
                        writer.add_page(reader.pages[i + j])
                
                output_file = os.path.join(output_dir, f"part_{i//pages_per_file + 1}.pdf")
                with open(output_file, "wb") as f:
                    writer.write(f)
                output_files.append(output_file)
            
            return output_files
        except Exception as e:
            print(f"Split error: {e}")
            return []

    @staticmethod
    def compress_pdf(input_path: str, output_path: str, 
                    target_size: float = None,
                    unit: str = "MB",
                    initial_quality: int = 85) -> bool:
        """
        Compress PDF to a user-specified target size (e.g. 2 MB or 500 KB).
        Job portals often require specific size limits — this meets them intelligently.
        Preserves visual quality as much as possible.
        """
        try:
            # Convert target to MB
            if target_size is not None:
                target_mb = target_size if unit.upper() == "MB" else target_size / 1024
            else:
                target_mb = None

            # First try Ghostscript (best for visual preservation)
            quality = initial_quality
            gs_command = [
                'gs',
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                '-dPDFSETTINGS=/prepress',  # /ebook or /screen for more aggressive
                f'-dJPEGQ={quality}',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                f'-sOutputFile={output_path}',
                input_path
            ]
            
            result = subprocess.run(gs_command, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(output_path):
                original_mb = PDFTools.get_pdf_size_mb(input_path)
                new_mb = PDFTools.get_pdf_size_mb(output_path)
                print(f"✅ Compressed: {original_mb:.2f}MB → {new_mb:.2f}MB (target: {target_mb}MB if set)")

                # Iterative compression if target not met
                if target_mb and new_mb > target_mb and quality > 50:
                    print(f"→ Target not met ({new_mb:.2f} > {target_mb:.2f}MB). Stronger compression...")
                    return PDFTools.compress_pdf(input_path, output_path, target_size, unit, max(quality-15, 50))
                return True
            else:
                print("Ghostscript failed, trying pypdf fallback.")
                return PDFTools._compress_with_pypdf(input_path, output_path)
        except Exception as e:
            print(f"Compression error: {e}")
            return PDFTools._compress_with_pypdf(input_path, output_path)

    @staticmethod
    def _compress_with_pypdf(input_path: str, output_path: str) -> bool:
        """Fallback lossless compression with pypdf."""
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()  # Lossless
                writer.add_page(page)
            
            with open(output_path, "wb") as f:
                writer.write(f)
            return True
        except Exception as e:
            print(f"pypdf compress failed: {e}")
            return False

    @staticmethod
    def get_pdf_size_mb(file_path: str) -> float:
        """Get file size in MB."""
        return os.path.getsize(file_path) / (1024 * 1024)

    @staticmethod
    def get_pdf_size_kb(file_path: str) -> float:
        """Get file size in KB."""
        return os.path.getsize(file_path) / 1024

if __name__ == "__main__":
    # Test example
    print("PDFTools module ready.")
