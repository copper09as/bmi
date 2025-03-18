import json
def Save(data):
    with open('BmiData.json', 'w') as file_to_write:
        json.dump(data, file_to_write)

def Load():
    with open('BmiData.json', 'r') as file_to_read:
        result = json.load(file_to_read)
    return result
def Delete():
    result = []
    Save(result)
    return result
