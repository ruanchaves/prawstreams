-- Taken from https://stackoverflow.com/a/39224859/4882300
-- Integrate this into a template later

with accounts_json (doc) as ( values ('{0}'::json) )
insert into accounts (id, client_id, client_secret, password, user_agent, username)
select p.*
from accounts_json l
  cross join lateral json_populate_recordset(null::accounts, doc) as p
on conflict (id) do update 
  set id = excluded.id, 
      client_id = excluded.client_id,
	  client_secret = excluded.client_secret,
	  password = excluded.password,
	  user_agent = excluded.user_agent,
	  username = excluded.username;
