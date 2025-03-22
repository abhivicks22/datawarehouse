# Bank Data Warehouse - Logical Data Model

## Core Entities

### Branch
```
BranchID (INT, PK)
BranchName (VARCHAR(100))
Address (VARCHAR(200))
City (VARCHAR(100))
State (VARCHAR(50))
ZipCode (VARCHAR(10))
RegionID (INT, FK)
ManagerID (INT, FK)
OpenDate (DATE)
OperatingHours (VARCHAR(100))
SquareFootage (INT)
NumberOfTellers (INT)
NumberOfATMs (INT)
OperationalCost (DECIMAL(10,2))
LastUpdated (TIMESTAMP)
```

### Customer
```
CustomerID (INT, PK)
FirstName (VARCHAR(50))
LastName (VARCHAR(50))
DateOfBirth (DATE)
Address (VARCHAR(200))
City (VARCHAR(100))
State (VARCHAR(50))
ZipCode (VARCHAR(10))
Email (VARCHAR(100))
Phone (VARCHAR(20))
CustomerSegmentID (INT, FK)
AcquisitionDate (DATE)
LastInteractionDate (TIMESTAMP)
SatisfactionScore (INT)
NPSScore (INT)
Status (VARCHAR(20))
LastUpdated (TIMESTAMP)
```

### Employee
```
EmployeeID (INT, PK)
FirstName (VARCHAR(50))
LastName (VARCHAR(50))
BranchID (INT, FK)
Position (VARCHAR(50))
Department (VARCHAR(50))
HireDate (DATE)
Salary (DECIMAL(10,2))
PerformanceRating (DECIMAL(3,2))
ManagerID (INT, FK)
Status (VARCHAR(20))
LastUpdated (TIMESTAMP)
```

### Transaction
```
TransactionID (INT, PK)
TransactionDate (DATE)
TransactionTime (TIME)
BranchID (INT, FK)
CustomerID (INT, FK)
ProductID (INT, FK)
Amount (DECIMAL(10,2))
TransactionTypeID (INT, FK)
EmployeeID (INT, FK)
ChannelID (INT, FK)
Status (VARCHAR(20))
LastUpdated (TIMESTAMP)
```

### Product
```
ProductID (INT, PK)
ProductName (VARCHAR(100))
ProductTypeID (INT, FK)
LaunchDate (DATE)
InterestRate (DECIMAL(5,2))
AnnualFee (DECIMAL(10,2))
MinimumBalance (DECIMAL(10,2))
TermsAndConditions (TEXT)
TargetSegmentID (INT, FK)
Status (VARCHAR(20))
LastUpdated (TIMESTAMP)
```

### Loan
```
LoanID (INT, PK)
CustomerID (INT, FK)
LoanTypeID (INT, FK)
Amount (DECIMAL(10,2))
InterestRate (DECIMAL(5,2))
Term (INT)
ApplicationDate (DATE)
ApprovalDate (DATE)
Status (VARCHAR(20))
RepaymentSchedule (VARCHAR(100))
DefaultRisk (DECIMAL(3,2))
BranchID (INT, FK)
LoanOfficerID (INT, FK)
LastUpdated (TIMESTAMP)
```

## Dimension Tables

### Region
```
RegionID (INT, PK)
RegionName (VARCHAR(100))
Country (VARCHAR(100))
LastUpdated (TIMESTAMP)
```

### CustomerSegment
```
CustomerSegmentID (INT, PK)
SegmentName (VARCHAR(50))
Description (VARCHAR(200))
LastUpdated (TIMESTAMP)
```

### TransactionType
```
TransactionTypeID (INT, PK)
TypeName (VARCHAR(50))
Description (VARCHAR(200))
LastUpdated (TIMESTAMP)
```

### ProductType
```
ProductTypeID (INT, PK)
TypeName (VARCHAR(50))
Description (VARCHAR(200))
LastUpdated (TIMESTAMP)
```

### LoanType
```
LoanTypeID (INT, PK)
TypeName (VARCHAR(50))
Description (VARCHAR(200))
LastUpdated (TIMESTAMP)
```

### Channel
```
ChannelID (INT, PK)
ChannelName (VARCHAR(50))
Description (VARCHAR(200))
LastUpdated (TIMESTAMP)
```

## Fact Tables

### TransactionFact
```
TransactionFactID (INT, PK)
TransactionID (INT, FK)
DateID (INT, FK)
BranchID (INT, FK)
CustomerID (INT, FK)
ProductID (INT, FK)
EmployeeID (INT, FK)
ChannelID (INT, FK)
TransactionTypeID (INT, FK)
Amount (DECIMAL(10,2))
Status (VARCHAR(20))
LastUpdated (TIMESTAMP)
```

### LoanFact
```
LoanFactID (INT, PK)
LoanID (INT, FK)
DateID (INT, FK)
CustomerID (INT, FK)
BranchID (INT, FK)
LoanTypeID (INT, FK)
EmployeeID (INT, FK)
Amount (DECIMAL(10,2))
InterestRate (DECIMAL(5,2))
DefaultRisk (DECIMAL(3,2))
Status (VARCHAR(20))
LastUpdated (TIMESTAMP)
```

### CustomerFact
```
CustomerFactID (INT, PK)
CustomerID (INT, FK)
DateID (INT, FK)
SegmentID (INT, FK)
RegionID (INT, FK)
TotalBalance (DECIMAL(10,2))
NumberOfProducts (INT)
SatisfactionScore (INT)
NPSScore (INT)
LastUpdated (TIMESTAMP)
```

## Time Dimension
```
DateID (INT, PK)
Date (DATE)
Year (INT)
Quarter (INT)
Month (INT)
DayOfWeek (INT)
IsHoliday (BOOLEAN)
LastUpdated (TIMESTAMP)
```

## Notes on Logical Design

1. **Normalization:**
   - All tables are normalized to 3NF
   - Surrogate keys are used for all primary keys
   - Foreign keys maintain referential integrity

2. **Data Types:**
   - Used appropriate data types for each attribute
   - Included precision for decimal fields
   - Added LastUpdated timestamp for tracking changes

3. **Fact Tables:**
   - Implemented star schema design
   - Fact tables contain measures and foreign keys to dimensions
   - Time dimension is used for temporal analysis

4. **Dimension Tables:**
   - Contains descriptive attributes
   - Used for filtering and grouping
   - Includes slowly changing dimension attributes

5. **Performance Considerations:**
   - Added appropriate indexes on foreign keys
   - Used surrogate keys for better performance
   - Included status fields for active/inactive records

This logical model will serve as the foundation for the physical database design and implementation. 