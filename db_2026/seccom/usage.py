from asyncio import run
from uuid import uuid4

from loguru import logger

from db_2026.seccom.model import Invite
from db_2026.seccom.pool import create_db_pool
from db_2026.seccom.repo import *


async def main():
    pool = await create_db_pool()
    logger.info(f"DB pool created")

    repo = InviteRepository(pool)
    invite = Invite(invite_id=uuid4(), challenge="example_challenge")
    await repo.create(invite)
    logger.info(f"Invite created: {invite.invite_id}")


    invites = await repo.get_all()
    for i in invites:
        print(i)




if __name__ == '__main__':
    run(main())