USE BNPPF;

-- Transactions
CREATE TABLE `Transactions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reference` text NOT NULL,
  `dateOf` text NOT NULL,
  `amount` double DEFAULT NULL,
  `currency` text NOT NULL,
  `typeOf` text NOT NULL,
  `comment` text NOT NULL,
  `account` text NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
