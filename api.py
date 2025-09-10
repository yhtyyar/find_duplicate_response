"""REST API for the duplicate finder application."""

import io
import logging
from typing import Dict, Any, List

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from model import read_csv_from_string, find_duplicates, get_stats, _create_comparison_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Duplicate Log Finder API",
    description="API for finding duplicates in HTTP logs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware for remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Check service status.
    
    Returns:
        Dict[str, str]: Service status
    """
    return {"status": "healthy"}


@app.post("/find-duplicates", 
          tags=["Processing"],
          summary="Find duplicates in CSV file",
          description="Uploads a CSV file and finds duplicate records based on URL, method, response code, and status.")
async def find_duplicates_endpoint(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Find duplicates in uploaded CSV file.
    
    Args:
        file (UploadFile): Uploaded CSV file
        
    Returns:
        Dict[str, Any]: Processing results
        
    Raises:
        HTTPException: When file processing fails
    """
    try:
        # Read file content
        content = (await file.read()).decode('utf-8')
        
        # Use StringIO to work with string as file
        csv_file = io.StringIO(content)
        
        # Process CSV data
        rows = read_csv_from_string(csv_file)
        
        # Check for empty data
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        total = len(rows)
        duplicates_info = find_duplicates(rows)
        stats = get_stats(rows)
        duplicates_count = sum(v - 1 for v in duplicates_info.values())

        # Group duplicate rows
        duplicates_full: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            # Use the same key creation function as in the model for proper grouping
            key = _create_comparison_key(row)
            if key in duplicates_info:
                if key not in duplicates_full:
                    duplicates_full[key] = []
                duplicates_full[key].append(row)

        # Prepare response with duplicate group information
        result = {
            "total_rows": total,
            "duplicates_count": duplicates_count,
            "duplicates": duplicates_full,
            "statistics": stats,
            "duplicate_groups": len(duplicates_full)  # Number of different duplicate groups
        }
        
        return result
        
    except ValueError as e:
        logger.error(f"Data error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data error: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def index() -> HTMLResponse:
    """
    Simple HTML interface for testing the API.
    
    Returns:
        HTMLResponse: HTML page with interface
    """
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>HTTP Request Log Duplicate Finder</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #f5f5f5;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        input[type="file"] { 
            margin-bottom: 10px; 
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button { 
            background-color: #4CAF50; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            cursor: pointer; 
            border-radius: 4px;
            font-size: 16px;
        }
        button:hover { 
            background-color: #45a049; 
        }
        #result { 
            margin-top: 20px; 
            padding: 15px; 
            border-radius: 4px;
            background-color: #f9f9f9;
            display: none;
            overflow-x: auto;
        }
        .error { 
            background-color: #ffebee; 
            color: #c62828;
            border-left: 4px solid #f44336;
        }
        .success { 
            background-color: #e8f5e9; 
            color: #2e7d32;
            border-left: 4px solid #4CAF50;
        }
        .warning { 
            background-color: #fff3e0; 
            color: #ef6c00;
            border-left: 4px solid #ff9800;
        }
        .duplicate-group {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 4px;
        }
        .duplicate-group-0 { background-color: #e3f2fd; } /* Light blue */
        .duplicate-group-1 { background-color: #e8f5e8; } /* Light green */
        .duplicate-group-2 { background-color: #fff8e1; } /* Light yellow */
        .duplicate-group-3 { background-color: #f3e5f5; } /* Light purple */
        .duplicate-group-4 { background-color: #e0f7fa; } /* Light cyan */
        .duplicate-group-5 { background-color: #ffebee; } /* Light red */
        .duplicate-group-6 { background-color: #fafafa; } /* Light gray */
        .duplicate-group-7 { background-color: #fff3e0; } /* Light orange */
        
        .error-4xx { background-color: #ffebee; border-left: 4px solid #f44336; }
        .error-5xx { background-color: #f3e5f5; border-left: 4px solid #9c27b0; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f5f5f5;
        }
        .error-code-4xx { color: #f44336; font-weight: bold; }
        .error-code-5xx { color: #9c27b0; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>HTTP Request Log Duplicate Finder</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label for="csvFile">Upload CSV file:</label><br>
                <input type="file" id="csvFile" name="file" accept=".csv" required>
            </div>
            <button type="submit">Find Duplicates</button>
        </form>
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('csvFile');
            const resultDiv = document.getElementById('result');
            
            if (fileInput.files.length === 0) {
                showResult('Please select a file', 'error');
                return;
            }
            
            formData.append('file', fileInput.files[0]);
            
            // Show loading message
            showResult('Processing... Please wait.', 'warning');
            
            fetch('/find-duplicates', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.detail) {
                    showResult('Error: ' + data.detail, 'error');
                } else {
                    showResult(formatResult(data), 'success');
                }
            })
            .catch(error => {
                showResult('Network error: ' + error, 'error');
            });
        });
        
        function showResult(message, type) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<pre>' + message + '</pre>';
            resultDiv.className = type;
            resultDiv.style.display = 'block';
        }
        
        function formatResult(data) {
            let result = '=== Processing statistics ===\\n';
            result += 'Processed rows: ' + data.total_rows + '\\n';
            result += 'Duplicates found: ' + data.duplicates_count + '\\n';
            result += 'Duplicate groups: ' + data.duplicate_groups + '\\n\\n';
            
            if (data.duplicates_count > 0) {
                result += '=== Duplicate rows ===\\n';
                result += 'Response code | Start time                | Method  | URL\\n';
                result += '-'.repeat(200) + '\\n';
                
                let groupIndex = 0;
                for (const [key, rows] of Object.entries(data.duplicates)) {
                    for (const row of rows) {
                        const code = row['Response Code'] || '';
                        let codeDisplay = code;
                        
                        // Add special formatting for error codes
                        if (code.startsWith('4')) {
                            codeDisplay = code + ' [4xx Error]';
                        } else if (code.startsWith('5')) {
                            codeDisplay = code + ' [5xx Error]';
                        }
                        
                        result += 
                            codeDisplay.padEnd(15) + ' | ' +
                            (row['Request Start Time'] || '').substring(0, 25).padEnd(25) + ' | ' +
                            (row['Method'] || '').padEnd(7) + ' | ' +
                            (row['URL'] || '').substring(0, 150) + '\\n';
                    }
                    result += '\\n'; // Separate groups with empty line
                    groupIndex = (groupIndex + 1) % 8;
                }
                result += '\\n';
            }
            
            return result;
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=5000,
        log_level="info",
        reload=False  # Disable reload in production
    )