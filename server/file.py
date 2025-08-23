from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import logging
import os


mcp = FastMCP("file")

# Set up logging (this just prints messages to your terminal for debugging)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


@mcp.tool()
def read_file(file_path: str) -> TextContent:
    """Read the content of a file.

    Args:
        file_path: Path to the file.

    Returns:
        Content of the file.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return TextContent(type="text", text=content)
    except Exception as e:
        return TextContent(type="text", text=f"Error reading file: {e}")


@mcp.tool()
def write_file(file_path: str, content: str) -> TextContent:
    """Write content to a file.

    Args:
        file_path: Path to the file.
        content: Content to write.

    Returns:
        Confirmation message.
    """
    try:
        with open(file_path, "w") as file:
            file.write(content)
        return TextContent(
            type="text", text=f"File written successfully to {file_path}"
        )
    except Exception as e:
        return TextContent(type="text", text=f"Error writing file: {e}")


@mcp.tool()
def edit_file(file_path: str, new_content: str) -> TextContent:
    """Edit an existing file with new content.

    Args:
        file_path: Path to the file.
        new_content: New content to write.

    Returns:
        Confirmation message.
    """
    try:
        with open(file_path, "r+") as file:
            file.seek(0)
            file.write(new_content)
            file.truncate()
        return TextContent(type="text", text=f"File edited successfully at {file_path}")
    except Exception as e:
        return TextContent(type="text", text=f"Error editing file: {e}")


@mcp.tool()
def create_directory(directory_path: str) -> TextContent:
    """Create a new directory.

    Args:
        directory_path: Path to the new directory.

    Returns:
        Confirmation message.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return TextContent(
            type="text", text=f"Directory created successfully at {directory_path}"
        )
    except Exception as e:
        return TextContent(type="text", text=f"Error creating directory: {e}")


@mcp.tool()
def list_directory(directory_path: str) -> TextContent:
    """List files in a directory.

    Args:
        directory_path: Path to the directory.

    Returns:
        List of files in the directory.
    """
    try:
        files = os.listdir(directory_path)
        return TextContent(type="text", text="\n".join(files))
    except Exception as e:
        return TextContent(type="text", text=f"Error listing directory: {e}")


@mcp.tool()
def move_file(source_path: str, destination_path: str) -> TextContent:
    """Move a file from source to destination.

    Args:
        source_path: Path to the source file.
        destination_path: Path to the destination.

    Returns:
        Confirmation message.
    """
    try:
        os.rename(source_path, destination_path)
        return TextContent(
            type="text",
            text=f"File moved successfully from {source_path} to {destination_path}",
        )
    except Exception as e:
        return TextContent(type="text", text=f"Error moving file: {e}")
    
@mcp.tool()
def delete_file(file_path: str) -> TextContent:
    """Delete a file.

    Args:
        file_path: Path to the file.

    Returns:
        Confirmation message.
    """
    try:
        os.remove(file_path)
        return TextContent(type="text", text=f"File deleted successfully at {file_path}")
    except Exception as e:
        return TextContent(type="text", text=f"Error deleting file: {e}")
    
@mcp.tool()
def delete_directory(directory_path: str) -> TextContent:
    """Delete a directory.

    Args:
        directory_path: Path to the directory.

    Returns:
        Confirmation message.
    """
    try:
        os.rmdir(directory_path)
        return TextContent(type="text", text=f"Directory deleted successfully at {directory_path}")
    except Exception as e:
        return TextContent(type="text", text=f"Error deleting directory: {e}")


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
