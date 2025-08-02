from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import os
import datetime
import zipfile
import io

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/export-data")
async def export_user_data(request: Request):
    """Export all user data as JSON"""
    try:
        # For now, we'll export file information since we don't have database access
        # Get available output files information
        output_dirs = ['gem', 'ireps', 'eproc', 'ap']
        available_files = []
        
        for dir_name in output_dirs:
            output_path = f"outputs/{dir_name}"
            if os.path.exists(output_path):
                try:
                    files = os.listdir(output_path)
                    for file in files:
                        file_path = os.path.join(output_path, file)
                        if os.path.isdir(file_path):
                            sub_files = os.listdir(file_path)
                            available_files.append({
                                "tool": dir_name.upper(),
                                "sessionId": file,
                                "files": [f for f in sub_files if f.endswith(('.xlsx', '.csv'))],
                                "path": f"outputs/{dir_name}/{file}"
                            })
                except Exception as e:
                    print(f"Error reading directory {output_path}: {e}")
        
        # Prepare export data
        export_data = {
            "exportDate": str(datetime.datetime.now()),
            "user": {"id": "export_user", "email": "export@example.com"},
            "scrapingJobs": [],
            "availableFiles": available_files,
            "summary": {
                "totalJobs": 0,
                "completedJobs": 0,
                "failedJobs": 0,
                "runningJobs": 0,
                "totalOutputFiles": sum(len(dir_info['files']) for dir_info in available_files),
                "availableSessions": len(available_files)
            }
        }
        
        return JSONResponse(export_data)
        
    except Exception as e:
        print(f"Export data error: {str(e)}")
        return JSONResponse({"error": "Failed to export data"}, status_code=500)

@app.get("/api/export-files")
async def export_output_files(request: Request):
    """Export all output files as ZIP"""
    try:
        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add output directories to the zip
            output_dirs = ['gem', 'ireps', 'eproc', 'ap']
            has_files = False
            
            for dir_name in output_dirs:
                output_path = f"outputs/{dir_name}"
                if os.path.exists(output_path):
                    try:
                        files = os.listdir(output_path)
                        if files:
                            # Add the entire directory to the zip
                            for root, dirs, files in os.walk(output_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arc_name = os.path.relpath(file_path, "outputs")
                                    zip_file.write(file_path, arc_name)
                                    has_files = True
                    except Exception as e:
                        print(f"Error adding directory {output_path} to zip: {e}")
            
            if not has_files:
                # If no files found, create an empty zip with a readme
                zip_file.writestr("README.txt", "No output files found at the time of export.")
        
        # Prepare response
        zip_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=output_files_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"}
        )
        
    except Exception as e:
        print(f"Export files error: {str(e)}")
        return JSONResponse({"error": "Failed to export files"}, status_code=500)

@app.get("/")
async def root():
    return {"message": "Export Server is running!"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Export Server on port 8000...")
    print("📡 API will be available at: http://localhost:8000")
    print("📦 Export endpoints:")
    print("   - GET /api/export-data")
    print("   - GET /api/export-files")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 