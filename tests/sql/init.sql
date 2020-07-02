CREATE DATABASE BNPPF;
CREATE USER 'myusername'@'%' IDENTIFIED BY 'mypassword';
GRANT EXECUTE ON BNPPF.* TO 'myusername'@'%';
