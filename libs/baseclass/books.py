import sqlite3
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivymd.utils import asynckivy
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivy.clock import Clock


Builder.load_file('./libs/kv/books.kv')


class BookCard(MDCard):
    index = NumericProperty()
    name = StringProperty('')
    image = StringProperty('')
    stocks = NumericProperty(0)
    price = StringProperty('')
    icon = StringProperty()
    title = StringProperty()
    category = StringProperty('')

    def to_cart(self):
        conn = sqlite3.connect('./assets/data/app_data.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS cart(id integer unique primary key autoincrement, product_id, '
                       'name, price, stocks, count, category)')
        cursor.execute(f'SELECT * FROM cart where product_id = {self.index}')
        get_product = cursor.fetchone()
        if get_product is None:
            insert = 'INSERT INTO cart (product_id, name, price, stocks, count, category) VALUES (?,?,?,?,?,?)'
            cursor.execute(insert, (self.index, self.name, self.price,  self.stocks, 1, self.category))
        else:
            cursor.execute(f'SELECT count FROM cart WHERE product_id = {self.index}')
            get_count = cursor.fetchone()
            if get_count[0] != self.stocks:
                cursor.execute(f'UPDATE cart SET count = {get_count[0] + 1} WHERE product_id = {self.index}')

        conn.commit()
        conn.close()


class Books(Screen):
    def __init__(self, **kwargs):
        super(Books, self).__init__(**kwargs)

        self.get = MDApp.get_running_app()

    def on_enter(self, *args):
        self.get.product_category = 'Book'
        data_items = self.store_direct()

        async def on_enter():
            for info in data_items:
                await asynckivy.sleep(0)
                store_widgets = BookCard(index=info[0], name=info[1], price=info[2], stocks=info[3], category=info[4])
                
                self.ids.content.add_widget(store_widgets)

        asynckivy.start(on_enter())

    def store_direct(self):
        data_items = []
        conn = sqlite3.connect('./assets/data/app_data.db')
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS shop(
        id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, 
        items TEXT, 
        price TEXT,
        stocks INTEGER)""")
        cursor.execute('SELECT * FROM shop WHERE category = "Book"')

        rows = cursor.fetchall()

        for row in rows:
            data_items.append(row)

        conn.close()

        return data_items  # data_items

    def on_leave(self, *args):
        self.ids.content.clear_widgets()


