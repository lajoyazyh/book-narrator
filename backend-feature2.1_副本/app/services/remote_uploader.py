from pathlib import Path
import paramiko


REMOTE_HOST = "connect.westd.seetacloud.com"
REMOTE_PORT = 29495
REMOTE_USER = "root"
REMOTE_PASSWORD = "你的云端密码"  # 临时可用，后面可以改成 .env
REMOTE_BOOK_DIR = "/root/shared/books"


def upload_pdf_to_agent_server(local_pdf_path: str) -> str:
    """
    把本地 PDF 上传到云端 Agent 可访问的 /root/shared/books 目录。
    返回云端 PDF 路径。
    """
    local_path = Path(local_pdf_path)

    if not local_path.exists():
        raise FileNotFoundError(f"本地 PDF 文件不存在：{local_pdf_path}")

    remote_pdf_path = f"{REMOTE_BOOK_DIR}/{local_path.name}"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=REMOTE_HOST,
            port=REMOTE_PORT,
            username=REMOTE_USER,
            password=REMOTE_PASSWORD,
            timeout=15,
        )

        ssh.exec_command(f"mkdir -p {REMOTE_BOOK_DIR}")

        sftp = ssh.open_sftp()
        sftp.put(str(local_path), remote_pdf_path)
        sftp.close()

        return remote_pdf_path

    finally:
        ssh.close()