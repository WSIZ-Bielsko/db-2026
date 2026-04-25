import uuid

import asyncpg
from asyncpg import Connection
from loguru import logger

from db_2026.seccom.model import *


class InviteRepository:
    def __init__(self, conn: asyncpg.Pool):
        self.conn = conn

    async def create(self, invite: Invite) -> Invite:
        record = await self.conn.fetchrow(
            "INSERT INTO invites (invite_id, challenge) VALUES ($1, $2) RETURNING *",
            invite.invite_id, invite.challenge
        )
        return Invite(**dict(record))

    async def get(self, invite_id: uuid.UUID) -> Invite | None:
        record = await self.conn.fetchrow("SELECT * FROM invites WHERE invite_id = $1", invite_id)
        return Invite(**dict(record)) if record else None

    async def get_all(self) -> list[Invite]:
        records = await self.conn.fetch("SELECT * FROM invites")
        return [Invite(**dict(r)) for r in records]

    async def update(self, invite: Invite) -> Invite | None:
        record = await self.conn.fetchrow(
            "UPDATE invites SET challenge = $2 WHERE invite_id = $1 RETURNING *",
            invite.invite_id, invite.challenge
        )
        return Invite(**dict(record)) if record else None

    async def delete(self, invite_id: uuid.UUID) -> Invite | None:
        record = await self.conn.fetchrow("DELETE FROM invites WHERE invite_id = $1 RETURNING *", invite_id)
        return Invite(**dict(record)) if record else None


class UserRepository:
    def __init__(self, conn: asyncpg.Pool):
        self.conn = conn

    async def create(self, user: User) -> User:
        record = await self.conn.fetchrow(
            "INSERT INTO users (pub_key, token) VALUES ($1, $2) RETURNING *",
            user.pub_key, user.token
        )
        return User(**dict(record))

    async def get(self, pub_key: str) -> User | None:
        record = await self.conn.fetchrow("SELECT * FROM users WHERE pub_key = $1", pub_key)
        return User(**dict(record)) if record else None

    async def get_all(self) -> list[User]:
        records = await self.conn.fetch("SELECT * FROM users")
        return [User(**dict(r)) for r in records]

    async def update(self, user: User) -> User | None:
        record = await self.conn.fetchrow(
            "UPDATE users SET token = $2 WHERE pub_key = $1 RETURNING *",
            user.pub_key, user.token
        )
        return User(**dict(record)) if record else None

    async def delete(self, pub_key: str) -> User | None:
        record = await self.conn.fetchrow("DELETE FROM users WHERE pub_key = $1 RETURNING *", pub_key)
        return User(**dict(record)) if record else None


class GroupRepository:
    def __init__(self, conn: asyncpg.Pool):
        self.conn = conn

    async def create(self, group: Group) -> Group:
        record = await self.conn.fetchrow(
            "INSERT INTO groups (id, name) VALUES ($1, $2) RETURNING *",
            group.id, group.name
        )
        return Group(**dict(record))

    async def get(self, group_id: uuid.UUID) -> Group | None:
        record = await self.conn.fetchrow("SELECT * FROM groups WHERE id = $1", group_id)
        return Group(**dict(record)) if record else None

    async def get_all(self) -> list[Group]:
        records = await self.conn.fetch("SELECT * FROM groups")
        return [Group(**dict(r)) for r in records]

    async def update(self, group: Group) -> Group | None:
        record = await self.conn.fetchrow(
            "UPDATE groups SET name = $2 WHERE id = $1 RETURNING *",
            group.id, group.name
        )
        return Group(**dict(record)) if record else None

    async def delete(self, group_id: uuid.UUID) -> Group | None:
        record = await self.conn.fetchrow("DELETE FROM groups WHERE id = $1 RETURNING *", group_id)
        return Group(**dict(record)) if record else None


class GroupUserRepository:
    def __init__(self, conn: asyncpg.Pool):
        self.conn = conn

    async def assign(self, group_id: uuid.UUID, user_key: str) -> GroupUser:
        record = await self.conn.fetchrow(
            "INSERT INTO group_users (group_id, user_key) VALUES ($1, $2) RETURNING *",
            group_id, user_key
        )
        return GroupUser(**dict(record))

    async def unassign(self, group_id: uuid.UUID, user_key: str) -> GroupUser | None:
        record = await self.conn.fetchrow(
            "DELETE FROM group_users WHERE group_id = $1 AND user_key = $2 RETURNING *",
            group_id, user_key
        )
        return GroupUser(**dict(record)) if record else None

    async def get_by_group(self, group_id: uuid.UUID) -> list[GroupUser]:
        records = await self.conn.fetch("SELECT * FROM group_users WHERE group_id = $1", group_id)
        return [GroupUser(**dict(r)) for r in records]

    async def get_by_user(self, user_key: str) -> list[GroupUser]:
        records = await self.conn.fetch("SELECT * FROM group_users WHERE user_key = $1", user_key)
        return [GroupUser(**dict(r)) for r in records]


class MessageRepository:
    def __init__(self, conn: asyncpg.Pool):
        self.conn = conn

    async def create(self, message: Message) -> Message:
        record = await self.conn.fetchrow(
            """INSERT INTO messages (id, sender_key, recipient_key, content, created_at, group_id)
               VALUES ($1, $2, $3, $4, $5, $6)
               RETURNING *""",
            message.id, message.sender_key, message.recipient_key,
            message.content, message.created_at, message.group_id
        )
        return Message(**dict(record))

    async def get(self, message_id: uuid.UUID) -> Message | None:
        record = await self.conn.fetchrow("SELECT * FROM messages WHERE id = $1", message_id)
        return Message(**dict(record)) if record else None

    async def get_all(self) -> list[Message]:
        records = await self.conn.fetch("SELECT * FROM messages")
        return [Message(**dict(r)) for r in records]

    async def update(self, message: Message) -> Message | None:
        record = await self.conn.fetchrow(
            """UPDATE messages
               SET sender_key    = $2,
                   recipient_key = $3,
                   content       = $4,
                   created_at    = $5,
                   group_id      = $6
               WHERE id = $1
               RETURNING *""",
            message.id, message.sender_key, message.recipient_key,
            message.content, message.created_at, message.group_id
        )
        return Message(**dict(record)) if record else None

    async def delete(self, message_id: uuid.UUID) -> Message | None:
        record = await self.conn.fetchrow("DELETE FROM messages WHERE id = $1 RETURNING *", message_id)
        return Message(**dict(record)) if record else None