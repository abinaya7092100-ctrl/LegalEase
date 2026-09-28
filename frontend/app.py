import base64
from datetime import date

import requests
import streamlit as st


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalEase - AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BACKEND_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .preview-box {
        border: 1px solid #cccccc;
        border-radius: 10px;
        padding: 25px;
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Generator</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    backend_url = st.text_input(
        "Backend URL",
        value=BACKEND_URL,
    )

    st.divider()

    st.info(
        "LegalEase helps generate customizable legal documents "
        "using AI. Review generated documents carefully before use."
    )


# ---------------------------------------------------------
# Main Input Section
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">📄 Document Details</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Agreement",
            "Lease Agreement",
            "Non-Disclosure Agreement (NDA)",
            "Service Agreement",
            "Sales Agreement",
            "Partnership Agreement",
            "Internship Agreement",
            "Freelance Agreement",
            "Loan Agreement",
            "Custom Legal Document",
        ],
    )


with col2:

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )


parties = st.text_area(
    "Parties",
    placeholder=(
        "Example:\n"
        "Party 1: ABC Technologies Pvt. Ltd.\n"
        "Party 2: John Kumar"
    ),
    height=120,
)


terms = st.text_area(
    "Terms and Conditions",
    placeholder=(
        "Enter the important terms of the agreement.\n\n"
        "Example:\n"
        "- Salary: ₹30,000 per month\n"
        "- Contract period: 1 year\n"
        "- Working hours: 9 AM to 6 PM\n"
        "- Notice period: 30 days"
    ),
    height=200,
)


# ---------------------------------------------------------
# Logo Upload
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">🎨 Branding</div>',
    unsafe_allow_html=True,
)

logo_file = st.file_uploader(
    "Upload Company / College Logo (optional)",
    type=["png", "jpg", "jpeg"],
)


logo_base64 = None

if logo_file is not None:

    logo_bytes = logo_file.getvalue()

    logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")

    st.image(
        logo_bytes,
        caption="Uploaded Logo",
        width=150,
    )


# ---------------------------------------------------------
# Generate Document
# ---------------------------------------------------------

st.divider()

generate_button = st.button(
    "🚀 Generate Legal Document",
    type="primary",
    use_container_width=True,
)


if generate_button:

    if not parties.strip():

        st.error("Please enter the parties involved.")

    elif not terms.strip():

        st.error("Please enter the terms and conditions.")

    else:

        request_data = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": str(effective_date),
        }

        try:

            with st.spinner("Generating legal document..."):

                response = requests.post(
                    f"{backend_url}/generate",
                    json=request_data,
                    timeout=120,
                )

            if response.status_code == 200:

                result = response.json()

                generated_document = result.get(
                    "document",
                    "",
                )

                st.session_state["generated_document"] = (
                    generated_document
                )

                st.session_state["document_type"] = document_type

                st.success("✅ Document generated successfully!")

            else:

                try:
                    error_message = response.json()
                except Exception:
                    error_message = response.text

                st.error(
                    f"Backend error ({response.status_code}): "
                    f"{error_message}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to the backend.\n\n"
                "Make sure FastAPI is running with:\n\n"
                "uvicorn backend.main:app --reload "
                "--host 127.0.0.1 --port 8000"
            )

        except requests.exceptions.Timeout:

            st.error(
                "❌ The request timed out. "
                "Please try again."
            )

        except Exception as e:

            st.error(
                f"❌ Unexpected error: {str(e)}"
            )


# ---------------------------------------------------------
# Generated Document
# ---------------------------------------------------------

if "generated_document" in st.session_state:

    st.divider()

    st.markdown(
        '<div class="section-title">📝 Generated Document</div>',
        unsafe_allow_html=True,
    )

    edited_document = st.text_area(
        "Edit your document",
        value=st.session_state["generated_document"],
        height=600,
    )

    st.session_state["generated_document"] = edited_document

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">👁️ Preview</div>',
        unsafe_allow_html=True,
    )

    preview_text = edited_document.replace(
        "\n",
        "<br>",
    )

    st.markdown(
        f"""
        <div class="preview-box">
            {preview_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # -----------------------------------------------------
    # Download Buttons
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">⬇️ Download</div>',
        unsafe_allow_html=True,
    )

    download_col1, download_col2, download_col3 = st.columns(3)


    # -----------------------------------------------------
    # TXT
    # -----------------------------------------------------

    with download_col1:

        if st.button(
            "📄 Prepare TXT",
            use_container_width=True,
        ):

            try:

                export_response = requests.post(
                    f"{backend_url}/export/txt",
                    json={
                        "document": edited_document,
                    },
                    timeout=60,
                )

                if export_response.status_code == 200:

                    st.download_button(
                        label="⬇️ Download TXT",
                        data=export_response.content,
                        file_name="legalease_document.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                else:

                    st.error("TXT export failed.")

            except Exception as e:

                st.error(
                    f"TXT export error: {str(e)}"
                )


    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------

    with download_col2:

        if st.button(
            "📝 Prepare DOCX",
            use_container_width=True,
        ):

            try:

                export_response = requests.post(
                    f"{backend_url}/export/docx",
                    json={
                        "document": edited_document,
                        "logo_base64": logo_base64,
                    },
                    timeout=60,
                )

                if export_response.status_code == 200:

                    st.download_button(
                        label="⬇️ Download DOCX",
                        data=export_response.content,
                        file_name="legalease_document.docx",
                        mime=(
                            "application/vnd.openxmlformats-"
                            "officedocument.wordprocessingml.document"
                        ),
                        use_container_width=True,
                    )

                else:

                    st.error("DOCX export failed.")

            except Exception as e:

                st.error(
                    f"DOCX export error: {str(e)}"
                )


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    with download_col3:

        if st.button(
            "📕 Prepare PDF",
            use_container_width=True,
        ):

            try:

                export_response = requests.post(
                    f"{backend_url}/export/pdf",
                    json={
                        "document": edited_document,
                        "logo_base64": logo_base64,
                    },
                    timeout=60,
                )

                if export_response.status_code == 200:

                    st.download_button(
                        label="⬇️ Download PDF",
                        data=export_response.content,
                        file_name="legalease_document.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                else:

                    st.error("PDF export failed.")

            except Exception as e:

                st.error(
                    f"PDF export error: {str(e)}"
                )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "LegalEase © 2026 | AI-Powered Legal Document Generator"
)