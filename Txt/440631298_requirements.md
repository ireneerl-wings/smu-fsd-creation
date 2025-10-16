Based on my analysis of the SAP Functional Specification Document for Interface C0331 "OUT I/F Reservation - Summary", here are the extracted requirements organized by category:

## **System Requirements**

### **Functional Requirements**
- **Primary Function**: Retrieve data from SAP for list of reservations that need to be processed and output information for satellite apps
- **Interface Type**: Outbound API interface from SAP to satellite applications
- **Processing Mode**: Real-time, synchronous processing
- **Frequency**: On-demand execution triggered by satellite apps
- **Complexity Level**: Low complexity interface
- **Stream Area**: Warehouse management operations

### **Non-Functional Requirements**
- **Performance**: Must handle average daily load as specified by system usage
- **Availability**: Real-time availability for on-demand requests
- **Response Format**: JSON structure with standardized field mappings

## **Interfaces / Integrations**

### **API Specifications**
- **API Name**: ZWMAPI_GET_RESERVATION_O4
- **Method**: POST
- **ODATA Service**: ZWM_GET_RSV --> getData{}
- **Authentication**: Bearer Token
- **Response Format**: JSON with standard HTTP status codes
- **Base URL**: To be provided by development team

### **System Dependencies**
- **Development Dependencies**: 
  - C0149 - Out I/F Sending Picking Order from SAP to Satellite
  - C0155 - Create Reservation Request with approval
  - C0157 - Auto Create Reservation based on final approval
  - C0332 - OUT I/F Reservation - Item Level WO Level
  - C0333 - OUT I/F Reservation - Warehouse Task
  - C0334 - IN I/F Create Warehouse Order with simulation

- **Runtime Dependencies**: Same as development dependencies plus satellite app C0298 - Outstanding Reservation - Warehouse Apps

## **Data Structures**

### **Input Data Structure (Import Parameters)**
| Field | Type | Length | Mandatory | Description |
|-------|------|--------|-----------|-------------|
| I_WRH | CHAR | 4 | Optional | Warehouse Number |
| I_PLANT | CHAR | 4 | Mandatory | Plant |
| I_SLOC | CHAR | 4 | Mandatory | Storage Location |
| I_DCFLAG | CHAR | 3 | Mandatory | D/C Indicator (OUT=H/Credit, IN=S/Debit) |
| I_TRFLAG | CHAR | 1 | Optional | Transfer Note Flag (blank=Consumption, X=Transfer Note) |
| T_MVT (table) | CHAR | 3 | Optional | Movement Type(s) |
| T_RESERVATION (table) | NUMC | 10 | Optional | Reservation Number(s) |

### **Output Data Structure (Export Parameters)**
| Field | Type | Length | Description |
|-------|------|--------|-------------|
| E_TYPE | CHAR | 1 | Return Type (S=Success, E=Error) |
| E_MESSAGE | CHAR | 220 | Return Message |
| E_RESERVATION | NUMC | 10 | Reservation Number |
| E_MVT | CHAR | 3 | Movement Type |
| E_MVT_DESC | CHAR | 20 | Movement Type Description |
| E_RSV_TYPE | CHAR | 4 | Reservation Type |
| E_RSVTYPE_DESC | CHAR | 50 | Reservation Type Description |
| E_DOC_DATE | DATS | - | Document Date |
| E_REQ_DATE | DATS | - | Requirement Date (oldest from detail) |
| E_PLANT | CHAR | 4 | Plant |
| E_PLANT_DESC | CHAR | 30 | Plant Description |
| E_SLOC | CHAR | 4 | Storage Location |
| E_SLOC_DESC | CHAR | 16 | Storage Location Description |
| E_WRH | CHAR | 4 | Warehouse Number |
| E_WRH_DESC | CHAR | 40 | Warehouse Description |
| E_WP_RSV | CHAR | 1 | Wavepick Reservation Flag |
| E_COST_CENTER | CHAR | 10 | Cost Center |
| E_CC_DESC | CHAR | 20 | Cost Center Description |
| E_INT_ORDER | CHAR | 12 | Internal Order |
| E_IO_DESC | CHAR | 40 | Internal Order Description |
| E_ORDER_TYPE | CHAR | 4 | Order Type |
| E_ORDTYP_DESC | CHAR | 40 | Order Type Description |
| E_WBS_NO | CHAR | 24 | WBS Number |
| E_WBS_DESC | CHAR | 40 | WBS Description |
| E_ASSET_NO | CHAR | 12 | Asset Number |
| E_ASSET_DESC | CHAR | 50 | Asset Description |
| E_GL_ACC | CHAR | 10 | GL Account |
| E_GL_DESC | CHAR | 20 | GL Account Description |
| E_RECIPIENT | CHAR | 12 | Recipient |
| E_TEXT | CHAR | 200 | Header Text |
| E_RCV_PLANT | CHAR | 4 | Receiving Plant |
| E_RPLANT_DESC | CHAR | 30 | Receiving Plant Description |
| E_RCV_SLOC | CHAR | 4 | Receiving Storage Location |
| E_RSLOC_DESC | CHAR | 16 | Receiving Storage Location Description |
| E_RCV_WRH | CHAR | 4 | Receiving Warehouse Number |
| E_RWRH_DESC | CHAR | 40 | Receiving Warehouse Description |
| E_PICK_STATUS | CHAR | 20 | Picking Status (Unprocessed/In Progress/Completed) |

## **Process/Workflow Steps**

### **Validation Process**
1. **Warehouse Number Validation**: Validate against /SCWM/TMAPWHNUM table if provided
2. **Plant & Storage Location Validation**: Validate combination exists in T001L table
3. **D/C Indicator Conversion**: Convert satellite app format (IN/OUT) to SAP format (S/H)
4. **Transfer Flag Processing**: Handle consumption vs transfer note logic
5. **Movement Type Validation**: Validate against T158B and STVARV-ZMM_RSV_TCODE configuration
6. **Reservation Validation**: Validate against I_ReservationDocumentItem with status checks

### **Data Retrieval Process**
1. **Get Movement Type List**: Based on D/C indicator and transfer flag or from input parameters
2. **Get Reservation List**: Based on plant, storage location, and movement types
3. **Get Detail Data**: Primary source from ZMMT_T_RSVREQ_H with fallback to standard SAP views
4. **Get Descriptions**: Retrieve descriptive texts from various configuration tables
5. **Calculate Pick Status**: Complex logic involving delivery documents, warehouse orders, and status checks

## **Test Scenarios**

### **Positive Test Cases**
1. Get List Reservation Consumption OUT for Inventory Management Warehouse
2. Get List Reservation Consumption IN for Inventory Management Warehouse  
3. Get List Reservation Transfer Note OUT for Inventory Management Warehouse
4. Get List Reservation Transfer Note IN for Inventory Management Warehouse
5. Get List Reservation Consumption OUT for Extended Warehouse Management (EWM)
6. Get List Reservation Consumption IN for Extended Warehouse Management (EWM)
7. Get List Reservation Transfer Note OUT for Extended Warehouse Management (EWM)
8. Get List Reservation Transfer Note IN for Extended Warehouse Management (EWM)

### **Negative Test Cases**
9. Input Invalid Warehouse Number
10. Input Invalid Plant & Storage Location
11. Input Invalid Movement Type
12. Input Invalid Reservation Number
13. Input Parameter with no retrievable data

## **Error Handling and Exception Flows**

### **Error Messages**
| Error Type | Message (EN) | Message (ID) |
|------------|--------------|--------------|
| Invalid Warehouse | "Warehouse Number [I_WRH] does not exist" | "Warehouse Number [I_WRH] tidak ditemukan" |
| Invalid Plant/SLoc | "Plant [I_PLANT] and Storage Location [I_SLOC] does not exist" | "Plant [I_PLANT] dan Storage Location [I_SLOC] tidak ditemukan" |
| Invalid Movement Type | "Movement Type incorrect, please check your input" | "Movement Type tidak sesuai, periksa kembali input Anda" |
| Invalid Reservation | "Entered Reservation(s) not valid, please check your input" | "Nomor Reservasi tidak valid, periksa kembali input Anda" |
| No Data Found | "No Reservations found that meet the selection criteria" | "Tidak ada reservasi yang sesuai dengan kriteria" |
| Success | "Data successfully retrieved" | "Data berhasil ditampilkan" |

## **Security Requirements**

### **Authorization**
- **Plant Authorization**: Must be validated within satellite applications before API call
- **Storage Location Authorization**: Must be validated within satellite applications before API call  
- **Warehouse Authorization**: Must be validated within satellite applications before API call
- **Authentication**: Bearer Token required for API access

## **Data Sources and Table References**

### **Primary Tables**
- **ZMMT_T_RSVREQ_H**: Custom reservation request header table (primary data source)
- **I_ReservationDocumentItem**: Standard SAP reservation item view (fallback)
- **I_ReservationDocumentHeader**: Standard SAP reservation header view (fallback)

### **Configuration Tables**
- **/SCWM/TMAPWHNUM**: Warehouse number mapping
- **T001L**: Plant/Storage Location master
- **T156**: Movement type configuration  
- **T158B**: Movement type for reservation transactions
- **STVARV**: Configuration variables (ZMM_RSV_TCODE)
- **ZMMT_M_RSVTYPE**: Custom reservation type master
- **ZWMT_M_WPPCKRULE**: Wave pick configuration

### **Description Tables**
- **T156T**: Movement type descriptions
- **T001W**: Plant descriptions
- **T320**: Warehouse number assignments
- **/SCWM/T300T**: Warehouse descriptions
- **I_CostCenterText**: Cost center descriptions
- **I_OrderBasic**: Internal order descriptions
- **T003O**: Order type descriptions
- **I_WBSElementBasicData**: WBS descriptions
- **I_AssetTP**: Asset descriptions
- **I_GLAccountText**: GL account descriptions

## **Constraints and Assumptions**

### **Business Assumptions**
- Interface is for retrieving outstanding reservation data for satellite app visibility
- Without this interface, monitoring must be done directly in SAP
- Reservation data includes both consumption and transfer note types
- Pick status determination requires complex warehouse order status checking

### **Technical Constraints**
- Real-time processing only (no batch processing)
- Synchronous API calls only
- JSON response format mandatory
- Multi-language support required (EN/ID)
- Date format: DD-MM-YYYY in API response
- Requirement date selection: oldest date when multiple dates exist for single reservation