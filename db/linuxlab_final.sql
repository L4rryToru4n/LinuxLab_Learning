-- MySQL Script generated by MySQL Workbench
-- Fri Jan 26 22:07:47 2024
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
SHOW WARNINGS;
-- -----------------------------------------------------
-- Schema linuxlab
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema linuxlab
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `linuxlab` DEFAULT CHARACTER SET utf8mb4 ;
SHOW WARNINGS;
USE `linuxlab` ;

-- -----------------------------------------------------
-- Table `linuxlab`.`players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`players` (
  `table_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_player` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `username` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `email` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `password` VARCHAR(255) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `role` VARCHAR(32) NULL,
  `create_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_player`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  INDEX `table_id_INDEX` (`table_id` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`admins`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`admins` (
  `table_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_admin` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `username` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `email` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `password` VARCHAR(255) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `role` VARCHAR(32) NULL,
  `create_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_admin`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  INDEX `table_id_INDEX` (`table_id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`flags`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`flags` (
  `id_flag` INT(10) NOT NULL AUTO_INCREMENT,
  `admin_id` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `flag_string` TEXT(50) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin' NOT NULL,
  `level` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `category` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `points` INT UNSIGNED NOT NULL,
  `bonus_point` INT UNSIGNED NULL,
  `number_of_bonus` INT UNSIGNED NULL,
  `period` DATE NULL,
  `is_active` TINYINT(1) NULL,
  `create_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  `story` TEXT(65535) NULL,
  `task` TEXT(65535) NULL,
  `commands_needed` TEXT(65535) NULL,
  `helpful_references` TEXT(65535) NULL,
  `hint` MEDIUMTEXT NULL,
  `access_port` TEXT(65535) NULL,
  PRIMARY KEY (`id_flag`),
  INDEX `ADMIN_ID` (`admin_id` ASC),
  CONSTRAINT `fk_flags_admin_id_idx`
    FOREIGN KEY (`admin_id`)
    REFERENCES `linuxlab`.`admins` (`id_admin`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`flag_submissions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`flag_submissions` (
  `id_flag_submissions` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `flag_id` INT(10) NULL,
  `player_id` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `period` DATE NULL,
  `submission_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_flag_submissions`),
  INDEX `fk_flag_submissions_flag_id_idx` USING BTREE (`flag_id`),
  INDEX `fk_flag_submissions_player_id_idx` (`player_id` ASC),
  CONSTRAINT `fk_flag_submissions_flag_id`
    FOREIGN KEY (`flag_id`)
    REFERENCES `linuxlab`.`flags` (`id_flag`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_flag_submissions_player_id`
    FOREIGN KEY (`player_id`)
    REFERENCES `linuxlab`.`players` (`id_player`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`achievements_tracker`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`achievements_tracker` (
  `id_achievements_tracker` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `player_id` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `achievement_name` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `description` LONGTEXT NULL,
  `period` DATE NULL,
  `collection_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_achievements_tracker`),
  INDEX `player_id_idx` USING BTREE (`player_id`),
  CONSTRAINT `player_id`
    FOREIGN KEY (`player_id`)
    REFERENCES `linuxlab`.`players` (`id_player`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`scoreboard`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`scoreboard` (
  `id_scoreboard` VARCHAR(32) NOT NULL,
  `player_id` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `total_score` INT UNSIGNED NULL,
  `period` DATE NULL,
  `create_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_scoreboard`),
  INDEX `PLAYER_ID` (`player_id` ASC),
  CONSTRAINT `fk_scoreboard_player_id_idx`
    FOREIGN KEY (`player_id`)
    REFERENCES `linuxlab`.`players` (`id_player`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`sessions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`sessions` (
  `id_session` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `player_id` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `time_signin` TIMESTAMP NULL,
  `time_signout` TIMESTAMP NULL,
  `last_activity` TIMESTAMP NULL,
  `period` DATE NULL,
  PRIMARY KEY (`id_session`),
  INDEX `PLAYER_ID` (`player_id` ASC),
  CONSTRAINT `fk_session_player_id_idx`
    FOREIGN KEY (`player_id`)
    REFERENCES `linuxlab`.`players` (`id_player`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`questions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`questions` (
  `id_question` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `admin_id` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `quiz` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `question` TEXT(100) NOT NULL,
  `points` INT UNSIGNED NULL,
  `is_active` TINYINT NULL,
  `period` DATE NULL,
  `create_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_question`),
  INDEX `admin_id_fk_idx` (`admin_id` ASC),
  CONSTRAINT `fk_questions_admin_id`
    FOREIGN KEY (`admin_id`)
    REFERENCES `linuxlab`.`admins` (`id_admin`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`answers_tracker`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`answers_tracker` (
  `id_answers_tracker` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `player_id` VARCHAR(32) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NULL,
  `question_id` INT UNSIGNED NULL,
  `answered_correct` TINYINT NULL,
  `create_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_answers_tracker`),
  INDEX `question_id_fk_idx` (`question_id` ASC),
  INDEX `player_id_fk_idx` (`player_id` ASC),
  CONSTRAINT `fk_answers_tracker_question_id`
    FOREIGN KEY (`question_id`)
    REFERENCES `linuxlab`.`questions` (`id_question`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_answers_tracker_player_id`
    FOREIGN KEY (`player_id`)
    REFERENCES `linuxlab`.`players` (`id_player`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `linuxlab`.`question_choices`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`question_choices` (
  `id_question_choice` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `question_id` INT UNSIGNED NULL,
  `question_choice` TEXT(50) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci' NOT NULL,
  `is_correct_answer` TINYINT NULL,
  `create_time` TIMESTAMP NULL,
  `update_time` TIMESTAMP NULL,
  `delete_time` TIMESTAMP NULL,
  PRIMARY KEY (`id_question_choice`),
  INDEX `question_id_fk_idx` (`question_id` ASC),
  CONSTRAINT `question_id_fk`
    FOREIGN KEY (`question_id`)
    REFERENCES `linuxlab`.`questions` (`id_question`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SHOW WARNINGS;
USE `linuxlab` ;

-- -----------------------------------------------------
-- Placeholder table for view `linuxlab`.`submission_graph`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`submission_graph` (`id_flag_submissions` INT, `id_player` INT, `username` INT, `points` INT, `submission_time` INT, `period` INT);
SHOW WARNINGS;

-- -----------------------------------------------------
-- Placeholder table for view `linuxlab`.`level_0_submission_time_length`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`level_0_submission_time_length` (`id_session` INT, `player_id` INT, `id_flag_submissions` INT, `level` INT, `submission_time_length` INT, `submission_time` INT, `period` INT);
SHOW WARNINGS;

-- -----------------------------------------------------
-- Placeholder table for view `linuxlab`.`players_playing_time_length`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`players_playing_time_length` (`id_session` INT, `player_id` INT, `playing_time` INT, `period` INT);
SHOW WARNINGS;

-- -----------------------------------------------------
-- Placeholder table for view `linuxlab`.`level_submission_time_length`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `linuxlab`.`level_submission_time_length` (`id` INT);
SHOW WARNINGS;

-- -----------------------------------------------------
-- View `linuxlab`.`submission_graph`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `linuxlab`.`submission_graph`;
SHOW WARNINGS;
USE `linuxlab`;
CREATE  OR REPLACE VIEW `submission_graph` AS 
SELECT fs.id_flag_submissions, p.id_player, p.username, f.points, fs.submission_time, fs.period 
FROM flag_submissions AS fs JOIN players AS p ON fs.player_id = p.id_player
JOIN flags AS f ON fs.flag_id = f.id_flag;
SHOW WARNINGS;

-- -----------------------------------------------------
-- View `linuxlab`.`level_0_submission_time_length`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `linuxlab`.`level_0_submission_time_length`;
SHOW WARNINGS;
USE `linuxlab`;
CREATE  OR REPLACE VIEW `level_0_submission_time_length` AS
    SELECT 
        `sessions`.`id_session` AS `id_session`,
        `sessions`.`player_id` AS `player_id`,
        `flag_submissions`.`id_flag_submissions` AS `id_flag_submissions`,
        `flags`.`level` AS `level`,
        TIMEDIFF(`flag_submissions`.`submission_time`,
                `sessions`.`time_signin`) AS `submission_time_length`,
        `flag_submissions`.`submission_time`,
        `sessions`.`period`
    FROM
        (((`sessions`
        JOIN (SELECT 
			`sessions`.`id_session`,
            `sessions`.`player_id` AS `player_id`,
                MIN(`sessions`.`time_signin`) AS `MinTimeSignIn`,
                `sessions`.`period`
        FROM
            `sessions`
        GROUP BY `sessions`.`player_id`, `sessions`.`period`) `session_inner` ON (`session_inner`.`player_id` = `sessions`.`player_id`))
        JOIN `flag_submissions` ON (`flag_submissions`.`player_id` = `sessions`.`player_id`))
        JOIN `flags` ON (`flags`.`id_flag` = `flag_submissions`.`flag_id`))
    WHERE
        `session_inner`.`MinTimeSignIn` = `sessions`.`time_signin`
            AND `flags`.`level` = 'level_0'
            AND `sessions`.`period` = `flag_submissions`.`period`;
SHOW WARNINGS;

-- -----------------------------------------------------
-- View `linuxlab`.`players_playing_time_length`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `linuxlab`.`players_playing_time_length`;
SHOW WARNINGS;
USE `linuxlab`;
CREATE  OR REPLACE VIEW `players_playing_time_length` AS
    SELECT 
        `sessions`.`id_session` AS `id_session`,
        `sessions`.`player_id` AS `player_id`,
        TIMEDIFF(`sessions`.`time_signout`,
                `sessions`.`time_signin`) AS `playing_time`,
        `sessions`.`period` AS `period`
    FROM
        `sessions`;
SHOW WARNINGS;

-- -----------------------------------------------------
-- View `linuxlab`.`level_submission_time_length`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `linuxlab`.`level_submission_time_length`;
SHOW WARNINGS;
USE `linuxlab`;
CREATE  OR REPLACE VIEW `level_submission_time_length` AS
	WITH player_submissions AS (
	    SELECT id_flag_submissions, player_id, level, submission_time, `flag_submissions`.`period`
		FROM flag_submissions
		INNER JOIN players ON player_id = id_player
		INNER JOIN flags ON flag_id = id_flag
		ORDER BY player_id, level
)

	SELECT id_flag_submissions, player_id, level, 
    submission_time_length, submission_time
    FROM
	(SELECT id_flag_submissions, player_id, level, 
     submission_time,
	TIMEDIFF(submission_time, (LAG(submission_time, 1) OVER (
		PARTITION BY player_id, `player_submissions`.`period`
	    ORDER BY level))
		) submission_time_length
	FROM player_submissions) AS submission_time_length
WHERE submission_time_length > '00:00:00'
ORDER BY level;
SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;