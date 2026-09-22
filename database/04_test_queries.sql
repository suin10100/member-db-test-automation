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