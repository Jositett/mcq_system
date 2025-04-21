"""
File storage service for the MCQ Test & Attendance System.
This module provides functions to store and retrieve files, with support for local and cloud storage.
"""

import os
import uuid
import shutil
import logging
from typing import Optional, BinaryIO, Dict, Any, List
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

from app.core.settings import settings

logger = logging.getLogger(__name__)

# Base directory for file storage
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), settings.UPLOAD_DIR)


class FileStorageService:
    """Service for handling file storage operations."""
    
    @staticmethod
    def ensure_upload_dir(subdir: Optional[str] = None) -> str:
        """
        Ensure the upload directory exists.
        
        Args:
            subdir: Optional subdirectory within the upload directory
            
        Returns:
            Path to the upload directory
        """
        # Create base upload directory if it doesn't exist
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
        
        # If subdirectory is specified, create it
        if subdir:
            subdir_path = os.path.join(UPLOAD_DIR, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
            return subdir_path
        
        return UPLOAD_DIR
    
    @staticmethod
    async def save_upload_file(
        upload_file: UploadFile,
        subdir: Optional[str] = None,
        filename: Optional[str] = None,
        max_size_mb: float = 5.0,
        allowed_types: Optional[List[str]] = None
    ) -> str:
        """
        Save an uploaded file to storage.
        
        Args:
            upload_file: The uploaded file
            subdir: Optional subdirectory within the upload directory
            filename: Optional filename to use (if None, a UUID will be generated)
            max_size_mb: Maximum file size in MB
            allowed_types: List of allowed MIME types
            
        Returns:
            Path to the saved file (relative to the upload directory)
        """
        # Validate file size
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        file_size = 0
        
        # Read file content
        content = await upload_file.read()
        file_size = len(content)
        
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the limit of {max_size_mb} MB"
            )
        
        # Validate file type if allowed_types is specified
        if allowed_types and upload_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {upload_file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Generate filename if not provided
        if not filename:
            # Get file extension from content type or original filename
            ext = ""
            if "." in upload_file.filename:
                ext = os.path.splitext(upload_file.filename)[1]
            elif "/" in upload_file.content_type:
                mime_type = upload_file.content_type.split("/")[1]
                ext = f".{mime_type}"
            
            # Generate a unique filename
            filename = f"{uuid.uuid4()}{ext}"
        
        # Ensure upload directory exists
        upload_dir = FileStorageService.ensure_upload_dir(subdir)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        
        # Write file content
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return relative path
        if subdir:
            return os.path.join(subdir, filename)
        return filename
    
    @staticmethod
    def save_base64_image(
        base64_data: str,
        subdir: Optional[str] = None,
        filename: Optional[str] = None,
        max_size_mb: float = 5.0
    ) -> str:
        """
        Save a base64-encoded image to storage.
        
        Args:
            base64_data: Base64-encoded image data
            subdir: Optional subdirectory within the upload directory
            filename: Optional filename to use (if None, a UUID will be generated)
            max_size_mb: Maximum file size in MB
            
        Returns:
            Path to the saved file (relative to the upload directory)
        """
        # Remove data URL prefix if present
        if "," in base64_data:
            # Extract content type and base64 data
            prefix, base64_data = base64_data.split(",", 1)
            content_type = prefix.split(";")[0].split(":")[1] if ":" in prefix else "image/jpeg"
        else:
            content_type = "image/jpeg"
        
        # Decode base64 data
        try:
            image_data = base64.b64decode(base64_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid base64 data: {str(e)}"
            )
        
        # Validate file size
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        if len(image_data) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image size exceeds the limit of {max_size_mb} MB"
            )
        
        # Generate filename if not provided
        if not filename:
            # Get file extension from content type
            ext = ".jpg"  # Default to .jpg
            if "/" in content_type:
                mime_type = content_type.split("/")[1]
                ext = f".{mime_type}"
            
            # Generate a unique filename
            filename = f"{uuid.uuid4()}{ext}"
        
        # Ensure upload directory exists
        upload_dir = FileStorageService.ensure_upload_dir(subdir)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        
        # Write file content
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Return relative path
        if subdir:
            return os.path.join(subdir, filename)
        return filename
    
    @staticmethod
    def get_file_url(file_path: str) -> str:
        """
        Get the URL for a file.
        
        Args:
            file_path: Path to the file (relative to the upload directory)
            
        Returns:
            URL to access the file
        """
        # In production, this would return a CDN URL or a signed URL for cloud storage
        # For now, we'll just return a local URL
        base_url = settings.API_PREFIX + "/static/uploads"
        return f"{base_url}/{file_path}"
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file (relative to the upload directory)
            
        Returns:
            True if the file was deleted, False otherwise
        """
        # Get absolute path
        abs_path = os.path.join(UPLOAD_DIR, file_path)
        
        # Check if file exists
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            return False
        
        # Delete file
        try:
            os.remove(abs_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting file {abs_path}: {str(e)}")
            return False
    
    @staticmethod
    def resize_image(
        image_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: int = 85
    ) -> str:
        """
        Resize an image.
        
        Args:
            image_path: Path to the image (relative to the upload directory)
            width: Target width (if None, will be calculated from height)
            height: Target height (if None, will be calculated from width)
            quality: JPEG quality (0-100)
            
        Returns:
            Path to the resized image (relative to the upload directory)
        """
        # Get absolute path
        abs_path = os.path.join(UPLOAD_DIR, image_path)
        
        # Check if file exists
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            raise FileNotFoundError(f"Image {image_path} not found")
        
        # Open image
        try:
            img = Image.open(abs_path)
        except Exception as e:
            raise ValueError(f"Error opening image {image_path}: {str(e)}")
        
        # Calculate new dimensions
        orig_width, orig_height = img.size
        
        if width and height:
            new_width, new_height = width, height
        elif width:
            ratio = width / orig_width
            new_width = width
            new_height = int(orig_height * ratio)
        elif height:
            ratio = height / orig_height
            new_height = height
            new_width = int(orig_width * ratio)
        else:
            # No resizing needed
            return image_path
        
        # Resize image
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Generate new filename
        path_parts = os.path.splitext(image_path)
        new_filename = f"{path_parts[0]}_resized_{new_width}x{new_height}{path_parts[1]}"
        new_abs_path = os.path.join(UPLOAD_DIR, new_filename)
        
        # Save resized image
        resized_img.save(new_abs_path, quality=quality)
        
        return new_filename
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file (relative to the upload directory)
            
        Returns:
            Dictionary with file information
        """
        # Get absolute path
        abs_path = os.path.join(UPLOAD_DIR, file_path)
        
        # Check if file exists
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            raise FileNotFoundError(f"File {file_path} not found")
        
        # Get file stats
        stats = os.stat(abs_path)
        
        # Get file extension
        _, ext = os.path.splitext(abs_path)
        
        # Determine file type
        file_type = "unknown"
        if ext.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]:
            file_type = "image"
        elif ext.lower() in [".pdf", ".doc", ".docx", ".txt", ".csv"]:
            file_type = "document"
        
        # Return file info
        return {
            "path": file_path,
            "url": FileStorageService.get_file_url(file_path),
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "type": file_type,
            "extension": ext.lower()[1:] if ext else ""
        }
