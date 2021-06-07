import csv

with open('test.csv', encoding='utf-8-sig', mode='w') as csv_file:
    fieldnames = ['emp_name', 'dept', 'birth_month']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})


def touch_csv(filename):
    with open(f"{filename}.csv", "w") as file:
        pass

    
touch_csv('another')

# def write_to_csv(fieldnames, obj):
#     with open('')
#     writer = csv.DictWriter()