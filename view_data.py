from firebase_config import ref

data = ref.get()

if data:
    for key, value in data.items():
        print(value)
else:
    print("No student data found")
