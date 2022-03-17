USE BNPPF;

DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `addTransaction`(IN sequence VARCHAR(10), IN day VARCHAR(8), IN amount DOUBLE, IN currency VARCHAR(3), IN type TEXT, IN comment TEXT, IN account VARCHAR(34))
BEGIN
	INSERT INTO Transactions (reference,dateOf,amount,currency,typeOf,comment,account,created)
		SELECT * FROM (SELECT sequence, day, amount, currency, type, comment, account,NOW()) AS tmp
		WHERE NOT EXISTS (
    			SELECT Transactions.`id` FROM Transactions WHERE Transactions.`account` = account AND Transactions.`reference` = sequence AND Transactions.`amount` = amount
		) LIMIT 1;
END;;
DELIMITER ;
