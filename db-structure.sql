SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

CREATE TABLE `sms_inbox` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `received` datetime NOT NULL,
  `sender` varchar(15) DEFAULT NULL,
  `message` text,
  `sent` datetime NOT NULL,
  `status` tinyint(2) NOT NULL DEFAULT '0' COMMENT '0-received; 1-processed',
  `ts_processed` datetime DEFAULT NULL,
  `error` varchar(50) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `status` (`status`),
  KEY `ts` (`received`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `sms_outbox` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ts` datetime NOT NULL,
  `recipient` varchar(15) NOT NULL,
  `message` text NOT NULL,
  `expires` datetime NOT NULL,
  `status` tinyint(2) NOT NULL COMMENT '0-waiting; 1-sending',
  `retries` tinyint(1) NOT NULL,
  `ts_processed` datetime NOT NULL,
  `error` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `status` (`status`),
  KEY `ts` (`ts`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `sms_sent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ts` datetime NOT NULL,
  `recipient` varchar(15) NOT NULL,
  `message` text NOT NULL,
  `expires` datetime NOT NULL,
  `status` tinyint(1) NOT NULL COMMENT '0-sent; 1-error',
  `ts_processed` datetime NOT NULL,
  `error` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `status` (`status`),
  KEY `ts` (`ts`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
