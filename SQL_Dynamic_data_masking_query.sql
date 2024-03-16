-- Schema to contain user tables
--CREATE SCHEMA Data;
GO

-- Drop the table if it exists to start fresh
DROP TABLE  IF EXISTS Data.Customer;
GO

-- Create the table without masking rules
CREATE TABLE Data.Customer
(
    CustomerId   INT IDENTITY(1, 1) PRIMARY KEY,  -- Unique identifier for each customer
    CustomerName VARCHAR(50) NOT NULL,           -- Name of the customer
    [Address]    VARCHAR(50) NOT NULL,           -- Address of the customer
    Phone        VARCHAR(50) NOT NULL,           -- Phone number of the customer
    Email        VARCHAR(50) NOT NULL,           -- Email address of the customer
    SSN          VARCHAR(11) NOT NULL,           -- Social Security Number of the customer
    CreditCard   VARCHAR(16) NOT NULL,           -- Credit card number of the customer
    BirthDate    DATE NOT NULL                   -- Birth date of the customer
);

-- Add masking rules to the existing table
ALTER TABLE Data.Customer
ALTER COLUMN Phone VARCHAR(50) MASKED WITH (FUNCTION = 'default()') NOT NULL;  -- Masking phone number

ALTER TABLE Data.Customer
ALTER COLUMN Email VARCHAR(50) MASKED WITH (FUNCTION = 'email()') NOT NULL;    -- Masking email address

ALTER TABLE Data.Customer
ALTER COLUMN SSN VARCHAR(11) MASKED WITH (FUNCTION = 'partial(1,"XX-XX-XXX",1)') NOT NULL;  -- Masking SSN

ALTER TABLE Data.Customer
ALTER COLUMN CreditCard VARCHAR(16) MASKED WITH (FUNCTION = 'default()') NOT NULL;  -- Masking credit card number

ALTER TABLE Data.Customer
ALTER COLUMN BirthDate DATE MASKED WITH (FUNCTION = 'datetime("Y")') NOT NULL;  -- Masking birth date

-- Insert sample data into the Customer table
INSERT [Data].[Customer] ([CustomerName], [Address], [Phone], [Email], [SSN], [CreditCard], [BirthDate])
VALUES (N'Sherman Mc Mahon', N'317 Oak Blvd.', N'419-842-0053', N'Stefanie@hotmail.com', N'954-06-4725', N'4671310490474734', CAST(N'1970-04-07' AS Date)),
       (N'Raul Whitaker', N'162 Clarendon Freeway', N'727-3376906', N'Lee@yahoo.com', N'575-47-3864', N'4917802982169511', CAST(N'1966-07-08' AS Date)),
       (N'Bridget Bass', N'36 Fabien Street', N'910-676-2249', N'Daniel@gmail.com', N'031-36-9009', N'4510909781406266', CAST(N'1962-10-03' AS Date)),
       (N'Chris Hammond', N'477 Old Parkway', N'043-6080402', N'Myra@yahoo.com', N'102-84-0365', N'4555818416957682', CAST(N'1981-06-09' AS Date)),
       (N'Tina Newman', N'769 Nobel Parkway', N'835-9919560', N'Annie@gmail.com', N'785-39-3139', N'4407242384738505', CAST(N'1977-03-03' AS Date)),
       (N'Vickie Mueller', N'52 Rocky Second Freeway', N'087-156-9249', N'Jenifer@hotmail.com', N'571-76-5814', N'4028402375877642', CAST(N'1957-11-27' AS Date)),
       (N'Owen Hartman', N'743 White Oak Freeway', N'263-974-0388', N'Chastity@yahoo.com', N'525-94-4869', N'4514329407819360', CAST(N'1970-12-04' AS Date)),
       (N'Shelia Young', N'41 East First Freeway', N'0482672747', N'Jeannie@gmail.com', N'196-06-7150', N'4184323130074467', CAST(N'1982-08-28' AS Date)),
       (N'Dan Lutz', N'110 Oak Blvd.', N'7523113457', N'Bobbie@gmail.com', N'262-40-5409', N'4584769333955694', CAST(N'1981-05-21' AS Date)),
       (N'Carla Frazier', N'871 West Milton Road', N'877-4365989', N'Shawna@yahoo.com', N'453-55-9879', N'4592096673443325', CAST(N'1969-02-26' AS Date));
GO

-- Drop the TestUser if it exists
DROP USER IF EXISTS [TestUser];

-- Create the TestUser without a login
CREATE USER [TestUser] WITHOUT LOGIN;
 
-- Assign the default schema for the TestUser
ALTER USER [TestUser] WITH DEFAULT_SCHEMA=[Data];
 
-- Add TestUser to the db_Datareader role
ALTER ROLE [db_Datareader] ADD MEMBER [TestUser];
GO
 
-- Execute queries as TestUser
EXECUTE AS USER = 'TestUser';
 
-- Select data from the Customer table
SELECT * FROM Customer;
 
-- Revert back to the original user
REVERT;

-- Create roles for different permissions
CREATE ROLE PhoneSales;
CREATE ROLE MailAdCampagins;
CREATE ROLE PaymentProcessing;
CREATE ROLE Manager;
GO

-- Grant unmask permission to different roles
GRANT UNMASK ON  Data.Customer(Phone) TO PhoneSales;
GRANT UNMASK ON  Data.Customer(Email) TO MailAdCampagins;
GRANT UNMASK ON  Data.Customer(CreditCard) TO PaymentProcessing;
GRANT UNMASK ON  Data.Customer(SSN) TO PaymentProcessing;
GRANT UNMASK ON  Data.Customer TO Manager;
GO

-- Add TestUser to PhoneSales role
ALTER ROLE PhoneSales ADD MEMBER TestUser;

-- Execute queries as TestUser
EXECUTE AS USER = 'TestUser';
 
-- Select data from the Customer table
SELECT * FROM Customer;
 
-- Revert back to the original user
REVERT;

-- Remove TestUser from PhoneSales role
ALTER ROLE PhoneSales DROP MEMBER TestUser;

-- Add TestUser to MailAdCampagins role
ALTER ROLE MailAdCampagins ADD MEMBER TestUser;
 
-- Execute queries as TestUser
EXECUTE AS USER = 'TestUser';
 
-- Select data from the Customer table
SELECT * FROM Customer;
 
-- Revert back to the original user
REVERT;

-- Remove TestUser from MailAdCampagins role
ALTER ROLE MailAdCampagins DROP MEMBER TestUser;

-- Add TestUser to PaymentProcessing role
ALTER ROLE PaymentProcessing ADD MEMBER TestUser;
 
-- Execute queries as TestUser
EXECUTE AS USER = 'TestUser';
 
-- Select data from the Customer table
SELECT * FROM Customer;
 
-- Revert back to the original user
REVERT;

-- Remove TestUser from PaymentProcessing role
ALTER ROLE PaymentProcessing DROP MEMBER TestUser;

-- Add TestUser to Manager role
ALTER ROLE Manager ADD MEMBER TestUser;
 
-- Execute queries as TestUser
EXECUTE AS USER = 'TestUser';
 
-- Select data from the Customer table
SELECT * FROM Customer;
 
-- Revert back to the original user
REVERT;

-- Remove TestUser from Manager role
ALTER ROLE Manager DROP MEMBER TestUser;
