# Simple static file route addition for PureApex
# Serves files from /opt/pureapex/static/ at /s/ path

from starlette.responses import HTMLResponse, Response
from pathlib import Path
import mimetypes

STATIC_DIR = Path(__file__).parent / "static"

async def serve_static(request):
    filename = request.path_params.get("path", "")
    filepath = STATIC_DIR / filename
    if not filepath.exists() or not filepath.is_file() or ".." in filename:
        return Response("Not found", status_code=404)
    content_type = mimetypes.guess_type(str(filepath))[0] or "text/html"
    return Response(filepath.read_bytes(), media_type=content_type)
