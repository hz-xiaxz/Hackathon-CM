from mcp.server.fastmcp import FastMCP
import subprocess
import sys


mcp = FastMCP("script")


@mcp.tool()
async def handle_python_tool(code: str, timeout: int) -> str:
    """执行Python代码并返回结果，处理一些通过执行简单的Python脚本来实现的功能。
    注意脚本的路径为/tmp/mcp_script.py，所以code中执行的代码如果需要访问文件系统，请确保使用绝对路径。
    必须提供timeout参数，防止命令执行时间过长。
    Args:
        code: 要执行的Python代码
        timeout: 执行超时时间（秒）
    """

    try:
        # 创建临时文件执行Python代码
        with open("/tmp/mcp_script.py", "w") as f:
            f.write(code)

        # 执行Python脚本
        result = subprocess.run(
            [sys.executable, "/tmp/mcp_script.py"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return f"执行结果:\n输出:\n{result.stdout}\n错误:\n{result.stderr}\n返回码: {result.returncode}"

    except subprocess.TimeoutExpired:
        return f"执行超时（超过{timeout}秒）"
    except Exception as e:
        return f"执行出错: {str(e)}"


@mcp.tool()
async def handle_shell_tool(command: str, timeout: int) -> str:
    """执行Shell命令并返回结果。
    时刻注意查询当前路径是否正确。
    由于安全原因，建议不要执行任何不受信任的Shell命令。凡是涉及到文件操作的命令都需要使用绝对路径。执行可能会有风险的命令，必须让用户确认。
    必须提供timeout参数，防止命令执行时间过长。
    Args:
        command: 要执行的Shell命令
        timeout: 执行超时时间（秒）
    """
    try:
        # 执行Shell命令
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return f"执行结果:\n输出:\n{result.stdout}\n错误:\n{result.stderr}\n返回码: {result.returncode}"

    except subprocess.TimeoutExpired:
        return f"执行超时（超过{timeout}秒）"
    except Exception as e:
        return f"执行出错: {str(e)}"


@mcp.tool()
async def handle_bash_tool(script: str, timeout: int) -> str:
    """执行Bash脚本并返回结果。
    注意脚本的路径为/tmp/mcp_script.sh，所以script中执行的脚本如果需要访问文件系统，请确保使用绝对路径。
    由于安全原因，建议不要执行任何不受信任的Bash脚本。凡是涉及到文件操作的脚本都需要使用绝对路径。执行可能会有风险的脚本，必须让用户确认。
    必须提供timeout参数，防止命令执行时间过长。
    Args:
        script: 要执行的Bash脚本
        timeout: 执行超时时间（秒）
    """

    try:
        # 创建临时文件执行Bash脚本
        with open("/tmp/mcp_script.sh", "w") as f:
            f.write(script)

        # 执行Bash脚本
        result = subprocess.run(
            ["/bin/bash", "/tmp/mcp_script.sh"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return f"执行结果:\n输出:\n{result.stdout}\n错误:\n{result.stderr}\n返回码: {result.returncode}"

    except subprocess.TimeoutExpired:
        return f"执行超时（超过{timeout}秒）"
    except Exception as e:
        return f"执行出错: {str(e)}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
