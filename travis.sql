# Create DB
CREATE DATABASE IF NOT EXISTS `testDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `testDB`;

# Create Table
CREATE TABLE IF NOT EXISTS TestDiscordQuestions
(
    `id` int(6) unsigned auto_increment primary key,
    `username` varchar(30)  not null,
    `question` varchar(255) not null,
    `question_date` date not null,
    `question_time` time not null,
    `channel` varchar(30) not null
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS TestDiscordAnswers
(
    `id` int(6) unsigned auto_increment primary key,
    `asked_by` varchar(30)  not null,
    `question` varchar(255) not null,
    `question_date` date not null,
    `question_time` time not null,

    `answered_by` varchar(30)  not null,
    `answer` varchar(255) not null,
    `answer_date` date not null,
    `answer_time` time not null,
    `channel` varchar(30) not null
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS TestLecturerQuestions
(
    `id` int(6) unsigned auto_increment primary key,
    `asked_by` varchar(30)  not null,
    `question_id` int(6),
    `question` varchar(255) not null,
    `question_date` date not null,
    `question_time` time not null,

    `referred_by` varchar(30)  not null,
    `channel` varchar(30) not null

) ENGINE=InnoDB DEFAULT CHARSET=utf8;