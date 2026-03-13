from firebase_config import ref

ref.push({
    "name": "Test Student",
    "roll": "001",
    "marks": [80, 75, 90],
    "percentage": 81.67
})

print("Firebase connection working!")
