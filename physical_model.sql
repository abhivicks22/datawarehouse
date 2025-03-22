-- Bank Data Warehouse - Physical Data Model
-- PostgreSQL Implementation

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_partman";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS dimension;
CREATE SCHEMA IF NOT EXISTS fact;

-- Core Entities

-- Branch Table
CREATE TABLE core.branch (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    region_id INTEGER NOT NULL,
    manager_id INTEGER,
    open_date DATE NOT NULL,
    operating_hours VARCHAR(100),
    square_footage INTEGER,
    number_of_tellers INTEGER,
    number_of_atms INTEGER,
    operational_cost DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_region FOREIGN KEY (region_id) REFERENCES dimension.region(region_id),
    CONSTRAINT fk_manager FOREIGN KEY (manager_id) REFERENCES core.employee(employee_id)
);

-- Customer Table
CREATE TABLE core.customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    customer_segment_id INTEGER NOT NULL,
    acquisition_date DATE NOT NULL,
    last_interaction_date TIMESTAMP,
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 0 AND 10),
    nps_score INTEGER CHECK (nps_score BETWEEN 0 AND 10),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_segment FOREIGN KEY (customer_segment_id) REFERENCES dimension.customer_segment(customer_segment_id)
);

-- Employee Table
CREATE TABLE core.employee (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    branch_id INTEGER NOT NULL,
    position VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    performance_rating DECIMAL(3,2) CHECK (performance_rating BETWEEN 0 AND 5),
    manager_id INTEGER,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_branch FOREIGN KEY (branch_id) REFERENCES core.branch(branch_id),
    CONSTRAINT fk_manager FOREIGN KEY (manager_id) REFERENCES core.employee(employee_id)
);

-- Transaction Table (Partitioned by date)
CREATE TABLE core.transaction (
    transaction_id SERIAL,
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    branch_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'COMPLETED',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_transaction PRIMARY KEY (transaction_id, transaction_date),
    CONSTRAINT fk_branch FOREIGN KEY (branch_id) REFERENCES core.branch(branch_id),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES core.customer(customer_id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES core.product(product_id),
    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES core.employee(employee_id),
    CONSTRAINT fk_transaction_type FOREIGN KEY (transaction_type_id) REFERENCES dimension.transaction_type(transaction_type_id),
    CONSTRAINT fk_channel FOREIGN KEY (channel_id) REFERENCES dimension.channel(channel_id)
) PARTITION BY RANGE (transaction_date);

-- Create partitions for transaction table
CREATE TABLE core.transaction_y2023m01 PARTITION OF core.transaction
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
CREATE TABLE core.transaction_y2023m02 PARTITION OF core.transaction
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');
-- Add more partitions as needed

-- Product Table
CREATE TABLE core.product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    product_type_id INTEGER NOT NULL,
    launch_date DATE NOT NULL,
    interest_rate DECIMAL(5,2),
    annual_fee DECIMAL(10,2),
    minimum_balance DECIMAL(10,2),
    terms_and_conditions TEXT,
    target_segment_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_type FOREIGN KEY (product_type_id) REFERENCES dimension.product_type(product_type_id),
    CONSTRAINT fk_target_segment FOREIGN KEY (target_segment_id) REFERENCES dimension.customer_segment(customer_segment_id)
);

-- Loan Table (Partitioned by date)
CREATE TABLE core.loan (
    loan_id SERIAL,
    customer_id INTEGER NOT NULL,
    loan_type_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    term INTEGER NOT NULL,
    application_date DATE NOT NULL,
    approval_date DATE,
    status VARCHAR(20) DEFAULT 'PENDING',
    repayment_schedule VARCHAR(100),
    default_risk DECIMAL(3,2) CHECK (default_risk BETWEEN 0 AND 1),
    branch_id INTEGER NOT NULL,
    loan_officer_id INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_loan PRIMARY KEY (loan_id, application_date),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES core.customer(customer_id),
    CONSTRAINT fk_loan_type FOREIGN KEY (loan_type_id) REFERENCES dimension.loan_type(loan_type_id),
    CONSTRAINT fk_branch FOREIGN KEY (branch_id) REFERENCES core.branch(branch_id),
    CONSTRAINT fk_loan_officer FOREIGN KEY (loan_officer_id) REFERENCES core.employee(employee_id)
) PARTITION BY RANGE (application_date);

-- Create partitions for loan table
CREATE TABLE core.loan_y2023m01 PARTITION OF core.loan
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
CREATE TABLE core.loan_y2023m02 PARTITION OF core.loan
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');
-- Add more partitions as needed

-- Dimension Tables

-- Region Table
CREATE TABLE dimension.region (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer Segment Table
CREATE TABLE dimension.customer_segment (
    customer_segment_id SERIAL PRIMARY KEY,
    segment_name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Type Table
CREATE TABLE dimension.transaction_type (
    transaction_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Type Table
CREATE TABLE dimension.product_type (
    product_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loan Type Table
CREATE TABLE dimension.loan_type (
    loan_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Channel Table
CREATE TABLE dimension.channel (
    channel_id SERIAL PRIMARY KEY,
    channel_name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time Dimension Table
CREATE TABLE dimension.date_dim (
    date_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    is_holiday BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact Tables

-- Transaction Fact Table (Partitioned by date)
CREATE TABLE fact.transaction_fact (
    transaction_fact_id SERIAL,
    transaction_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    transaction_type_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'COMPLETED',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_transaction_fact PRIMARY KEY (transaction_fact_id, date_id),
    CONSTRAINT fk_transaction FOREIGN KEY (transaction_id) REFERENCES core.transaction(transaction_id),
    CONSTRAINT fk_date FOREIGN KEY (date_id) REFERENCES dimension.date_dim(date_id),
    CONSTRAINT fk_branch FOREIGN KEY (branch_id) REFERENCES core.branch(branch_id),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES core.customer(customer_id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES core.product(product_id),
    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES core.employee(employee_id),
    CONSTRAINT fk_channel FOREIGN KEY (channel_id) REFERENCES dimension.channel(channel_id),
    CONSTRAINT fk_transaction_type FOREIGN KEY (transaction_type_id) REFERENCES dimension.transaction_type(transaction_type_id)
) PARTITION BY RANGE (date_id);

-- Create partitions for transaction fact table
CREATE TABLE fact.transaction_fact_y2023m01 PARTITION OF fact.transaction_fact
    FOR VALUES FROM (20230101) TO (20230201);
CREATE TABLE fact.transaction_fact_y2023m02 PARTITION OF fact.transaction_fact
    FOR VALUES FROM (20230201) TO (20230301);
-- Add more partitions as needed

-- Loan Fact Table (Partitioned by date)
CREATE TABLE fact.loan_fact (
    loan_fact_id SERIAL,
    loan_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    loan_type_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    default_risk DECIMAL(3,2) CHECK (default_risk BETWEEN 0 AND 1),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_loan_fact PRIMARY KEY (loan_fact_id, date_id),
    CONSTRAINT fk_loan FOREIGN KEY (loan_id) REFERENCES core.loan(loan_id),
    CONSTRAINT fk_date FOREIGN KEY (date_id) REFERENCES dimension.date_dim(date_id),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES core.customer(customer_id),
    CONSTRAINT fk_branch FOREIGN KEY (branch_id) REFERENCES core.branch(branch_id),
    CONSTRAINT fk_loan_type FOREIGN KEY (loan_type_id) REFERENCES dimension.loan_type(loan_type_id),
    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES core.employee(employee_id)
) PARTITION BY RANGE (date_id);

-- Create partitions for loan fact table
CREATE TABLE fact.loan_fact_y2023m01 PARTITION OF fact.loan_fact
    FOR VALUES FROM (20230101) TO (20230201);
CREATE TABLE fact.loan_fact_y2023m02 PARTITION OF fact.loan_fact
    FOR VALUES FROM (20230201) TO (20230301);
-- Add more partitions as needed

-- Customer Fact Table (Partitioned by date)
CREATE TABLE fact.customer_fact (
    customer_fact_id SERIAL,
    customer_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    segment_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    total_balance DECIMAL(10,2) NOT NULL,
    number_of_products INTEGER NOT NULL,
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 0 AND 10),
    nps_score INTEGER CHECK (nps_score BETWEEN 0 AND 10),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_customer_fact PRIMARY KEY (customer_fact_id, date_id),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES core.customer(customer_id),
    CONSTRAINT fk_date FOREIGN KEY (date_id) REFERENCES dimension.date_dim(date_id),
    CONSTRAINT fk_segment FOREIGN KEY (segment_id) REFERENCES dimension.customer_segment(customer_segment_id),
    CONSTRAINT fk_region FOREIGN KEY (region_id) REFERENCES dimension.region(region_id)
) PARTITION BY RANGE (date_id);

-- Create partitions for customer fact table
CREATE TABLE fact.customer_fact_y2023m01 PARTITION OF fact.customer_fact
    FOR VALUES FROM (20230101) TO (20230201);
CREATE TABLE fact.customer_fact_y2023m02 PARTITION OF fact.customer_fact
    FOR VALUES FROM (20230201) TO (20230301);
-- Add more partitions as needed

-- Create Indexes

-- Branch Indexes
CREATE INDEX idx_branch_region ON core.branch(region_id);
CREATE INDEX idx_branch_manager ON core.branch(manager_id);

-- Customer Indexes
CREATE INDEX idx_customer_segment ON core.customer(customer_segment_id);
CREATE INDEX idx_customer_status ON core.customer(status);

-- Employee Indexes
CREATE INDEX idx_employee_branch ON core.employee(branch_id);
CREATE INDEX idx_employee_manager ON core.employee(manager_id);
CREATE INDEX idx_employee_status ON core.employee(status);

-- Transaction Indexes
CREATE INDEX idx_transaction_date ON core.transaction(transaction_date);
CREATE INDEX idx_transaction_customer ON core.transaction(customer_id);
CREATE INDEX idx_transaction_branch ON core.transaction(branch_id);
CREATE INDEX idx_transaction_product ON core.transaction(product_id);

-- Loan Indexes
CREATE INDEX idx_loan_date ON core.loan(application_date);
CREATE INDEX idx_loan_customer ON core.loan(customer_id);
CREATE INDEX idx_loan_branch ON core.loan(branch_id);
CREATE INDEX idx_loan_officer ON core.loan(loan_officer_id);

-- Fact Table Indexes
CREATE INDEX idx_transaction_fact_date ON fact.transaction_fact(date_id);
CREATE INDEX idx_transaction_fact_customer ON fact.transaction_fact(customer_id);
CREATE INDEX idx_transaction_fact_branch ON fact.transaction_fact(branch_id);

CREATE INDEX idx_loan_fact_date ON fact.loan_fact(date_id);
CREATE INDEX idx_loan_fact_customer ON fact.loan_fact(customer_id);
CREATE INDEX idx_loan_fact_branch ON fact.loan_fact(branch_id);

CREATE INDEX idx_customer_fact_date ON fact.customer_fact(date_id);
CREATE INDEX idx_customer_fact_segment ON fact.customer_fact(segment_id);
CREATE INDEX idx_customer_fact_region ON fact.customer_fact(region_id);

-- Create Materialized Views

-- Monthly Branch Performance
CREATE MATERIALIZED VIEW fact.monthly_branch_performance AS
SELECT 
    b.branch_id,
    b.branch_name,
    d.year,
    d.month,
    COUNT(DISTINCT tf.transaction_id) as transaction_count,
    SUM(tf.amount) as total_transaction_amount,
    AVG(tf.amount) as avg_transaction_amount
FROM fact.transaction_fact tf
JOIN core.branch b ON tf.branch_id = b.branch_id
JOIN dimension.date_dim d ON tf.date_id = d.date_id
GROUP BY b.branch_id, b.branch_name, d.year, d.month;

-- Monthly Customer Segment Performance
CREATE MATERIALIZED VIEW fact.monthly_segment_performance AS
SELECT 
    cs.segment_name,
    d.year,
    d.month,
    COUNT(DISTINCT cf.customer_id) as customer_count,
    AVG(cf.total_balance) as avg_balance,
    AVG(cf.satisfaction_score) as avg_satisfaction
FROM fact.customer_fact cf
JOIN dimension.customer_segment cs ON cf.segment_id = cs.customer_segment_id
JOIN dimension.date_dim d ON cf.date_id = d.date_id
GROUP BY cs.segment_name, d.year, d.month;

-- Refresh Materialized Views Function
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW fact.monthly_branch_performance;
    REFRESH MATERIALIZED VIEW fact.monthly_segment_performance;
END;
$$ LANGUAGE plpgsql;

-- Create Partition Management Function
CREATE OR REPLACE FUNCTION create_monthly_partition(
    p_table text,
    p_date date
)
RETURNS void AS $$
DECLARE
    v_partition_name text;
    v_start_date date;
    v_end_date date;
BEGIN
    v_start_date := date_trunc('month', p_date);
    v_end_date := v_start_date + interval '1 month';
    v_partition_name := p_table || '_y' || to_char(v_start_date, 'YYYYmMM');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
        v_partition_name,
        p_table,
        v_start_date,
        v_end_date
    );
END;
$$ LANGUAGE plpgsql; 