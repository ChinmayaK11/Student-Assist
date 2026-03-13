from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView

from firebase_config import ref


# ---------------- HOME SCREEN ----------------
class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20
        )

        title = MDLabel(
            text="StudentAssist",
            halign="center",
            font_style="H4"
        )

        add_btn = MDRaisedButton(
            text="Add Student",
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_add
        )

        view_btn = MDRaisedButton(
            text="View Students",
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_view
        )

        layout.add_widget(title)
        layout.add_widget(add_btn)
        layout.add_widget(view_btn)

        self.add_widget(layout)

    def go_to_add(self, instance):
        self.manager.current = "add"

    def go_to_view(self, instance):
        self.manager.current = "view"


# ---------------- ADD STUDENT SCREEN ----------------
class AddStudentScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        self.name_input = MDTextField(hint_text="Student Name")
        self.roll_input = MDTextField(hint_text="Roll Number")
        self.m1_input = MDTextField(hint_text="Marks 1")
        self.m2_input = MDTextField(hint_text="Marks 2")
        self.m3_input = MDTextField(hint_text="Marks 3")

        submit_btn = MDRaisedButton(
            text="Submit",
            pos_hint={"center_x": 0.5},
            on_release=self.submit
        )

        back_btn = MDRaisedButton(
            text="Back",
            pos_hint={"center_x": 0.5},
            on_release=self.go_back
        )

        layout.add_widget(self.name_input)
        layout.add_widget(self.roll_input)
        layout.add_widget(self.m1_input)
        layout.add_widget(self.m2_input)
        layout.add_widget(self.m3_input)
        layout.add_widget(submit_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def submit(self, instance):
        name = self.name_input.text
        roll = self.roll_input.text

        try:
            marks = [
                int(self.m1_input.text),
                int(self.m2_input.text),
                int(self.m3_input.text)
            ]
        except ValueError:
            print("Enter valid numeric marks")
            return

        percentage = round((sum(marks) / 300) * 100, 2)

        ref.push({
            "name": name,
            "roll": roll,
            "marks": marks,
            "percentage": percentage
        })

        print("Student saved to Firebase")

        # Clear fields after submit
        self.name_input.text = ""
        self.roll_input.text = ""
        self.m1_input.text = ""
        self.m2_input.text = ""
        self.m3_input.text = ""

    def go_back(self, instance):
        self.manager.current = "home"


# ---------------- VIEW STUDENTS SCREEN ----------------
class ViewStudentScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )

        title = MDLabel(
            text="Student Records",
            halign="center",
            font_style="H5"
        )

        self.scroll = MDScrollView()
        self.list_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        self.scroll.add_widget(self.list_layout)

        refresh_btn = MDRaisedButton(
            text="Refresh",
            pos_hint={"center_x": 0.5},
            on_release=self.load_data
        )

        back_btn = MDRaisedButton(
            text="Back",
            pos_hint={"center_x": 0.5},
            on_release=self.go_back
        )

        main_layout.add_widget(title)
        main_layout.add_widget(self.scroll)
        main_layout.add_widget(refresh_btn)
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)

    def load_data(self, instance=None):
        self.list_layout.clear_widgets()
        data = ref.get()

        if not data:
            self.list_layout.add_widget(
                MDLabel(text="No students found", halign="center")
            )
            return

        for _, student in data.items():
            text = f"{student['name']} | Roll: {student['roll']} | {student['percentage']}%"
            self.list_layout.add_widget(
                MDLabel(text=text, size_hint_y=None, height=30)
            )

    def go_back(self, instance):
        self.manager.current = "home"


# ---------------- APP ----------------
class StudentAssistApp(MDApp):
    def build(self):
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddStudentScreen(name="add"))
        sm.add_widget(ViewStudentScreen(name="view"))
        return sm


StudentAssistApp().run()

