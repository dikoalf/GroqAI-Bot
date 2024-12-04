import os
import json
import io
import fitz
import minsearch
from deep_translator import GoogleTranslator
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Fungsi membaca PDF
def readPDF(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# fungsi melakukan retrieval augmented generation
def rag(text, data):
    # Inisialisasi index
    index = minsearch.Index(text_fields=["content","input"], keyword_fields=[])

    # Memasukkan data ke index
    if data:
        index.fit(data)

        # Terjemahkan teks input ke bahasa Inggris
        translatedText = GoogleTranslator(source='auto', target='en').translate(text)

        searchResult = index.search(
            query=translatedText,
            boost_dict={'content': 5.0, 'input': 1},
            num_results=min(len(data), 5),
            relevance_threshold=0.1
        )

        if searchResult:
            combinedInput = "\n\n".join([result["content"] for result in searchResult]) + "\n\n" + text
        else:
            combinedInput = text
    else:
        combinedInput = text

    return combinedInput

# Fungsi memecah teks jadi chunks
def textChunk(text, size=500):
    tokens = text.split()
    for i in range(0, len(tokens), size):
        chunk = ' '.join(tokens[i:i + size])
        yield chunk

# Fungsi sliding window untuk memori percakapan
def slidingWindowContext(messages, window_size=5):
    return messages[-window_size:]

# Fungsi autentikasi Google Drive menggunakan Service Account
def googleAuth():
    # Load service account info dari secrets
    serviceAccInfo = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_INFO'))
    
    # Buat kredensial menggunakan service account
    credentials = Credentials.from_service_account_info(serviceAccInfo)
    
    # Buat instance Google Drive service
    service = build('drive', 'v3', credentials=credentials)
    
    return service

# Fungsi menyimpan memory bot ke Google Drive
def saveToDrive(messages, drive, fileName, folderId = '1H1zWkXy8jgY-Xzc2QDTRFYm-pRkKcBX7'):
    # Simpan message history ke dalam memori menggunakan StringIO
    buffer = io.StringIO()
    json.dump(messages, buffer, indent=4)
    buffer.seek(0)

    # Konversi StringIO buffer menjadi BytesIO buffer
    bytesBuffer = io.BytesIO(buffer.getvalue().encode('utf-8'))

    # Buat metadata file
    fileMetadata = {'name': fileName}
    if folderId:
        fileMetadata['parents'] = [folderId]

    # Unggah file ke Google Drive
    media = MediaIoBaseUpload(bytesBuffer, mimetype='application/json')
    file = drive.files().create(body=fileMetadata, media_body=media, fields='id').execute()