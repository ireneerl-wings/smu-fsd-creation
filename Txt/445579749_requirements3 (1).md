# Requirements Analysis - SAP POD Interface (E0067)

## **System Requirements**

### **Functional Requirements**
- **Interface Type**: Inbound API interface from DELMAN system to SAP S4
- **Processing Mode**: Real-time synchronous processing
- **Frequency**: Every 5 minutes
- **Complexity**: Medium complexity interface
- **Stream Area**: Distribution module
- **Middleware Required**: Yes, webservices will group DELMAN data sources into 2 interface structures

### **Non-Functional Requirements**
- **Performance**: Real-time processing with 5-minute frequency intervals
- **Reliability**: Interface must handle failed processing with reprocessing capability
- **Availability**: Must be available for continuous operation as delivery orders are goods issued

## **Interfaces / Integrations**

### **Source System Integration**
- **Source**: DELMAN (Delivery Man Apps) system
- **Target**: SAP S4 system
- **Integration Method**: API calls through middleware/webservices
- **Trigger**: Upon call from DELMAN source system
- **Dependencies**: 
  - POD Relevant configuration
  - Send Freight Data to DELMAN interface (development dependency)

### **Interface Functions**
- **ZSDT_PODALL** (requires renaming): Processes header-level delivery data (all accepted/rejected)
- **ZSDT_PODPARTIAL** (requires renaming): Processes item-level delivery data (partial rejections)

## **Data Structures**

### **Input Data Structures**

#### **ZSDT_PODALL Input**
| Field Name | Data Type | Sample | Description |
|------------|-----------|---------|-------------|
| TOR_ID | CHAR (20) | 100147109 | Freight Order No |
| VBELN | CHAR (10) | 2245907510 | Delivery No |
| KUNNR | CHAR (10) | 18765 | Customer ID |
| GRUND | CHAR (4) | H0 | Rejection Reason |
| FILE_PATH_TOKO | TEXT | 49189_93372469_250301.jpg\|140897_93373029_250308.jpg | Image file paths |

#### **ZSDT_PODPARTIAL Input**
| Field Name | Data Type | Sample | Description |
|------------|-----------|---------|-------------|
| TOR_ID | CHAR (20) | 100147109 | Freight Order No |
| VBELN | CHAR (10) | 2245907510 | Delivery No |
| POSNR | NUMC (6) | 10 | Delivery Item |
| MATNR | CHAR (40) | 10025 | Material No |
| LFIMG | QUAN (17) | 36 | Delivered Quantity |
| VRKME | UNIT | BOX | Unit of Measure |
| GRUND | CHAR (4) | H0 | Rejection Reason |
| PODAT | DATS (10) | 20250210 | POD Date |
| POTIM | TIMS (8) | 230130 | POD Time |
| KUNNR | CHAR (10) | 18765 | Customer ID |
| FILE_PATH_TOKO | TEXT | 49189_93372469_250301.jpg\|140897_93373029_250308.jpg | Image file paths |

### **Output/Return Data Structures**

#### **ZSDT_PODALL Return**
| Field Name | Data Type | Description |
|------------|-----------|-------------|
| TOR_ID | CHAR (20) | Freight Order No |
| LFART | CHAR (4) | Delivery Type |
| VBELN | CHAR (10) | Delivery No |
| KUNNR | CHAR (10) | Customer ID |
| GRUND | CHAR (4) | Rejection Reason |
| MANUAL | CHAR (1) | Manual Processing Indicator |
| ERNAM | CHAR (12) | Created By User |
| PODAT | DATUM (8) | POD Date |
| POTIM | TIME (8) | POD Time |
| SUBRC | CHAR (3) | Return Code |
| MESSAGE | STRING | Return Message |

#### **ZSDT_PODPARTIAL Return**
| Field Name | Data Type | Description |
|------------|-----------|-------------|
| TOR_ID | CHAR (20) | Freight Order No |
| LFART | CHAR (4) | Delivery Type |
| VBELN | CHAR (10) | Delivery No |
| KUNNR | CHAR (10) | Customer ID |
| PODAT | DATUM (8) | POD Date |
| POTIM | TIME (8) | POD Time |
| POSNR | NUMC (6) | Delivery Item |
| MATNR | CHAR (40) | Material No |
| LFIMG | QUAN (17) | Delivered Quantity |
| VRKME | CHAR (3) | Unit of Measure |
| GRUND | CHAR (4) | Rejection Reason |
| MANUAL | CHAR (1) | Manual Processing Indicator |
| ERNAM | CHAR (12) | Created By User |
| SUBRC | CHAR (3) | Return Code |
| MESSAGE | STRING | Return Message |

### **Database Table Structure**

#### **ZSDT_PODINT [POD Quantity from DELMAN]**
| Field Name | Data Type | Primary Key | Description | Value Field |
|------------|-----------|-------------|-------------|-------------|
| TOR_ID | CHAR (20) | Yes | Freight Order No | |
| VBELN | CHAR (10) | Yes | Delivery No | |
| POSNR | NUMC (6) | Yes | Delivery Item | |
| SUMMARY | CHAR (1) | | Summary Indicator | |
| KUNNR | CHAR (10) | | Customer ID | |
| MATNR | CHAR (4) | | Material No | |
| GRUND | CHAR (4) | | Rejection Reason | |
| LFIMG_DIFF | QUAN (17) | | Reject Quantity | |
| VRKME | CHAR | | Unit of Measure | |
| PODAT | DATS (10) | | POD Date | |
| POTIM | TIMS (8) | | POD Time | |
| IMGL | STRING | | Image Link | |
| STATS | CHAR (1) | | Status | 1-Error, 2-Success |
| ERDAT | DATS (10) | | Created On | |
| ERZET | TIMS (8) | | Created Time | |

## **Process/Workflow Steps**

### **ZSDT_PODALL Processing Logic**
1. **Data Validation**: Check if delivery order exists in LIKP table
2. **Manual Processing Check**: Verify if POD was completed manually
3. **POD Update Logic**:
   - For accepted items (GRUND = INITIAL): Update PODAT and POTIM using BAPI WS_DELIVERY_UPDATE
   - For rejected items: Update rejection data and POD information
4. **Change Document Tracking**: Get username from CDPOS and CDHDR tables for manual entries
5. **Status Update**: Update processing status in ZSDT_PODINT table
6. **Return Processing**: Return synchronous response to caller

### **ZSDT_PODPARTIAL Processing Logic**
1. **Delivery Level Processing**: Group data by delivery number
2. **Item Level Processing**: Process each delivery item with rejection quantities
3. **Batch Split Handling**: Handle batch-managed items with quantity distribution
4. **BOM Component Processing**: Handle ZTAQ/ZTAE item categories for BOM sales
5. **POD Update**: Use BAPI WS_DELIVERY_UPDATE for POD completion
6. **TVPOD Table Update**: Update rejection quantities and reasons
7. **Status Management**: Track processing status for each item

## **User Interface Requirements**

### **Selection Screen**
- **Input Fields**:
  - Freight No (S_TORID)
  - Delivery No (S_VBELN)
  - Created On (S_ERDAT)
  - Reject Only (S_REJECT)
- **Processing Options**:
  - Display Data (S_DIS)
  - Reprocess Failed Data (S_REP)

### **Display Data Functionality**
- **Data Display**: Show POD data from ZSDT_PODINT table
- **Authorization Check**: Validate user access based on freight organization
- **Image Viewing**: Pop-up screen to view images via AWS login
- **Data Summarization**: Group data by delivery number
- **Status Indicators**: Show processing status (Processed/Unprocessed)

### **Reprocess Failed Data Functionality**
- **Error Data Selection**: Get records with status = 1 (error)
- **Authorization Validation**: Check user permissions for freight orders
- **POD Reprocessing**: Re-execute POD logic for failed records
- **Status Update**: Update processing status after reprocessing

## **Security Requirements**

### **Authorization Objects**
| Authorization Object | Authorization Field | Description |
|---------------------|-------------------|-------------|
| T_TOR_EXE | ACTVT = 03 | Activity (Display) |
| T_TOR_EXE | TM_XEORG | Transportation Management Execution Organization |

### **Security Validation**
- **Freight Organization Check**: Validate EXEC_ORG_ID from /SCMTMS/D_TORROT against T_TOR_EXE authorization
- **User Access Control**: Remove unauthorized records from display
- **Image Access Security**: Require AWS login credentials for image viewing

## **Error Handling and Exception Flows**

### **Error Messages**
| Exception Description | Message Type | Language | Message Text |
|----------------------|--------------|----------|--------------|
| No Authorization | E | E | "Tidak ada otorisasi, silahkan coba hubungi bagian IT" |
| No Data Found | E | E | "Tidak ada data berdasarkan hasil pencarian" |
| Reprocessing Completed | W | E | "Proses ulang selesai dilakukan, silahkan melihat status dari menu display data" |
| No Data to Reprocess | W | E | "Tidak ada data untuk di proses ulang." |

### **Exception Handling Logic**
- **Delivery Not Found**: Return SUBRC = 100 with appropriate message
- **Manual POD Completion**: Skip processing and mark as completed
- **BAPI Failure**: Return SUBRC = 200 with BAPI error message
- **Authorization Failure**: Remove unauthorized records and show error message

## **Test Scenarios/Validation Criteria**

### **Test Cases**
| Step | Test Type | Scenario | Steps | Expected Results |
|------|-----------|----------|-------|------------------|
| 1 | POD_ALL - FULL SKR | Auto Success | Create DO, Perform Interface | POD updated, Status = 2 |
| 2 | POD_ALL - FULL SKR | Auto Fail | Create DO, Open via VLPOD, Perform Interface | POD not updated, Status = 1 |
| 3 | POD_ALL - FULL SKR | Manual POD | Create DO, Manual POD via VLPOD, Perform Interface | Skip process, Status = 2 |
| 4 | POD_ALL - Accept All | Auto Success | Create DO, Perform Interface | POD updated, Status = 2 |
| 5 | POD_ALL - Accept All | Auto Fail | Create DO, Open via VLPOD, Perform Interface | POD not updated, Status = 1 |
| 6 | POD_ALL - Accept All | Manual POD | Create DO, Manual POD, Perform Interface | Skip process, Status = 2 |
| 7 | POD_PARTIAL | Auto Success | Create DO, Perform Interface | POD updated, Status = 2 |
| 8 | POD_PARTIAL | Auto Fail | Create DO, Open via VLPOD, Perform Interface | POD not updated, Status = 1 |
| 9 | POD_PARTIAL | Manual POD | Create DO, Manual POD, Perform Interface | Skip process, Status = 2 |

## **Assumptions and Constraints**

### **Assumptions**
- DELMAN system will only send each record once
- FULL SKR due to "TOKO TUTUP" will only be sent during Security IN process
- POD Relevant configuration is properly set up

### **Constraints**
- Interface requires middleware for data grouping
- Real-time processing may fail and requires reprocessing capability
- Manual POD completion takes longer due to batch management
- AWS credentials required for image viewing functionality

### **Risks**
- Delay in waiting time for truck arrival from transport to warehouse
- Manual POD processing takes longer due to batch management requirements