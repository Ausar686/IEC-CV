from datetime import datetime


now = datetime.now()
s = f"{now.date()} {now.time()}\n"
with open("on_boot_time.txt", "a", encoding="utf-8") as file:
	file.write(s)