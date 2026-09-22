CREATE TABLE `members` (
   `user_id` int NOT NULL AUTO_INCREMENT,
   `username` varchar(30) NOT NULL,
   `email` varchar(100) NOT NULL,
   `password` varchar(255) NOT NULL,
   `status` varchar(20) NOT NULL,
   `created_at` datetime NOT NULL,
   PRIMARY KEY (`user_id`),
   UNIQUE KEY `username` (`username`),
   UNIQUE KEY `email` (`email`)
 );
 
CREATE TABLE user_profiles ( -- making a user_profiles table 
profile_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
phone VARCHAR(20),
birth_date DATE,
updated_at DATETIME  NOT NULL, 
constraint fk_user_profiles_member
	FOREIGN KEY (user_id)
    REFERENCES members(user_id)
);

ALTER TABLE user_profiles -- changed default value of updated_at
MODIFY COLUMN updated_at DATETIME
NOT NULL
DEFAULT CURRENT_TIMESTAMP
ON UPDATE CURRENT_TIMESTAMP;

CREATE TABLE login_history ( -- Making a login_history table
	login_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_at DATETIME NOT NULL,
    login_result VARCHAR(20) NOT NULL,
    CONSTRAINT fk_login_history_member
		FOREIGN KEY (user_id)
        REFERENCES members(user_id)
);

