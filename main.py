from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar

from firebase_config import ref


# ---------------- GRADE HELPER ----------------
def get_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "F"


# ---------------- HOME SCREEN ----------------
class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(orientation="vertical", spacing=0)

        toolbar = MDTopAppBar(
            title="🎓 StudentAssist",
            md_bg_color=(0.2, 0.4, 0.8, 1)
        )

        content = MDBoxLayout(orientation="vertical", padding=30, spacing=16)

        stats_card = MDCard(
            orientation="vertical",
            padding=20,
            spacing=10,
            size_hint_y=None,
            height=140,
            md_bg_color=(0.95, 0.97, 1, 1),
            radius=[12]
        )

        self.count_label = MDLabel(
            text="👨‍🎓 Total Students: ...",
            halign="center",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0.2, 0.4, 0.8, 1)
        )

        self.pass_label = MDLabel(
            text="✅ Passed: 0  |  ❌ Failed: 0",
            halign="center",
            font_style="Subtitle1"
        )

        self.avg_label = MDLabel(
            text="📊 Class Average: 0%",
            halign="center",
            font_style="Subtitle1"
        )

        stats_card.add_widget(self.count_label)
        stats_card.add_widget(self.pass_label)
        stats_card.add_widget(self.avg_label)

        add_btn = MDRaisedButton(
            text="➕  Add Student",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.7, 0.4, 1),
            size_hint_x=0.8,
            on_release=self.go_to_add
        )

        view_btn = MDRaisedButton(
            text="📋  View Students",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.4, 0.8, 1),
            size_hint_x=0.8,
            on_release=self.go_to_view
        )

        search_btn = MDRaisedButton(
            text="🔍  Search Student",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.6, 0.2, 0.8, 1),
            size_hint_x=0.8,
            on_release=self.go_to_search
        )

        content.add_widget(stats_card)
        content.add_widget(add_btn)
        content.add_widget(view_btn)
        content.add_widget(search_btn)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)

    def on_enter(self):
        self.update_count()

    def update_count(self):
        data = ref.get()
        count = len(data) if data else 0
        self.count_label.text = f"👨‍🎓 Total Students: {count}"

        if data:
            passed = sum(1 for s in data.values() if s.get('percentage', 0) >= 40)
            failed = count - passed
            avg = round(sum(s.get('percentage', 0) for s in data.values()) / count, 2)
        else:
            passed, failed, avg = 0, 0, 0

        self.pass_label.text = f"✅ Passed: {passed}  |  ❌ Failed: {failed}"
        self.avg_label.text = f"📊 Class Average: {avg}%"

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

        layout = MDBoxLayout(orientation="vertical", spacing=0)

        toolbar = MDTopAppBar(
            title="➕ Add Student",
            md_bg_color=(0.2, 0.7, 0.4, 1)
        )

        content = MDBoxLayout(orientation="vertical", padding=30, spacing=14)

        self.name_input = MDTextField(hint_text="Student Name", icon_right="account")
        self.roll_input = MDTextField(hint_text="Roll Number", icon_right="identifier")
        self.m1_input = MDTextField(hint_text="Marks - Subject 1", icon_right="numeric-1-circle", input_filter="int")
        self.m2_input = MDTextField(hint_text="Marks - Subject 2", icon_right="numeric-2-circle", input_filter="int")
        self.m3_input = MDTextField(hint_text="Marks - Subject 3", icon_right="numeric-3-circle", input_filter="int")

        submit_btn = MDRaisedButton(
            text="💾  Save Student",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.7, 0.4, 1),
            size_hint_x=0.8,
            on_release=self.submit
        )

        back_btn = MDFlatButton(
            text="⬅  Back",
            pos_hint={"center_x": 0.5},
            on_release=self.go_back
        )

        content.add_widget(self.name_input)
        content.add_widget(self.roll_input)
        content.add_widget(self.m1_input)
        content.add_widget(self.m2_input)
        content.add_widget(self.m3_input)
        content.add_widget(submit_btn)
        content.add_widget(back_btn)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)

    def submit(self, instance):
        name = self.name_input.text.strip()
        roll = self.roll_input.text.strip()

        if not name or not roll:
            print("Name and Roll number are required!")
            return

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

        print("Student saved to Firebase!")

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
        main_layout = MDBoxLayout(orientation="vertical", spacing=0)

        toolbar = MDTopAppBar(
            title="📋 Student Records",
            md_bg_color=(0.2, 0.4, 0.8, 1)
        )

        content = MDBoxLayout(orientation="vertical", padding=20, spacing=10)

        self.scroll = MDScrollView()
        self.list_layout = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)

        btn_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)

        refresh_btn = MDRaisedButton(
            text="🔄 Refresh",
            md_bg_color=(0.2, 0.4, 0.8, 1),
            on_release=self.load_data
        )

        back_btn = MDFlatButton(text="⬅ Back", on_release=self.go_back)

        btn_row.add_widget(refresh_btn)
        btn_row.add_widget(back_btn)

        content.add_widget(self.scroll)
        content.add_widget(btn_row)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(content)

        self.add_widget(main_layout)

    def load_data(self, instance=None):
        self.list_layout.clear_widgets()
        data = ref.get()

        if not data:
            self.list_layout.add_widget(MDLabel(text="No students found", halign="center"))
            return

        for key, student in data.items():
            card = MDCard(
                orientation="horizontal",
                padding=12,
                spacing=10,
                size_hint_y=None,
                height=60,
                md_bg_color=(0.95, 0.97, 1, 1),
                radius=[8]
            )

            status = "✅" if student['percentage'] >= 40 else "❌"
            grade = get_grade(student['percentage'])
            text = f"{status} {student['name']}  |  Roll: {student['roll']}  |  {student['percentage']}%  |  Grade: {grade}"
            label = MDLabel(text=text, size_hint_x=0.8, font_style="Body2")

            delete_btn = MDRaisedButton(
                text="🗑",
                size_hint_x=0.2,
                md_bg_color=(0.9, 0.2, 0.2, 1),
                on_release=lambda inst, k=key: self.delete_student(k)
            )

            card.add_widget(label)
            card.add_widget(delete_btn)
            self.list_layout.add_widget(card)

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

        layout = MDBoxLayout(orientation="vertical", spacing=0)

        toolbar = MDTopAppBar(
            title="🔍 Search Student",
            md_bg_color=(0.6, 0.2, 0.8, 1)
        )

        content = MDBoxLayout(orientation="vertical", padding=30, spacing=16)

        self.search_input = MDTextField(hint_text="Enter Roll Number", icon_right="magnify")

        search_btn = MDRaisedButton(
            text="🔍  Search",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.6, 0.2, 0.8, 1),
            size_hint_x=0.8,
            on_release=self.search_student
        )

        self.result_card = MDCard(
            orientation="vertical",
            padding=20,
            size_hint_y=None,
            height=220,
            md_bg_color=(0.95, 0.97, 1, 1),
            radius=[12]
        )

        self.result_label = MDLabel(
            text="Search results will appear here...",
            halign="center",
            font_style="Body1"
        )

        self.result_card.add_widget(self.result_label)

        back_btn = MDFlatButton(
            text="⬅  Back",
            pos_hint={"center_x": 0.5},
            on_release=self.go_back
        )

        content.add_widget(self.search_input)
        content.add_widget(search_btn)
        content.add_widget(self.result_card)
        content.add_widget(back_btn)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)

    def search_student(self, instance):
        roll = self.search_input.text.strip()

        if not roll:
            self.result_label.text = "⚠️ Please enter a roll number!"
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
                grade = get_grade(student['percentage'])
                self.result_label.text = (
                    f"👤 Name: {student['name']}\n"
                    f"🔢 Roll: {student['roll']}\n"
                    f"📝 Marks: {marks}\n"
                    f"📊 Percentage: {student['percentage']}%\n"
                    f"🏅 Grade: {grade}\n"
                    f"Status: {status}"
                )
                found = True
                break

        if not found:
            self.result_label.text = f"❌ No student found with Roll No: {roll}"

    def go_back(self, instance):
        self.manager.current = "home"


# ---------------- APP ----------------
class StudentAssistApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddStudentScreen(name="add"))
        sm.add_widget(ViewStudentScreen(name="view"))
        sm.add_widget(SearchStudentScreen(name="search"))
        return sm


StudentAssistApp().run()
