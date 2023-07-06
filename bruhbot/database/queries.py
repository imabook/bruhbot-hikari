# CREATE/INSERTS
STORE_USER_LONG = """
INSERT INTO users (id, religion, recieved, given, lvl, xp, prayed, started_at)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

STORE_USER = """
INSERT INTO users (id, started_at)
VALUES (%s, %s);
"""

STORE_ECONOMY_LONG = """
INSERT INTO economy (id, coins, abuelas, iglesias, amuletos, guiris, donaciones, angeles)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

STORE_ECONOMY = """
INSERT INTO economy (id)
VALUES (%s);
"""

STORE_ECONOMY_REBIRTH_LONG = """
INSERT INTO economy_rebirth (id, coins, libros, pecados, mandamientos, santos, diablos)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

STORE_ECONOMY_REBIRTH = """
INSERT INTO economy_rebirth (id)
VALUES (%s);
"""

STORE_TIMEOUT = """
INSERT INTO timeouts (id, executed)
VALUES (%s, %s);
"""

STORE_ITEM = """
INSERT INTO user_items (user_id, item_id, amount)
VALUES (%s, %s, %s);
"""
# STORE_TRANSACTION = """
# INSERT INTO transactions (user_1, user_2, amount, time)
# VALUES (%s, %s, %s, %s);
# """

# READS/FETCHS
FETCH_AMULETOS = """
SELECT amuletos
FROM economy
WHERE id = %s;
"""

FETCH_COINS = """
SELECT coins
FROM economy
WHERE id = %s;
"""

FETCH_PRAYS = """
SELECT prayed
FROM users
WHERE id = %s;
"""

FETCH_PRAYINFO_USER = """
SELECT religion, prayed, started_at, recieved, given
FROM users
WHERE id = %s;
"""
FETCH_PRAYINFO_ECONOMY = """
SELECT coins, abuelas, iglesias, amuletos, guiris, donaciones, angeles
FROM economy
WHERE id = %s;
"""

FETCH_RELIGION = """
SELECT religion
FROM users
WHERE id = %s;
"""

FETCH_LVL = """
SELECT lvl, xp
FROM users
WHERE id = %s;
"""

FETCH_LVL_ONLY = """
SELECT lvl
FROM users
WHERE id = %s;
"""

FETCH_SHOP = """
SELECT SUM(abuelas), SUM(iglesias), SUM(guiris), SUM(donaciones), SUM(angeles)
FROM economy;
"""

FETCH_TIMEOUT = """
SELECT executed
FROM timeouts
WHERE id = %s;
"""

FETCH_USER_ITEMS = """
SELECT item_id, amount
FROM user_items
WHERE user_id = %s;
"""

FETCH_ITEM_AMOUNT = """
SELECT amount
FROM user_items
WHERE user_id = %s AND item_id = %s;
"""

FETCH_USER_MISSIONS = """
SELECT um.mission_id, um.ends_at, um.reward, um.amount, um.goal 
FROM user_missions um
INNER JOIN missions m ON um.mission_id = m.id 
WHERE um.user_id = %s AND m.is_7d IS FALSE;
"""

FETCH_USER_MISSIONS_WEEKLY = """
SELECT um.mission_id, um.ends_at, um.reward, um.amount, um.goal 
FROM user_missions um
INNER JOIN missions m ON um.mission_id = m.id 
WHERE um.user_id = %s AND m.is_7d IS TRUE;
"""

FETCH_MISSION_INFO = """
SELECT id, description
FROM missions
WHERE id IN %s;
"""

# FETCH_ITEM_INFO = """
# SELECT id, name, description, emoji
# FROM items
# WHERE id = %s;
# """

# UPDATES
UPDATE_COINS = """
UPDATE economy
SET coins = %s
WHERE id = %s;
"""

UPDATE_COINS_ADD = """
UPDATE economy
SET coins = coins + %s
WHERE id = %s;
"""

UPDATE_COINS_SUB = """
UPDATE economy
SET coins = coins - %s
WHERE id = %s;
"""

UPDATE_PRAYS = """
UPDATE users
SET prayed = prayed + 1
WHERE id = %s;
"""

UPDATE_RELIGION = """
UPDATE users
SET religion = %s
WHERE id = %s;
"""

UPDATE_GIVEN = """
UPDATE users
SET given = given + %s
WHERE id = %s;
"""

UPDATE_RECIEVED = """
UPDATE users
SET recieved = recieved + %s
WHERE id = %s;
"""

UPDATE_XP = """
UPDATE users
SET xp = %s
WHERE id = %s;
"""

UPDATE_LVL = """
UPDATE users
SET lvl = %s, xp = %s
WHERE id = %s;
"""

# had $ROW = $ROW + %s but people can get a benefit by bying 2 things at the same time
# having it like this the problem "persists" but they wont get any benefit from it,, too lazy to explain the though process and shit so try to imagine it yourself
UPDATE_ECONOMY_OBJECT = """
UPDATE economy
SET coins = %s, $ROW = %s
WHERE id = %s;
"""

UPDATE_TIMEOUT = """
UPDATE timeouts
SET executed = %s
WHERE id = %s;
"""

UPDATE_USER_ITEM = """
UPDATE user_items
SET amount = %s
WHERE user_id = %s AND item_id = %s
"""

DELETE_USER_ITEM = """
DELETE FROM user_items
WHERE user_id = %s AND item_id = %s;
"""