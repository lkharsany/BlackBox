# Create Testuser
CREATE USER 'dev'@'localhost' IDENTIFIED BY 'dev';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP ON *.* TO 'dev'@'localhost';

# Create DB
CREATE DATABASE IF NOT EXISTS `testDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `testDB`;

# Create Table
CREATE TABLE IF NOT EXISTS TestDiscordQuestions
(
    `id` int(6) unsigned auto_increment primary key,
    `username` varchar(30)  not null,
    `question` varchar(255) not null
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


# Add Data