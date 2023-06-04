-- school_lib.author definition

CREATE TABLE `author` (
  `author_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `author_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`author_id`)
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.book definition

CREATE TABLE `book` (
  `ISBN` int(10) unsigned NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `publisher` varchar(100) DEFAULT NULL,
  `num_pages` int(10) unsigned DEFAULT NULL,
  `summary` text DEFAULT NULL,
  `num_copies` int(10) unsigned DEFAULT NULL,
  `images` varchar(1) DEFAULT NULL,
  `language` varchar(100) DEFAULT NULL,
  `book_status` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`ISBN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.category definition

CREATE TABLE `category` (
  `category_name` varchar(100) DEFAULT NULL,
  `category_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.key_word definition

CREATE TABLE `key_word` (
  `key_word_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `word` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`key_word_id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.school definition

CREATE TABLE `school` (
  `admin_name` varchar(100) NOT NULL,
  `operator_name` varchar(100) NOT NULL,
  `director_name` varchar(100) NOT NULL,
  `phone` mediumtext NOT NULL,
  `email` varchar(100) NOT NULL,
  `city` varchar(100) NOT NULL,
  `zip_code` int(10) unsigned NOT NULL,
  `name` varchar(100) NOT NULL,
  `school_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`school_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.book_author definition

CREATE TABLE `book_author` (
  `ISBN` int(10) unsigned DEFAULT NULL,
  `book_author_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `author_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`book_author_id`),
  KEY `book_author_FK_1` (`ISBN`),
  KEY `book_author_FK` (`author_id`),
  CONSTRAINT `book_author_FK` FOREIGN KEY (`author_id`) REFERENCES `author` (`author_id`),
  CONSTRAINT `book_author_FK_1` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`)
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.book_category definition

CREATE TABLE `book_category` (
  `book_category_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ISBN` int(10) unsigned DEFAULT NULL,
  `category_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`book_category_id`),
  KEY `book_category_FK` (`ISBN`),
  KEY `book_category_FK_1` (`category_id`),
  CONSTRAINT `book_category_FK` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`),
  CONSTRAINT `book_category_FK_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.book_key_words definition

CREATE TABLE `book_key_words` (
  `ISBN` int(10) unsigned NOT NULL,
  `book_key_word_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `key_word_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`book_key_word_id`),
  KEY `book_key_words_FK` (`ISBN`),
  KEY `book_key_words_FK_1` (`key_word_id`),
  CONSTRAINT `book_key_words_FK` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`),
  CONSTRAINT `book_key_words_FK_1` FOREIGN KEY (`key_word_id`) REFERENCES `key_word` (`key_word_id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.school_book definition

CREATE TABLE `school_book` (
  `school_book_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ISBN` int(10) unsigned DEFAULT NULL,
  `school_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`school_book_id`),
  KEY `school_book_FK` (`school_id`),
  KEY `school_book_FK_1` (`ISBN`),
  CONSTRAINT `school_book_FK` FOREIGN KEY (`school_id`) REFERENCES `school` (`school_id`),
  CONSTRAINT `school_book_FK_1` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.`user` definition

CREATE TABLE `user` (
  `email` varchar(100) DEFAULT NULL,
  `user_type` int(10) unsigned DEFAULT 0,
  `last_name` varchar(100) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `user_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `school_id` int(10) unsigned DEFAULT NULL,
  `age` int(10) unsigned DEFAULT NULL,
  `user_status` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `user_FK` (`school_id`),
  CONSTRAINT `user_FK` FOREIGN KEY (`school_id`) REFERENCES `school` (`school_id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.review definition

CREATE TABLE `review` (
  `review_status` int(11) DEFAULT 0,
  `date_of_review` timestamp NULL DEFAULT current_timestamp(),
  `review_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ISBN` int(10) unsigned DEFAULT NULL,
  `text_of_review` text DEFAULT NULL,
  `user_id` int(10) unsigned DEFAULT NULL,
  `likert_rating` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`review_id`),
  KEY `review_FK` (`ISBN`),
  KEY `review_FK_1` (`user_id`),
  CONSTRAINT `review_FK` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`),
  CONSTRAINT `review_FK_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- school_lib.`transaction` definition

CREATE TABLE `transaction` (
  `date_of_max_return` timestamp NULL DEFAULT current_timestamp(),
  `date_of_borrowing` varchar(27) DEFAULT 'current_timestamp()',
  `transaction_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `transaction_status` int(11) DEFAULT 0,
  `date_of_reservation` timestamp NULL DEFAULT current_timestamp(),
  `transaction_type` int(11) DEFAULT 0,
  `date_of_return` timestamp NULL DEFAULT current_timestamp(),
  `ISBN` int(10) unsigned DEFAULT NULL,
  `user_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `transaction_FK` (`ISBN`),
  KEY `transaction_FK_1` (`user_id`),
  CONSTRAINT `transaction_FK` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`),
  CONSTRAINT `transaction_FK_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=294 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
