import csv
import os
from datetime import datetime
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
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

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


# ---------------- ATTENDANCE HELPER ----------------
def _calc_attendance(student):
    """Returns (present_days, total_days, attend_pct) for a student dict.
    Returns (0, 0, 0.0) if no attendance data exists.
    """
    attendance = student.get('attendance', {})
    if not attendance:
        return 0, 0, 0.0
    total_days   = len(attendance)
    present_days = sum(1 for v in attendance.values() if v == "Present")
    attend_pct   = round((present_days / total_days) * 100, 1)
    return present_days, total_days, attend_pct


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
            height=175,
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

        self.top_label = MDLabel(
            text="🏆 Top Scorer: ...",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(0.8, 0.5, 0.0, 1)
        )

        stats_card.add_widget(self.count_label)
        stats_card.add_widget(self.pass_label)
        stats_card.add_widget(self.avg_label)
        stats_card.add_widget(self.top_label)

        add_btn = MDRaisedButton(
            text="➕  Add Student",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.7, 0.4, 1),
            size_hint_x=0.8,
            on_release=self.go_to_add
        )

        self.view_btn = MDRaisedButton(
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

        dark_btn = MDRaisedButton(
            text="🌙  Dark Mode",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.15, 0.15, 0.15, 1),
            size_hint_x=0.8,
            on_release=self.toggle_dark_mode
        )

        about_btn = MDRaisedButton(
            text="ℹ️  About",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.4, 0.4, 0.4, 1),
            size_hint_x=0.8,
            on_release=self.go_to_about
        )

        attend_btn = MDRaisedButton(
            text="📅  Attendance",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.8, 0.3, 0.1, 1),
            size_hint_x=0.8,
            on_release=self.go_to_attendance
        )

        content.add_widget(stats_card)
        content.add_widget(add_btn)
        content.add_widget(self.view_btn)
        content.add_widget(search_btn)
        content.add_widget(attend_btn)
        content.add_widget(dark_btn)
        content.add_widget(about_btn)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)

    def on_enter(self):
        self.update_count()

    def toggle_dark_mode(self, instance):
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            app.theme_cls.theme_style = "Dark"
            instance.text = "☀️  Light Mode"
            instance.md_bg_color = (0.3, 0.3, 0.3, 1)
        else:
            app.theme_cls.theme_style = "Light"
            instance.text = "🌙  Dark Mode"
            instance.md_bg_color = (0.15, 0.15, 0.15, 1)

    def update_count(self):
        data = ref.get()
        count = len(data) if data else 0
        self.count_label.text = f"👨‍🎓 Total Students: {count}"
        self.view_btn.text = f"📋  View Students  ({count})"

        if data:
            passed = sum(1 for s in data.values() if s.get('percentage', 0) >= 40)
            failed = count - passed
            avg = round(sum(s.get('percentage', 0) for s in data.values()) / count, 2)
            top = max(data.values(), key=lambda s: s.get('percentage', 0))
            self.top_label.text = f"🏆 Top Scorer: {top['name']} ({top['percentage']}%)"
        else:
            passed, failed, avg = 0, 0, 0
            self.top_label.text = "🏆 Top Scorer: N/A"

        self.pass_label.text = f"✅ Passed: {passed}  |  ❌ Failed: {failed}"
        self.avg_label.text = f"📊 Class Average: {avg}%"

    def go_to_add(self, instance):
        self.manager.current = "add"

    def go_to_view(self, instance):
        self.manager.current = "view"

    def go_to_search(self, instance):
        self.manager.current = "search"

    def go_to_about(self, instance):
        self.manager.current = "about"

    def go_to_attendance(self, instance):
        self.manager.current = "attendance"


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

        self.error_label = MDLabel(
            text="",
            halign="center",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.9, 0.2, 0.2, 1),
            size_hint_y=None,
            height=30
        )

        self.success_label = MDLabel(
            text="",
            halign="center",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.1, 0.7, 0.3, 1),
            size_hint_y=None,
            height=30
        )

        content.add_widget(self.name_input)
        content.add_widget(self.roll_input)
        content.add_widget(self.m1_input)
        content.add_widget(self.m2_input)
        content.add_widget(self.m3_input)
        content.add_widget(self.error_label)
        content.add_widget(self.success_label)
        content.add_widget(submit_btn)
        content.add_widget(back_btn)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)

    def submit(self, instance):
        name = self.name_input.text.strip()
        roll = self.roll_input.text.strip()
        self.error_label.text = ""
        self.success_label.text = ""

        # Highlight empty fields in red
        self.name_input.line_color_focus = (0.9, 0.2, 0.2, 1) if not name else (0.2, 0.7, 0.4, 1)
        self.roll_input.line_color_focus = (0.9, 0.2, 0.2, 1) if not roll else (0.2, 0.7, 0.4, 1)
        self.m1_input.line_color_focus = (0.9, 0.2, 0.2, 1) if not self.m1_input.text else (0.2, 0.7, 0.4, 1)
        self.m2_input.line_color_focus = (0.9, 0.2, 0.2, 1) if not self.m2_input.text else (0.2, 0.7, 0.4, 1)
        self.m3_input.line_color_focus = (0.9, 0.2, 0.2, 1) if not self.m3_input.text else (0.2, 0.7, 0.4, 1)

        # Validate name
        if not name:
            self.error_label.text = "⚠️ Student name cannot be empty!"
            return

        # Validate name — only letters and spaces
        if not all(c.isalpha() or c.isspace() for c in name):
            self.error_label.text = "⚠️ Name should contain only letters!"
            return

        # Validate roll
        if not roll:
            self.error_label.text = "⚠️ Roll number cannot be empty!"
            return

        # Validate marks
        if not self.m1_input.text or not self.m2_input.text or not self.m3_input.text:
            self.error_label.text = "⚠️ Please enter all 3 subject marks!"
            return

        try:
            marks = [
                int(self.m1_input.text),
                int(self.m2_input.text),
                int(self.m3_input.text)
            ]
        except ValueError:
            self.error_label.text = "⚠️ Marks must be valid numbers!"
            return

        # Validate marks range
        if any(m < 0 or m > 100 for m in marks):
            self.error_label.text = "⚠️ Marks must be between 0 and 100!"
            return

        # All good — clear errors
        self.error_label.text = ""
        percentage = round((sum(marks) / 300) * 100, 2)
        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

        ref.push({
            "name": name,
            "roll": roll,
            "marks": marks,
            "percentage": percentage,
            "added_on": timestamp
        })

        self.success_label.text = f"✅ {name} saved successfully!"

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

        self.sort_btn = MDRaisedButton(
            text="⬆ Sort: High",
            md_bg_color=(0.2, 0.6, 0.5, 1),
            on_release=self.toggle_sort
        )

        export_btn = MDRaisedButton(
            text="📤 Export CSV",
            md_bg_color=(0.8, 0.4, 0.0, 1),
            on_release=self.export_csv
        )

        back_btn = MDFlatButton(text="⬅ Back", on_release=self.go_back)

        btn_row.add_widget(refresh_btn)
        btn_row.add_widget(self.sort_btn)
        btn_row.add_widget(export_btn)
        btn_row.add_widget(back_btn)

        content.add_widget(self.scroll)
        content.add_widget(btn_row)

        main_layout.add_widget(toolbar)
        main_layout.add_widget(content)

        self.add_widget(main_layout)
        self.sort_order = "high"

    def toggle_sort(self, instance):
        if self.sort_order == "high":
            self.sort_order = "low"
            self.sort_btn.text = "⬇ Sort: Low"
        else:
            self.sort_order = "high"
            self.sort_btn.text = "⬆ Sort: High"
        self.load_data()

    def load_data(self, instance=None):
        self.list_layout.clear_widgets()
        data = ref.get()

        if not data:
            self.list_layout.add_widget(MDLabel(text="No students found", halign="center"))
            return

        reverse = self.sort_order == "high"
        sorted_students = sorted(data.items(), key=lambda x: x[1].get('percentage', 0), reverse=reverse)

        for rank, (key, student) in enumerate(sorted(data.items(), key=lambda x: x[1].get('percentage', 0), reverse=True), start=1):
            # Assign rank medal
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"#{rank}"

            status = "✅" if student['percentage'] >= 40 else "❌"
            grade = get_grade(student['percentage'])

            # use shared helper — fixes duplicate MDCard creation that was here before
            present_days, total_days, attend_pct = _calc_attendance(student)
            if total_days > 0:
                if attend_pct < 75:
                    attend_str = f"⚠️ {attend_pct}% LOW"
                    card_color = (1.0, 0.95, 0.90, 1)
                else:
                    attend_str = f"📅 {attend_pct}%"
                    card_color = (0.95, 0.97, 1, 1)
            else:
                attend_str = "📅 N/A"
                card_color = (0.95, 0.97, 1, 1)

            card = MDCard(
                orientation="horizontal",
                padding=12,
                spacing=10,
                size_hint_y=None,
                height=60,
                md_bg_color=card_color,
                radius=[8]
            )

            text = f"{medal} {status} {student['name']}  |  Roll: {student['roll']}  |  {student['percentage']}%  |  Grade: {grade}  |  {attend_str}"
            label = MDLabel(text=text, size_hint_x=0.8, font_style="Body2")

            delete_btn = MDRaisedButton(
                text="🗑",
                size_hint_x=0.2,
                md_bg_color=(0.9, 0.2, 0.2, 1),
                on_release=lambda inst, k=key, n=student['name']: self.confirm_delete(k, n)
            )

            card.add_widget(label)
            card.add_widget(delete_btn)
            self.list_layout.add_widget(card)

    def export_csv(self, instance=None):
        data = ref.get()

        if not data:
            print("No data to export!")
            return

        filepath = os.path.expanduser("~/Desktop/students_export.csv")

        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Name", "Roll", "Marks", "Percentage", "Grade", "Status"])
            for _, student in data.items():
                grade = get_grade(student.get('percentage', 0))
                status = "Pass" if student.get('percentage', 0) >= 40 else "Fail"
                writer.writerow([
                    student.get('name', ''),
                    student.get('roll', ''),
                    str(student.get('marks', [])),
                    student.get('percentage', ''),
                    grade,
                    status
                ])

        print(f"✅ Exported to {filepath}")

    def confirm_delete(self, key, name):
        self.dialog = MDDialog(
            title="🗑 Delete Student?",
            text=f"Are you sure you want to delete [b]{name}[/b]? This cannot be undone!",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.delete_student(key)
                ),
            ],
        )
        self.dialog.open()

    def delete_student(self, key):
        if hasattr(self, 'dialog'):
            self.dialog.dismiss()
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

        self.remarks_input = MDTextField(
            hint_text="Add/update remarks for this student...",
            icon_right="note-edit"
        )

        save_remarks_btn = MDRaisedButton(
            text="💾 Save Remarks",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.6, 0.2, 0.8, 1),
            size_hint_x=0.8,
            on_release=self.save_remarks
        )

        back_btn = MDFlatButton(
            text="⬅  Back",
            pos_hint={"center_x": 0.5},
            on_release=self.go_back
        )

        content.add_widget(self.search_input)
        content.add_widget(search_btn)
        content.add_widget(self.result_card)
        content.add_widget(self.remarks_input)
        content.add_widget(save_remarks_btn)
        content.add_widget(back_btn)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)
        self.current_key = None

    def save_remarks(self, instance):
        if not self.current_key:
            return
        remarks = self.remarks_input.text.strip()
        if not remarks:
            return
        ref.child(self.current_key).update({"remarks": remarks})
        self.remarks_input.text = ""
        self.result_label.text += f"\n✅ Remarks saved: {remarks}"

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
                added_on = student.get('added_on', 'N/A')

                # Calculate attendance percentage using shared helper
                present_days, total_days, attend_pct = _calc_attendance(student)
                if total_days > 0:
                    if attend_pct < 75:
                        attend_str = f"⚠️ {present_days}/{total_days} days ({attend_pct}%) — LOW ATTENDANCE!"
                    else:
                        attend_str = f"{present_days}/{total_days} days ({attend_pct}%)"
                else:
                    attend_str = "No attendance recorded"

                self.result_label.text = (
                    f"👤 Name: {student['name']}\n"
                    f"🔢 Roll: {student['roll']}\n"
                    f"📝 Marks: {marks}\n"
                    f"📊 Percentage: {student['percentage']}%\n"
                    f"🏅 Grade: {grade}\n"
                    f"Status: {status}\n"
                    f"📅 Attendance: {attend_str}\n"
                    f"🗒️ Remarks: {student.get('remarks', 'No remarks added')}\n"
                    f"🕒 Added on: {added_on}"
                )
                self.current_key = key
                found = True
                break

        if not found:
            self.result_label.text = f"❌ No student found with Roll No: {roll}"

    def go_back(self, instance):
        self.manager.current = "home"


# ---------------- ABOUT SCREEN ----------------
class AboutScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(orientation="vertical", spacing=0)

        toolbar = MDTopAppBar(
            title="ℹ️ About",
            md_bg_color=(0.4, 0.4, 0.4, 1)
        )

        content = MDBoxLayout(orientation="vertical", padding=30, spacing=20)

        card = MDCard(
            orientation="vertical",
            padding=24,
            spacing=14,
            size_hint_y=None,
            height=380,
            md_bg_color=(0.95, 0.97, 1, 1),
            radius=[12]
        )

        card.add_widget(MDLabel(
            text="🎓 StudentAssist",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(0.2, 0.4, 0.8, 1)
        ))
        card.add_widget(MDLabel(
            text="Version 1.0.0",
            halign="center",
            font_style="Subtitle2"
        ))
        card.add_widget(MDLabel(
            text="──────────────────────",
            halign="center"
        ))
        card.add_widget(MDLabel(
            text="A student record management app\nbuilt with KivyMD & Firebase.",
            halign="center",
            font_style="Body1"
        ))
        card.add_widget(MDLabel(
            text="👨‍💻 Developed by\nChinmaya Kagolli",
            halign="center",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 0.4, 1)
        ))
        card.add_widget(MDLabel(
            text="🛠 Built with\nPython • KivyMD • Firebase",
            halign="center",
            font_style="Caption"
        ))

        back_btn = MDRaisedButton(
            text="⬅  Back to Home",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.4, 0.8, 1),
            size_hint_x=0.8,
            on_release=self.go_back
        )

        content.add_widget(card)
        content.add_widget(back_btn)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "home"


# ---------------- ATTENDANCE SCREEN ----------------
class AttendanceScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=0)

        toolbar = MDTopAppBar(
            title="📅 Attendance Tracker",
            md_bg_color=(0.8, 0.3, 0.1, 1)
        )

        content = MDBoxLayout(orientation="vertical", padding=20, spacing=10)

        self.date_label = MDLabel(
            text=f"📆 Date: {__import__('datetime').date.today().strftime('%d %b %Y')}",
            halign="center",
            font_style="H6"
        )

        self.scroll = MDScrollView()
        self.list_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)

        btn_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)

        load_btn = MDRaisedButton(
            text="🔄 Load Students",
            md_bg_color=(0.8, 0.3, 0.1, 1),
            on_release=self.load_students
        )

        save_btn = MDRaisedButton(
            text="💾 Save",
            md_bg_color=(0.2, 0.7, 0.4, 1),
            on_release=self.save_attendance
        )

        back_btn = MDFlatButton(text="⬅ Back", on_release=self.go_back)

        btn_row.add_widget(load_btn)
        btn_row.add_widget(save_btn)

        history_btn = MDRaisedButton(
            text="📜 History",
            md_bg_color=(0.3, 0.3, 0.7, 1),
            on_release=self.go_to_history
        )

        btn_row.add_widget(history_btn)
        btn_row.add_widget(back_btn)

        self.status_label = MDLabel(
            text="",
            halign="center",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.2, 0.7, 0.4, 1),
            size_hint_y=None,
            height=30
        )

        content.add_widget(self.date_label)
        content.add_widget(self.scroll)
        content.add_widget(self.status_label)
        content.add_widget(btn_row)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)
        self.attendance_map = {}

    def load_students(self, instance=None):
        self.list_layout.clear_widgets()
        self.attendance_map = {}
        data = ref.get()

        if not data:
            self.list_layout.add_widget(MDLabel(text="No students found", halign="center"))
            return

        for key, student in data.items():
            self.attendance_map[key] = "Present"

            row = MDCard(
                orientation="horizontal",
                padding=12,
                spacing=10,
                size_hint_y=None,
                height=55,
                md_bg_color=(0.95, 0.97, 1, 1),
                radius=[8]
            )

            label = MDLabel(
                text=f"👤 {student['name']}  |  Roll: {student['roll']}",
                size_hint_x=0.65,
                font_style="Body2"
            )

            toggle_btn = MDRaisedButton(
                text="✅ Present",
                size_hint_x=0.35,
                md_bg_color=(0.2, 0.7, 0.4, 1),
                on_release=lambda inst, k=key: self.toggle_attendance(inst, k)
            )

            row.add_widget(label)
            row.add_widget(toggle_btn)
            self.list_layout.add_widget(row)

    def toggle_attendance(self, btn, key):
        if self.attendance_map[key] == "Present":
            self.attendance_map[key] = "Absent"
            btn.text = "❌ Absent"
            btn.md_bg_color = (0.9, 0.2, 0.2, 1)
        else:
            self.attendance_map[key] = "Present"
            btn.text = "✅ Present"
            btn.md_bg_color = (0.2, 0.7, 0.4, 1)

    def save_attendance(self, instance=None):
        if not self.attendance_map:
            self.status_label.text = "⚠️ Load students first!"
            return

        today = __import__('datetime').date.today().strftime('%Y-%m-%d')
        present = sum(1 for v in self.attendance_map.values() if v == "Present")
        total = len(self.attendance_map)

        for key, status in self.attendance_map.items():
            ref.child(key).child("attendance").child(today).set(status)

        self.status_label.text = f"✅ Saved! Present: {present}/{total}"

    def go_back(self, instance):
        self.manager.current = "home"

    def go_to_history(self, instance):
        self.manager.current = "attendance_history"


# ---------------- ATTENDANCE HISTORY SCREEN ----------------
class AttendanceHistoryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=0)

        toolbar = MDTopAppBar(
            title="📜 Attendance History",
            md_bg_color=(0.3, 0.3, 0.7, 1)
        )

        content = MDBoxLayout(orientation="vertical", padding=20, spacing=10)

        self.scroll = MDScrollView()
        self.list_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)

        btn_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)

        refresh_btn = MDRaisedButton(
            text="🔄 Load",
            md_bg_color=(0.3, 0.3, 0.7, 1),
            on_release=self.load_history
        )

        back_btn = MDFlatButton(text="⬅ Back", on_release=self.go_back)

        btn_row.add_widget(refresh_btn)
        btn_row.add_widget(back_btn)

        content.add_widget(self.scroll)
        content.add_widget(btn_row)

        layout.add_widget(toolbar)
        layout.add_widget(content)

        self.add_widget(layout)

    def on_enter(self):
        self.load_history()

    def load_history(self, instance=None):
        self.list_layout.clear_widgets()
        data = ref.get()

        if not data:
            self.list_layout.add_widget(MDLabel(text="No students found", halign="center"))
            return

        for key, student in data.items():
            attendance = student.get('attendance', {})

            # Header card per student
            header = MDCard(
                orientation="vertical",
                padding=12,
                spacing=6,
                size_hint_y=None,
                md_bg_color=(0.85, 0.90, 1.0, 1),
                radius=[8]
            )

            if attendance:
                present_days, total_days, attend_pct = _calc_attendance(student)
                warn = " ⚠️ LOW" if attend_pct < 75 else ""
                summary = f"{student['name']} | Roll: {student['roll']} | {present_days}/{total_days} days ({attend_pct}%){warn}"
                header.height = 40 + (len(attendance) * 28)

                header.add_widget(MDLabel(
                    text=summary,
                    halign="left",
                    font_style="Body2",
                    size_hint_y=None,
                    height=36
                ))

                for date, status in sorted(attendance.items()):
                    icon = "✅" if status == "Present" else "❌"
                    header.add_widget(MDLabel(
                        text=f"   {icon} {date} — {status}",
                        halign="left",
                        font_style="Caption",
                        size_hint_y=None,
                        height=26
                    ))
            else:
                header.height = 40
                header.add_widget(MDLabel(
                    text=f"{student['name']} | Roll: {student['roll']} — No attendance recorded",
                    halign="left",
                    font_style="Body2",
                    size_hint_y=None,
                    height=36
                ))

            self.list_layout.add_widget(header)

    def go_back(self, instance):
        self.manager.current = "attendance"
class StudentAssistApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddStudentScreen(name="add"))
        sm.add_widget(ViewStudentScreen(name="view"))
        sm.add_widget(SearchStudentScreen(name="search"))
        sm.add_widget(AboutScreen(name="about"))
        sm.add_widget(AttendanceScreen(name="attendance"))
        sm.add_widget(AttendanceHistoryScreen(name="attendance_history"))
        return sm


StudentAssistApp().run()
