# Extracted Requirements from SAP Functional Specification Document

## **System Requirements**

### **Functional Requirements**
- **Object ID**: A0001 - Enhancement for Custom Contract and Custom Order Unit in Purchase Order with Contract
- **System**: SAP system enhancement (not satellite application)
- **Stream Area**: Procurement
- **Complexity**: High
- **Impacted Sub-Process**: A-030-060 Outline Agreement
- **Business Process**: Accommodate contracts based on consumed weight of packaging material (KG) while PO transactions are based on PCS/ROL and by specification
- **Contract Processing**: Support external material group and item splitting per MID within same external material group
- **Unit Conversion**: Automatic conversion between PO order unit and contract order unit
- **Halfway Design Support**: Accommodate non-go live companies through distributed quantity identification

### **Non-Functional Requirements**
- **Expected System Load**: Average load execution
- **Performance**: System must handle automatic field population and validation in real-time during contract creation
- **Reliability**: Manual input reduction during contract creation to minimize errors

## **Data Structures**

### **Input Data Structures**

#### **Custom Table: ZMM_MAP_MATGROUP (Material Group Mapping)**
| Field Name | Field Description | Data Type/Size | Key | Remarks |
|------------|-------------------|----------------|-----|---------|
| MTART | Material Group | MARA-MTART | Key | Primary key field |
| EXTWG | External Material Group | MARA-EXTWG | Key | Primary key field |
| ZEXT_GROUP_DESC | External Material Group Description | Char (50) | No | Long description field |
| ZGEN_SPEC | General Specification | Char (60) | No | Used in PO form, BI reports, MDG |
| ZSPEC_CODE | Specification Code | Char (150) | No | Additional specification data |
| ZWIDTH | Width (mm) | Num (5) | No | Dimension specification |
| ZHEIGHT | Height (mm) | Num (5) | No | Dimension specification |
| ZLENGTH_MM | Length (mm) | Num (5) | No | Dimension specification |
| ZLENGTH_M | Length (M) | Num (5) | No | Dimension specification |
| ZBOTTOM | Bottom (mm) | Num (5) | No | Dimension specification |
| ZCOLOR | Color | Num (2) | No | Color specification |
| ZFINISHING | Finishing | Char (50) | No | Finishing specification |
| ZUOM | UoM | Char (3) | No | Unit of measure |

#### **Custom Fields in EKPO Table (Purchase Contract/RFQ)**
| Field Name | Field Description | Data Type/Size | Remarks |
|------------|-------------------|----------------|---------|
| ZEXTWG | External Material Group | MARA-EXTWG | Input field |
| ZEXT_GROUP_DESC | External Material Group Description | Char (60) | Display only |
| ZGEN_SPEC | General Specification | Char (150) | Input field |
| ZSPEC_CODE | Specification Code | Num (5) | Input field |
| ZWIDTH | Width (mm) | Num (5) | Input field |
| ZHEIGHT | Height (mm) | Num (5) | Input field |
| ZLENGTH_MM | Length (mm) | Num (5) | Input field |
| ZLENGTH_M | Length (M) | Num (5) | Input field |
| ZBOTTOM | Bottom (mm) | Num (2) | Input field |
| ZCOLOR | Color | Char (50) | Input field |
| ZFINISHING | Finishing | Char (60) | Input field |
| ZPROC_PARTNER | Related Company Buyer | BUT000-PARTNER | For non-go live companies |

#### **Search Help Input Structure**
- **External Material Group**: Input field [A]
- **Material Group**: Input field [B]

#### **Function Module Input for PIR Conversion**
| Field | Input Value |
|-------|-------------|
| OBJECTKEY | [EKPO-MATNR] + [EKPO-LIFNR] |
| OBJECTTABLE | 'EINA' |
| CLASSNUM | '057' |
| CLASSTYPE | 'CL_PIR' |

### **Output Data Structures**

#### **Search Help Output Structure**
| Column | Description | Label |
|--------|-------------|-------|
| External Material Group | External material group code | [R-A] |
| Ext. Mat Group | External material group short | [R-B] |
| Material Group | Material group code | [R-C] |
| Mat. Group Desc | Material group description | [R-D] |

#### **Function Module Output**
- **ALLOCVALUESNUM**: Contains conversion values
- **ALLOCVALUESNUM-VALUE_FROM**: Conversion value for characteristic 'CT_KONVERSI'

#### **Automatic Field Population Output**
When external material group is selected:
1. **Material group (EKPO-MATKL)**: Automatically filled
2. **External material group (EKPO-ZEXTWG)**: Automatically filled
3. **Short text (EKPO-TXZ01)**: Automatically filled

## **Interfaces and Integrations**

### **SAP Standard Interfaces**
- **Transaction Codes**: ME31K, ME32K, ME33K (Contract), ME21N, ME22N, ME23N (Purchase Order)
- **Fiori Applications**: Manage Purchase Contract, Manage Purchase Order, Manage RFQs
- **Standard Tables**: EKPO (Purchase Document Item), EINA (Purchasing Info Record), MARA (Material Master)

### **Custom Integrations**
- **BADI Implementations**:
  - MM_PUR_S4_CTR_MODIFY_ITEM: For automatic field modification
  - MM_PUR_S4_CTR_CHECK: For contract validation
  - ME_PROCESS_PO_CUST: For PO unit conversion
- **Function Module**: BAPI_OBJCL_GETDETAIL for PIR characteristic retrieval

## **Process and Workflow Steps**

### **Contract Creation Workflow**
1. User accesses contract transaction (ME31K/ME32K/ME33K)
2. User presses F4 on material group field
3. Custom search help displays external material groups
4. User selects external material group
5. System automatically populates:
   - Material group (EKPO-MATKL)
   - External material group (EKPO-ZEXTWG)
   - Short text (EKPO-TXZ01)
6. User completes other contract fields
7. System validates contract data
8. Contract is saved if validation passes

### **PO Unit Conversion Workflow**
1. System retrieves PIR characteristic using BAPI_OBJCL_GETDETAIL
2. System extracts conversion value for 'CT_KONVERSI' characteristic
3. System converts value to integer
4. System updates order unit ↔ order price unit in PO
5. System modifies numerator for order price unit (MEPOITEM-BPUMZ)

### **Validation Workflow**
1. System checks if item category = 'M'
2. System validates plant and related company buyer fields
3. System displays appropriate error messages if validation fails
4. Process continues if validation passes

## **Test Scenarios and Validation Criteria**

### **Positive Test Cases**
1. **Search Help Functionality**:
   - **Steps**: Press F4 in material group field, select external material group
   - **Expected**: Material group, external material group, and description automatically filled

2. **Business Partner Input**:
   - **Steps**: Input business partner for non-go live company
   - **Expected**: Business partner can be successfully inputted

3. **Contract Save with Complete Data**:
   - **Steps**: Complete all required fields (plant, external material group, BP), press save
   - **Expected**: Contract saves successfully with success message

### **Negative Test Cases**
1. **Missing Plant or BP**:
   - **Steps**: Leave both plant and BP empty, press save
   - **Expected**: Error message "Plant or related company buyer must be filled in for contract with item category M"

2. **Both Plant and BP Filled**:
   - **Steps**: Fill both plant and BP fields, press save
   - **Expected**: Error message "Please input only plant or related company buyer for contract with item category M"

## **Error Handling and Exception Flows**

### **Validation Rules**
- **Condition**: Applies only to line items with item category (EPSTP) = 'M'
- **Rule 1**: If plant is empty AND related company buyer is empty → Display error
- **Rule 2**: If plant is not empty AND related company buyer is not empty → Display error

### **Error Messages**
| No. | Exception Description | Message Type | Language | Message Text |
|-----|----------------------|--------------|----------|--------------|
| 1 | Plant or BP not filled in contract line item | E | EN | Plant or related company buyer must be filled in for contract with item category M |
| 2 | Both plant and BP filled in contract line item | E | EN | Please input only plant or related company buyer for contract with item category M |

## **Security Requirements**

### **Authorization**
- **Authorization Objects**: N/A (no specific authorization objects mentioned)
- **Access Control**: Standard SAP transaction and Fiori app security applies

### **Auditing and Control Requirements**
- **Auditing**: N/A (no specific auditing requirements mentioned)
- **Controls**: Standard SAP controls for procurement processes

## **User Interaction Requirements**

### **User Interface Elements**
- **Custom Search Help**: Material group field with F4 functionality
- **Field Locations**: 
  - External material group field in contract items section
  - Related company buyer field in contract items section
- **Field Behavior**:
  - External material group description: Display only
  - Automatic population of fields upon selection
- **User Roles**: Contract creators, procurement team members

### **Accessibility**
- Standard SAP accessibility features apply
- Custom fields follow SAP field design standards

## **Dependencies and Prerequisites**

### **Configuration Dependencies**
- **Plant Configuration**: Required for plant-based contracts
- **Outline Agreement Type**: Must be configured
- **Item Category for Outline Agreement**: Must be configured

### **Development Dependencies**
- **Custom Table**: ZMM_MAP_MATGROUP must be created and maintained
- **Transaction Code**: Required for maintaining custom table
- **BADI Implementations**: Must be implemented for functionality

### **Execution Dependencies**
- **Master Data**: Material master, vendor master, purchasing info records
- **Business Partner Data**: Required for non-go live companies

## **Assumptions and Constraints**

### **Business Assumptions**
- Contracts dealt based on consumed weight of packaging material (KG)
- PO transactions based on PCS/ROL and by specification
- Procurement team creates contracts for external material groups
- PO items split per MID within same external material group
- Related company buyer only filled for companies not in S4 (no plant information in BP)

### **Technical Constraints**
- Enhancement applies to SAP system only
- High complexity development
- Must maintain compatibility with standard SAP procurement processes

### **Operational Constraints**
- Manual input during contract creation must be minimized
- System must support both go-live and non-go-live companies
- Conversion between PO order unit and contract order unit must be seamless