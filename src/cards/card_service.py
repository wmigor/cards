import asyncio
from datetime import datetime

from peewee import fn

from cards.model import Card


class CardService:

	@staticmethod
	def get_all():
		return Card.select().order_by(fn.LOWER(Card.key)).execute()

	@staticmethod
	def add(key: str, value: str) -> Card:
		return Card.create(key=key, value=value)

	@staticmethod
	def delete(card: Card):
		card.delete_instance(recursive=True)

	@staticmethod
	def update(card: Card):
		card.save()

	@staticmethod
	def find_by_key(name: str):
		return Card.get_or_none(fn.LOWER(Card.key) == name.lower())

	@staticmethod
	def get_by_id(card: int):
		return Card.get_by_id(card)

	@staticmethod
	def truncate():
		Card.truncate_table()

	@classmethod
	def get_cards_for_repeat(cls):
		return Card.select().where(fn.julianday(datetime.now()) >= fn.julianday(Card.access) + Card.interval).execute()

	@classmethod
	def filter(cls, text: str):
		if not text:
			return cls.get_all()
		text = text.lower()
		return Card.select().where((fn.LOWER(Card.key) ** f"%{text}%") | (fn.LOWER(Card.value) ** f"%{text}%")).order_by(Card.key)


class CardServiceAsync:

	@staticmethod
	async def _run(function, *args):
		return await asyncio.to_thread(function, *args)

	@classmethod
	async def get_all(cls):
		return await cls._run(CardService.get_all)

	@classmethod
	async def add(cls, key: str, value: str) -> Card:
		return await cls._run(CardService.add, key, value)

	@classmethod
	async def delete(cls, card: Card):
		return await cls._run(CardService.delete, card)

	@classmethod
	async def update(cls, card: Card):
		return await cls._run(CardService.update, card)

	@classmethod
	async def find_by_key(cls, name: str):
		return await cls._run(CardService.find_by_key, name)

	@classmethod
	async def get_by_id(cls, card: int):
		return await cls._run(CardService.get_by_id, card)

	@classmethod
	async def truncate(cls):
		return await cls._run(CardService.truncate)

	@classmethod
	async def get_cards_for_repeat(cls):
		return await cls._run(CardService.get_cards_for_repeat)

	@classmethod
	async def filter(cls, text: str):
		return await cls._run(CardService.filter, text)
