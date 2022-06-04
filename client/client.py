import os.path
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import funcs


class Client(App):
    """Client Graphics"""
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.7, 0.8)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.greeting = Label(text="Welcome to my FTPing!",
                              font_size=22, color='#00FFCE')
        self.window.add_widget(self.greeting)

        self.file_path = TextInput(
            text='Please type in the path of the file.', multiline=False, padding_y=(20, 20), size_hint=(1, 0.5))
        self.window.add_widget(self.file_path)

        self.file_name = TextInput(
            text='Please type in the name you wish to save the file as.', multiline=False, padding_y=(20, 20), size_hint=(1, 0.5))
        self.window.add_widget(self.file_name)

        self.button = Button(text="SEND", size_hint=(
            1, 0.5), bold=True, background_color='#00FFCE')
        self.button.bind(on_press=self.callback)
        self.window.add_widget(self.button)

        self.popup_content = Button(text='Please specify file name & file path!')
        self.popup = Popup(title='WARNING',
                      content=self.popup_content,
                      size_hint=(None, None), size=(400, 400))
        self.popup_content.bind(on_press=self.popup.dismiss)

        return self.window

    def callback(self, instance):
        """Launch the program"""
        if self.file_path.text and self.file_name.text and os.path.isfile(self.file_path.text):
            print('Launching...')
            funcs.launch(self.file_path.text, self.file_name.text)
        else:
            self.popup.open()


if __name__ == '__main__':
    Client().run()
