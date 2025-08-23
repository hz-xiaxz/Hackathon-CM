from mcp.server.fastmcp import FastMCP

# Import the main function from the comparison script
from run_finite_infinite_comparison import run_finite_infinite_comparison

# Initialize the MCP server
mcp = FastMCP("Finite_Infinite_Comparison_Server")

@mcp.tool()
def generate_finite_infinite_comparison() -> str:
    """
    Runs a finite-size scaling comparison between finite-size, periodic ED
    and infinite-size DMRG. Generates a plot of the results.

    Returns:
        A message indicating that the comparison is complete and the plot is saved.
    """
    try:
        run_finite_infinite_comparison()
        return "Comparison complete. Plot saved to finite_infinite_comparison.png"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    mcp.run("stdio")
