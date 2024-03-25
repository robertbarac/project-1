import kivy
from kivy.config import Config
import os
import sqlite3

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup


Config.set("graphics", "width", "340")
Config.set("graphics", "height", "640")

def connect_to_database(path):
    try:
        con = sqlite3.connect(path)
        cursor = con.cursor()
        create_table_products(cursor)
        con.commit()
        con.close()
        
    except Exception as e:
        print(e)
#60618386naf...
def create_table_products(cursor):
    cursor.execute(
    """
    CREATE TABLE  Productos(
        ID       INT PRIMARY KEY NOT NULL,
        Nombre   TEXT NOT NULL,
        Marca    TEXT NOT NULL,
        Costo    FLOAT NOT NULL,
        Almacen  INT NOT NULL
    )
    """
    )


class MessagePopup(Popup):
    pass

class MainWid(ScreenManager):
    def __init__(self, **kwargs):
        super(MainWid, self).__init__(**kwargs)
        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH + "/my_database.db"
        
        self.startwid = StartWid(self) # le estamos pasando MainWid a StartWid, increíble
        self.DataBaseWid = DataBaseWid(self)
        
        self.InsertDataWid = BoxLayout()
        self.UpdateDataWid = BoxLayout() # para hacer una limpieza de boslayoute insertar un widget nuevo
        self.Popup = MessagePopup()
        
        wid = Screen(name='start')
        wid.add_widget(self.startwid)
        self.add_widget(wid)
        wid = Screen(name='database')
        wid.add_widget(self.DataBaseWid)
        self.add_widget(wid)
        wid = Screen(name='insertdata')
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)
        wid = Screen(name='updatedata')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)
        
        self.goto_start()
    
    def goto_start(self):
        self.current = 'start'
    
    def goto_database(self):
        self.DataBaseWid.check_memory()
        self.current = 'database'
    
    def goto_insert_data(self):
        self.InsertDataWid.clear_widgets()
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = 'insertdata'
    
    def goto_update_data(self, data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self, data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'updatedata'

class StartWid(BoxLayout): 
    def __init__(self, mainwid, *args, **kwargs):
        super(StartWid, self).__init__(*args, **kwargs)
        self.mainwid = mainwid
        
    def create_database(self):
        connect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()
    

class DataBaseWid(BoxLayout):
    
    def __init__(self, mainwid, *args, **kwargs):
        super(DataBaseWid, self).__init__(*args, **kwargs)
        self.mainwid = mainwid
    
    def check_memory(self):
        self.ids.container.clear_widgets() # con esto granatizamos que databasewid no tenga containers
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('SELECT ID, Nombre, Marca, Costo, Almacen from Productos')
        for i in cursor:
            wid = DataWid(self.mainwid)
            r1 = 'ID: ' + str(i[0]) + '\n'
            r2 = i[1] + ', ' + i[2] + '\n'
            r3 = 'Precio por unidad: ' + str(i[3]) + '\n'
            r4 = 'En almacén: ' + str(i[4])
            wid.data_id = str(i[0])
            wid.data = r1 + r2 + r3 + r4
            self.ids.container.add_widget(wid)
        wid = NewDataButton(self.mainwid)
        self.ids.container.add_widget(wid) # asi se visualiza nuestro botón
        con.close()

class InsertDataWid(BoxLayout):
    
    def __init__(self, mainwid, *args, **kwargs):
        super(InsertDataWid, self).__init__(*args, **kwargs)
        self.mainwid = mainwid
        
    def insert_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        id_ = self.ids.ti_id.text
        nombre = self.ids.ti_nombre.text
        marca = self.ids.ti_marca.text
        costo = self.ids.ti_costo.text
        almacen = self.ids.ti_almacen.text
        registro = (id_, nombre, marca, costo, almacen)
        # s1 = 'INSERT INTO Productos(ID, Nombre, Marca, Costo, Almacen)'
        # s2 = f'VALUES({registro})'
        # Verificar si algún campo está vacío
        if not id_ or not nombre or not marca or not costo or not almacen:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error de registro"
            message.text = "Uno o más campos están vacíos"
        elif ',' in costo:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error de registro"
            message.text = "Hay una coma en el campo Costo, en su lugar, use un punto (.)"
        else:
            try:
                cursor.execute('INSERT INTO Productos (ID, Nombre, Marca, Costo, Almacen) VALUES (?, ?, ?, ?, ?)', registro)
                con.commit()
                con.close()
                self.mainwid.goto_database()
            except Exception as e:
                message = self.mainwid.Popup.ids.message
                self.mainwid.Popup.open()
                self.mainwid.Popup.title = "Data base error"
                # pass
                # if '' in registro:
                #     print("Uno o más campos están vacíos")
                # else:
                message.text = str(e)
        
        
        
    def back_to_dbw(self):
        self.mainwid.goto_database()

class UpdateDataWid(BoxLayout):
    
    def __init__(self, mainwid, data_id, *args, **kwargs):
        super(UpdateDataWid, self).__init__(*args, **kwargs)
        self.mainwid = mainwid
        self.data_id = data_id
        self.check_memory()
    
    def check_memory(self):
        # print("haciendo check memory")
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = "SELECT Nombre, Marca, Costo, Almacen from Productos WHERE ID ="
        cursor.execute(s+self.data_id)
        for i in cursor:
            self.ids.ti_nombre.text = i[0]
            self.ids.ti_marca.text = i[1]
            self.ids.ti_costo.text = str(i[2])
            self.ids.ti_almacen.text = str(i[3])
        con.close()
    def update_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        nombre = self.ids.ti_nombre.text
        marca = self.ids.ti_marca.text
        costo = self.ids.ti_costo.text
        almacen = self.ids.ti_almacen.text
        registro = (nombre, marca, costo, almacen, self.data_id)
        # s1 = 'INSERT INTO Productos(ID, Nombre, Marca, Costo, Almacen)'
        # s2 = f'VALUES({registro})'
        # Verificar si algún campo está vacío
        if not nombre or not marca or not costo or not almacen:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error de registro"
            message.text = "Uno o más campos están vacíos"
        elif ',' in costo:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error de registro"
            message.text = "Hay una coma en el campo Costo \n En su lugar, use un punto (.)"
        else:
            try:
                cursor.execute('UPDATE Productos SET Nombre=?, Marca=?, Costo=?, Almacen=? WHERE ID=?', registro)
                con.commit()
                con.close()
                self.mainwid.goto_database()
            except Exception as e:
                message = self.mainwid.Popup.ids.message
                self.mainwid.Popup.open()
                self.mainwid.Popup.title = "Data base error"
                # pass
                # if '' in registro:
                #     print("Uno o más campos están vacíos")
                # else:
                message.text = str(e)
                con.close()
    
    def delete_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute("DELETE FROM Productos WHERE ID="+self.data_id)
        con.commit()
        con.close()
        self.mainwid.goto_database()
    # def delete_data(self, confirm=False):
    #     if not confirm:
    #         # Si no se ha confirmado, muestra el popup de confirmación
    #         popup = ConfirmationPopup(update_data_wid=self)
    #         popup.title = "Confirmación de eliminación"
    #         message = popup.ids.message
    #         message.text = "¿Desea eliminar el registro?"
    #         popup.open()
    #     else:
    #         # Lógica de eliminación si se confirma
    #         con = sqlite3.connect(self.mainwid.DB_PATH)
    #         cursor = con.cursor()
    #         cursor.execute("DELETE FROM Productos WHERE ID=?", (self.data_id,))
    #         con.commit()
    #         con.close()
    #         self.mainwid.goto_database()

    
    def back_to_databasewid(self):
        self.mainwid.goto_database()
        

# class ConfirmationPopup(Popup):
#     def confirm(self):
#         self.dismiss()  # Cierra el popup
#         # Llama a la función delete_data en UpdateDataWid con confirmación de eliminar
#         self.parent.parent.delete_data(confirm=True)

class DataWid(BoxLayout):
    
    def __init__(self, mainwid, *args, **kwargs):
        super(DataWid, self).__init__(*args, **kwargs)
        self.mainwid = mainwid
    
    def update_data(self, data_id):
        self.mainwid.goto_update_data(data_id)
    

class NewDataButton(Button):
    
    def __init__(self, mainwid, *args, **kwargs):
        super(NewDataButton, self).__init__(*args, **kwargs)
        self.mainwid = mainwid
    
    # Crear nuevo producto 
    def create_new_product(self):
        self.mainwid.goto_insert_data()

class MainApp(App):
    title = "Inventario Simple"
    def build(self):
        return MainWid()


if __name__ == "__main__":
    MainApp().run()