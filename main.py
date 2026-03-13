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

        search_btn = MDRaisedButton(
            text="Search Student",
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_search
        )

        layout.add_widget(title)
        layout.add_widget(add_btn)
        layout.add_widget(view_btn)
        layout.add_widget(search_btn)

        self.add_widget(layout)

    def go_to_add(self, instance):
        self.manager.current = "add"

    def go_to_view(self, instance):
        self.manager.current = "view"

    def go_to_search(self, instance):
        self.manager.current = "search"


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

        for key, student in data.items():
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=40,
                spacing=10
            )

            status = "✅ Pass" if student['percentage'] >= 40 else "❌ Fail"
            text = f"{student['name']} | Roll: {student['roll']} | {student['percentage']}% | {status}"
            label = MDLabel(text=text, size_hint_x=0.8)

            delete_btn = MDRaisedButton(
                text="Delete",
                size_hint_x=0.2,
                on_release=lambda inst, k=key: self.delete_student(k)
            )

            row.add_widget(label)
            row.add_widget(delete_btn)
            self.list_layout.add_widget(row)

    def delete_student(self, key):
        ref.child(key).delete()
        print(f"Student {key} deleted")
        self.load_data()

    def go_back(self, instance):
        self.manager.current = "home"


# ---------------- SEARCH STUDENT SCREEN ----------------
class SearchStudentScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = MDLabel(
            text="Search Student",
            halign="center",
            font_style="H5"
        )

        self.search_input = MDTextField(hint_text="Enter Roll Number")

        search_btn = MDRaisedButton(
            text="Search",
            pos_hint={"center_x": 0.5},
            on_release=self.search_student
        )

        self.result_label = MDLabel(
            text="",
            halign="center",
            size_hint_y=None,
            height=200
        )

        back_btn = MDRaisedButton(
            text="Back",
            pos_hint={"center_x": 0.5},
            on_release=self.go_back
        )

        layout.add_widget(title)
        layout.add_widget(self.search_input)
        layout.add_widget(search_btn)
        layout.add_widget(self.result_label)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def search_student(self, instance):
        roll = self.search_input.text.strip()

        if not roll:
            self.result_label.text = "Please enter a roll number!"
            return

        data = ref.get()

        if not data:
            self.result_label.text = "No students found in database."
            return

        found = False
        for key, student in data.items():
            if student['roll'] == roll:
                marks = student.get('marks', [])
                status = "✅ Pass" if student['percentage'] >= 40 else "❌ Fail"
                self.result_label.text = (
                    f"Name: {student['name']}\n"
                    f"Roll: {student['roll']}\n"
                    f"Marks: {marks}\n"
                    f"Percentage: {student['percentage']}%\n"
                    f"Status: {status}"
                )
                found = True
                break

        if not found:
            self.result_label.text = f"No student found with Roll No: {roll}"

    def go_back(self, instance):
        self.manager.current = "home"


# ---------------- APP ----------------
class StudentAssistApp(MDApp):
    def build(self):
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddStudentScreen(name="add"))
        sm.add_widget(ViewStudentScreen(name="view"))
        sm.add_widget(SearchStudentScreen(name="search"))
        return sm


StudentAssistApp().run()
