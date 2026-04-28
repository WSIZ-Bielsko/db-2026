from uuid import uuid4

from loguru import logger

from db_2026.seccom.common import *
from db_2026.seccom.repo import *


class SeccomService:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self._users = UserRepository(pool)
        self._groups = GroupRepository(pool)
        self._messages = MessageRepository(pool)
        self._invites = InviteRepository(pool)
        self._group_user = GroupUserRepository(pool)

    # admin section

    async def create_group(self, name: str):
        pass

    async def create_invite(self) -> Invite:
        iid = uuid4()
        ivt = Invite(invite_id=iid, challenge=None)
        ivt_ = await self._invites.create(ivt)
        return ivt_

    async def elevate_user_admin(self, pub_key: str):
        logger.info(f"Elevating user {short_key(pub_key)} to admin")
        user = await self._users.get(pub_key)
        if not user:
            logger.warning(f"User {short_key(pub_key)} not found")
            raise ValueError("Invalid user")
        user.admin = True
        await self._users.update(user)
        logger.info(f"User {short_key(pub_key)} elevated to admin")


    # user section (self-actions)

    async def signup_init(self, pub_key: str, invite_id: UUID) -> str :
        """

        :param pub_key:
        :param invite_id:
        :return: challenge as string
        """
        invite: Invite = await self._invites.get(invite_id)
        if not invite:
            logger.warning(f"Invite {invite_id} not found")
            raise ValueError("Invalid invite")
        challenge = str(uuid4())
        invite.challenge = challenge
        await self._invites.update(invite)

        # encode with pub_key
        pub_key_ = public_from_string(pub_key)
        challenge_ = encrypt_string(pub_key_, challenge)
        return challenge_

    async def signup_finish(self, pub_key: str, invite_id: UUID , solution: str):
        invite: Invite | None = await self._invites.get(invite_id)
        if not invite:
            logger.warning(f"Invite {invite_id} not found")
            raise ValueError("Invalid invite")

        if not invite.challenge == solution:
            logger.warning(f"Invalid solution for invite {invite_id}")
            raise ValueError("Invalid solution")

        logger.warning(f"User {short_key(pub_key)} signed up")
        await self._users.create(User(pub_key=pub_key, token=None, challenge=None))
        await self._invites.delete(invite_id)

    async def login_user(self, pub_key: str) -> str:
        """

        :param pub_key:
        :return: challenge as string, encoded with pub_key
        """
        logger.info(f"User {short_key(pub_key)} logging in")
        user = await self._users.get(pub_key)
        if not user:
            logger.warning(f"User {short_key(pub_key)} not found")
            raise ValueError("Invalid user")
        challenge = str(uuid4())
        user.challenge = challenge
        await self._users.update(user)
        logger.info(f"Challenge generated: {challenge}")

        encode_challenge = encrypt_string(public_from_string(pub_key), challenge)
        return encode_challenge

    async def login_finish(self, pub_key: str, solution: str):
        """
        :param pub_key:
        :param solution:
        :return: token as string (new or existing, if exists)
        """
        logger.info(f"User {short_key(pub_key)} logging in; solution: {solution}")
        user = await self._users.get(pub_key)
        if not user:
            logger.warning(f"User {short_key(pub_key)} not found")
            raise ValueError("Invalid user")
        if not user.challenge == solution:
            logger.warning(f"Invalid solution for user {short_key(pub_key)}")
            raise ValueError("Invalid solution")
        if not user.token:
            user.token = str(uuid4())
            await self._users.update(user)
        logger.info(f"User {short_key(pub_key)} logged in with token {user.token}")
        return user.token

    async def logout_user(self, pub_key: str):
        """
        Erases user.token.

        :param pub_key:
        :return:
        """
        user = await self._users.get(pub_key)
        if not user:
            logger.warning(f"User {short_key(pub_key)} not found")
            raise ValueError("Invalid user")
        user.token = None
        await self._users.update(user)

    async def user_by_token(self, token: str) -> User | None:
        """
        Main authorization method. All requests must provide token.
        :param token:
        :return:
        """
        return await self._users.get_by_token(token)

    async def post_message(self, group_id: UUID, sender_key: str, content: str):
        logger.info(f"User {short_key(sender_key)} posting message in group {group_id}")
        recipients = await self._group_user.get_by_group(group_id)
        for r in recipients:
            content_encoded = encrypt_string(public_from_string(r.user_key), content)
            await self._messages.create(Message(
                id=uuid.uuid4(),
                sender_key=sender_key,
                recipient_key=r.user_key,
                content=content_encoded,
                created_at=datetime.now(UTC),
                group_id=group_id
            ))

        logger.info(f"Message posted to {len(recipients)} recipients in group {group_id}")

    async def fetch_messages(self, group_id: UUID, recipient_key: str, since: datetime | None = None) -> list[Message]:
        logger.info(f"Fetching messages in group {group_id} by user {short_key(recipient_key)}")
        msgs = await self._messages.get_selected(group_id, recipient_key, since)
        logger.info(f"Found {len(msgs)} messages")
        return msgs

    async def fetch_groups(self, user_key: str) -> list[UUID]:
        """groups assigned to user"""
        logger.info(f"Fetching groups for user {short_key(user_key)}")
        groups = await self._group_user.get_by_user(user_key)
        return [g.group_id for g in groups]

    async def join_group(self, user_key: str, group_id: UUID):
        logger.info(f"User {short_key(user_key)} joining group {group_id}")
        await self._group_user.assign(group_id, user_key)

    async def leave_group(self, user_key: str, group_id: UUID):
        logger.info(f"User {short_key(user_key)} leaving group {group_id}")
        await self._group_user.unassign(group_id, user_key)




