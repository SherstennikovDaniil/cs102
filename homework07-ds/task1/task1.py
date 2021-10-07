import typing as tp
from pprint import pprint

import psycopg2
import psycopg2.extras
from tabulate import tabulate

conn = psycopg2.connect("host=localhost port=5432 dbname=odscourse user=postgres password=secret")

cursor = conn.cursor()  # cursor_factory=psycopg2.extras.DictCursor)


def fetch_all(cursor: tp.Any) -> tp.List[tp.Dict[tp.Any, tp.Any]]:
    colnames = [desc[0] for desc in cursor.description]
    records = cursor.fetchall()
    return [{colname: value for colname, value in zip(colnames, record)} for record in records]


cursor.execute("SELECT * FROM adult_data LIMIT 5")
records = cursor.fetchall()
print(tabulate(records, "keys", "pqsl"))

print("Сколько мужчин и женщин (признак sex) представлено в этом наборе данных?")

cursor.execute(
    """
    SELECT sex, COUNT(*)
        FROM adult_data
        GROUP BY sex
    """
)
print(tabulate(fetch_all(cursor), "keys", "psql"))

print("Каков средний возраст (признак age) женщин?")

cursor.execute(
    """
    SELECT sex, AVG(age)
        FROM adult_data
    GROUP BY sex;
    """
)
print(tabulate(fetch_all(cursor), "keys", "psql"))

print("Какова доля граждан Германии (признак native-country)?")

cursor.execute("SELECT COUNT(*) FROM adult_data WHERE native_country = 'Germany'")
count = cursor.fetchall()[0][0]
cursor.execute("SELECT COUNT(*) FROM adult_data")
length = cursor.fetchall()[0][0]
print(count / length)

print(
    "Каковы средние значения и среднеквадратичные отклонения возраста тех, кто получает более 50K в год (признак salary) и тех, кто получает менее 50K в год?"
)

cursor.execute("SELECT AVG(age), STDDEV(age) FROM adult_data WHERE salary = '>50K'")
data_rich = cursor.fetchall()[0]
cursor.execute("SELECT AVG(age), STDDEV(age) FROM adult_data WHERE salary = '<=50K'")
data_poor = cursor.fetchall()[0]
print(f"Rich people average age: {data_rich[0]} +- {data_rich[1]}")
print(f"Poor people average age: {data_poor[0]} +- {data_poor[1]}")

print(
    "Правда ли, что люди, которые получают больше 50k, имеют как минимум высшее образование? (признак education - Bachelors, Prof-school, Assoc-acdm, Assoc-voc, Masters или Doctorate)?"
)

cursor.execute("SELECT DISTINCT education FROM adult_data WHERE salary = '>50K'")
data = [i[0] for i in cursor.fetchall()]
print(data)
print("Неверно.")

print(
    "Выведите статистику возраста для каждой расы (признак race) и каждого пола. Найдите таким образом максимальный возраст мужчин расы Amer-Indian-Eskimo."
)
cursor.execute("SELECT DISTINCT race, sex FROM adult_data")
data = cursor.fetchall()
for race, sex in data:
    print(f"Race: {race}, sex: {sex}")
    cursor.execute(
        f"SELECT COUNT(age), AVG(age), STDDEV(age), MIN(age), MAX(age) FROM adult_data WHERE race = '{race}' AND sex = '{sex}'"
    )
    description = list(cursor.fetchall()[0])
    cursor.execute(
        f"SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY age) FROM adult_data WHERE race = '{race}' AND sex = '{sex}'"
    )
    description.append(cursor.fetchall()[0][0])
    cursor.execute(
        f"SELECT PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY age) FROM adult_data WHERE race = '{race}' AND sex = '{sex}'"
    )
    description.append(cursor.fetchall()[0][0])
    cursor.execute(
        f"SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY age) FROM adult_data WHERE race = '{race}' AND sex = '{sex}'"
    )
    description.append(cursor.fetchall()[0][0])
    print(f"Count: {description[0]}")
    print(f"Average: {description[1]}")
    print(f"Standard deviation: {description[2]}")
    print(f"Minimum: {description[3]}")
    print(f"Maximum: {description[4]}")
    print(f"25%: {description[5]}")
    print(f"50%: {description[6]}")
    print(f"75%: {description[7]}")

print(
    "Среди кого больше доля зарабатывающих много (>50K): среди женатых или холостых мужчин (признак marital-status)? Женатыми считаем тех, у кого marital-status начинается с Married (Married-civ-spouse, Married-spouse-absent или Married-AF-spouse), остальных считаем холостыми."
)
cursor.execute(
    "SELECT salary, COUNT(*) FROM adult_data WHERE sex = 'Male' AND marital_status LIKE '%Married%' GROUP BY salary;"
)
print(tabulate(fetch_all(cursor), "keys", "psql"))
cursor.execute(
    "SELECT salary, COUNT(*) FROM adult_data WHERE sex = 'Male' AND marital_status IN ('Never-married', 'Separated', 'Divorced') GROUP BY salary;"
)
print(tabulate(fetch_all(cursor), "keys", "psql"))
cursor.execute(
    "SELECT marital_status, COUNT(marital_status) FROM adult_data GROUP BY marital_status;"
)
print(tabulate(fetch_all(cursor), "keys", "psql"))
print("Среди женатых мужчин доля зарабатывающих >50K больше.")

print(
    "Какое максимальное число часов человек работает в неделю (признак *hours-per-week*)? Сколько людей работают такое количество часов и каков среди них процент зарабатывающих много?"
)
cursor.execute("SELECT MAX(hours_per_week) FROM adult_data;")
max_working_hours = cursor.fetchall()[0][0]
cursor.execute(f"SELECT COUNT(*) FROM adult_data WHERE hours_per_week = {max_working_hours}")
workers = cursor.fetchall()[0][0]
cursor.execute(
    f"SELECT COUNT(*) FROM adult_data WHERE hours_per_week = {max_working_hours} AND salary = '>50K'"
)
earnings_share = cursor.fetchall()[0][0] / workers
print(f"Largest workload: {max_working_hours} hrs per week")
print(f"{workers} workers work maximum hours")
print(f"Rich share: {100 * earnings_share}%")

print(
    "Посчитайте среднее время работы (hours-per-week) зарабатывающих мало и много (salary) для каждой страны (native-country)."
)
cursor.execute(
    "SELECT native_country, AVG(hours_per_week), salary FROM adult_data GROUP BY native_country, salary ORDER BY native_country ASC, salary ASC;"
)
print(tabulate(fetch_all(cursor), "keys", "psql"))
