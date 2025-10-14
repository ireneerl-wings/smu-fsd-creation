# Requirements Analysis - SAP Material Master Status Automation Enhancement (Z0003)

## **System Requirements**

### **Functional Requirements**
- **Object ID**: Z0003 - Enhancement for automation on Material Master status change when cost is released (NPD Not Launched and Active Status)
- **System**: SAP (Master Data Governance stream area)
- **Complexity**: Low
- **Sub-Process**: MDM-010-030 - Material Master Data Automatic Changes
- **Primary Function**: Automatically update material master status at both plant level and client level based on predefined control parameters and business logic
- **Execution Method**: Background job running hourly every day
- **Access Methods**: 
  - Custom Transaction Code (to be defined)
  - Custom Fiori App (to be defined)

### **Non-Functional Requirements**
- **Performance**: System must handle total data validation equal to total material master for every plant created on S4
- **Execution Frequency**: Hourly background job execution every day
- **System Load**: Expected to process all active materials across all plants hourly
- **Complexity Level**: Low complexity enhancement

## **Interfaces / Integrations**

### **External System Dependencies**
- **Blue Yonder**: Integration for auto status change functionality
- **WINGS5 Group**: Integration for auto CR withdraw functionality

### **Internal SAP Dependencies**
- **Development Dependencies**: 
  - RICEFW Z0034 (Derivation Table)
  - RICEFW Z0035 (Derivation Rules)

### **BAPI Integration**
- **BAPI_MATERIAL_SAVEDATA**: Used for updating material status at both plant and client levels
  - **Plant Level Update Parameters**:
    - HEADDATA.MATERIAL = I_MATNR
    - PURCHASE_VIEW = "X"
    - PLANTDATA.PLANT = I_WERKS
    - PLANTDATA.PUR_STATUS = I_ZNEWMMSTA
    - PLANTDATX.PLANT = I_WERKS
    - PLANTDATX.PUR_STATUS = "X"
  - **Client Level Update Parameters**:
    - HEADDATA.MATERIAL = I_MATNR
    - BASIC_VIEW = "X"
    - CLIENTDATA.PUR_STATUS = I_ZNEWMSTAE
    - CLIENTDATAX.PUR_STATUS = "X"

## **Data Sources and Data Structures**

### **Input Data Sources**
1. **Table MARA** - General Material Data
   - MATNR (Material Number)
   - MSTAE (Material Client Status)
   - MTART (Material Type)

2. **Table MARC** - Plant Data for Material
   - MATNR (Material Number)
   - WERKS (Plant)
   - MMSTA (Material Plant Status)

3. **Table MBEW** - Material Valuation
   - MATNR (Material Number)
   - BWKEY (Valuation Area/Plant)
   - VPRSV (Price Control)
   - LPLPR (Planned Price)
   - VERPR (Moving Average Price)
   - BWTAR (Valuation Type)

4. **Table ZMDT_MSTAT** - Control Parameter Table for Material Status
   - ZPROGID (Program ID)
   - ZCURMMSTA (Current Status)
   - ZNEWMMSTA (New Status)
   - MTART (Material Type)

### **Custom Tables Structure**

#### **ZMDT_MSTAT - Control Parameter Table**
| Field | Technical Name | Type | Length | Key | Source | Search Help |
|-------|---------------|------|--------|-----|--------|-------------|
| Program ID | ZPROGID | CHAR | 20 | Yes | N/A | N/A |
| Current Status | ZCURMMSTA | CHAR | 2 | Yes | MARA-MSTAE | T141T-MMSTA and MTSTB |
| New Status | ZNEWMMSTA | CHAR | 2 | Yes | T141T | T141T-MMSTA and MTSTB |
| Material Type | MTART | CHAR | 4 | Yes | T134T | T134T-MTART and MTBEZ |

#### **ZMDT_MSTAT_RPT - Job Result Table**
| Field | Technical Name | Type | Length | Key | Source |
|-------|---------------|------|--------|-----|--------|
| Program ID | ZPROGID | CHAR | 20 | Yes | I_ZPROGID |
| Date | ZDATE | CHAR | 8 | Yes | SY_DATUM |
| Time | ZTIME | CHAR | 8 | Yes | SY_UZEIT |
| Item | ZITEM | CHAR | 8 | Yes | Running number |
| Material Number | MATNR | CHAR | 40 | No | I_MATNR |
| Material Type | MTART | CHAR | 4 | No | I_MTART |
| Plant | WERKS | CHAR | 4 | No | I_WERKS |
| Current Plant Status | ZCURMMSTA | CHAR | 2 | No | I_MMSTA |
| Current Client Status | ZCURMSTAE | CHAR | 2 | No | I_MSTAE |
| New Plant Status | ZNEWMMSTA | CHAR | 2 | No | I_NEWMMSTA |
| New Client Status | ZNEWMSTAE | CHAR | 2 | No | I_NEWMSTAE |
| Plant Job Status | ZPLTSTAT | CHAR | 1 | No | Return status 1st Job |
| Plant Job Detail | ZPLTDETAIL | CHAR | 220 | No | Return detail 1st Job |
| Client Job Status | ZCLTSTAT | CHAR | 1 | No | Return status 2nd Job |
| Client Job Detail | ZCLTDETAIL | CHAR | 220 | No | Return detail 2nd Job |

### **Internal Table Structure**
- I_ZPROGID (Program ID)
- I_MATNR (Material Number)
- I_MTART (Material Type)
- I_WERKS (Plant)
- I_MMSTA (Current Plant Status)
- I_ZNEWMMSTA (New Plant Status)
- I_MSTAE (Current Client Status)
- I_ZNEWMSTAE (New Client Status)

### **Output Data Structure**
- **ALV Report**: Contains Type and Messages columns
- **Excel Download**: Available for result report
- **Success Messages**:
  - Plant Level: "Material [I_MATNR] Plant [I_WERKS], status [I_MMSTA] update to [I_ZNEWMMSTA]"
  - Client Level: "Material [I_MATNR], status [I_MSTAE] update to [I_ZNEWMSTAE]"

## **Process or Workflow Steps**

### **Main Process Flow**
1. **MDM-010-030-010**: Query All Active Materials
2. **MDM-010-030-020**: Check the Group of Companies
3. **MDM-010-030-030**: Check if There is Missing Plants
4. **MDM-010-030-040**: Automatic Plant Extend
5. **MDM-010-030-050**: Automatic Material Status Update
6. **MDM-010-030-060**: Automatic CR Withdraw
7. **MDM-010-020**: Material Master Data Maintenance
8. **Email Notifications**

### **Detailed Program Logic**

#### **Step 1: Data Extraction**
- **1a**: Extract material numbers and client status from MARA where material type matches ZMDT_MSTAT entries for Program IDs "Z0003-01" (Finished Goods) and "Z0003-02" (Non-Finished Goods)
- **1b**: Join MARA and MARC tables to get plant-specific material data where plant status matches control parameters
- **1c**: Filter materials based on price control criteria:
  - **Finished Goods (Z0003-01)**: VPRSV = "S" and (LPLPR ≠ 0 or VERPR ≠ 0) and BWTAR = " "
  - **Non-Finished Goods (Z0003-02)**: VPRSV = "V" and (LPLPR ≠ 0 or VERPR ≠ 0) and BWTAR = " "

#### **Step 2: Plant Level Status Update**
- Check if I_MMSTA ≠ I_ZNEWMMSTA
- If different, call BAPI_MATERIAL_SAVEDATA with plant-specific parameters
- Process return messages and create appropriate success/error messages

#### **Step 3: Client Level Status Update**
- Check if I_MSTAE ≠ I_ZNEWMSTAE
- If different, call BAPI_MATERIAL_SAVEDATA with client-specific parameters
- Process return messages and create appropriate success/error messages

#### **Step 4: Result Reporting**
- Generate ALV report with all messages
- Store results in ZMDT_MSTAT_RPT table
- Enable Excel download functionality

## **Test Scenarios / Validation Criteria**

### **Positive Test Cases**
1. **Test 1**: Update material status for Finished Goods
   - **Steps**: Run program based on table maintenance on ZMDT_MSTAT
   - **Expected Result**: Program successfully updates material status

2. **Test 2**: Update material status for Non-Finished Goods
   - **Steps**: Run program based on table maintenance on ZMDT_MSTAT
   - **Expected Result**: Program successfully updates material status

### **Negative Test Cases**
3. **Test 3**: Failed update material status
   - **Steps**: Before running program, open material data in change mode via MM02 in parallel
   - **Expected Result**: Program fails to update material status due to lock

## **Error Handling and Exception Flows**

### **Error Messages**
| No. | Exception Description | Message Type | Language | Message Text |
|-----|----------------------|--------------|----------|--------------|
| 1 | Success update material status in client level | S | EN | Material [I_MATNR], status [I_MSTAE] update to [I_ZNEWMMSTA] |
| 2 | Success update material status in plant level | S | EN | Material [I_MATNR] Plant [I_WERKS], status [I_MSTAE] update to [I_ZNEWMSTAE] |
| 3 | BAPI error messages | E | EN | Error messages from BAPI_MATERIAL_SAVEDATA RETURN parameter |

### **Error Handling Logic**
- **BAPI Return Processing**: Check TYPE field in RETURN parameter
  - If TYPE = "S": Create success message
  - If TYPE = "E": Display error message from RETURN
- **Data Validation**: Skip processing if current status equals new status
- **Lock Handling**: Process BAPI return messages for material lock situations

## **Security Requirements**

### **Authorization Requirements**
- Authorization objects and fields to be defined (table provided but not populated in document)
- Access control for custom transaction code and Fiori app
- Security access to affected transactions (MM02, material master maintenance)

### **Auditing and Control Requirements**
- Audit control requirements to be defined for balancing legacy system controls with new system
- All job results stored in ZMDT_MSTAT_RPT for audit trail

## **Performance, Scalability, Reliability Requirements**

### **Performance Requirements**
- **Execution Frequency**: Hourly background job execution
- **Data Volume**: Process all material masters for every plant in S4
- **Response Time**: Must complete within hourly window

### **Scalability Requirements**
- System must handle growing number of materials and plants
- Background job must scale with increasing data volume

### **Reliability Requirements**
- **Error Recovery**: Comprehensive error handling and logging
- **Data Integrity**: Ensure material status updates are consistent
- **Monitoring**: Result reporting and audit trail capabilities

## **User Interaction Requirements**

### **Fiori Application Features**
- **Display Mode**: View control parameter data
- **Change Mode**: Modify control parameter data
- **Upload Mode**: Mass upload via template
- **Template Download**: Excel template for mass maintenance
- **File Browser**: Upload file selection
- **Pre-Upload Validation**: ALV screen for data validation before execution

### **Screen Navigation Flow**
- Initial Screen → Display/Change/Upload options
- Display ↔ Change screen switching
- Upload screen with template download and file browse
- File explorer dialogs for download/upload
- Pre-upload ALV validation screen
- Result reporting screen with filter options

### **Report Interface**
- **Filter Fields**: Program ID, Job Date, Job Time, Material Number, Plant, Plant Job Status, Client Job Status
- **Output Display**: 14-column ALV grid with all job result details
- **Download Capability**: Excel export functionality

## **Dependencies and Assumptions**

### **Configuration Dependencies**
- Material master data configuration (Material type, Material status, Price control)
- Sales type configuration
- Movement type configuration

### **Development Dependencies**
- RICEFW Z0034 and Z0035 (Derivation Table & Rules) must be completed first

### **Business Assumptions**
- Material statuses are critical for lifecycle tracking, inventory control, warehouse zone management, and reporting/analysis
- Automatic updates ensure accuracy, consistency, and timeliness compared to manual processes

### **Business Risks**
- **Without Development**: Increased probability of inaccurate and inconsistent data during manual material status changes
- **Business Impact**: Inaccurate purchasing, inventory management issues, cross-functional miscommunication

### **Execution Dependencies**
- Background job setup with hourly execution schedule
- Proper authorization and access control implementation
- Integration with Blue Yonder and WINGS5 Group systems