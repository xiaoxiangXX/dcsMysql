import pymysql
import random
import string
import time

def generate_random_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def generate_data():
    supplier_codes = {
        "华晨科技": "7iE2w9vF",
    }
    suppliers = ['华晨科技']
    products = {
        '华晨科技': ['CHIP-908', 'CHIP-X3090', 'CHIP-4090', 'CHIP-P60']
    }
    product_categories = ['电子产品', '机械设备', '化工材料']
    product_specifications = ['规格A', '规格B', '规格C', '规格D']
    warehouse_codes = ['WH001', 'WH002', 'WH003']

    # 随机生成
    product_category = random.choice(product_categories)
    product_specification = random.choice(product_specifications)
    supplier_name = random.choice(suppliers)
    product_code = random.choice(products[supplier_name])
    supplier_code = supplier_codes[supplier_name]
    warehouse_code = random.choice(warehouse_codes)
    # 生成1000到50000之间以千位单位的整数
    plan_quantity = round(random.randint(1, 50) * 1000)


    # 生成real_production_quantity 值
    if random.random() < 0.1:
        real_production_quantity = plan_quantity - random.randint(1, 100)
    else:
        real_production_quantity = plan_quantity

    min_inventory = 500
    max_inventory = 500000
    unit = '个'

    # 连接到MySQL服务器
    connection = pymysql.connect(host='10.30.5.3',
                                 port=3306,
                                 user='dcsUser',
                                 password='dcs@123',
                                 database='dcs')
    cursor = connection.cursor()

    # 获取当前产品的库存
    cursor.execute("SELECT inventorv_quantity FROM repertory WHERE product_code = %s ORDER BY id DESC LIMIT 1", (product_code,))
    current_inventory = cursor.fetchone()
    current_inventory = current_inventory[0] if current_inventory else 0

    # 判断库存是否超过最大库存
    if current_inventory + real_production_quantity > max_inventory:
        # 如果超过最大库存，则出库超过最大库存的所有数量 + 最大库存的一半
        excess_quantity = (current_inventory + real_production_quantity) - max_inventory
        outgoing_quantity = excess_quantity + max_inventory // 2
        updated_inventory = current_inventory - outgoing_quantity
    else:
    # 如果没有超过最大库存，则出库数量为1000到50000之间的整数，但不能大于剩余库存
        outgoing_quantity = min(random.randint(1000, 50000), current_inventory)
        updated_inventory = current_inventory - outgoing_quantity

    # 插入数据
    sql = "INSERT INTO repertory (supplier_name, supplier_code, product_code, plan_quantity, real_production_quantity, inventorv_quantity, product_category, product_specification, min_inventory, max_inventory, warehouse_code, unit, incoming_quantity, outgoing_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (supplier_name, supplier_code, product_code, plan_quantity, real_production_quantity, updated_inventory, product_category, product_specification, min_inventory, max_inventory, warehouse_code, unit, real_production_quantity, outgoing_quantity)
    cursor.execute(sql, val)

    # 关闭连接
    connection.commit()
    connection.close()

next_run = 1

def job():
    global next_run 
    generate_data()
    next_run = random.randint(1, 20)  # 1 到 20 之间的随机数
    print(f"下次执行将在 {next_run} 分钟后")

# 设置定时任务
while True:
    job()
    time.sleep(next_run * 60)
