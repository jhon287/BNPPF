USE BNPPF;

-- addTransaction
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `addTransaction`(IN sequence VARCHAR(10), IN day VARCHAR(8), IN amount DOUBLE, IN currency VARCHAR(3), IN type TEXT, IN comment TEXT, IN account VARCHAR(34))
BEGIN
	INSERT INTO Transactions (reference, dateOf, amount, currency, typeOf, comment, account, created)
		SELECT * FROM (SELECT sequence, day, amount, currency, type, comment, account,NOW()) AS tmp
		WHERE NOT EXISTS (
  		SELECT Transactions.`id` FROM Transactions WHERE Transactions.`account` = account AND Transactions.`reference` = sequence AND Transactions.`amount` = amount
		) LIMIT 1;
END;;
DELIMITER ;

-- getYears
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `getYears`()
BEGIN
	SELECT DISTINCT SUBSTRING(T.`dateOf`,1,4) AS date_of
	FROM `Transactions` T
	ORDER BY date_of ASC;
END;;
DELIMITER ;

-- getTypes
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `getTypes`()
BEGIN
	SELECT DISTINCT T.`typeOf` AS type_of
	FROM `Transactions` T
	ORDER BY type_of ASC;
END;;
DELIMITER ;

-- getExpenseAmountsByYear
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `getExpenseAmountsByYear`(IN yearNeeded VARCHAR(4), IN accountNeeded VARCHAR(16))
BEGIN
	SELECT T.`typeOf` as type_of, SUBSTRING(T.`dateOf`,1,6) AS date_of, SUM(T.`amount`) * -1 AS amount
	FROM `Transactions` T
	WHERE T.`dateOf` LIKE CONCAT(yearNeeded,'%') AND amount < 0 AND T.`account` = accountNeeded
	GROUP BY type_of, date_of
	ORDER BY date_of DESC, type_of ASC;
END;;
DELIMITER ;

-- getAmountsYearByAccount
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `getAmountsYearByAccount`(IN yearNeeded VARCHAR(4), IN accountNeeded VARCHAR(16))
BEGIN
SELECT T.`amount` AS amount, T.`account` AS account, T.`dateOf` AS date_of
FROM `Transactions` T
WHERE T.`dateOf` LIKE CONCAT(yearNeeded,'%') AND T.`account` = accountNeeded
ORDER By T.`account`, T.`dateOf` DESC ;
END;;
DELIMITER ;

-- getAccounts
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `getAccounts`()
BEGIN
	SELECT DISTINCT T.`account` AS account, COUNT(T.id) as count
	FROM `Transactions` T
	GROUP BY account
	ORDER BY count DESC;
END;;
DELIMITER ;

-- checkTransactionsDone
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `checkTransactionsDone`(IN Y VARCHAR(4), IN M VARCHAR(2))
BEGIN
	SELECT DISTINCT T.dateOf, T.amount, T.currency, T.typeOf, TM.id, TM.match
	FROM Transactions T INNER JOIN TransactionMatches TM
	ON ( 
		T.comment REGEXP TM.match
		AND T.dateOf LIKE CONCAT(Y, M, "%") 
		AND T.amount = TM.amount
		AND T.currency = TM.currency
		AND T.typeOf = TM.typeOf
		AND T.account = TM.account
		AND T.dateOf >= TM.dateStart 
		AND (
			T.dateOf <= TM.dateEnd
			OR TM.dateEnd = ""
			OR TM.dateEnd IS NULL
		)
	)
	ORDER BY T.dateOf;
END;;
DELIMITER ;
