import os

with open('generate_report.py', 'r', encoding='utf-8') as f_orig:
    header = f_orig.read().split('def build_title_page()')[0]

with open('generate_report_body1.py', 'r', encoding='utf-8') as f2:
    b1 = f2.read()
with open('generate_report_body2.py', 'r', encoding='utf-8') as f3:
    b2 = f3.read()
with open('generate_report_body3.py', 'r', encoding='utf-8') as f4:
    b3 = f4.read()

with open('generate_report.py', 'w', encoding='utf-8') as f_out:
    f_out.write(header + '\n\n' + b1 + '\n\n' + b2 + '\n\n' + b3)

print("Merged successfully")
