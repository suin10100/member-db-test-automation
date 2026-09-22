SHOW DATABASES;
USE member_db;
SHOW TABLES;
SHOW CREATE TABLE user_profiles;
SHOW CREATE TABLE login_history;
DESCRIBE members;
DESCRIBE user_profiles;
DESCRIBE login_history;
SELECT * FROM members;
SELECT * FROM user_profiles;
SELECT COUNT(*) FROM members;
DESC members;

INSERT INTO members -- Insert some datas into members database
(username, email, password, status, created_at)
VALUES
('test01', 'test01@example.com', 'password01', 'ACTIVE', NOW()),
('test02', 'test02@example.com', 'password02', 'ACTIVE', NOW()),
('test03', 'test03@example.com', 'password03', 'INACTIVE', NOW()),
('test04', 'test04@example.com', 'password04', 'SUSPENDED', NOW()),
('test05', 'test05@example.com', 'password05', 'ACTIVE', NOW());

INSERT INTO user_profiles -- Insert some datas into user_profiles
    (user_id, phone, birth_date, updated_at)
VALUES
    (1, '010-1111-1111', '2000-01-01', NOW()),
    (2, '010-2222-2222', '1999-05-10', NOW()),
    (3, '010-3333-3333', '2001-08-20', NOW()),
    (4, '010-4444-4444', '1998-03-15', NOW()),
    (5, '010-5555-5555', '2002-11-30', NOW());
    
SELECT email, COUNT(*) -- checking a duplicated data
FROM members
GROUP BY email
HAVING COUNT(*) > 1;

SELECT * -- checking a data is not NULL
FROM members
WHERE username IS NULL
   OR email IS NULL
   OR password IS NULL
   OR status IS NULL
   OR created_at IS NULL;
   
SELECT * -- Check status value
FROM members
WHERE status NOT IN (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);

SELECT p.* -- check FK data
FROM user_profiles p
LEFT JOIN members m -- check with user_id in members table and user_id in user_profiles table
    ON p.user_id = m.user_id
WHERE m.user_id IS NULL; -- if it has a NULL, it means that doesn't matched.

SHOW DATABASES;


