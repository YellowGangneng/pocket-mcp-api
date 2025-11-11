"""
MCP Mail Server - Email Read/Write MCP Server using FastMCP
"""
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# FastMCP 인스턴스 생성
mcp = FastMCP("Mail MCP Server")


class Priority(str, Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


# Email Models
class EmailAddress(BaseModel):
    name: Optional[str] = None
    email: str


class Attachment(BaseModel):
    filename: str
    content_type: str
    size: int
    content: Optional[str] = None  # Base64 encoded


class EmailMessage(BaseModel):
    message_id: str
    subject: str
    sender: EmailAddress
    to: List[EmailAddress]
    cc: Optional[List[EmailAddress]] = []
    bcc: Optional[List[EmailAddress]] = []
    date: datetime
    body_plain: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[Attachment]] = []
    in_reply_to: Optional[str] = None
    references: Optional[List[str]] = []
    folder: str = "inbox"


# Mock email storage
email_storage: List[EmailMessage] = []


# Initialize with sample emails
def init_sample_emails():
    sample_email = EmailMessage(
        message_id="<sample123@mail.server.com>",
        subject="[업무 협의] 홀딩스 주주총회 대응건",
        sender=EmailAddress(name="윤재훈", email="jaejae@poscodx.com"),
        to=[EmailAddress(name="이유진", email="nyamdae@poscodx.com")],
        cc=[EmailAddress(name="경선재", email="sunney_j@poscodx.com")],
        date=datetime.now(),
        body_plain="안녕하세요, 홀딩스 주주총회 대응건으로 연락드립니다. 11/20 오후 2시에 경선재, 이유진, 윤재훈 참석할 예정입니다. 회의실 예약부탁드립니다.",
        body_html="<p>안녕하세요, 홀딩스 주주총회 대응건으로 연락드립니다. 11/20 오후 2시에 경선재, 이유진, 윤재훈 참석할 예정입니다. 회의실 예약부탁드립니다.</p>",
        folder="inbox",
        references=[]
    )
    email_storage.append(sample_email)


init_sample_emails()


@mcp.tool()
def read_email(
    folder: str = "inbox",
    limit: int = 10,
    search_query: Optional[str] = None,
    message_id: Optional[str] = None
) -> dict:
    """
    메일함에서 이메일을 읽습니다.

    Args:
        folder: 메일 폴더 (inbox, sent, drafts, trash)
        limit: 반환할 최대 이메일 수
        search_query: 검색 쿼리 (제목과 본문에서 검색)
        message_id: 특정 메시지 ID로 조회

    Returns:
        이메일 목록과 개수를 포함한 딕셔너리
    """
    search_lower = search_query.lower() if search_query else ""

    # Filter emails
    filtered_emails = []
    for email in email_storage:
        if message_id and email.message_id != message_id:
            continue
        if email.folder != folder:
            continue
        if search_lower:
            if search_lower not in email.subject.lower() and \
               search_lower not in (email.body_plain or "").lower():
                continue
        filtered_emails.append(email)

    # Apply limit
    filtered_emails = filtered_emails[:limit]

    # Convert to dict
    result = []
    for email in filtered_emails:
        result.append({
            "message_id": email.message_id,
            "subject": email.subject,
            "sender": {
                "name": email.sender.name,
                "email": email.sender.email
            },
            "to": [{"name": addr.name, "email": addr.email} for addr in email.to],
            "cc": [{"name": addr.name, "email": addr.email} for addr in (email.cc or [])],
            "bcc": [{"name": addr.name, "email": addr.email} for addr in (email.bcc or [])],
            "date": email.date.isoformat(),
            "body_plain": email.body_plain,
            "body_html": email.body_html,
            "attachments": [
                {
                    "filename": att.filename,
                    "content_type": att.content_type,
                    "size": att.size
                } for att in (email.attachments or [])
            ],
            "in_reply_to": email.in_reply_to,
            "references": email.references or [],
            "folder": email.folder
        })

    return {
        "success": True,
        "count": len(result),
        "emails": result
    }


@mcp.tool()
def send_email(
    subject: str,
    sender_email: str,
    to_emails: List[str],
    body_plain: str,
    sender_name: Optional[str] = None,
    to_names: Optional[List[str]] = None,
    cc_emails: Optional[List[str]] = None,
    cc_names: Optional[List[str]] = None,
    bcc_emails: Optional[List[str]] = None,
    bcc_names: Optional[List[str]] = None,
    body_html: Optional[str] = None,
    priority: str = "normal",
    read_receipt: bool = False
) -> dict:
    """
    이메일을 전송합니다.

    Args:
        subject: 이메일 제목
        sender_email: 발신자 이메일 주소
        to_emails: 수신자 이메일 주소 리스트
        body_plain: 이메일 본문 (텍스트)
        sender_name: 발신자 이름
        to_names: 수신자 이름 리스트
        cc_emails: 참조 이메일 주소 리스트
        cc_names: 참조자 이름 리스트
        bcc_emails: 숨은참조 이메일 주소 리스트
        bcc_names: 숨은참조자 이름 리스트
        body_html: 이메일 본문 (HTML)
        priority: 우선순위 (high, normal, low)
        read_receipt: 읽음 확인 요청 여부

    Returns:
        전송 결과 딕셔너리
    """
    try:
        # Parse sender
        sender = EmailAddress(name=sender_name, email=sender_email)

        # Parse recipients
        to = [EmailAddress(name=to_names[i] if to_names and i < len(to_names) else None, email=email)
              for i, email in enumerate(to_emails)]

        cc = []
        if cc_emails:
            cc = [EmailAddress(name=cc_names[i] if cc_names and i < len(cc_names) else None, email=email)
                  for i, email in enumerate(cc_emails)]

        bcc = []
        if bcc_emails:
            bcc = [EmailAddress(name=bcc_names[i] if bcc_names and i < len(bcc_names) else None, email=email)
                   for i, email in enumerate(bcc_emails)]

        # Generate message ID
        message_id = f"<{datetime.now().timestamp()}@mail.server.com>"

        # Create email message
        email = EmailMessage(
            message_id=message_id,
            subject=subject,
            sender=sender,
            to=to,
            cc=cc,
            bcc=bcc,
            date=datetime.now(),
            body_plain=body_plain,
            body_html=body_html,
            attachments=[],
            folder="sent"
        )

        # Store email
        email_storage.append(email)

        return {
            "success": True,
            "message": "Email sent successfully",
            "message_id": message_id,
            "priority": priority,
            "read_receipt_requested": read_receipt
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
