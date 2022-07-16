create table if not exists record(
	id serial primary key,
	address varchar(225),
	"date" date
);

create table if not exists role(
	id serial primary key,
	name varchar(32) unique,
	permission integer
);

create table if not exists userdetails(
	id serial primary key,
	fullname varchar(112),
	about text,
	company varchar(112),
	job varchar(112),
	country varchar(112),
	address varchar(112),
	phone varchar(112),
	twitter_profile varchar(112),
	facebook_profile varchar(112),
	instagram_profile varchar(112),
	linkedin_profile varchar(112)
);


create table if not exists webuser(
	id serial primary key,
	username varchar(112),
	email varchar(112),
	authenticated bool default false,
	admin_authenticated bool default false,
	restricted bool default false,
	user_app_id varchar(75) unique,
	confirm bool default false,
	image_url varchar(225),
	_password varchar(225),
	role_id integer references role (id),
	userdetails_id integer unique references userdetails(id)
);



create table if not exists image(
	id serial primary key,
	name varchar(225),
	user_id integer references webuser(id) on delete cascade
);

create table if not exists category(
	id serial primary key,
	name varchar(32) unique
);

create table if not exists tag(
	id serial primary key,
	name varchar(32) unique
);

create table if not exists blogpost(
	id serial primary key,
	title varchar(150) unique,
	description varchar(225),
	search tsvector,
	content text,
	reads integer default 0,
	creation_date timestamp,
	updated_date timestamp,
	image_id integer references image(id),
	user_id integer references webuser(id) on delete cascade,
	category_id integer references category(id) on delete cascade
);




create table if not exists blogpost_to_tags(
	id serial primary key,
	blogpost_id integer references blogpost (id),
	tag_id integer references tag(id)
);

create table if not exists comment(
	id serial primary key,
	comment text not null,
	seen bool default false,
	post_id integer references blogpost(id) on delete cascade,
	user_id integer references webuser(id) on delete cascade,
	"date" timestamp not null
);

create table if not exists notification(
	id serial primary key,
	name varchar(122) not null,
	message text not null,
	"date" timestamp not null,
	seen bool default false,
	link text,
	notification_type integer
);

/* make all sequences editable */
grant usage, select on all sequences in schema public to publicuser;


/* blogpost permissions */
grant update on blogpost to publicuser;
grant select on blogpost to publicuser;
grant insert on blogpost to publicuser;


/* notification permissions */
grant insert on notification to publicuser;

/* webuser permissions */
grant update on webuser to publicuser;
grant insert on webuser to publicuser;
grant delete on webuser to publicuser;
grant select on webuser to publicuser;

/* comment permissions */
grant select on comment to publicuser;
grant delete on comment to publicuser;
grant update on comment to publicuser;
grant insert on comment to publicuser;

/*  image permissions */
grant select on image to publicuser;

/* tag permissions */
grant select on tag to publicuser;
grant select on category to publicuser;
grant select on role to publicuser;


GRANT SELECT on blogpost_to_tags, notification, tag, category,image, role, userdetails,record to publicuser;
GRANT UPDATE,INSERT,DELETE on  userdetails to publicuser;


CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE ON blogpost FOR EACH ROW EXECUTE PROCEDURE tsvector_update_trigger(search, 'pg_catalog.english', title, content);
CREATE INDEX textsearch_idx ON blogpost USING GIN (search);