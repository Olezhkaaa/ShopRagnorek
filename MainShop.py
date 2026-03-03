from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLabel, QPushButton, QVBoxLayout, 
                             QListView, QListWidget, QWidget, QGridLayout, 
                             QApplication, QScrollArea, QFrame, QDialog,QLineEdit,QListWidgetItem,QFormLayout,QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QComboBox, QMessageBox)

from PyQt5.QtGui import QPixmap  # QtGui импортируем отдельно
from PyQt5.QtCore import Qt,QSize  # Убрали QtGui
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
import os
import mysql.connector
import sqlite3

# Подключение к базе данных
db_config = {
    'host': '',
    'port': ,
    'user': '',
    'password': '',
    'database': ''
}

def connect_db():
    return mysql.connector.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )


class MainShop(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('shop.ui', self)
        self.cart = []
        self.user_id = None 

        self.login_button.clicked.connect(self.show_login_window)
        self.cart_button.clicked.connect(self.show_cart)

        # Привязка кнопок категорий
        self.women_button.clicked.connect(lambda: self.show_category('women'))
        self.men_button.clicked.connect(lambda: self.show_category('men'))
        self.kids_button.clicked.connect(lambda: self.show_category('kids'))

        # Привязка поиска
        self.search_button.clicked.connect(self.search_products)
        self.search_bar.returnPressed.connect(self.search_products)

        # Инициализация прокручиваемой области
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)  # Горизонтальный layout
        self.scroll_area_layout.setSpacing(15)

        self.scrollArea.setWidget(self.scroll_area_widget)
        self.scrollArea.setWidgetResizable(True)

    def show_login_window(self):
        self.login_window = LoginWindow(self)
        self.login_window.exec_()

    def show_category(self, category):
        print(f"Загружаю товары для категории: {category}")

        # Очистка старого контента
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Запрос к базе данных
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, name, price, description, image_path FROM products1 WHERE category = %s", (category,))
        products = cursor.fetchall()

        if products:
            for row_number, row_data in enumerate(products):
                card = self.create_product_card(row_data)
                self.scroll_area_layout.addWidget(card)
        else:
            self.scroll_area_layout.addWidget(QLabel("Товары не найдены."))

        cursor.close()
        conn.close()

    def create_product_card(self, product):
        product_id, name, price, description, image_path = product  

        product_frame = QFrame()
        product_frame.setFixedSize(850, 150)
        product_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background-color: white;
                padding: 5px;
            }
            QLabel { 
                color: #333; 
                font-size: 14px; 
            }
            QPushButton {
                background-color: #ff9900;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                min-width: 120px;
            }
        """)

        layout = QHBoxLayout(product_frame)

        # Загрузка изображения
        image_label = QLabel()
        image_label.setFixedSize(120, 120)

        if image_path and os.path.exists(image_path):  
            pixmap = QPixmap(image_path).scaled(image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:  
            print("⚠ Изображение не найдено, использую заглушку.")
            pixmap = QPixmap("default_image.png").scaled(image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        # Блок информации
        info_layout = QVBoxLayout()
        
        name_label = QLabel(f"<b>{name}</b>")
        name_label.setFixedWidth(500)  # Фиксированная ширина строки
        
        description_label = QLabel(description)
        description_label.setStyleSheet("color: #555; font-size: 12px;")
        description_label.setWordWrap(True)
        description_label.setFixedWidth(500)  # Описание тоже фиксированной ширины

        price_label = QLabel(f"<font color='green'><b>{price} ₽</b></font>")
        price_label.setFixedWidth(500)  # Цена тоже той же ширины

        # Добавляем виджеты в инфо-блок
        info_layout.addWidget(name_label)
        info_layout.addWidget(description_label)
        info_layout.addWidget(price_label)

        # Кнопка "В корзину"
        add_to_cart_button = QPushButton("🛒 В корзину")
        add_to_cart_button.setFixedSize(140, 50)
        add_to_cart_button.setCursor(Qt.PointingHandCursor)
        add_to_cart_button.clicked.connect(lambda: self.add_to_cart(product_id, name, price))

        # Собираем карточку
        layout.addWidget(image_label)
        layout.addLayout(info_layout)
        layout.addWidget(add_to_cart_button)

        return product_frame


    def add_to_cart(self, product_id, name, price):
        if self.user_id is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Ошибка")
            msg.setText("Вы должны войти в аккаунт, чтобы добавить товар в корзину.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        # Добавляем товар в корзину в базе данных
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cart_items (product_id, product_name, product_price, user_id) 
            VALUES (%s, %s, %s, %s)
        """, (product_id, name, price, self.user_id))
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Товар {name} добавлен в корзину.")
    
    def show_cart(self):
        # Окно корзины
        self.cart_window = QDialog(self)
        self.cart_window.setWindowTitle("Корзина")
        self.cart_window.setGeometry(150, 150, 500, 500)

        try:
            # Загружаем UI корзины
            loadUi('cart.ui', self.cart_window)
            print("UI корзины успешно загружен.")
        except Exception as e:
            print(f"Ошибка при загрузке UI файла корзины: {e}")
            return

        # Найдем виджеты и проверим их существование
        self.total_sum_label = self.cart_window.findChild(QLabel, 'totalSumLabel')
        self.items_list_widget = self.cart_window.findChild(QListWidget, 'itemsList')

        buy_button = self.cart_window.findChild(QPushButton, 'buyButton')
        clear_button = self.cart_window.findChild(QPushButton, 'clearCartButton')  # исправлено!

        print(f"Кнопка 'Купить' найдена: {buy_button}")  
        print(f"Кнопка 'Очистить корзину' найдена: {clear_button}")  

        if buy_button is None or clear_button is None:
            print("Ошибка: одна из кнопок не найдена. Проверьте objectName в cart.ui")
            return  

        # Привязка кнопок
        buy_button.clicked.connect(self.buy_items)
        clear_button.clicked.connect(self.clear_cart)

        # Обновляем содержимое корзины
        self.update_cart(self.items_list_widget, self.total_sum_label)

        self.cart_window.exec_()

    
    def update_cart(self, items_list_widget, total_sum_label):
        # Очистить список перед обновлением
        items_list_widget.clear()

        # Получаем товары из базы данных
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT product_id, product_name, product_price, quantity 
            FROM cart_items WHERE user_id = %s
        """, (self.user_id,))
        cart_items = cursor.fetchall()

        total_sum = 0
        if cart_items:
            for item in cart_items:
                item_id = item[0]
                item_name = item[1]
                item_price = item[2]
                quantity = item[3]

                # Создаем виджет для текста и кнопки
                item_widget = QWidget()

                # Создаем макет для текстовой информации и кнопки
                layout = QHBoxLayout()

                # Создаем метку для текста
                item_label = QLabel(f"{item_name} - {item_price} ₽ x {quantity}")
                layout.addWidget(item_label)

                # Создаем кнопку удаления с изменением стиля
                delete_button = QPushButton("X")
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: red;
                        color: white;
                        border-radius: 50%;  /* Округление кнопки */
                        font-size: 12px;
                        width: 30px;   /* Ширина кнопки */
                        height: 30px;  /* Высота кнопки (одинаковая ширина и высота для круга) */
                        padding: 0;
                        text-align: center;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: darkred;
                    }
                """)
                delete_button.setFixedSize(30, 30)  # Устанавливаем фиксированные размеры (ширина и высота одинаковые)

                delete_button.clicked.connect(lambda _, product_id=item_id: self.remove_item_from_cart(product_id, items_list_widget, total_sum_label))

                layout.addWidget(delete_button)
                item_widget.setLayout(layout)

                # Добавляем виджет в список
                list_item = QListWidgetItem()
                items_list_widget.addItem(list_item)
                items_list_widget.setItemWidget(list_item, item_widget)

                total_sum += item_price * quantity
        else:
            items_list_widget.addItem("Нет товаров в корзине.")

        # Обновляем метку с общей суммой
        total_sum_label.setText(f"Сумма: {total_sum} ₽")

        cursor.close()
        conn.close()





    def remove_item_from_cart(self, product_id, items_list_widget, total_sum_label):
        # Удалить товар из корзины
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM cart_items WHERE product_id = %s AND user_id = %s
        """, (product_id, self.user_id))
        conn.commit()
        cursor.close()
        conn.close()

        # Обновляем корзину после удаления
        self.update_cart(items_list_widget, total_sum_label)

    def clear_cart(self):
        if not hasattr(self, 'items_list_widget') or not hasattr(self, 'total_sum_label'):
            print("Ошибка: Корзина не открыта или отсутствуют элементы.")
            return

        # Очищаем всю корзину
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (self.user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        # Обновляем корзину после очистки
        self.update_cart(self.items_list_widget, self.total_sum_label)

    def buy_items(self):
        if not hasattr(self, 'items_list_widget') or not hasattr(self, 'total_sum_label'):
            print("Ошибка: Корзина не открыта или отсутствуют элементы.")
            return

        # Показать всплывающее сообщение о успешной покупке
        QMessageBox.information(self, "Успех", "Вы успешно купили товары! Можете прийти в магазин забрать их.")

        # Очищаем корзину после покупки
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (self.user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        self.update_cart(self.items_list_widget, self.total_sum_label)
   
            
    def load_all_products(self, manager_window):
        # Получаем таблицу товаров из UI
            product_table = manager_window.findChild(QTableWidget, 'productTable')

        # Получаем все товары из базы данных
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT product_id, name,description, price,category, image_path FROM products1")
            products = cursor.fetchall()

            if products:
                # Устанавливаем количество строк в таблице
                product_table.setRowCount(len(products))

                # Заполняем таблицу товарами
                for row_index, product in enumerate(products):
                    product_id, name, category, price, quantity = product

                    # Добавляем данные в таблицу
                    product_table.setItem(row_index, 0, QTableWidgetItem(name))
                    product_table.setItem(row_index, 1, QTableWidgetItem(category))
                    product_table.setItem(row_index, 2, QTableWidgetItem(str(price)))
                    product_table.setItem(row_index, 3, QTableWidgetItem(str(quantity)))
                    # Здесь можно добавить кнопку для действий, например, редактирования или удаления
                    action_button = QPushButton('Изменить')
                    product_table.setCellWidget(row_index, 4, action_button)

            cursor.close()
            conn.close()

    def show_manager_window(self):
            # Покажем окно менеджера
            self.manager_window = ManagerWindow(self)
            self.manager_window.show()   

    def search_products(self):
        search_text = self.search_bar.text().strip()

        if not search_text:
            print("⚠ Поисковая строка пуста")
            return  

        print(f"🔍 Ищем товары по запросу: {search_text}")

        # Очистка старого контента
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT product_id, name, price, description, image_path 
                FROM products1 
                WHERE LOWER(name) LIKE %s
            """
            cursor.execute(query, ('%' + search_text.lower() + '%',))
            products = cursor.fetchall()
            print(f"🔹 Найдено товаров: {len(products)}")

            if products:
                for row_data in products:
                    card = self.create_product_card(row_data)
                    self.scroll_area_layout.addWidget(card)
            else:
                self.scroll_area_layout.addWidget(QLabel("❌ Товары не найдены."))

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"⚠ Ошибка при поиске: {e}")
    



class ManagerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('manager.ui', self)

        # Подключаем кнопки к функциям
        self.addProductButton.clicked.connect(self.add_product)
        self.deleteButton.clicked.connect(self.delete_product)
        self.editProductButton.clicked.connect(self.edit_product)

        

        # Загружаем все продукты
        self.load_all_products()

    def load_all_products(self):
        self.product_table = self.findChild(QtWidgets.QTableWidget, "tableWidget")

        if not self.product_table:
            print("Ошибка: не найден виджет tableWidget!")
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT product_id, name, description, price, category, image_path FROM products1")
        products = cursor.fetchall()

        # Устанавливаем правильное количество колонок и их заголовки
        self.product_table.setColumnCount(6)  # Теперь 6 колонок
        self.product_table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Цена", "Категория", "Изображение"])

        self.product_table.setRowCount(len(products))

        for row, product in enumerate(products):
            self.product_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(product[0])))  # ID
            self.product_table.setItem(row, 1, QtWidgets.QTableWidgetItem(product[1]))  # Название
            self.product_table.setItem(row, 2, QtWidgets.QTableWidgetItem(product[2] if product[2] else ""))  # Описание
            self.product_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(product[3])))  # Цена
            self.product_table.setItem(row, 4, QtWidgets.QTableWidgetItem(product[4]))  # Категория
            self.product_table.verticalHeader().setVisible(False)
            # Добавляем изображение
            image_label = QtWidgets.QLabel()
            pixmap = QPixmap(product[5]) if product[5] else QPixmap("no_image.png")  
            image_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
            self.product_table.setCellWidget(row, 5, image_label)  # Добавляем изображение в таблицу

        cursor.close()
        conn.close()

    def add_product(self):
        dialog = AddProductDialog(self)
        if dialog.exec_():  # Если пользователь нажал "Добавить"
            self.load_all_products()  # Обновляем таблицу

    def delete_product(self):
        product_table = self.product_table
        selected_row = product_table.currentRow()

        if selected_row >= 0:
            product_id = product_table.item(selected_row, 0).text()  # Получаем product_id из первого столбца

            # Удаляем товар из базы данных
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products1 WHERE product_id = %s", (product_id,))
            conn.commit()
            cursor.close()
            conn.close()

            print(f"Товар с ID {product_id} был удален.")
            self.load_all_products()  # Обновляем таблицу после удаления товара
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите товар для удаления.")

    def edit_product(self):
        # Получаем выбранную строку из таблицы
        selected_row = self.product_table.currentRow()
        
        if selected_row >= 0:
            product_id = self.product_table.item(selected_row, 0).text()  # Получаем product_id из первого столбца
            print(f"Редактирование товара с ID {product_id}")
            
            # Открываем окно редактирования товара с переданным ID
            edit_window = EditProductWindow(int(product_id), self)
            edit_window.exec_()
            self.load_all_products()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите товар для редактирования.")


 


       
# Окно логина
class LoginWindow(QDialog):  # Используем QMainWindow вместо QWidget
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('login.ui', self)
        self.parent_window = parent

        self.login_button.clicked.connect(self.login)
        self.register_redirect_button.clicked.connect(self.show_register_window)

        # Окно регистрации
        self.register_window = RegisterWindow(self)

    
    def login(self):
        login = self.login_field.text()
        password = self.password_field.text()

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, id_user FROM users WHERE username = %s AND password = %s", (login, password))

        user = cursor.fetchone()

        if user:
            print("Авторизация успешна!")
            self.parent().user_id = user[0]  # Сохраняем ID пользователя в родительском окне
            if user[1] == 2:
                # Открыть окно для менеджера
                self.parent().show_manager_window()  # Это теперь будет работать
            else:
                self.parent().show_category("women")  # Окно для обычного пользователя
            self.close()  # Закрываем окно логина
        else:
            print("Ошибка: неверный логин или пароль.")

        cursor.close()
        conn.close()


    def show_register_window(self):
        self.register_window.show()  # Показываем окно регистрации
        self.hide()  # Скрываем окно логина


# Окно регистрации
class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi('register.ui', self)

        self.register_button.clicked.connect(self.register)

    def register(self):
        login = self.register_login_field.text()
        email = self.register_email_field.text()
        password = self.register_password_field.text()

        conn = connect_db()
        cursor = conn.cursor()

        # Проверка существования пользователя
        cursor.execute("SELECT * FROM users WHERE username = %s", (login,))
        existing_user = cursor.fetchone()

        if existing_user:
            print("Пользователь с таким логином уже существует.")
        else:
            # Регистрация нового пользователя с id_user = 1
            cursor.execute("""
                INSERT INTO users (Id_user, username, email, password) 
                VALUES (1, %s, %s, %s)
            """, (login, email, password))
            conn.commit()
            print("Пользователь успешно зарегистрирован с Id_user = 1!")
            self.close()  # Закрываем окно регистрации

            # После регистрации показываем окно логина
            self.parent().show()  # Показываем окно логина

        cursor.close()
        conn.close()


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление товара")
        self.setGeometry(100, 100, 350, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit, QComboBox {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
                background-color: white;
            }
            QPushButton {
                background-color: #20b2aa;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008b8b;
            }
        """)

        layout = QFormLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Название товара")
        layout.addRow(QLabel("Название:"), self.name_input)

        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText("Описание")
        layout.addRow(QLabel("Описание:"), self.description_input)

        self.price_input = QLineEdit(self)
        self.price_input.setPlaceholderText("Цена")
        layout.addRow(QLabel("Цена:"), self.price_input)

        self.category_combo = QComboBox(self)
        self.category_combo.addItems(["women", "men", "kids"])
        layout.addRow(QLabel("Категория:"), self.category_combo)

        self.image_path = ""
        self.image_button = QPushButton("Выбрать изображение")
        self.image_button.clicked.connect(self.choose_image)
        layout.addRow(self.image_button)

        self.add_button = QPushButton("Добавить товар")
        self.add_button.clicked.connect(self.add_product_to_db)
        layout.addRow(self.add_button)

        self.setLayout(layout)

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image_path = file_path
            self.image_button.setText("Изображение выбрано ✅")

    def add_product_to_db(self):
        name = self.name_input.text()
        description = self.description_input.text()
        price = self.price_input.text()
        category = self.category_combo.currentText()

        if not name or not price:
            QMessageBox.warning(self, "Ошибка", "Название и цена обязательны!")
            return

        try:
            # Try to convert price to float
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом!")
            return

        if not self.image_path:
            QMessageBox.warning(self, "Ошибка", "Не выбрано изображение!")
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Add the product to the database, storing the image path
            cursor.execute("""
                INSERT INTO products1 (name, price, description, image_path, category) 
                VALUES (%s, %s, %s, %s, %s)
            """, (name, price, description, self.image_path, category))  # Directly store the image path
            conn.commit()

            QMessageBox.information(self, "Успех", "Товар добавлен!")
            self.accept()
        except Exception as e:
            conn.rollback()
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка при добавлении товара: {str(e)}")
        finally:
            conn.close()




class EditProductWindow(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id  # ID товара, который редактируем
        loadUi('edit_product.ui', self)  # Загружаем UI для редактирования товара

        # Загружаем данные товара
        self.product_data = self.load_product_data(product_id)

        # Заполняем поля данными товара
        self.name_input.setText(self.product_data['name'])
        self.price_input.setText(str(self.product_data['price']))  # Преобразуем цену в строку
        self.description_input.setText(self.product_data['description'])

        # Связь кнопок с методами
        self.save_button.clicked.connect(self.save_product)
        self.cancel_button.clicked.connect(self.reject)
        self.change_image_button.clicked.connect(self.change_image)

    def load_product_data(self, product_id):
        """
        Метод для загрузки данных товара из базы данных.
        Он должен вернуть словарь с данными товара.
        """
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, description, image_path FROM products1 WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if result:
            # Возвращаем данные в виде словаря
            return {
                'name': result[0],
                'price': result[1],
                'description': result[2],
                'image_path': result[3] if result[3] else ''  # Если нет изображения, передаем пустую строку
            }
        else:
            # Если товар не найден, возвращаем пустые значения
            return {'name': '', 'price': 0, 'description': '', 'image_path': ''}

    def save_product(self):
        """
        Метод для сохранения изменений в товаре.
        """
        name = self.name_input.text()
        price = float(self.price_input.text()) if self.price_input.text() else 0
        description = self.description_input.toPlainText()

        # Обновляем данные товара в базе данных
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products1 
            SET name = %s, price = %s, description = %s
            WHERE product_id = %s
        """, (name, price, description, self.product_id))
        conn.commit()
        cursor.close()
        conn.close()

        QMessageBox.information(self, "Успех", "Данные товара успешно сохранены.")
        self.accept()  # Закрываем окно после успешного сохранения

    def change_image(self):
        """
        Метод для изменения изображения товара.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        
        if file_name:
            # Здесь вы можете обновить путь к изображению в базе данных
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products1
                SET image_path = %s
                WHERE product_id = %s
            """, (file_name, self.product_id))
            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "Успех", "Фото товара успешно изменено.")


      

if __name__ == "__main__":
    app = QApplication([])

    # Создаем окно магазина
    main_shop_window = MainShop()

    # Показываем главное окно магазина
    main_shop_window.show()

    # Запуск приложения
    app.exec_()
