import asyncio
import json
from datetime import datetime

from cards.card_service import CardService
from cards.model import Card


class Exchange:

	@staticmethod
	def serialize() -> dict:
		cards = []
		for card in CardService.get_all():
			cards.append({
				"key": card.key,
				"value": card.value,
				"access": card.access.timestamp() * 1000,
				"easy_factor": card.easy_factor,
				"interval": card.interval,
				"success": card.success,
			})
		data = {
			"version": "1.0",
			"cards": cards}
		return data

	@staticmethod
	def load_from_file(path: str):
		data = json.load(open(path, "r", encoding="utf-8"))
		CardService.truncate()
		for card_data in data.get("cards", []):
			access = card_data.get("access")
			access = datetime.fromtimestamp(access / 1000.0) if access else datetime.now()
			easy_factor = card_data.get("easy_factor", 2.5)
			interval = card_data.get("easy_factor", 0.0)
			key = card_data.get("key")
			success = card_data.get("success", 0)
			value = card_data.get("value")
			Card.create(access=access, easy_factor=easy_factor, interval=interval, key=key, success=success, value=value)

	@classmethod
	def save_to_file(cls, path):
		data = cls.serialize()
		with open(path, "w", encoding="utf-8") as f:
			json.dump(data, f)


class ExchangeAsync:
	@staticmethod
	async def _run(function, *args):
		return await asyncio.to_thread(function, *args)

	@classmethod
	async def load_from_file(cls, path):
		return await cls._run(Exchange.load_from_file, path)

	@classmethod
	async def save_to_file(cls, path):
		return await cls._run(Exchange.save_to_file, path)
