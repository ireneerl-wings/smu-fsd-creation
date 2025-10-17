# Extracted Requirements from SAP Functional Specification Document

## **System Requirements**

### **Functional Requirements**
- **Custom Program Development**: Create a custom program in SAP S/4 Hana to support outbound data to Blue Yonder
- **Processing Modes**: Support both manual trigger (foreground process) and periodic job (background process)
- **Six Outbound Data Types**:
  1. Transmode
  2. Vehicle load (header)
  3. Vehicle load line (item)
  4. Vehicle load text
  5. Actual in transit detail
  6. Last mile data
- **Document Flow Support**: Handle two types of document flows:
  - SO → DO (w/ or w/o PGI) → FO → FB (optional) → FO (optional) → PO/PO STO → GR
  - PO STO → DO (w/ or w/o PGI) → FO → GR PO STO
- **Load ID Determination**: Complex logic to determine which document serves as Load ID based on document status, quantities, and business rules
- **Data Aggregation**: Sum quantities for same material and batch combinations within one Load ID
- **Unit Conversion**: Convert quantities to sales units with 3-decimal precision limit

### **Non-Functional Requirements**
- **Complexity Level**: Very High
- **Processing Type**: Synchronous
- **Processing Mode**: Batch
- **Interface Type**: API
- **Frequency**: Daily
- **Expected System Load**: 
  - Average Load: Daily
  - Peak demand timing: 2AM (periodic background job)

## **Interfaces and Integrations**

### **External Systems**
- **Blue Yonder System**: Target system for outbound data
- **AWS S3**: File storage destination for generated TXT files
- **Email System**: For success/error notifications

### **Interface Configuration**
- **Outbound Interface**: B0149 - Outbound Interface Blueyonder Transaction
- **Stream Area**: Distribution
- **Processing Options**:
  - Outbound: Yes
  - Batch: Yes
  - Synchronous: Yes
  - API: Yes
  - Daily frequency: Yes

## **Data Sources and Data Structures**

### **Input Data Sources (SAP Tables)**
- **VBAK**: SO header
- **VBAP**: SO item
- **VBFA**: Document flow
- **LIKP**: DO header
- **LIPS**: DO item
- **EKKO**: PO & PO STO header
- **EKPO**: PO & PO STO item
- **EKPV**: PO & PO STO shipping data
- **ZSDT_INTERCO**: Intercompany document flow
- **/SCMTMS/D_TORROT**: FO header level
- **/SCMTMS/D_TOREXE**: FO execution data with event
- **/SCMTMS/D_TORITE**: FO item level
- **/SCMTMS/D_TORSTP**: FO location
- **/SCMTMS/D_TORDRF**: FO reference
- **ZZXT_BY_LOCF_H**: Blueyonder location fulfillment
- **ZZXT_BY_ITEM**: Blueyonder master item
- **ZSDT_LOG_DELIVOP**: Log Delivery Optimization
- **MCH1**: Batch master data
- **MVKE**: Material sales data
- **BUT000**: Business partner data
- **TVARVC**: System variables
- **ZZXT_BY_EXINTRA**: Exception master Blue Yonder
- **ZZXT_EMAIL_REC**: Email recipients configuration

### **Input Parameters Structure**
| Field Label | Data Type/Size | Mandatory | Reference Table | Field Control Type |
|-------------|----------------|-----------|-----------------|-------------------|
| Coverage User | CHAR 3 | Yes | Custom selection range: SMUWGOWS | Input value within search help |
| Plant + Sloc | CHAR 8 | No | N/A | Free text |
| Division | CHAR 2 | No | VBAK-SPART | Check table TVTA |
| Creation Range days | NUM 3 | Yes | N/A | Integer only |
| PGI Range days | NUM 3 | Yes | N/A | Integer only |
| SO type | CHAR 4 | No | VBAK-AUART | Check table TVAK |
| SO return type | CHAR 4 | No | VBAK-AUART | Check table TVAK |
| SO type MTO | CHAR 4 | No | VBAK-AUART | Check table TVAK |
| PO STO type | CHAR 4 | No | EKKO-BSART | Check table T161 |
| FO type | CHAR 10 | No | /SCMTMS/D_TORROT-TOR_TYPE | Check table /SCMTMS/C_TORTY |
| FB type | CHAR 10 | No | /SCMTMS/D_TORROT-TOR_TYPE | Check table /SCMTMS/C_TORTY |

### **Output Data Structures**

#### **Vehicle Load Header**
| Field Name | Data Type | Length | Description | Source/Formula |
|------------|-----------|--------|-------------|----------------|
| LOADID | CHAR | 20 | Document no. Blueyonder | Formula: C/A-(document number)-1/3 |
| SOURCE | CHAR | 8 | Source Location | Plant + Storage Location |
| DEST | CHAR | 8 | Destination Location | Plant + Storage Location |
| SHIPDATE | DATS | 8 | Shipment Date | DD/MM/YYYY format |
| ARRIVDATE | DATS | 8 | Arrive Date | DD/MM/YYYY format |
| TRANSMODE | CHAR | 10 | Transportation Mode | From FO data |
| DOC_NO | CHAR | 20 | Document Number | Load ID document number |
| SO_NO | CHAR | 10 | SO number | From SO data |
| POSTO_NO | CHAR | 10 | POSTO number | From PO STO data |
| DELIV_NO | CHAR | 10 | Delivery Number | From delivery data |
| FO_NO_FIRST | CHAR | 20 | Freight Order Number 1 | Earliest FO number |
| FO_NO_LAST | CHAR | 20 | Freight Order Number 2 | Latest FO number |
| PO_NO | CHAR | 10 | PO Number | From PO data |

#### **Vehicle Load Line**
| Field Name | Data Type | Length | Description | Source/Formula |
|------------|-----------|--------|-------------|----------------|
| LOADID | CHAR | 20 | Document no. Blueyonder | Same as header |
| ITEM | CHAR | 40 | Material number | From material data |
| QTY | QUAN | 13,3 | Quantity in sales unit | Calculated quantity |
| EXPDATE | DATS | 8 | Expired date | SHIPDATE + 3 years |
| PRIMARYITEM | CHAR | 40 | Material number | Same as ITEM |
| BATCHNUMBER | CHAR | 10 | Batch number | From delivery data |
| PRODDATE | DATS | 8 | Production date | From batch master |

#### **Vehicle Load Text**
| Field Name | Data Type | Length | Description | Source/Formula |
|------------|-----------|--------|-------------|----------------|
| LOADID | CHAR | 20 | Document no. Blueyonder | FO documents only |
| FreightOrder | CHAR | 20 | Freight Order number | Latest FO number |
| LicensePlate | CHAR | 10 | License Plate | From FO data |

#### **Actual In Transit Detail**
Contains all Vehicle Load fields plus additional fields:
- WeightinTon (QUAN 31,14): FO Gross weight in MT
- VolumeinM3 (QUAN 31,14): FO Gross volume in M3
- ETD/ATD/ETA/ATA (DATS 8): Various time stamps
- Vendor (CHAR 80): Vendor Carrier Name
- Container (CHAR 20): Container number
- Pre Confirmed Date (DATS 8): Pre-confirmation date

#### **Last Mile Data**
| Field Name | Data Type | Length | Description | Source/Formula |
|------------|-----------|--------|-------------|----------------|
| LOADID | CHAR | 20 | Document no. Blueyonder | C-(SO status)-(Source Location) |
| SOURCE | CHAR | 8 | Source Location | Plant + Storage Location |
| DEST | CHAR | 8 | Destination Location | [Coverage User]+DUMMY |
| ITEM | CHAR | 40 | Material number | From material data |
| QTY | QUAN | 13,3 | Quantity in sales unit | Calculated quantity |

## **Process and Workflow Steps**

### **Data Selection Process**
1. **Coverage User to Location Fulfillment**: Get plant and storage location list
2. **Material Selection**: Get material list from master item (Blueyonder) excluding discontinued materials
3. **Document Collection**: Collect SO/PO STO documents with filtering
4. **Delivery Data Collection**: Get delivery documents from SO/PO STO
5. **Freight Order Collection**: Get FO information linked with deliveries
6. **Freight Booking Collection**: Get FB information linked with deliveries
7. **PO Document Collection**: Get PO documents from FO
8. **Load ID Determination**: Apply complex business rules to determine Load ID
9. **Data Aggregation**: Group and sum data as required
10. **File Generation**: Create TXT files with proper formatting
11. **File Transmission**: Send files to AWS S3

### **Load ID Determination Logic**
1. Check SO item rejection reason - exclude if not empty
2. Compare SO quantity with delivery quantity - exclude if equal or delivery complete
3. Apply checkbox CH2 validation for SO exclusion
4. Check PO STO quantity and deletion indicator
5. Verify GR PO/PO STO status - exclude if complete
6. Handle delivery without FO as Load ID
7. Select latest FO for multiple FO scenarios

### **File Generation Process**
1. **File Naming Convention**:
   - Normal: [Coverage User]_[DATA_TYPE]_YYYYMMDD.TXT
   - Substitution: [Coverage User]_SUB[DATA_TYPE]_YYYYMMDD.TXT
2. **File Format**: CSV with quoted fields and comma separators
3. **File Transmission**: Upload to AWS S3 Blueyonder bucket

## **Test Scenarios and Validation Criteria**

### **Functional Unit Test Scenarios**
| Step | Test Type | Scenario | Expected Results |
|------|-----------|----------|------------------|
| 1 | Outbound data | Vehicle load data trigger | Generate 3 TXT files (header, line, text) to AWS S3 |
| 2 | Outbound data | Actual in transit detail trigger | Generate 1 TXT file to AWS S3 |
| 3 | Outbound data | Last mile data trigger | Generate 1 TXT file to AWS S3 |

### **Validation Rules**
- Material must exist in Blueyonder master item
- Plant/Storage location must exist in location fulfillment
- Coverage user must be valid (SMU, WS, WGO)
- Quantities must be converted to sales units
- Dates must be in DD/MM/YYYY format
- Decimal precision limited to 3 digits

## **Error Handling and Exception Flows**

### **Error Notification System**
- **Email Recipients**: Retrieved from ZZXT_EMAIL_REC table based on application code and coverage user
- **Error Email Subject**: [ERROR] [Job Name] Terminated - Immediate Attention Required
- **Success Email Subject**: [SUCCESS] [Job Name] Finished Successfully | DD-MMM-YYYY

### **Exception Handling**
- **Unit Conversion Failures**: Fallback to original quantity
- **Missing Data**: Skip records with critical missing information
- **File Generation Errors**: Send error notifications to configured recipients
- **AWS S3 Upload Failures**: Log errors and notify administrators

### **Data Exclusions**
- Materials with status 'C0' (discontinued)
- Delivery items in exception master (ZZXT_BY_EXINTRA)
- Documents with completed GR status
- SO items with rejection reasons
- PO STO items with deletion indicators

## **Security Requirements**

### **Access Control**
- **User Access**: Program available only to IT team
- **Usage**: Setup periodic background jobs or manual trigger jobs
- **Authorization**: Restricted access for job configuration and execution

### **Data Security**
- **File Transmission**: Secure upload to AWS S3
- **Data Filtering**: Coverage user-based data segregation
- **Audit Trail**: Log all data transmissions and errors

## **Performance and Scalability Requirements**

### **Scheduling Requirements**
- **Daily Jobs**: 
  - 2 AM for regular data transmission
  - 2 PM for substitution/addition indicator data
- **On-demand Execution**: Manual trigger capability
- **Job Dependencies**: BY-M0004 - Create ZXMANU Loc Fulf

### **Data Volume Handling**
- **Creation Range**: Default 90 days for document selection
- **PGI Range**: Default 90 days for PGI date filtering
- **Batch Processing**: Handle large data volumes efficiently
- **Memory Management**: Optimize internal table processing

## **Dependencies and Assumptions**

### **Development Dependencies**
- **BY-M0004**: Create ZXMANU Loc Fulf (required before testing and execution)

### **System Assumptions**
- Sales transaction documents already created in SAP S/4 Hana
- Intercompany documents triggered from t-code ZS4SDT0002 and saved in ZSDT_INTERCO
- Location fulfillment and master item maintained in SAP Fiori Blueyonder menus

### **Configuration Dependencies**
- Blueyonder location fulfillment configuration
- Master item configuration in Blueyonder
- Email recipient configuration in ZZXT_EMAIL_REC
- System variables in TVARVC (dummy material configuration)

## **User Interaction Requirements**

### **Selection Screen Parameters**
- **Outbound Data Type**: Radio button selection (4 options)
- **Input Parameters**: 12 configurable fields with validation
- **Checkboxes**: 2 optional processing flags
- **Field Validation**: Mandatory field checking and reference table validation

### **Screen Variants**
- **Background Job Setup**: Use screen variants for automated execution
- **Coverage User Specific**: Different variants for SMU, WS, WGO users
- **Processing Options**: Separate variants for normal vs. substitution data