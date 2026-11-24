CREATE DATABASE IF NOT EXISTS slang_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE slang_db;

CREATE TABLE IF NOT EXISTS words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE,
    meaning TEXT NOT NULL,
    origin TEXT,
    image_name VARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word_id INT NULL,
    question TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NULL,
    correct_options VARCHAR(15) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fill_blank_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word_id INT NULL,
    sentence TEXT NOT NULL,
    correct_answer VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    meaning TEXT NOT NULL,
    origin TEXT,
    image_name VARCHAR(255) NULL,
    user_contact VARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    admin_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status)
);