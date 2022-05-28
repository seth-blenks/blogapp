create role publicuser login password '8d81d76459a6e0ec3484712b2732d7e292df690af0e57de361d02a0bfef2dbd3'
create role privateuser login password '94dde4d057e110378d45528bb9094e51809238f407b4d826a3288d331eef0550'
alter table "Like" rename to userlike;
alter table table_name owner to privateuser;/* Do this for all the table names available on the application */
