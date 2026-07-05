import fitz
import os
import sys
import json
import urllib.request
import time

def get_media_dir():
    try:
        payload = {"action": "getMediaDirPath", "version": 6}
        req = urllib.request.Request("http://127.0.0.1:8765", data=json.dumps(payload).encode("utf-8"))
        response = urllib.request.urlopen(req)
        res = json.loads(response.read().decode("utf-8"))
        if res.get("result"):
            return res["result"]
    except Exception as e:
        sys.stderr.write(f"Warning: Could not connect to AnkiConnect: {e}\n")
    return None

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No PDF path provided."}))
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(json.dumps({"error": f"PDF path '{pdf_path}' does not exist."}))
        sys.exit(1)
        
    media_dir = get_media_dir()
    if not media_dir:
        # Fallback to local scratch dir if Anki is not open
        media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_images")
        os.makedirs(media_dir, exist_ok=True)
        
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(json.dumps({"error": f"Failed to open PDF: {str(e)}"}))
        sys.exit(1)
        
    pages_data = []
    timestamp = int(time.time())
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_elements = []
        
        # Get images
        image_list = page.get_images()
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            try:
                rects = page.get_image_rects(xref)
                if rects:
                    # Use the first rect to position the image
                    rect = rects[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    filename = f"mcp_pdf_{timestamp}_p{page_num+1}_img_{img_idx+1}.{image_ext}"
                    filepath = os.path.join(media_dir, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                        
                    page_elements.append({
                        "type": "image",
                        "filename": filename,
                        "y": rect.y0,
                        "x": rect.x0,
                        "height": rect.y1 - rect.y0,
                        "width": rect.x1 - rect.x0
                    })
            except Exception as e:
                sys.stderr.write(f"Error extracting image {xref}: {e}\n")
                
        # Get text blocks
        text_blocks = page.get_text("blocks")
        for block in text_blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            clean_text = text.strip()
            if clean_text:
                page_elements.append({
                    "type": "text",
                    "text": clean_text,
                    "y": y0,
                    "x": x0,
                    "height": y1 - y0,
                    "width": x1 - x0
                })
                
        # Sort elements by vertical position (y), then horizontal (x)
        page_elements.sort(key=lambda el: (el["y"], el["x"]))
        
        pages_data.append({
            "page": page_num + 1,
            "elements": page_elements
        })
        
    print(json.dumps({"success": True, "pages": pages_data}))

if __name__ == "__main__":
    main()
