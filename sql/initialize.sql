CREATE TABLE IF NOT EXISTS subreddits(
    id SERIAL PRIMARY KEY,
    name VARCHAR);

CREATE TABLE IF NOT EXISTS accounts(
    id SERIAL PRIMARY KEY,
    client_id VARCHAR,
    client_secret VARCHAR,
    password VARCHAR,
    user_agent VARCHAR,
    username VARCHAR);

CREATE TABLE IF NOT EXISTS inbox(
    id INTEGER PRIMARY KEY,
    all_ BOOLEAN,
    comment_replies BOOLEAN,
    mentions BOOLEAN,
    messages BOOLEAN,
    stream BOOLEAN,
    submission_replies BOOLEAN
);

INSERT INTO inbox (id, all_, comment_replies, mentions, messages, stream, submission_replies)
VALUES (1, False, False, False, False, False, False)
ON CONFLICT DO NOTHING;

-- Function copied from http://coussej.github.io/2015/09/15/Listening-to-generic-JSON-notifications-from-PostgreSQL-in-Go/
-- ( http://archive.ph/gy6Qs )
CREATE OR REPLACE FUNCTION notify_event() RETURNS TRIGGER AS $$

    DECLARE
        data json;
        notification json;

    BEGIN
        -- Convert the old or new row to JSON, based on the kind of action.
        -- Action = DELETE?             -> OLD row
        -- Action = INSERT or UPDATE?   -> NEW row
        IF (TG_OP = 'DELETE') THEN
            data = row_to_json(OLD);
        ELSE
            data = row_to_json(NEW);
        END IF;
        -- Contruct the notification as a JSON string.
        notification = json_build_object(
            'table',TG_TABLE_NAME,
            'action', TG_OP,
            'data', data);
        -- Execute pg_notify(channel, notification)
        PERFORM pg_notify('events',notification::text);
                -- Result is ignored since this is an AFTER trigger
        RETURN NULL;
            END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS stream_notify_event ON stream;

CREATE TRIGGER stream_notify_event
AFTER INSERT OR UPDATE OR DELETE ON stream
    FOR EACH ROW EXECUTE PROCEDURE notify_event();
