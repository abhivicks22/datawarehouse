# Bank Data Warehouse - Data Sources

## Core Banking System
**Format:** Relational Database (SQL Server)
**Refresh Rate:** Daily
**Sample Fields:**
- TransactionID (INT)
- TransactionDate (DATETIME)
- TransactionTime (TIME)
- BranchID (INT)
- CustomerID (INT)
- ProductID (INT)
- Amount (DECIMAL)
- TransactionType (VARCHAR)
- EmployeeID (INT)
- ChannelID (INT)

## Customer Relationship Management (CRM)
**Format:** Cloud-based API (JSON)
**Refresh Rate:** Daily
**Sample Fields:**
- CustomerID (INT)
- FirstName (VARCHAR)
- LastName (VARCHAR)
- DateOfBirth (DATE)
- Address (VARCHAR)
- City (VARCHAR)
- State (VARCHAR)
- ZipCode (VARCHAR)
- Email (VARCHAR)
- Phone (VARCHAR)
- CustomerSegment (VARCHAR)
- AcquisitionDate (DATE)
- LastInteractionDate (DATETIME)
- SatisfactionScore (INT)
- NPSScore (INT)

## Human Resources System
**Format:** Relational Database (MySQL)
**Refresh Rate:** Weekly
**Sample Fields:**
- EmployeeID (INT)
- FirstName (VARCHAR)
- LastName (VARCHAR)
- BranchID (INT)
- Position (VARCHAR)
- Department (VARCHAR)
- HireDate (DATE)
- Salary (DECIMAL)
- PerformanceRating (DECIMAL)
- ManagerID (INT)

## Loan Processing System
**Format:** Relational Database (Oracle)
**Refresh Rate:** Daily
**Sample Fields:**
- LoanID (INT)
- CustomerID (INT)
- LoanType (VARCHAR)
- Amount (DECIMAL)
- InterestRate (DECIMAL)
- Term (INT)
- ApplicationDate (DATE)
- ApprovalDate (DATE)
- Status (VARCHAR)
- RepaymentSchedule (VARCHAR)
- DefaultRisk (DECIMAL)
- BranchID (INT)
- LoanOfficerID (INT)

## Branch Management System
**Format:** Flat Files (CSV)
**Refresh Rate:** Monthly
**Sample Fields:**
- BranchID (INT)
- BranchName (VARCHAR)
- Address (VARCHAR)
- City (VARCHAR)
- State (VARCHAR)
- ZipCode (VARCHAR)
- Region (VARCHAR)
- ManagerID (INT)
- OpenDate (DATE)
- OperatingHours (VARCHAR)
- SquareFootage (INT)
- NumberOfTellers (INT)
- NumberOfATMs (INT)
- OperationalCost (DECIMAL)

## Product Catalog
**Format:** Relational Database (PostgreSQL)
**Refresh Rate:** Weekly
**Sample Fields:**
- ProductID (INT)
- ProductName (VARCHAR)
- ProductType (VARCHAR)
- LaunchDate (DATE)
- InterestRate (DECIMAL)
- AnnualFee (DECIMAL)
- MinimumBalance (DECIMAL)
- TermsAndConditions (TEXT)
- TargetSegment (VARCHAR)
- MarketingCampaignID (INT)

## Marketing Campaign System
**Format:** API (JSON)
**Refresh Rate:** Weekly
**Sample Fields:**
- CampaignID (INT)
- CampaignName (VARCHAR)
- StartDate (DATE)
- EndDate (DATE)
- Budget (DECIMAL)
- TargetSegment (VARCHAR)
- TargetRegion (VARCHAR)
- ChannelMix (VARCHAR)
- CampaignType (VARCHAR)
- ProductID (INT)
- Impressions (INT)
- Conversions (INT)
- ConversionRate (DECIMAL)
- CostPerAcquisition (DECIMAL)

## ATM Transaction System
**Format:** Log Files (Text)
**Refresh Rate:** Daily
**Sample Fields:**
- ATMId (INT)
- TransactionID (INT)
- TransactionDate (DATE)
- TransactionTime (TIME)
- CustomerID (INT)
- TransactionType (VARCHAR)
- Amount (DECIMAL)
- ResponseCode (VARCHAR)
- CardType (VARCHAR)
- BranchID (INT)

## External Data Sources

### Economic Indicators
**Format:** API (JSON)
**Refresh Rate:** Quarterly
**Sample Fields:**
- IndicatorName (VARCHAR)
- Region (VARCHAR)
- Date (DATE)
- Value (DECIMAL)
- Source (VARCHAR)

### Competitor Data
**Format:** Flat Files (CSV)
**Refresh Rate:** Quarterly
**Sample Fields:**
- CompetitorName (VARCHAR)
- ProductType (VARCHAR)
- InterestRate (DECIMAL)
- Fee (DECIMAL)
- MarketShare (DECIMAL)
- CustomerSatisfaction (DECIMAL)
- Region (VARCHAR)

### Demographic Data
**Format:** Flat Files (CSV)
**Refresh Rate:** Annually
**Sample Fields:**
- ZipCode (VARCHAR)
- Population (INT)
- MedianIncome (DECIMAL)
- MedianAge (DECIMAL)
- EducationLevel (VARCHAR)
- HousingCost (DECIMAL)
- BusinessCount (INT)

## Sample Dataset Options

1. **Synthetic Data Generation:**
   - Use Python's Faker library to generate realistic banking data
   - Create relationships between entities to reflect real-world scenarios

2. **Public Datasets:**
   - Kaggle Banking Datasets (anonymized transaction data)
   - Federal Reserve Economic Data (FRED)
   - FDIC banking statistics

3. **Open-Source Banking Simulation:**
   - Generate transactions based on statistical models
   - Simulate customer behavior patterns 