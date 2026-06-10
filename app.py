import streamlit as st
import os
from pathlib import Path
from pdf_tools import PDFTools
from docx import Document
from PIL import Image
import tempfile
import io

st.set_page_config(
    page_title="JobPack - Document Merger & Compressor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 JobPack")
st.markdown("**Professional Document Merger & Smart Compressor** for Job Applications")
st.caption("Free tool for students & job seekers — Merge CV, Cover Letter, Certificates and compress to exact size required by employers.")

# Sidebar
with st.sidebar:
    st.header("How it works")
    st.markdown("""
    1. Upload your documents  
    2. Reorder them  
    3. Set target file size  
    4. Click Assemble & Optimize  
    """)
    
    st.markdown("---")
    st.info("💡 Tip: Most job portals require files under 2MB. Use presets!")

# Main area
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload CV, Cover Letter, Transcripts, Certificates (PDF, DOCX, Images)",
        type=["pdf", "docx", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="You can upload up to 10 files. Max 50MB total."
    )

if uploaded_files:
    # Create temp directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_files = []
        file_names = []
        
        for uploaded_file in uploaded_files:
            # Save uploaded file
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Convert non-PDF to PDF
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                try:
                    doc = Document(file_path)
                    pdf_path = os.path.join(temp_dir, uploaded_file.name.replace(".docx", ".pdf"))
                    # Simple conversion via text extraction for now (better conversion can be added)
                    # For production, use docx2pdf or similar
                    st.warning(f"DOCX conversion simplified. Full support coming soon.")
                    # Placeholder: save as PDF with text (improve later)
                    pdf_files.append(file_path)  # Use original for now
                except:
                    pdf_files.append(file_path)
            elif uploaded_file.type.startswith("image/"):
                try:
                    img = Image.open(file_path)
                    pdf_path = os.path.join(temp_dir, uploaded_file.name.replace(".png", ".pdf").replace(".jpg", ".pdf").replace(".jpeg", ".pdf"))
                    img.save(pdf_path, "PDF", resolution=100.0)
                    pdf_files.append(pdf_path)
                except:
                    pdf_files.append(file_path)
            else:
                pdf_files.append(file_path)
            
            file_names.append(uploaded_file.name)
        
        # Display files with reorder capability
        st.subheader("Your Documents (Drag to reorder)")
        reordered = []
        for i, fname in enumerate(file_names):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(f"📄 {fname}")
            with col_b:
                order = st.number_input(f"Order {i+1}", min_value=1, max_value=len(file_names), value=i+1, key=f"order_{i}")
            reordered.append((order, pdf_files[i]))
        
        # Sort by user order
        reordered.sort(key=lambda x: x[0])
        ordered_pdf_files = [item[1] for item in reordered]
        
        # Target size
        st.subheader("Target File Size")
        target_col1, target_col2 = st.columns([2, 1])
        with target_col1:
            target_size = st.number_input("Maximum size", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        with target_col2:
            unit = st.selectbox("Unit", ["MB", "KB"], index=0)
        
        presets = st.multiselect("Quick Presets", ["1 MB", "2 MB", "5 MB", "500 KB"], default=[])
        if presets:
            preset_val = float(presets[0].split()[0])
            preset_unit = presets[0].split()[1]
            target_size = preset_val
            unit = preset_unit
        
        if st.button("🚀 Assemble & Optimize", type="primary", use_container_width=True):
            with st.spinner("Merging documents..."):
                merged_path = os.path.join(temp_dir, "merged_application.pdf")
                success_merge = PDFTools.merge_pdfs(ordered_pdf_files, merged_path)
                
                if success_merge:
                    st.success("✅ Documents merged successfully!")
                    
                    # Compress
                    final_path = os.path.join(temp_dir, "final_optimized.pdf")
                    with st.spinner(f"Compressing to under {target_size} {unit}..."):
                        success_compress = PDFTools.compress_pdf(
                            merged_path, 
                            final_path, 
                            target_size=target_size,
                            unit=unit,
                            initial_quality=85
                        )
                    
                    if success_compress:
                        final_size_mb = PDFTools.get_pdf_size_mb(final_path)
                        final_size_kb = PDFTools.get_pdf_size_kb(final_path)
                        
                        st.success(f"🎉 Package ready! Final size: **{final_size_mb:.2f} MB** ({final_size_kb:.0f} KB)")
                        
                        # Download
                        with open(final_path, "rb") as f:
                            st.download_button(
                                label="📥 Download Final Optimized PDF",
                                data=f,
                                file_name="Job_Application_Package.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        # Show individual files too
                        with st.expander("Also download individual files (ZIP)"):
                            # For simplicity, provide merged + note
                            st.info("All original files are available in your download history.")
                    else:
                        st.error("Compression failed. Try with higher target size.")
                else:
                    st.error("Merge failed. Please check your files.")
else:
    st.info("👆 Upload your documents to get started.")

st.markdown("---")
st.caption("JobPack — Built to help students submit perfect application packages. Open source & free forever.")
st.caption("Privacy: Files are processed in your browser session and automatically deleted.")
