from faker import Faker
import psycopg2
import random
from datetime import datetime
import psycopg2
from uuid import uuid4

conn = psycopg2.connect('dbname=secury user=privateuser password=private host=localhost port=5432')
cursor = conn.cursor()
fake = Faker()

for a in range(200):
	title = fake.text()[:15] + ' ' + uuid4().hex
	description = fake.text()
	content = fake.text() * 5
	reads = a
	date = datetime.now()
	update = datetime.now()
	category_id = random.choice([1,2])
	image_id = random.choice([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
	cursor.execute('insert into blogpost(title, description, content, reads, creation_date, updated_date, user_id, image_id, category_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',(title, description, content, reads, date,update, 1, image_id,category_id))
conn.commit()

for a in range(1,200):
	tag = random.choice([1,2,3])
	cursor.execute('insert into blogpost_to_tags(blogpost_id, tag_id) values(%s,%s)',(a,tag))

conn.commit()



print('Done')