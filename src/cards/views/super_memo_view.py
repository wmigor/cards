import random

import flet as ft

from cards.card_service import CardServiceAsync
from cards.model import Card


class SuperMemoView(ft.View):

	def __init__(self):
		super().__init__()
		self._question = ft.Text()
		self._answer = ft.TextField(on_submit=self._check_answer)
		self._quality_buttons = ft.Column()
		self._card_count = ft.Text()
		self.controls.append(ft.Column(controls=[
			self._card_count,
			self._question,
			self._answer,
			ft.Row(controls=[
				ft.Row(controls=[ft.Button("Подсказка", autofocus=True, on_click=self._on_help)]),
				ft.Row(controls=[ft.Button("ОК", autofocus=True, on_click=self._check_answer)])
			]),
			self._quality_buttons
		]))
		self.appbar = ft.AppBar(title="Super Memo", actions=[
			ft.IconButton(icon=ft.Icons.LIST, on_click=self._on_cards_click),
		])
		self._cards = []
		self._key = ""
		self._value = ""
		self._help_count = 0
		self._error_count = 0

	def did_mount(self):
		self._load()

	def _load(self):
		self.page.run_task(self._load_cards)

	async def _load_cards(self):
		self._clear()
		self._cards.extend(await CardServiceAsync.get_cards_for_repeat())
		self._update_card_count()
		random.shuffle(self._cards)
		self._step()
		self.update()

	def _update_card_count(self):
		count = len(self._cards)
		if self._card:
			count += 1
		self._card_count.value = f"Осталось карт: {count}"

	async def _on_cards_click(self, _):
		await self.page.push_route("/cards")

	def _step(self):
		if self._cards:
			self._set_card(self._cards.pop())
		else:
			self._clear()
		self._update_card_count()

	def _clear(self):
		self._card = None
		self._help_count = 0
		self._error_count = 0
		self._key = ""
		self._value = ""
		self._answer.error = ""
		self._question.value = ""
		self._answer.value = ""
		self._cards.clear()
		self._update_card_count()

	def _set_card(self, card: Card):
		self._card = card
		self._help_count = 0
		self._error_count = 0
		self._answer.error = ""
		swap = random.random() > 0.5
		self._key = self._get_first_value(card.value if swap else card.key)
		self._value = card.key if swap else card.value
		self._question.value = self._key
		self._answer.value = ""
		self._quality_buttons.visible = False

	@staticmethod
	def _get_first_value(text: str):
		words = text.split(":")
		return words[0].strip() if words else ""

	async def _check_answer(self, _):
		text = self._answer.value.lower().strip()
		if not self._card or not text:
			await self._answer.focus()
			self.update()
			return
		for value in self._value.lower().split(":"):
			if value == text:
				await self._on_success(self._card)
				await self._answer.focus()
				self.update()
				return
		self._on_error()
		await self._answer.focus()
		self.update()

	async def _on_success(self, card: Card):
		if self._error_count > 0 or self._help_count > 0:
			quality = max(0, 4 - self._error_count - self._help_count)
			card.update_super_memo_2(quality)
			await CardServiceAsync.update(card)
			self._step()
			return
		# TODO show quality buttons for select quality
		card.update_super_memo_2(4)
		await CardServiceAsync.update(card)
		self._step()

	def _on_error(self):
		self._answer.error = "Error!!!"
		self._error_count += 1

	async def _on_help(self, _):
		if not self._value:
			return
		value = self._get_first_value(self._value)
		if not self._card or self._help_count >= len(value):
			return
		self._help_count += 1
		self._card.success //= 2
		text = value[0 : self._help_count]
		for i in range(len(value) - self._help_count):
			text += "*"
		self._answer.value = text
		self._answer.selection = ft.TextSelection(self._help_count, len(value))
		await self._answer.focus()
		await CardServiceAsync.update(self._card)
