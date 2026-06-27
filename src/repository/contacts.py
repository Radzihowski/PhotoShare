from datetime import datetime, timedelta

from sqlalchemy import select, exists, delete, or_, func

from src.database.db import sessionmanager
from src.database.models import Contact
from src.schemas.contacts import ContactUpdateRequest


class ContactCRUD:
    # Function to add a user to the database
    @staticmethod
    async def create_contact(body, user_id:int):
        async with sessionmanager.session() as session:
            async with session.begin():
                new_user = Contact(first_name=body.first_name, last_name=body.last_name,
                                   email=body.email, phone=body.phone, date_of_birth=body.date_of_birth,
                                   info=body.info, user_id=user_id)
                session.add(new_user)
                await session.flush()
                user_id = new_user.id
            print(f"User {body.first_name} added successfully!")
            return user_id

    @staticmethod
    async def read_contact(contact_id:int, user_id:int):
        async  with sessionmanager.session() as session:
            query = select(Contact).where(Contact.id == contact_id, Contact.user_id==user_id)
            print(query)
            result = await session.execute(query)
            print(result)
            return result.scalar()

    @staticmethod
    async def read_contacts(skip:int, limit:int, user_id:int):
        async with sessionmanager.session() as session:
            query = select(Contact).where(Contact.user_id==user_id).offset(skip).limit(limit)
            print(query)
            result = await session.execute(query)
            print(result)
            return result.scalars()

    @staticmethod
    async def delete_contact(contact_id:int, user_id:int):
        async with sessionmanager.session() as session:
            query = delete(Contact).where(Contact.id == contact_id, Contact.user_id==user_id)
            print(query)
            result = await session.execute(query)
            print(result)
            await session.commit()
            return result.rowcount

    @staticmethod
    async def check_email(email):
        async with sessionmanager.session() as session:
            query = select(exists().where(Contact.email==email))
            print(query)
            result = await session.execute(query)
            print(result)
            return result.scalar()

    @staticmethod
    async def update_contact(contact_id, body: ContactUpdateRequest, user_id:int):
        async with sessionmanager.session() as session:
            query = select(Contact).where(Contact.id == contact_id, Contact.user_id==user_id)
            result = await session.execute(query)
            print(result)
            contact = result.scalar()
            print(f"{contact=}")
            if contact is None:
                return None
            if body.first_name != "":
                contact.first_name = body.first_name
            if body.last_name != "":
                contact.last_name = body.last_name
            if body.email != "":
                contact.email = body.email
            if body.date_of_birth != datetime.today().date():
                contact.date_of_birth = body.date_of_birth
            print(datetime.today().date())
            if body.info != "":
                contact.info = body.info
            await session.commit()
            result = await session.execute(query)
            print(result)
            print(contact)
            return result.scalar()

    @staticmethod
    async def search_contacts(skip:int, limit:int, first_name:str, last_name:str, email:str, user_id:int):
        async  with (sessionmanager.session() as session):
            filters = [Contact.user_id==user_id]
            if first_name:
                filters.append(Contact.first_name.ilike(f"%{first_name}%"))
            if last_name:
                filters.append(Contact.last_name.ilike(f"%{last_name}%"))
            if email:
                filters.append(Contact.email.ilike(f"%{email}%"))

            query = select(Contact)
            if filters:
                query = query.where(or_(*filters))

            query = query.offset(skip).limit(limit).order_by(Contact.id)

            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def upcoming_dob(skip: int, limit: int, days_range: int, user_id: int):
        async with sessionmanager.session() as session:
            today = datetime.today().date()
            target = today + timedelta(days=days_range)

            today_str = today.strftime('%m-%d')
            target_str = target.strftime('%m-%d')
            print(today_str)
            print(target_str)
            dob_md = func.to_char(Contact.date_of_birth, 'MM-DD')
            print(dob_md)
            if today_str < target_str:
                # Range within same year
                query = select(Contact).where(
                    Contact.user_id==user_id, dob_md.between(today_str, target_str)
                )
            else:
                # Wraps over end of year (e.g., Dec 30 to Jan 5)
                query = select(Contact).where(
                    Contact.user_id==user_id, (dob_md >= today_str) | (dob_md <= target_str)
                )

            query = query.offset(skip).limit(limit).order_by(Contact.id)

            result = await session.execute(query)
            return result.scalars().all()
