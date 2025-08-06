import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_extractor import extract_text_from_pdf
from app.db.pinecone_handler import store_embeddings
from app.db.postgres_handler import log_pdf_data

from fastapi import Body
from app.services.llm import generate_response

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)

        file_location = f"temp/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Extract text
        extracted_text = extract_text_from_pdf(file_location)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF.")

        # Store embeddings in Pinecone
        embedding_ids = store_embeddings(extracted_text)

        # Log into PostgreSQL
        log_pdf_data(file.filename, embedding_ids)

        return {
            "message": "PDF processed and stored successfully.",
            "file": file.filename,
            "embeddings_stored": len(embedding_ids)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.post("/query")
async def semantic_query(query: str = Body(..., embed=True)):
    try:
        response = generate_response(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
