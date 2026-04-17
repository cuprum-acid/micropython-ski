print("Импорт модулей...")
try:
    from mpu9250 import MPU9250
    from mpu6500 import MPU6500
    print("[OK] Модули найдены и импортированы.")
except ImportError as e:
    print("[FAIL] Ошибка импорта:", e)

print("\nПроверка атрибутов MPU9250:")
print(dir(MPU9250))

# Создание файла с timestamp
# t = time.localtime()
# 
# timestamp = "{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(
#     t[0], t[1], t[2], t[3], t[4], t[5]
# )
# 
# filename = timestamp + ".txt"
# 
# with open(filename, "w") as f:
#     f.write("Timestamp: " + timestamp)
# 
# print("Created file:", filename)
