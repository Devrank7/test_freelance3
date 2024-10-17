import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from api.pdf_handler import handle_pdf, PDFHandlerStrict, PDFHandlerImpl, SAVE_PATH

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/upload", response_class=HTMLResponse)
async def upload_pdf_form(request: Request):
    return templates.TemplateResponse("upload_file.html", {"request": request})


@app.post("/upload")
async def upload_pdf_file(request: Request, pdf_file: UploadFile = File(...)):
    path_for = await handle_pdf(PDFHandlerImpl(upload_pdf_file=pdf_file))
    return templates.TemplateResponse("download_file.html",
                                      {"request": request, "pdf_file_name": path_for})


@app.post("/freelance/upload")
async def upload_pdf_file(request: Request, pdf_file: UploadFile = File(...)):
    try:
        path_for = await handle_pdf(PDFHandlerStrict(upload_pdf_file=pdf_file))
        return templates.TemplateResponse("download_file.html",
                                          {"request": request, "pdf_file_name": path_for})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Некорректный PDF файл") from e


@app.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    file_path = f"{SAVE_PATH}/{filename}"
    if os.path.exists(file_path):
        response = FileResponse(path=file_path, filename=filename, media_type="application/pdf")

        async def remove_file():
            os.remove(file_path)

        response.background = remove_file
        return response
    else:
        return JSONResponse(content={"error": "Файл был удален из сервера, потому что вы его уже скачали"},
                            status_code=404)
