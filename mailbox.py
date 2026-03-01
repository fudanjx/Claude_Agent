"""Mailbox-based communication protocol for multi-agent coordination."""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Message:
    """Protocol message."""
    type: str  # REQUEST, RESPONSE, CLAIM, PROGRESS, COMPLETE, BLOCKED
    msg_id: str
    from_agent: str
    to_agent: str
    task_id: str
    timestamp: str
    body: Dict[str, Any]
    in_reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Message':
        """Create from dictionary."""
        return Message(**data)


class MailboxManager:
    """Manages mailbox-based communication between agents."""

    def __init__(self, state_dir: Path):
        """Initialize mailbox manager.

        Args:
            state_dir: Root state directory
        """
        self.state_dir = state_dir
        self.mailboxes_dir = state_dir / "mailboxes"
        self.mailboxes_dir.mkdir(parents=True, exist_ok=True)

    def _get_inbox_dir(self, agent_name: str) -> Path:
        """Get inbox directory for an agent."""
        inbox = self.mailboxes_dir / agent_name / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        return inbox

    def _get_outbox_dir(self, agent_name: str) -> Path:
        """Get outbox directory for an agent."""
        outbox = self.mailboxes_dir / agent_name / "outbox"
        outbox.mkdir(parents=True, exist_ok=True)
        return outbox

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        msg_type: str,
        task_id: str,
        body: Dict[str, Any],
        in_reply_to: Optional[str] = None
    ) -> Message:
        """Send a message from one agent to another.

        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name (or "BOARD" for broadcast)
            msg_type: Message type
            task_id: Associated task ID
            body: Message body
            in_reply_to: Optional message ID this is replying to

        Returns:
            Sent Message object
        """
        msg_id = str(uuid.uuid4())

        message = Message(
            type=msg_type,
            msg_id=msg_id,
            from_agent=from_agent,
            to_agent=to_agent,
            task_id=task_id,
            timestamp=datetime.now().isoformat(),
            body=body,
            in_reply_to=in_reply_to
        )

        # Write to sender's outbox
        outbox = self._get_outbox_dir(from_agent)
        outbox_file = outbox / f"{msg_id}.json"
        with open(outbox_file, "w") as f:
            json.dump(message.to_dict(), f, indent=2)

        # Write to recipient's inbox (unless BOARD)
        if to_agent != "BOARD":
            inbox = self._get_inbox_dir(to_agent)
            inbox_file = inbox / f"{msg_id}.json"
            with open(inbox_file, "w") as f:
                json.dump(message.to_dict(), f, indent=2)

        return message

    def read_inbox(
        self,
        agent_name: str,
        mark_read: bool = True,
        msg_type: Optional[str] = None
    ) -> List[Message]:
        """Read messages from an agent's inbox.

        Args:
            agent_name: Agent name
            mark_read: If True, move messages to .read/ subdirectory
            msg_type: Optional filter by message type

        Returns:
            List of Message objects
        """
        inbox = self._get_inbox_dir(agent_name)
        messages = []

        for msg_file in sorted(inbox.glob("*.json")):
            with open(msg_file, "r") as f:
                data = json.load(f)
                message = Message.from_dict(data)

                # Filter by type if specified
                if msg_type is None or message.type == msg_type:
                    messages.append(message)

            # Mark as read
            if mark_read:
                read_dir = inbox / ".read"
                read_dir.mkdir(exist_ok=True)
                msg_file.rename(read_dir / msg_file.name)

        return messages

    def get_unread_count(self, agent_name: str) -> int:
        """Get count of unread messages."""
        inbox = self._get_inbox_dir(agent_name)
        return len(list(inbox.glob("*.json")))

    def get_inbox_summary(
        self,
        agent_name: str,
        msg_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get lightweight inbox summaries with file pointers.

        This method returns minimal message metadata plus file paths,
        allowing the agent to selectively read full messages only when needed.
        This dramatically reduces token usage compared to loading full messages.

        Args:
            agent_name: Agent name
            msg_type: Optional filter by message type

        Returns:
            List of summary dicts with keys:
            - msg_id: Message ID
            - type: Message type (CLAIM, PROGRESS, COMPLETE, BLOCKED, etc.)
            - from_agent: Sender agent name
            - task_id: Associated task ID
            - timestamp: ISO timestamp
            - summary: First 100 chars of deliverable/reason/summary
            - file_path: Path to full message JSON file
        """
        inbox = self._get_inbox_dir(agent_name)
        summaries = []

        for msg_file in sorted(inbox.glob("*.json")):
            with open(msg_file, "r") as f:
                data = json.load(f)
                message = Message.from_dict(data)

                # Filter by type if specified
                if msg_type is not None and message.type != msg_type:
                    continue

                # Extract short summary from body based on message type
                body = message.body
                summary_text = ""
                if message.type == "COMPLETE":
                    summary_text = body.get("deliverable", "")[:100]
                elif message.type == "BLOCKED":
                    summary_text = body.get("reason", "")[:100]
                elif message.type == "PROGRESS":
                    summary_text = body.get("summary", "")[:100]
                elif message.type == "CLAIM":
                    summary_text = body.get("why_me", "")[:100]
                else:
                    # For other types, try to find any text field
                    for key in ["summary", "notes", "reason", "deliverable"]:
                        if key in body:
                            summary_text = str(body[key])[:100]
                            break

                summaries.append({
                    "msg_id": message.msg_id,
                    "type": message.type,
                    "from_agent": message.from_agent,
                    "task_id": message.task_id,
                    "timestamp": message.timestamp,
                    "summary": summary_text,
                    "file_path": str(msg_file)
                })

        return summaries

    def create_request_message(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        intent: str,
        goal: str,
        inputs: List[str] = None,
        constraints: Dict[str, Any] = None,
        acceptance_criteria: List[str] = None,
        priority: str = "med"
    ) -> Message:
        """Create and send a REQUEST message."""
        body = {
            "intent": intent,
            "goal": goal,
            "inputs": inputs or [],
            "constraints": constraints or {},
            "acceptance_criteria": acceptance_criteria or [],
            "priority": priority
        }

        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            msg_type="REQUEST",
            task_id=task_id,
            body=body
        )

    def create_response_message(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        in_reply_to: str,
        status: str,
        notes: str = "",
        questions: List[str] = None
    ) -> Message:
        """Create and send a RESPONSE message."""
        body = {
            "status": status,  # accept, decline, need_clarification
            "notes": notes,
            "questions": questions or []
        }

        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            msg_type="RESPONSE",
            task_id=task_id,
            body=body,
            in_reply_to=in_reply_to
        )

    def create_claim_message(
        self,
        from_agent: str,
        task_id: str,
        why_me: str,
        eta_hint: str = "medium",
        workdir: str = ""
    ) -> Message:
        """Create and send a CLAIM message."""
        body = {
            "why_me": why_me,
            "eta_hint": eta_hint,  # short, medium, long
            "workdir": workdir
        }

        return self.send_message(
            from_agent=from_agent,
            to_agent="BOARD",
            msg_type="CLAIM",
            task_id=task_id,
            body=body
        )

    def create_progress_message(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        percent: int,
        summary: str,
        artifacts: List[str] = None,
        blockers: List[str] = None
    ) -> Message:
        """Create and send a PROGRESS message."""
        body = {
            "percent": percent,
            "summary": summary,
            "artifacts": artifacts or [],
            "blockers": blockers or []
        }

        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            msg_type="PROGRESS",
            task_id=task_id,
            body=body
        )

    def create_complete_message(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        deliverable: str,
        files: List[str] = None,
        risks: List[str] = None,
        next_steps: List[str] = None
    ) -> Message:
        """Create and send a COMPLETE message."""
        body = {
            "deliverable": deliverable,
            "files": files or [],
            "risks": risks or [],
            "next_steps": next_steps or []
        }

        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            msg_type="COMPLETE",
            task_id=task_id,
            body=body
        )

    def create_blocked_message(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        reason: str,
        unblock_options: List[str] = None
    ) -> Message:
        """Create and send a BLOCKED message."""
        body = {
            "reason": reason,
            "unblock_options": unblock_options or []
        }

        return self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            msg_type="BLOCKED",
            task_id=task_id,
            body=body
        )
