import os

import flet as ft

from cards.exchange import ExchangeAsync
from cards.card_service import CardServiceAsync
from cards.views.card_dialog import CardDialog


class CardsView(ft.View):
	expands = [3, 3, 1]

	def __init__(self):
		super().__init__(route="/cards")
		self._sort_column = 0
		self._sort_reverse = False
		self._loading = False
		self._queue_load = False
		self._cards_list = ft.ListView(expand=True, spacing=0, padding=0, item_extent=48)
		self._header_buttons = [
			ft.TextButton("Фраза", expand=self.expands[0], on_click=lambda _: self._on_sort_clicked(0)),
			ft.TextButton("Перевод", expand=self.expands[1], on_click=lambda _: self._on_sort_clicked(1)),
		]
		header = ft.Container(
			content=ft.Row([
				self._header_buttons[0],
				self._header_buttons[1],
				ft.Text("Меню", expand=self.expands[2], text_align=ft.TextAlign.CENTER)
			]),
			bgcolor=ft.Colors.BLUE_GREY_100,
			padding=10,
			border_radius=5
		)
		self._search_field = ft.TextField(
			label="Поиск...",
			on_change=self._on_search_change
		)
		self.controls.append(ft.Column(controls=[header, self._cards_list], expand=True))
		self._card_dialog = CardDialog(self._load)
		self._file_picker = ft.FilePicker()
		self.appbar = ft.AppBar(
			title=ft.Row(controls=[ft.Text("Карточки"), self._search_field]),
			actions=[
				ft.IconButton(icon=ft.Icons.ADD, on_click=lambda _: self._card_dialog.open_for_add(self.page)),
				ft.PopupMenuButton(
					items=[
						ft.PopupMenuItem(content="Экспорт", on_click=self._export),
						ft.PopupMenuItem(content="Импорт", on_click=self._import)
					]
				)]
		)
		self._update_header_sort()

	def did_mount(self):
		self.page.overlay.append(self._card_dialog)
		self._load()

	def _load(self):
		self.page.run_task(self._load_cards)

	async def _load_cards(self):
		self._loading = True
		search = self._search_field.value.lower()
		cards = await CardServiceAsync.filter(search)
		self._cards_list.controls.clear()
		for card in cards:
			row = ft.Row([
					ft.Text(card.key, expand=self.expands[0]),
					ft.Text(str(card.value), expand=self.expands[1]),
					ft.PopupMenuButton(
						expand=self.expands[2],
						icon=ft.Icons.MORE_VERT,
						items=[
							ft.PopupMenuItem(
								content="Изменить",
								icon=ft.Icons.EDIT,
								data=card,
								on_click=self._on_edit_click
							),
							ft.PopupMenuItem(
								content="Удалить",
								icon=ft.Icons.DELETE,
								data=card,
								on_click=self._on_delete_total_amount_menu
							)
						]
					)
				])
			row.data = card
			self._cards_list.controls.append(row)
		self._cards_list.update()
		self._loading = False
		if self._queue_load:
			self._queue_load = False
			await self._load_cards()

	async def _on_delete_total_amount_menu(self, event):
		card = event.control.data
		await CardServiceAsync.delete(card)
		await self._load_cards()

	async def _on_edit_click(self, event):
		card = event.control.data
		if card:
			self._card_dialog.open_for_edit(self.page, card)

	def _on_sort_clicked(self, column):
		if self._sort_column == column:
			self._sort_reverse = not self._sort_reverse
		else:
			self._sort_reverse = False
			self._sort_column = column
		self._update_header_sort()
		self._cards_list.controls.sort(
			key=lambda row: row.controls[self._sort_column].value,
			reverse=self._sort_reverse
		)
		self.update()

	def _update_header_sort(self):
		for i, button in enumerate(self._header_buttons):
			if i == self._sort_column:
				button.icon = ft.Icons.ARROW_DROP_UP if self._sort_reverse else ft.Icons.ARROW_DROP_DOWN
			else:
				button.icon = None

	async def _export(self, _):
		path = await self._file_picker.get_directory_path(
			dialog_title="Выберите файл для сохранения")
		if path:
			await ExchangeAsync.save_to_file(os.path.join(path, "cards.crd"))

	async def _import(self, _):
		paths = await self._file_picker.pick_files(
			dialog_title="Выберите файл для импорта",
			file_type=ft.FilePickerFileType.CUSTOM,
			allowed_extensions=["crd"],
			allow_multiple=False)
		if paths and paths[0].path:
			await ExchangeAsync.load_from_file(paths[0].path)
			await self._load_cards()

	def _on_search_change(self, event):
		if self._loading:
			self._queue_load = True
		else:
			self._load()
