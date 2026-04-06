from firebase_config import ref


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


def display_students():
    data = ref.get()

    if not data:
        print("No student data found.")
        return

    print("\n========== STUDENT RECORDS ==========")
    print(f"{'#':<4} {'Name':<20} {'Roll':<8} {'Marks':<18} {'%':<8} {'Grade':<6} {'Status'}")
    print("-" * 75)

    for idx, (key, student) in enumerate(data.items(), start=1):
        name     = student.get('name', 'N/A')
        roll     = student.get('roll', 'N/A')
        marks    = student.get('marks', [])
        pct      = student.get('percentage', 0)
        grade    = get_grade(pct)
        status   = "Pass" if pct >= 40 else "Fail"
        marks_str = str(marks) if marks else "N/A"

        print(f"{idx:<4} {name:<20} {roll:<8} {marks_str:<18} {pct:<8} {grade:<6} {status}")

    print("=" * 75)
    print(f"Total Students: {len(data)}")


if __name__ == "__main__":
    display_students()
