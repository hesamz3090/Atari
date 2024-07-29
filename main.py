from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCardSwipe

KV = '''
<Content>:
    orientation: "vertical"
    spacing: "12dp"
    padding: "16dp"
    size_hint_y: None
    height: self.minimum_height

    MDTextField:
        id: field1
        hint_text: "Start Time"
        mode: "rectangle"
        size_hint_y: None
        height: "48dp"

    MDTextField:
        id: field2
        hint_text: "Exit Time"
        mode: "rectangle"
        size_hint_y: None
        height: "48dp"

    MDTextField:
        id: field3
        hint_text: "Table"
        mode: "rectangle"
        size_hint_y: None
        height: "48dp"
        on_focus: if self.focus: app.menu.open()

<SwipeToDeleteItem>:
    size_hint_y: None
    height: "56dp"

    MDCardSwipeLayerBox:
        padding: "8dp"

        MDIconButton:
            icon: "trash-can"
            pos_hint: {"center_y": .5}
            on_release: app.remove_item(root)

    MDCardSwipeFrontBox:
        OneLineListItem:
            id: content
            text: root.text
            _no_ripple_effect: True

Screen:
    BoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Atari"
            elevation: 10

        BoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(10)

            ScrollView:
                MDList:
                    id: list_view

            MDFloatingActionButton:
                id: button
                icon: "plus"
                pos_hint: {"right": 1, "bottom": 1}
                elevation_normal: 8
                elevation_pressed: 12
                on_release: app.show_dialog()
'''

class Content(BoxLayout):
    pass

class SwipeToDeleteItem(MDCardSwipe):
    text = StringProperty()

class TapTargetViewDemo(MDApp):
    dialog = None
    edit_index = None
    data_list = []

    def build(self):
        screen = Builder.load_string(KV)
        self.menu_items = [
            {"text": "One", "viewclass": "OneLineListItem", "on_release": lambda x="one": self.set_item(x)},
            {"text": "Two", "viewclass": "OneLineListItem", "on_release": lambda x="two": self.set_item(x)},
        ]
        self.menu = MDDropdownMenu(
            caller=screen.ids.button,
            items=self.menu_items,
            position="center",
            width_mult=4,
        )
        return screen

    def time_to_minutes(self, time_str):
        """Convert time string in 'hh:mm' format to minutes."""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except ValueError:
            return 0

    def set_item(self, text_item):
        self.dialog.content_cls.ids.field3.text = text_item
        self.menu.dismiss()

    def show_dialog(self, instance=None, index=None):
        self.edit_index = index
        if not self.dialog:
            self.dialog = MDDialog(
                title="Enter Values",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=self.close_dialog
                    ),
                    MDFlatButton(
                        text="SUBMIT", on_release=self.get_values
                    ),
                ],
            )
        if instance:
            values = instance.text.split(' | ')
            self.dialog.content_cls.ids.field1.text = values[1] if len(values) > 1 else ''
            self.dialog.content_cls.ids.field2.text = values[2] if len(values) > 2 else ''
            self.dialog.content_cls.ids.field3.text = values[0] if len(values) > 0 else ''
        else:
            self.dialog.content_cls.ids.field1.text = ''
            self.dialog.content_cls.ids.field2.text = ''
            self.dialog.content_cls.ids.field3.text = ''
        self.dialog.open()

    def close_dialog(self, *args):
        self.dialog.dismiss()

    def get_values(self, *args):
        content = self.dialog.content_cls
        start_time = content.ids.field1.text
        exit_time = content.ids.field2.text
        table = content.ids.field3.text

        result = f'{table} | {start_time}'
        if exit_time:
            time1_minutes = self.time_to_minutes(start_time)
            time2_minutes = self.time_to_minutes(exit_time)
            play_time = max(time2_minutes - time1_minutes, 0)
            cost = play_time * 833
            result += f' | {exit_time} | {play_time} M | {cost} Toman'

        if self.edit_index is not None:
            self.data_list[self.edit_index] = result
            item = self.root.ids.list_view.children[::-1][self.edit_index]
            item.text = result
            self.edit_index = None
        else:
            self.data_list.append(result)
            self.root.ids.list_view.add_widget(
                SwipeToDeleteItem(
                    text=result,
                    on_release=lambda instance: self.show_dialog(
                        instance,
                        index=self.root.ids.list_view.children[::-1].index(instance))
                )
            )
        self.dialog.dismiss()

    def remove_item(self, instance):
        self.data_list.remove(instance.text)
        self.root.ids.list_view.remove_widget(instance)

TapTargetViewDemo().run()
