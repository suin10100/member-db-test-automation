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
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci