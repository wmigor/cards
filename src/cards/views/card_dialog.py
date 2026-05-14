from typing import Callable

import flet as ft

from cards.card_service import CardServiceAsync
from cards.model import Card


class CardDialog(ft.AlertDialog):

	def __init__(self, on_save: Callable|None = None):
		super().__init__()
		self._card: Card|None = None
		self._on_save = on_save
		self._key = ft.TextField(label="Фраза")
		self._value = ft.TextField(label="Перевод")
		self.content = ft.Column([self._key, self._value], tight=True)
		self.actions = [
			ft.TextButton("Сохранить", on_click=self._save),
			ft.TextButton("Отмена", on_click=self._close)
		]

	def open_for_add(self, page):
		self._card = None
		self._open(page, "Добавление", "", "")

	def open_for_edit(self, page, card: Card):
		self._card = card
		self._open(page, "Редактирование", card.key, card.value)

	def _open(self, page, title, key, value):
		self.title = ft.Text(title)
		self._key.value = key
		self._value.value = str(value)
		self._clear_errors()
		self.open = True
		page.update()

	async def _save(self, _):
		if not await self._valid():
			return
		key = self._key.value
		value = self._value.value
		if self._card:
			self._card.key = key
			self._card.value = value
			await CardServiceAsync.update(self._card)
		else:
			await CardServiceAsync.add(key, value)
		self._on_save()
		self._close(None)

	async def _valid(self):
		valid = True
		key = self._key.value.strip() if self._key.value else ""
		value = self._value.value.strip()
		self._clear_errors()
		if not key:
			valid = False
			self._key.error = "Не должно быть пустым"
		if valid:
			card = await CardServiceAsync.find_by_key(key)
			if card and (not self._card or self._card.card != card.card):
				valid = False
				self._key.error = f"\"{key}\" уже есть"
		if not value:
			valid = False
			self._value.error = "Не должно быть пустым"
		return valid

	def _clear_errors(self):
		self._key.error = None
		self._value.error = None

	def _close(self, _):
		self.open = False
		self.page.update()