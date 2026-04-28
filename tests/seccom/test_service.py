from uuid import uuid4

import pytest
import pytest_asyncio
from _testcapi import awaitType
from pydantic import BaseModel

from db_2026.seccom.common import *
from db_2026.seccom.model import Invite, User, Group
from db_2026.seccom.pool import create_db_pool
from db_2026.seccom.service import SeccomService



@pytest_asyncio.fixture
async def service():
    pool = await create_db_pool()
    return SeccomService(pool)


@pytest_asyncio.fixture
async def invite(service: SeccomService):
    return await service.create_invite()


@pytest_asyncio.fixture
async def keypair():
    pub, prv = generate_keypair()
    return pub, prv


@pytest_asyncio.fixture
async def user(service: SeccomService, keypair: tuple):
    user_ = User(pub_key=public_to_string(keypair[0]), token=None, challenge=None)
    await service._users.create(user_)
    return user_

@pytest_asyncio.fixture
async def group(service: SeccomService):
    group_ = Group(name="test_group", id=uuid4())
    await service._groups.create(group_)
    return group_


@pytest.mark.asyncio
async def test_create_invites(service: SeccomService):
    ivt = await service.create_invite()
    assert ivt.invite_id is not None
    ivt_ = await service._invites.get(ivt.invite_id)
    assert ivt_ == ivt


@pytest.mark.asyncio
async def test_full_invite_positive(service: SeccomService, invite: Invite):
    pub, prv = generate_keypair()
    pub_s = public_to_string(pub)
    challenge = await service.signup_init(pub_s, invite.invite_id)

    decrypted_challenge = decrypt_string(prv, challenge)
    await service.signup_finish(pub_key=pub_s, invite_id=invite.invite_id, solution=decrypted_challenge)

    # check user created in DB
    user = await service._users.get(pub_s)
    assert user is not None

@pytest.mark.asyncio
async def test_full_login_positive(service: SeccomService, keypair: tuple, user: User, ):
    assert user.pub_key == public_to_string(keypair[0])

    # act - login flow
    challenge = await service.login_user(pub_key=user.pub_key)
    decrypted_challenge = decrypt_string(keypair[1], challenge)
    token = await service.login_finish(pub_key=user.pub_key, solution=decrypted_challenge)

    # assert
    token_db = (await service._users.get(user.pub_key)).token
    assert token == token_db

    user_from_token = await service.user_by_token(token)
    assert user.pub_key == user_from_token.pub_key


@pytest.mark.asyncio
async def test_user_can_send_to_group(service: SeccomService, group: Group):
    KP1 = generate_keypair()
    KP2 = generate_keypair()
    pub1 = public_to_string(KP1[0])
    pub2 = public_to_string(KP2[0])
    user1 = await service._users.create(User(pub_key=pub1, token=None, challenge=None))
    user2 = await service._users.create(User(pub_key=pub2, token=None, challenge=None))
    await service._group_user.assign(group.id, pub1)
    await service._group_user.assign(group.id, pub2)

    # act
    await service.post_message(group.id, sender_key=pub1, content="Hello")

    # assert
    msg_user1 = await service.fetch_messages(group_id=group.id, recipient_key=pub1)
    msg_user2 = await service.fetch_messages(group_id=group.id, recipient_key=pub2)

    msg_user1 = [m for m in msg_user1 if m.sender_key == pub1]
    msg_user2 = [m for m in msg_user2 if m.sender_key == pub1]

    assert len(msg_user1) == 1
    assert len(msg_user2) == 1

    decoded_1 = decrypt_string(KP1[1], msg_user1[0].content)
    decoded_2 = decrypt_string(KP2[1], msg_user2[0].content)

    assert decoded_1 == "Hello"
    assert decoded_2 == "Hello"