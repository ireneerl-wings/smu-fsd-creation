Based on my analysis of this SAP Functional Specification Document for the Threshold Master Data enhancement, here are the extracted requirements organized by category:

## **System Requirements**

### **Functional Requirements**
- **Enhancement Object**: D0169[JIRA:S4VRICEFW-668] for Threshold Master Data in SAP S/4HANA
- **System**: SAP (migrating from ECC to S/4HANA)
- **Stream Area**: Sales & Promotion
- **Complexity**: Very High
- **Core Function**: Implement threshold process within replenishment data pipeline sequence: PLU → Bridging UOM → Material Status → Substitution → Rasionalisasi → **Threshold** → Fair Share

### **Business Logic Requirements**
- **Threshold Validation**: System must read from Threshold table using Sales Order exit to limit customer orders for fast-moving products
- **Equal Distribution**: Ensure fair distribution among customers based on order history and remaining quantities
- **Order Splitting**: When threshold limits are partially used, split sales orders into two line items (one fulfilling remaining limit, remainder rejected with "Fairshare allocation" reason)
- **Monthly Reset**: Reset remaining limit quantities on 1st day of each month regardless of holidays

## **User Interface Requirements**

### **New Transaction Code**: ZS4SDM00XX (replacing ZTS130)
- **Excel Upload**: Upload master data using Excel template based on 'Template Master' sheet
- **CSV Upload**: Upload data using CSV file format
- **View Data**: Display data from ZSDT_M_LIMITQTY table with input parameters
- **Delete Data**: Remove master data that hasn't been transacted yet
- **Error Handling**: Display error message "Line item xxx tidak bisa diganti karena limit trader !!" when attempting to change line items in VA02 for registered threshold items

## **Data Structures**

### **Input Data Structures**

#### **Excel Template Format**:
```
Customer N | Material Number | TM1 | TD1 | TM2 | TD2 | UOM
55555      | 20030          | 500 | 50  | 1000| 10  | BOX
```

#### **Sales Order Input Parameters**:
- VBAK-AUART (Sales Order Type)
- VBAK-KUNNR (Customer Number)
- VBAP-MATNR (Material Number)
- VBAP-KWMENG (Order Quantity)
- VBAK-ERDAT (Creation Date)

### **Output/Return Data Structures**

#### **Master Table (ZSDT_M_LIMITQTY)**:
```sql
CREATE TABLE ZSDT_M_LIMITQTY (
    KUNNR      CHAR(10),    -- Customer Number
    MATNR      CHAR(18),    -- Material Number
    TM1        NUMBER,      -- Limit M1
    TD1        NUMBER,      -- Limit D1
    TM2        NUMBER,      -- Limit M2
    TD2        NUMBER,      -- Limit D2
    MEINS      CHAR(3),     -- Base Unit
    REMAIN1    NUMBER,      -- Remaining M1
    END_M1     DATE,        -- Date End M1
    REMAIN_TD1 NUMBER,      -- Remaining TD1
    REMAIN2    NUMBER,      -- Remaining M2
    END_M2     DATE,        -- Date End M2
    LAST_TD2   DATE,        -- Date Last SO TD2
    REMAIN_TD2 NUMBER,      -- Remaining TD2
    ERDAT      DATE,        -- Created on
    ERZET      TIME,        -- Created time
    ERNAM      CHAR(10),    -- Created by
    UPDAT      DATE,        -- Changed on
    UPZET      TIME,        -- Changed time
    UPNAM      CHAR(10),    -- Changed by
    COMPLETED  CHAR(1),     -- Completed flag
    PRIMARY KEY (KUNNR, MATNR)
);
```

#### **Historical Table (ZSDT_T_LIMITQTY)**:
```sql
CREATE TABLE ZSDT_T_LIMITQTY (
    VBELN       CHAR(10),   -- SO Number
    POSNR       NUMBER(5),  -- Line item SO
    KUNNR       CHAR(10),   -- Customer
    MATNR       CHAR(18),   -- Material ID
    REQ_QTY     NUMBER,     -- Qty Requested
    FULFILL_QTY NUMBER,     -- Qty Fulfilled
    MEINS       CHAR(3),    -- Base Unit
    FLAG        CHAR(3),    -- Flag TM1/TM2/TD2
    DEL_RJ      CHAR(1),    -- Deleted/Rejected
    [Additional threshold fields from master table]
    PRIMARY KEY (VBELN, POSNR)
);
```

## **Process/Workflow Requirements**

### **Sales Order Creation Workflow** (12 validation scenarios):

1. **Normal Creation**: REMAIN1 > QTY → Create SO normally, update tables
2. **Exact Match**: REMAIN1 = QTY → Create SO normally, update tables
3. **Partial Fulfillment**: REMAIN1 < QTY → Split SO into fulfilled and rejected line items
4. **Daily Limit Reached**: REMAIN1 = 0 and same day → Reject with ZPARAM REJECT_LIMIT_TRADER
5. **Secondary Threshold**: Use REMAIN2 and TD1 limits when REMAIN1 exhausted
6. **Daily Secondary Limit**: Apply TD1 splitting logic when SO quantity > TD1
7. **Secondary Exact Match**: Handle TD1 quantities ≤ limit
8. **All Limits Exhausted**: Reject when REMAIN2 = 0 and REMAIN_TD2 = 0 on same day
9. **Extended Period Access**: Allow TD2 usage when beyond END_M2 date within month
10. **TD2 Splitting**: Split orders when quantity > REMAIN_TD2
11. **TD2 Normal**: Process normally when quantity ≤ TD2
12. **Same Day Restriction**: Reject duplicate TD2 requests on same day

### **Background Job Requirements**:
- **Monthly Reset Job**: Copy TM1→REMAIN1, TM2→REMAIN2, update END_M1/END_M2
- **Real-time Processing**: Process SO creation from satellite apps (SFA, Wings Online, WingsKita, WingsMart, Portal, UIPATH, EDI)

## **Integration Requirements**

### **Source Systems**:
- **Satellite Applications**: SFA, Wings Online, WingsKita, WingsMart, Portal, UIPATH, EDI
- **SAP Integration**: Sales Order creation triggers threshold validation

### **Data Sources**:
- **Current (AS IS)**: Program ZIT_S0130_MAINTAIN_LIMITQTY_M, Tcode ZTS130
- **Target (TO BE)**: Program ZXXX, Tcode ZS4SDD00XX
- **Tables**: ZSDT_M_LIMITQTY (master), ZSDT_T_LIMITQTY (historical)

## **Security Requirements**

### **Authorization Objects**:
- **V_VBAK_VKO**: ACTIVITY: 03, VKORG: $VKORG
- **User Tracking**: All create/update operations logged with user ID and timestamp

## **Performance Requirements**

### **Processing Characteristics**:
- **Asynchronous Processing**: Sales Order creation processed asynchronously via SAP RPA
- **Delay Tolerance**: Few minutes to longer during peak periods depending on system load
- **Execution Schedule**: Monthly reset job runs early morning on 1st of each month

## **Error Handling Requirements**

### **Validation Rules**:
- **Material Change Prevention**: Block material changes in VA02 for threshold-registered items
- **Deletion Handling**: Restore threshold quantities when SO with threshold items is deleted
- **Flag-based Recovery**: Different restoration logic based on FLAG values (TM1, TM2, TD2)

### **Error Messages**:
- **Indonesian Language**: "Line item xxx tidak bisa diganti karena limit trader !!"
- **Rejection Codes**: Use ZPARAM parameter REJECT_LIMIT_TRADER for systematic rejections

## **Test Scenarios**

### **Validation Criteria**:
- **Flow Chart Compliance**: All threshold validation must follow the specified flow chart diagram
- **Data Integrity**: Verify correct updates to both master and historical tables
- **Split Order Logic**: Confirm proper line item splitting and rejection reason assignment
- **Monthly Reset**: Validate correct quantity restoration and date updates

## **Dependencies**

### **Development Dependencies**:
- **Other RICEFW**: Depends on object DXXX
- **Configuration**: Requires ZPARAM setup for rejection codes
- **Exit Development**: Sales Order exit implementation for threshold reading

### **Assumptions**:
- **SAP Exit Availability**: SAP will provide exit for Sales Order creation
- **Master Data Management**: Threshold data can be uploaded and deleted
- **Historical Reference**: Logic references both master table and historical data before SO creation

This comprehensive extraction covers all functional, technical, data, security, and operational requirements specified in the document for implementing the Threshold Master Data enhancement in SAP S/4HANA.