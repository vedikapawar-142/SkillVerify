-- ==============================================================================
-- AI Skill Verification Platform — Complete MySQL Database Schema
-- Diploma in Computer Engineering Capstone Project
-- Compatible with XAMPP MySQL / MariaDB and MySQL Server 8.0+
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS `skillverify` 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE `skillverify`;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Users Table
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'candidate',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_user_email` (`email`),
  INDEX `idx_user_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Resumes Table
DROP TABLE IF EXISTS `resumes`;
CREATE TABLE `resumes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `filename` VARCHAR(255),
  `file_path` VARCHAR(255),
  `raw_text` LONGTEXT,
  `extracted_skills` TEXT,
  `parsed_data` LONGTEXT,
  `status` VARCHAR(30) DEFAULT 'processed',
  `uploaded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_resume_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Job Roles Table
DROP TABLE IF EXISTS `job_roles`;
CREATE TABLE `job_roles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `hr_id` INT NOT NULL,
  `title` VARCHAR(120) NOT NULL,
  `description` TEXT,
  `required_skills` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`hr_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_job_hr` (`hr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Questions Table
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `skill` VARCHAR(60) NOT NULL DEFAULT 'python',
  `type` VARCHAR(30) NOT NULL,
  `topic` VARCHAR(100) DEFAULT 'Python Fundamentals',
  `difficulty` INT NOT NULL DEFAULT 1,
  `statement` TEXT NOT NULL,
  `code_snippet` TEXT,
  `starter_code` TEXT,
  `options` TEXT,
  `correct_answer` TEXT,
  `test_cases` TEXT,
  `marks` INT DEFAULT 20,
  `explanation` TEXT,
  INDEX `idx_question_skill` (`skill`),
  INDEX `idx_question_difficulty` (`difficulty`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Attempts Table
DROP TABLE IF EXISTS `attempts`;
CREATE TABLE `attempts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `role_id` INT NULL,
  `skill` VARCHAR(60) DEFAULT 'python',
  `status` VARCHAR(20) DEFAULT 'in_progress',
  `started_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `completed_at` DATETIME NULL,
  `final_score` FLOAT DEFAULT 0.0,
  `coding_score` FLOAT DEFAULT 0.0,
  `debugging_score` FLOAT DEFAULT 0.0,
  `problem_solving_score` FLOAT DEFAULT 0.0,
  `interview_score` FLOAT DEFAULT 0.0,
  `performance_category` VARCHAR(50),
  `correct_count` INT DEFAULT 0,
  `total_questions` INT DEFAULT 5,
  `integrity_score` FLOAT DEFAULT 100.0,
  `adaptive_path` TEXT,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`role_id`) REFERENCES `job_roles`(`id`) ON DELETE SET NULL,
  INDEX `idx_attempt_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Answers Table
DROP TABLE IF EXISTS `answers`;
CREATE TABLE `answers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `attempt_id` INT NOT NULL,
  `question_id` INT NOT NULL,
  `submitted_answer` TEXT,
  `submitted_code` TEXT,
  `is_correct` BOOLEAN DEFAULT FALSE,
  `tests_passed` INT DEFAULT 0,
  `tests_total` INT DEFAULT 0,
  `score` FLOAT DEFAULT 0.0,
  `feedback` TEXT,
  `execution_output` TEXT,
  `execution_engine` VARCHAR(50) DEFAULT 'Local Runner',
  FOREIGN KEY (`attempt_id`) REFERENCES `attempts`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE,
  INDEX `idx_answer_attempt` (`attempt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Interview QA Table
DROP TABLE IF EXISTS `interview_qa`;
CREATE TABLE `interview_qa` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `attempt_id` INT NOT NULL,
  `question_text` TEXT NOT NULL,
  `answer_text` TEXT,
  `score` FLOAT DEFAULT 0.0,
  `feedback` TEXT,
  `rubric_evaluation` TEXT,
  `evaluated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`attempt_id`) REFERENCES `attempts`(`id`) ON DELETE CASCADE,
  INDEX `idx_interview_attempt` (`attempt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Violations Table
DROP TABLE IF EXISTS `violations`;
CREATE TABLE `violations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `attempt_id` INT NOT NULL,
  `type` VARCHAR(40) NOT NULL,
  `details` VARCHAR(255),
  `deduction` FLOAT DEFAULT 5.0,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `snapshot_path` VARCHAR(255),
  FOREIGN KEY (`attempt_id`) REFERENCES `attempts`(`id`) ON DELETE CASCADE,
  INDEX `idx_violation_attempt` (`attempt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Reports Table
DROP TABLE IF EXISTS `reports`;
CREATE TABLE `reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `attempt_id` INT NOT NULL UNIQUE,
  `user_id` INT NOT NULL,
  `verified_skills` TEXT,
  `claimed_skills` TEXT,
  `comparison_summary` TEXT,
  `strengths_weaknesses` TEXT,
  `improvement_suggestions` TEXT,
  `certificate_id` VARCHAR(60) UNIQUE,
  `generated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`attempt_id`) REFERENCES `attempts`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_report_user` (`user_id`),
  INDEX `idx_report_cert` (`certificate_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Certificates Table
DROP TABLE IF EXISTS `certificates`;
CREATE TABLE `certificates` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `certificate_id` VARCHAR(60) UNIQUE NOT NULL,
  `attempt_id` INT NOT NULL UNIQUE,
  `user_id` INT NOT NULL,
  `candidate_name` VARCHAR(120) NOT NULL,
  `skill` VARCHAR(60) NOT NULL DEFAULT 'Python',
  `score` FLOAT NOT NULL,
  `performance_category` VARCHAR(50) NOT NULL,
  `issued_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `qr_code_path` VARCHAR(255),
  `pdf_path` VARCHAR(255),
  `is_valid` BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (`attempt_id`) REFERENCES `attempts`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_cert_id` (`certificate_id`),
  INDEX `idx_cert_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
