# Bank Data Warehouse - Conceptual Data Model

## Entities and Their Relationships

```
[Branch] --(has many)--> [Employee]
[Branch] --(has many)--> [ATM]
[Branch] --(located in)--> [Region]
[Branch] --(processes many)--> [Transaction]

[Customer] --(performs many)--> [Transaction]
[Customer] --(belongs to)--> [Segment]
[Customer] --(applies for many)--> [Loan]
[Customer] --(purchases many)--> [Product]
[Customer] --(visits many)--> [Branch]
[Customer] --(provides)--> [Satisfaction]

[Employee] --(works at)--> [Branch]
[Employee] --(processes many)--> [Transaction]
[Employee] --(manages many)--> [Loan]
[Employee] --(sells many)--> [Product]

[Transaction] --(processed at)--> [Branch]
[Transaction] --(involves)--> [Product]
[Transaction] --(performed by)--> [Customer]
[Transaction] --(processed by)--> [Employee]
[Transaction] --(categorized as)--> [TransactionType]

[Product] --(sold at many)--> [Branch]
[Product] --(purchased by many)--> [Customer]
[Product] --(belongs to)--> [ProductCategory]
[Product] --(promoted in many)--> [MarketingCampaign]

[Loan] --(applied at)--> [Branch]
[Loan] --(issued to)--> [Customer]
[Loan] --(managed by)--> [Employee]
[Loan] --(categorized as)--> [LoanType]

[MarketingCampaign] --(targets many)--> [Customer]
[MarketingCampaign] --(promotes many)--> [Product]
[MarketingCampaign] --(runs in many)--> [Region]

[Region] --(contains many)--> [Branch]
[Region] --(has)--> [Demographics]
[Region] --(has)--> [EconomicIndicators]
[Region] --(has many)--> [Competitor]
```

## Entity Descriptions

### Branch
Represents physical bank locations where customers can perform transactions, meet with staff, and access banking services.

### Customer
Individuals or businesses that maintain accounts with the bank and utilize various banking services.

### Employee
Bank staff members who work at branches and serve customers in various capacities.

### Transaction
Represents a financial activity such as deposits, withdrawals, transfers, payments, or fees.

### Product
Financial offerings provided by the bank, such as checking accounts, savings accounts, credit cards, or investment products.

### Loan
Credit facilities provided to customers, such as mortgages, auto loans, personal loans, or business loans.

### MarketingCampaign
Promotional activities designed to attract new customers or encourage existing customers to purchase additional products.

### Region
Geographical areas used for organizing branches and analyzing performance across different locations.

### Segment
Customer classifications based on demographics, behavior, profitability, or other characteristics.

### ATM
Automated Teller Machines that provide self-service banking options.

### TransactionType
Categories of financial activities (deposit, withdrawal, transfer, payment, fee, etc.).

### ProductCategory
Classifications of bank products (deposit account, credit product, investment, insurance, etc.).

### LoanType
Categories of loan products (mortgage, auto loan, personal loan, business loan, etc.).

### Satisfaction
Customer feedback and satisfaction measurements.

### Demographics
Population statistics and characteristics for different regions.

### EconomicIndicators
Economic data points that influence banking activities in different regions.

### Competitor
Other financial institutions operating in the same markets as the bank.

## Notes on Conceptual Design

This conceptual model:
- Focuses on business entities rather than database tables
- Shows relationships between entities without specifying cardinality details
- Establishes the foundation for the logical data model
- Aligns with the business requirements document
- Captures all data sources identified in the data sources document

In a real-world implementation, this would be visualized as an Entity-Relationship Diagram (ERD) using a tool like Draw.io or Lucidchart. 